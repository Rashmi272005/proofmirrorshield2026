import os
import uuid
from io import BytesIO

from PIL import Image, UnidentifiedImageError

from flask import (
    Blueprint,
    request,
    jsonify,
    current_app,
    render_template,
    send_from_directory
)

from backend.image_detector import FaceDetector
from backend.ai_image_detector import AIImageDetector

from backend.database import (
    save_image_report,
    get_image_report,
    get_image_history
)


image_bp = Blueprint("image", __name__)

face_detector = None
ai_detector = None

MAX_IMAGE_SIZE = 2 * 1024 * 1024

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


def get_face_detector():
    global face_detector

    if face_detector is None:
        face_detector = FaceDetector()

    return face_detector


def get_ai_detector():
    global ai_detector

    if ai_detector is None:
        ai_detector = AIImageDetector()

    return ai_detector


@image_bp.route("/image-verify")
def image_page():
    return render_template("image_verify.html")


@image_bp.route("/api/image-analyze", methods=["POST"])
def analyze_image():

    if "image" not in request.files:
        return jsonify({
            "error": "Please select an image."
        }), 400

    uploaded_file = request.files["image"]

    image_bytes = uploaded_file.read(MAX_IMAGE_SIZE + 1)

    if not image_bytes:
        return jsonify({
            "error": "Empty image."
        }), 400

    if len(image_bytes) > MAX_IMAGE_SIZE:
        return jsonify({
            "error": "Image must be smaller than 2 MB."
        }), 413

    try:

        with Image.open(BytesIO(image_bytes)) as image:

            if image.format not in ALLOWED_FORMATS:
                return jsonify({
                    "error": "Only JPG, PNG and WEBP are supported."
                }), 400

            image.verify()

        # Face detection
        analysis = get_face_detector().analyze(image_bytes)

        # AI image detection
        ai_result = get_ai_detector().analyze(image_bytes)

        # Save processed image
        filename = f"{uuid.uuid4().hex}.jpg"

        result_directory = os.path.join(
            current_app.instance_path,
            "image_results"
        )

        os.makedirs(result_directory, exist_ok=True)

        output_path = os.path.join(
            result_directory,
            filename
        )

        with open(output_path, "wb") as output:
            output.write(analysis["processed_image"])

        # Combine both analysis results
        complete_analysis = {
            **analysis,
            **ai_result
        }

        # Save report
        report_id = save_image_report(
            current_app.config["DATABASE_PATH"],
            filename,
            complete_analysis
        )

        # Return results
        return jsonify({

            "success": True,
            "report_id": report_id,

            # Face detection
            "face_detected": analysis["face_detected"],
            "face_count": analysis["face_count"],
            "image_width": analysis["image_width"],
            "image_height": analysis["image_height"],
            "faces": analysis["faces"],

            # AI detection
            "ai_verdict": ai_result["verdict"],
            "ai_probability": ai_result["ai_probability"],
            "real_probability": ai_result["real_probability"],
            "ai_confidence": ai_result["confidence"],

            # Processed image
            "preview": f"/image-preview/{report_id}"

        })

    except (
        UnidentifiedImageError,
        Image.DecompressionBombError,
        OSError,
        ValueError
    ):

        return jsonify({
            "error": "Invalid or unsupported image."
        }), 400

    except Exception:

        current_app.logger.exception("Image analysis failed")

        return jsonify({
            "error": "Image analysis failed."
        }), 500


@image_bp.route("/image-preview/<int:report_id>")
def image_preview(report_id):

    report = get_image_report(
        current_app.config["DATABASE_PATH"],
        report_id
    )

    if report is None:
        return "Image not found", 404

    result_directory = os.path.join(
        current_app.instance_path,
        "image_results"
    )

    return send_from_directory(
        result_directory,
        report["filename"],
        mimetype="image/jpeg"
    )


@image_bp.route("/api/image-history")
def image_history():

    history = get_image_history(
        current_app.config["DATABASE_PATH"]
    )

    return jsonify({
        "history": history
    })