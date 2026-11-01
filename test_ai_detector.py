from backend.ai_image_detector import AIImageDetector

detector = AIImageDetector()

image_path = input("Enter image path: ")

with open(image_path.strip().strip('"'), "rb") as file:
    image_bytes = file.read()

result = detector.analyze(image_bytes)

print("\n===== PROOFMIRROR AI IMAGE ANALYSIS =====")
print("Verdict:", result["verdict"])
print("AI Probability:", result["ai_probability"], "%")
print("Real Probability:", result["real_probability"], "%")
print("Confidence:", result["confidence"], "%")