from backend.image_detector import FaceDetector

detector = FaceDetector()

print("Face detector initialized successfully!")
print("YuNet model loaded:", detector.model_path.exists())