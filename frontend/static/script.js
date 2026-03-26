let latestResult = null;
let stream = null;
let isTyping = false;

// ---------------- HELPERS ----------------
function getEl(id) {
    return document.getElementById(id);
}

function setText(id, text) {
    const el = getEl(id);
    if (el) el.innerText = text;
}

function clearList(id) {
    const el = getEl(id);
    if (el) el.innerHTML = "";
}

function setButtonState(disabled = true) {
    document.querySelectorAll(".btn").forEach(btn => {
        btn.disabled = disabled;
        btn.style.opacity = disabled ? "0.7" : "1";
        btn.style.pointerEvents = disabled ? "none" : "auto";
    });
}

function showToast(message) {
    let toast = document.getElementById("appToast");

    if (!toast) {
        toast = document.createElement("div");
        toast.id = "appToast";
        toast.style.position = "fixed";
        toast.style.bottom = "24px";
        toast.style.right = "24px";
        toast.style.padding = "14px 18px";
        toast.style.borderRadius = "14px";
        toast.style.background = "rgba(15,23,42,0.95)";
        toast.style.color = "#fff";
        toast.style.border = "1px solid rgba(255,255,255,0.15)";
        toast.style.boxShadow = "0 14px 30px rgba(0,0,0,0.25)";
        toast.style.zIndex = "9999";
        toast.style.fontSize = "14px";
        toast.style.maxWidth = "300px";
        toast.style.backdropFilter = "blur(12px)";
        toast.style.transition = "all 0.3s ease";
        document.body.appendChild(toast);
    }

    toast.innerText = message;
    toast.style.opacity = "1";
    toast.style.transform = "translateY(0)";

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(10px)";
    }, 2200);
}

function resetDoctorBox() {
    setText("doctorSpecialist", "-");
    setText("doctorUrgency", "-");
    setText("doctorAction", "-");
}

function resetResult(title = "Thinking...", answer = "Generating response...") {
    setText("resultTitle", title);
    setText("resultAnswer", answer);
    setText("riskLevel", "-");
    setText("explanation", "-");
    setText("scoreText", "0 / 100");

    const meter = getEl("meterFill");
    if (meter) {
        meter.style.width = "0%";
        meter.style.background = "#334155";
    }

    clearList("nextSteps");
    resetDoctorBox();
}

async function typeText(elementId, text, speed = 8) {
    const el = getEl(elementId);
    if (!el) return;

    isTyping = true;
    el.innerText = "";

    for (let i = 0; i < text.length; i++) {
        el.innerText += text[i];
        await new Promise(resolve => setTimeout(resolve, speed));
    }

    isTyping = false;
}

function pulseResultCard() {
    const card = document.querySelector(".result-card");
    if (!card) return;

    card.style.transform = "scale(0.995)";
    card.style.transition = "transform 0.2s ease";

    setTimeout(() => {
        card.style.transform = "scale(1)";
    }, 180);
}

function applyRiskStyle(riskLevel, score) {
    const meterFill = getEl("meterFill");
    const riskEl = getEl("riskLevel");

    if (!meterFill || !riskEl) return;

    let color = "#ef4444";

    if (riskLevel === "Emergency") {
        color = "#ef4444";
    } else if (score >= 80) {
        color = "#22c55e";
    } else if (score >= 55) {
        color = "#f59e0b";
    } else {
        color = "#ef4444";
    }

    meterFill.style.background = color;
    riskEl.style.color = color;
    riskEl.style.fontWeight = "800";
}

function showTyping(show = true, text = "AI is analyzing...") {
    const indicator = getEl("typingIndicator");
    if (!indicator) return;

    const label = indicator.querySelector("p");
    if (label) label.innerText = text;

    indicator.style.display = show ? "flex" : "none";
}

function animateResultCard() {
    const card = document.querySelector(".result-card");
    if (!card) return;

    card.classList.add("result-animate");
    setTimeout(() => {
        card.classList.remove("result-animate");
    }, 500);
}

function addFadeInEffects() {
    [
        "resultAnswer",
        "riskLevel",
        "explanation",
        "scoreText",
        "nextSteps",
        "doctorSpecialist",
        "doctorUrgency",
        "doctorAction"
    ].forEach(id => {
        const el = getEl(id);
        if (!el) return;

        el.classList.remove("fade-in-up");
        void el.offsetWidth;
        el.classList.add("fade-in-up");
    });
}

function fillQuestion(text) {
    const input = getEl("userInput");
    if (input) input.value = text;
    input?.focus();
}

