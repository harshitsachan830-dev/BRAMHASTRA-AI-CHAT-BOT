import os
import re
from io import BytesIO
import numpy as np

from PIL import Image, ImageOps, ImageFilter
from pypdf import PdfReader
from backend.services.llm_engine import ask_ai

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import easyocr
except ImportError:
    easyocr = None


_OCR_READER = None


def _get_ocr_reader():
    global _OCR_READER
    if _OCR_READER is None and easyocr is not None:
        _OCR_READER = easyocr.Reader(["en"], gpu=False)
    return _OCR_READER


def _reset_file_pointer(file) -> None:
    try:
        file.seek(0)
    except Exception:
        pass


def _normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _looks_like_meaningful_text(text: str) -> bool:
    cleaned = _normalize_text(text)
    if len(cleaned) < 20:
        return False

    alpha_count = sum(ch.isalpha() for ch in cleaned)
    digit_count = sum(ch.isdigit() for ch in cleaned)
    word_count = len(cleaned.split())

    return alpha_count >= 8 and (word_count >= 4 or digit_count >= 3)


def _prepare_image_for_ocr(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image)
    image = image.convert("L")
    image = ImageOps.autocontrast(image)
    image = image.filter(ImageFilter.MedianFilter(size=3))
    image = image.filter(ImageFilter.SHARPEN)
    return image


def _extract_text_from_txt(file) -> str:
    _reset_file_pointer(file)
    raw = file.read()
    if isinstance(raw, str):
        return _normalize_text(raw)
    return _normalize_text(raw.decode("utf-8", errors="ignore"))


