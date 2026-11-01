from io import BytesIO

from PIL import Image
from transformers import pipeline


class AIImageDetector:

    def __init__(self):

        self.model_name = (
            "aaronkantrowitz/"
            "ai-human-generated-image-detection"
        )

        print("Loading AI image detection model...")

        self.classifier = pipeline(
            "image-classification",
            model=self.model_name,
            device=-1
        )

        print("AI image detection model loaded successfully!")

    def analyze(self, image_bytes):

        image = Image.open(
            BytesIO(image_bytes)
        ).convert("RGB")

        predictions = self.classifier(image)

        ai_probability = 0.0
        real_probability = 0.0

        for prediction in predictions:

            label = prediction["label"].lower()
            score = float(prediction["score"])

            if "ai" in label or "generated" in label:
                ai_probability = score

            elif "human" in label or "real" in label:
                real_probability = score

        confidence = max(
            ai_probability,
            real_probability
        )

        if confidence < 0.65:
            verdict = "Uncertain"

        elif ai_probability > real_probability:
            verdict = "Likely AI-Generated"

        else:
            verdict = "Likely Real"

        return {
            "verdict": verdict,
            "ai_probability": round(
                ai_probability * 100, 2
            ),
            "real_probability": round(
                real_probability * 100, 2
            ),
            "confidence": round(
                confidence * 100, 2
            )
        }