// ---------------- CHAT ----------------
async function sendMessage() {
    const input = getEl("userInput");
    const message = input?.value.trim();

    if (!message) {
        showToast("Please enter a question.");
        return;
    }

    resetResult("Thinking...", "Generating smart health response...");
    showTyping(true, "AI is thinking...");
    setButtonState(true);
    pulseResultCard();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        latestResult = data;
        await renderResult(data);
        showToast("Analysis complete");
    } catch (error) {
        console.error("Fetch error:", error);
        setText("resultTitle", "Error");
        setText("resultAnswer", "Something went wrong while fetching response.");
        setText("riskLevel", "Error");
        setText("explanation", error.message);
        showToast("Failed to fetch response");
    } finally {
        showTyping(false);
        setButtonState(false);
    }
}

// ---------------- RESULT RENDER ----------------
async function renderResult(data) {
    pulseResultCard();

    setText("resultTitle", data.title || "Result");
    await typeText("resultAnswer", data.answer || "-", 4);

    setText("riskLevel", data.risk_level || "-");
    setText("explanation", data.explanation || "-");

    const score = data.health_score || 0;
    setText("scoreText", `${score} / 100`);

    const meterFill = getEl("meterFill");
    if (meterFill) {
        requestAnimationFrame(() => {
            meterFill.style.width = `${score}%`;
        });
    }

    applyRiskStyle(data.risk_level, score);

    const stepsList = getEl("nextSteps");
    if (stepsList) {
        stepsList.innerHTML = "";

        if (data.next_steps && data.next_steps.length > 0) {
            data.next_steps.forEach((step, index) => {
                const li = document.createElement("li");
                li.innerText = step;
                li.style.opacity = "0";
                li.style.transform = "translateY(8px)";
                li.style.transition = "all 0.3s ease";
                stepsList.appendChild(li);

                setTimeout(() => {
                    li.style.opacity = "1";
                    li.style.transform = "translateY(0)";
                }, 90 * index);
            });
        } else {
            const li = document.createElement("li");
            li.innerText = "No next steps available.";
            stepsList.appendChild(li);
        }
    }

    const doctor = data.doctor_recommendation || {};
    setText("doctorSpecialist", doctor.specialist || "-");
    setText("doctorUrgency", doctor.urgency || "-");
    setText("doctorAction", doctor.action || "-");

    animateResultCard();
    addFadeInEffects();
}

// ---------------- PDF ----------------
async function downloadReport() {
    if (!latestResult) {
        showToast("First generate a result.");
        return;
    }

    setButtonState(true);

    try {
        const response = await fetch("/generate-report", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(latestResult)
        });

        const data = await response.json();

        if (data.report_url) {
            window.open(data.report_url, "_blank");
            showToast("PDF report generated");
        } else {
            showToast("Failed to generate report.");
        }
    } catch (error) {
        console.error("Download error:", error);
        showToast("Error while generating report.");
    } finally {
        setButtonState(false);
    }
}

// ---------------- HOSPITAL ----------------
function findHospitals() {
    const fallback = "https://www.google.com/maps/search/nearby+hospitals";
    showToast("Opening nearby hospitals...");

    if (!navigator.geolocation) {
        window.location.href = fallback;
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            const mapsUrl = `https://www.google.com/maps/search/hospitals/@${lat},${lng},15z`;
            window.location.href = mapsUrl;
        },
        () => {
            window.location.href = fallback;
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

function openEmergencyHospitals() {
    const fallback = "https://www.google.com/maps/search/emergency+hospital";
    showToast("Opening emergency hospitals...");

    if (!navigator.geolocation) {
        window.open(fallback, "_blank");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;
            const url = `https://www.google.com/maps/search/emergency+hospital/@${lat},${lng},15z`;
            window.open(url, "_blank");
        },
        () => {
            window.open(fallback, "_blank");
        }
    );
}

// ---------------- CAMERA ----------------
async function startCamera() {
    try {
        if (stream) stopCamera();

        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        const video = getEl("camera");
        const shell = document.querySelector(".camera-shell");

        if (!video) {
            showToast("Camera element not found.");
            return;
        }

        video.srcObject = stream;
        if (shell) shell.classList.add("active");

        showToast("Camera started");
    } catch (error) {
        console.error("Camera error:", error);
        showToast("Camera access denied or unavailable.");
    }
}

function stopCamera() {
    const video = getEl("camera");
    const shell = document.querySelector(".camera-shell");

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }

    if (video) {
        video.srcObject = null;
    }

    if (shell) shell.classList.remove("active");

    showToast("Camera stopped");
}