def _extract_text_from_pdf_direct(pdf_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        pages = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(page_text)
        return _normalize_text("\n\n".join(pages))
    except Exception:
        return ""


def _extract_images_from_pdf(pdf_bytes: bytes) -> list[Image.Image]:
    images = []
    if fitz is None:
        return images

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page_index in range(len(doc)):
            page = doc.load_page(page_index)
            pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
            image = Image.open(BytesIO(pix.tobytes("png")))
            images.append(image)
        doc.close()
    except Exception:
        return []

    return images


def _extract_text_with_ocr_from_images(images: list[Image.Image]) -> str:
    reader = _get_ocr_reader()
    if reader is None:
        return ""

    extracted_chunks = []
    for index, image in enumerate(images, start=1):
        try:
            prepared = _prepare_image_for_ocr(image)
            prepared_np = np.array(prepared)
            result = reader.readtext(
                prepared_np,
                detail=0,
                paragraph=True,
                text_threshold=0.5,
                low_text=0.2,
                link_threshold=0.3,
                mag_ratio=1.5,
            )
            if result:
                extracted_chunks.append("\n".join(result))
            else:
                print(f"OCR returned no text for PDF page image {index}")
        except Exception as e:
            print(f"OCR failed for PDF page image {index}: {e}")
            continue

    return _normalize_text("\n\n".join(extracted_chunks))


def _extract_text_from_image_file(file) -> tuple[str, str]:
    reader = _get_ocr_reader()
    if reader is None:
        return "", "image-ocr-unavailable"

    try:
        _reset_file_pointer(file)
        image = Image.open(BytesIO(file.read()))
        prepared = _prepare_image_for_ocr(image)
        prepared_np = np.array(prepared)
        result = reader.readtext(
            prepared_np,
            detail=0,
            paragraph=True,
            text_threshold=0.5,
            low_text=0.2,
            link_threshold=0.3,
            mag_ratio=1.5,
        )
        extracted_text = _normalize_text("\n".join(result))
        print("Image OCR raw result count:", len(result))
        print("Image OCR preview:", extracted_text[:1000])
        return extracted_text, "image-ocr"
    except Exception as e:
        print("Image OCR failed:", e)
        return "", "image-ocr-failed"


def extract_text_from_pdf(file) -> tuple[str, str]:
    _reset_file_pointer(file)
    pdf_bytes = file.read()

    direct_text = _extract_text_from_pdf_direct(pdf_bytes)
    if _looks_like_meaningful_text(direct_text):
        return direct_text, "direct"

    images = _extract_images_from_pdf(pdf_bytes)
    print("PDF rendered image count:", len(images))
    ocr_text = _extract_text_with_ocr_from_images(images)
    print("PDF OCR preview:", ocr_text[:1000])

    if _looks_like_meaningful_text(ocr_text):
        return ocr_text, "ocr"

    combined = _normalize_text(f"{direct_text}\n\n{ocr_text}")
    return combined, "combined"


def _build_analysis_prompt(content: str) -> str:
    safe_content = content[:18000]
    return f"""
You are a medical report analyzer.

Analyze the uploaded medical report carefully.
The report may come from OCR and can contain noise, broken words, or handwritten/printed mixed content.
Infer the meaning carefully and do not invent values that are not present.
If something is unclear due to OCR quality, clearly mention that.

Return in this exact format:

Summary:
- short summary

Important Findings:
- point 1
- point 2

Abnormal Values / Concerns:
- point 1
- point 2

Risk Level:
- Low / Moderate / High

Recommended Next Steps:
- point 1
- point 2

When to See Doctor:
- point 1
- point 2

Medical report text:
{safe_content}
"""


def analyze_uploaded_report(file) -> dict:
    try:
        filename = (file.filename or "").lower()
        extension = os.path.splitext(filename)[1]
        extraction_method = "unknown"

        if extension == ".txt":
            content = _extract_text_from_txt(file)
            extraction_method = "text"
        elif extension == ".pdf":
            content, extraction_method = extract_text_from_pdf(file)
        elif extension in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}:
            content, extraction_method = _extract_text_from_image_file(file)
        else:
            return {
                "type": "report",
                "title": "Medical Report Analyzer",
                "answer": "This file type is not supported yet. Please upload a TXT, PDF, JPG, JPEG, PNG, WEBP, BMP, or TIFF report.",
                "risk_level": "Moderate",
                "health_score": 60,
                "explanation": "Report upload worked, but parser for this file type is not enabled yet.",
                "next_steps": [
                    "Upload a .txt, .pdf, .jpg, .jpeg, .png, .webp, .bmp, or .tiff report.",
                    "For the best results, upload a clear scan or a cropped report image."
                ],
                "doctor_recommendation": {
                    "specialist": "General Physician",
                    "urgency": "Moderate",
                    "action": "Share the report with a doctor for full interpretation."
                }
            }

        content = _normalize_text(content)

        print("========== REPORT DEBUG ==========")
        print("Filename:", filename)
        print("Extension:", extension)
        print("Extraction method:", extraction_method)
        print("Content length:", len(content))
        print("Content preview:", content[:1000])
        print("fitz available:", fitz is not None)
        print("easyocr available:", easyocr is not None)
        print("Meaningful text check:", _looks_like_meaningful_text(content))
        print("==================================")

        if not _looks_like_meaningful_text(content):
            explanation = (
                "The file was uploaded, but no usable report text was found. "
                "This usually happens with low-quality scans, very unclear handwriting, poor photo angle, "
                "or when OCR could not confidently read enough content."
            )
            if extraction_method in {"image-ocr-unavailable", "ocr", "combined", "image-ocr", "image-ocr-failed"} and easyocr is None:
                explanation = (
                    "The file was uploaded, but OCR support is not available on the server, "
                    "so image-based reports cannot be read yet."
                )

            return {
                "type": "report",
                "title": "Medical Report Analyzer",
                "answer": "Could not extract enough readable text from the uploaded report.",
                "risk_level": "Unknown",
                "health_score": 50,
                "explanation": explanation,
                "next_steps": [
                    "Try a clearer PDF, TXT, or cropped image file.",
                    "If this is a camera photo, crop only the report and upload it again.",
                    "Use a flat, bright, front-facing scan for better OCR accuracy."
                ],
                "doctor_recommendation": {
                    "specialist": "General Physician",
                    "urgency": "Moderate",
                    "action": "Use a clearer report or enable OCR support for scanned reports."
                }
            }

        prompt = _build_analysis_prompt(content)
        ai_result = ask_ai(prompt, mode="health")

        if ai_result.get("success"):
            answer = ai_result.get("answer", "").strip()
            answer_lower = answer.lower()

            risk_level = "Moderate"
            health_score = 65

            if any(word in answer_lower for word in ["high", "critical", "urgent", "emergency"]):
                risk_level = "High"
                health_score = 35
            elif "low" in answer_lower and "moderate" not in answer_lower and "high" not in answer_lower:
                risk_level = "Low"
                health_score = 85

            explanation_map = {
                "text": "AI-generated structured analysis of uploaded text report.",
                "direct": "AI-generated structured analysis of machine-readable PDF report.",
                "ocr": "AI-generated structured analysis of OCR-extracted scanned PDF report.",
                "combined": "AI-generated structured analysis using both direct PDF extraction and OCR fallback.",
                "image-ocr": "AI-generated structured analysis of OCR-extracted report image.",
            }

            return {
                "type": "report",
                "title": "Medical Report Analysis",
                "answer": answer,
                "risk_level": risk_level,
                "health_score": health_score,
                "explanation": explanation_map.get(extraction_method, "AI-generated structured analysis of uploaded medical report."),
                "next_steps": [
                    "Review highlighted findings carefully.",
                    "Consult a doctor for confirmation and treatment advice."
                ],
                "doctor_recommendation": {
                    "specialist": "General Physician" if risk_level != "High" else "Specialist / Physician",
                    "urgency": "Low" if risk_level == "Low" else ("Moderate" if risk_level == "Moderate" else "High"),
                    "action": "Show this report to a qualified doctor, especially if symptoms are present."
                }
            }

        return {
            "type": "report",
            "title": "Medical Report Analysis",
            "answer": "AI could not analyze the report properly.",
            "risk_level": "Unknown",
            "health_score": 50,
            "explanation": "Analysis failed after text extraction.",
            "next_steps": [
                "Try again with cleaner report text.",
                "Consult a doctor directly if the report has abnormal values."
            ],
            "doctor_recommendation": {
                "specialist": "General Physician",
                "urgency": "Moderate",
                "action": "Consult a doctor for proper interpretation."
            }
        }

    except Exception as e:
        return {
            "type": "report",
            "title": "Medical Report Analysis",
            "answer": "Error while analyzing report.",
            "risk_level": "Unknown",
            "health_score": 50,
            "explanation": str(e),
            "next_steps": [
                "Try again with a clearer file.",
                "Make sure OCR dependencies are installed for scanned, image-based, or handwritten reports."
            ],
            "doctor_recommendation": {
                "specialist": "General Physician",
                "urgency": "Moderate",
                "action": "Retry with a better quality report file."
            }
        }