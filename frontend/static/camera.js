let stream = null;

async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        const video = document.getElementById("camera");
        video.srcObject = stream;
    } catch (error) {
        alert("Camera access denied or not available.");
        console.error(error);
    }
}

async function captureImage() {
    const video = document.getElementById("camera");
    const canvas = document.getElementById("snapshot");
    const context = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL("image/jpeg");

    const response = await fetch("/detect-medicine-image", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ image: imageData })
    });

    const data = await response.json();
    latestResult = data;
    renderResult(data);
}