async function captureImage() {
    const video = getEl("camera");
    const canvas = getEl("snapshot");
    const context = canvas?.getContext("2d");
    const mode = getEl("scanMode")?.value;

    if (!video || !canvas || !context) {
        showToast("Camera not ready.");
        return;
    }

    if (!video.videoWidth || !video.videoHeight) {
        showToast("Start the camera first.");
        return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL("image/jpeg");

    stopCamera();
    resetResult("Processing...", mode === "food" ? "Analyzing food image..." : "Analyzing medicine image...");
    showTyping(true, mode === "food" ? "Analyzing food image..." : "Analyzing medicine image...");
    setButtonState(true);

    let endpoint = "/detect-medicine-image";
    if (mode === "food") {
        endpoint = "/detect-food-image";
    }

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ image: imageData })
        });

        const data = await response.json();
        latestResult = data;
        await renderResult(data);
        showToast("Scan complete");
    } catch (error) {
        console.error("Detection error:", error);
        showToast("Failed to analyze image.");
    } finally {
        showTyping(false);
        setButtonState(false);
    }
}

// ---------------- REPORT ANALYZER ----------------
async function analyzeReport() {
    const input = getEl("reportFileInput");

    if (!input || !input.files || input.files.length === 0) {
        showToast("Please select a report file first.");
        return;
    }

    const file = input.files[0];
    const formData = new FormData();
    formData.append("report", file);

    resetResult("Analyzing Report...", "Reading and understanding uploaded medical report...");
    showTyping(true, "Reading report and extracting insights...");
    setButtonState(true);

    try {
        const response = await fetch("/analyze-report", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        latestResult = data;
        await renderResult(data);
        showToast("Report analyzed successfully");
    } catch (error) {
        console.error("Report upload error:", error);
        showToast("Failed to analyze report.");
    } finally {
        showTyping(false);
        setButtonState(false);
    }
}

// ---------------- VOICE ----------------
function startVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        showToast("Speech recognition not supported.");
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = function () {
        showToast("Listening...");
    };

    recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        const input = getEl("userInput");
        if (input) input.value = text;
        showToast("Voice captured");
    };

    recognition.onerror = function(event) {
        console.error("Speech recognition error:", event.error);
        showToast("Voice input failed.");
    };

    recognition.start();
}

function speakResult() {
    const resultEl = getEl("resultAnswer");
    if (!resultEl) {
        showToast("No result found.");
        return;
    }

    let text = resultEl.innerText || "";

    if (!text.trim()) {
        showToast("No result to read.");
        return;
    }

    text = text
        .replace(/[#*`>-]/g, " ")
        .replace(/\n+/g, ". ")
        .replace(/\s+/g, " ")
        .trim();

    if (text.length > 500) {
        text = text.substring(0, 500) + ". Please read the full answer on screen.";
    }

    window.speechSynthesis.cancel();

    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = "en-US";
    speech.rate = 0.9;
    speech.pitch = 1;
    speech.volume = 1;

    const voices = window.speechSynthesis.getVoices();
    const preferredVoice =
        voices.find(v => v.lang === "en-US" && v.name.toLowerCase().includes("samantha")) ||
        voices.find(v => v.lang === "en-US" && v.name.toLowerCase().includes("google")) ||
        voices.find(v => v.lang === "en-US") ||
        voices[0];

    if (preferredVoice) {
        speech.voice = preferredVoice;
    }

    speech.onstart = () => showToast("Reading answer...");
    speech.onend = () => showToast("Finished reading");

    window.speechSynthesis.speak(speech);
}

window.speechSynthesis.onvoiceschanged = () => {
    window.speechSynthesis.getVoices();
};

function stopSpeaking() {
    window.speechSynthesis.cancel();
    showToast("Voice stopped");
}

function speakShortResult() {
    const title = getEl("resultTitle")?.innerText || "Result";
    const risk = getEl("riskLevel")?.innerText || "Unknown";
    const explanation = getEl("explanation")?.innerText || "";

    let text = `${title}. Risk level is ${risk}. ${explanation}`;
    text = text
        .replace(/[#*`>-]/g, " ")
        .replace(/\n+/g, ". ")
        .replace(/\s+/g, " ")
        .trim();

    window.speechSynthesis.cancel();

    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = "en-US";
    speech.rate = 0.9;
    speech.pitch = 1;

    const voices = window.speechSynthesis.getVoices();
    const preferredVoice =
        voices.find(v => v.lang === "en-US" && v.name.toLowerCase().includes("samantha")) ||
        voices.find(v => v.lang === "en-US") ||
        voices[0];

    if (preferredVoice) {
        speech.voice = preferredVoice;
    }

    window.speechSynthesis.speak(speech);
}

// ---------------- PAGE LOAD POLISH ----------------
window.addEventListener("load", () => {
    const cards = document.querySelectorAll(".card");
    cards.forEach((card, index) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(18px)";
        card.style.transition = "all 0.45s ease";

        setTimeout(() => {
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        }, 120 * index);
    });
});