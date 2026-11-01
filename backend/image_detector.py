import cv2
import numpy as np

from PIL import Image, ImageOps
from io import BytesIO
from pathlib import Path


class FaceDetector:

    def __init__(self):

        self.model_path = (
            Path(__file__).resolve().parent
            / "face_detection_yunet_2023mar.onnx"
        )

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"YuNet model not found: {self.model_path}"
            )

        self.detector = None

    def analyze(self, image_bytes):

        image = Image.open(BytesIO(image_bytes))
        image = ImageOps.exif_transpose(image).convert("RGB")

        width, height = image.size

        frame = cv2.cvtColor(
            np.array(image),
            cv2.COLOR_RGB2BGR
        )

        if self.detector is None:

            self.detector = cv2.FaceDetectorYN.create(
                str(self.model_path),
                "",
                (width, height),
                0.7,
                0.3,
                5000
            )

        else:
            self.detector.setInputSize((width, height))

        _, faces = self.detector.detect(frame)

        output = frame.copy()
        face_details = []

        if faces is not None:

            for number, face in enumerate(faces, 1):

                x, y, w, h = map(int, face[:4])
                confidence = float(face[14])

                cv2.rectangle(
                    output,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 100),
                    3
                )

                cv2.putText(
                    output,
                    f"Face {number}",
                    (x, max(y - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 100),
                    2
                )

                face_details.append({
                    "face_number": number,
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h,
                    "confidence": round(confidence, 3)
                })

        success, encoded = cv2.imencode(".jpg", output)

        if not success:
            raise RuntimeError("Image encoding failed")

        return {
            "face_detected": len(face_details) > 0,
            "face_count": len(face_details),
            "image_width": width,
            "image_height": height,
            "faces": face_details,
            "processed_image": encoded.tobytes()
        }