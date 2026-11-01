const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const analyzeBtn = document.getElementById("analyzeBtn");
const statusText = document.getElementById("status");
const results = document.getElementById("results");
const emptyState = document.getElementById("emptyState");

let selectedFile = null;

const MAX_SIZE = 2 * 1024 * 1024;

const ALLOWED_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp"
];


// INITIAL DISPLAY

results.style.display = "none";
emptyState.style.display = "block";


// IMAGE SELECTION

imageInput.addEventListener("change", function () {

    const file = this.files[0];

    if (!file) return;

    if (!ALLOWED_TYPES.includes(file.type)) {

        selectedFile = null;
        analyzeBtn.disabled = true;

        statusText.textContent =
            "Please select JPG, PNG or WEBP.";

        return;
    }

    if (file.size > MAX_SIZE) {

        selectedFile = null;
        analyzeBtn.disabled = true;

        statusText.textContent =
            "Maximum image size is 2 MB.";

        return;
    }

    selectedFile = file;

    const reader = new FileReader();

    reader.onload = function (event) {

        preview.src = event.target.result;
        preview.style.display = "block";

    };

    reader.readAsDataURL(file);

    document.getElementById("fileName").textContent = file.name;

    analyzeBtn.disabled = false;

    statusText.textContent =
        "Image ready for analysis.";

    results.style.display = "none";
    emptyState.style.display = "block";

});


// FACE AND AI IMAGE DETECTION

analyzeBtn.addEventListener("click", async function () {

    if (!selectedFile) {

        statusText.textContent =
            "Select an image first.";

        return;
    }

    const formData = new FormData();

    formData.append("image", selectedFile);

    analyzeBtn.disabled = true;

    statusText.textContent =
        "Analyzing image. Please wait...";

    try {

        const response = await fetch("/api/image-analyze", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.error || "Image analysis failed."
            );

        }


        // SHOW RESULTS

        emptyState.style.display = "none";
        results.style.display = "block";


        // FACE COUNT

        document.getElementById("faceCount").textContent =
            data.face_count;


        // IMAGE DIMENSIONS

        document.getElementById("dimensions").textContent =
            `${data.image_width} × ${data.image_height}`;


        // PROCESSED IMAGE

        const processedImage =
            document.getElementById("processedImage");

        processedImage.src =
            data.preview + "?t=" + Date.now();

        processedImage.style.display = "block";


        // FACE DETAILS

        const faceDetails =
            document.getElementById("faceDetails");

        faceDetails.replaceChildren();

        if (
            data.face_detected &&
            Array.isArray(data.faces) &&
            data.faces.length > 0
        ) {

            data.faces.forEach(function (face) {

                const item = document.createElement("li");

                item.textContent =
                    `Face ${face.face_number}: ` +
                    `Position (${face.x}, ${face.y}), ` +
                    `Size ${face.width} × ${face.height}, ` +
                    `Detection confidence: ${(face.confidence * 100).toFixed(1)}%`;

                faceDetails.appendChild(item);

            });

        } else {

            const item = document.createElement("li");

            item.textContent =
                "No faces detected in this image.";

            faceDetails.appendChild(item);

        }


        // AI IMAGE DETECTION

        document.getElementById("aiVerdict").textContent =
            data.ai_verdict ?? "Not available";


        document.getElementById("aiProbability").textContent =
            data.ai_probability != null
                ? data.ai_probability + "%"
                : "Not available";


        document.getElementById("realProbability").textContent =
            data.real_probability != null
                ? data.real_probability + "%"
                : "Not available";


        document.getElementById("aiConfidence").textContent =
            data.ai_confidence != null
                ? data.ai_confidence + "%"
                : "Not available";


        // REPORT ID

        document.getElementById("reportId").textContent =
            "Report ID: " + data.report_id;


        // SUCCESS MESSAGE

        statusText.textContent =
            "Face detection and AI image analysis completed successfully.";


        // SCROLL TO RESULTS

        results.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }

    catch (error) {

        statusText.textContent = error.message;

        console.error("Image analysis error:", error);

    }

    finally {

        analyzeBtn.disabled = false;

    }

});