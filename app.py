import io
import json

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    abort,
    send_file
)

from config import Config

from backend.analyzer import analyze_content
from backend.report_generator import generate_report

from backend.database import (
    init_db,
    init_image_table,
    save_report,
    get_report,
    get_recent_reports,
    get_dashboard_stats
)

from backend.image_routes import image_bp

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)
from reportlab.lib.units import mm
from xml.sax.saxutils import escape


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    init_db(app.config["DATABASE_PATH"])
    init_image_table(app.config["DATABASE_PATH"])

    app.register_blueprint(image_bp)

    # ---------------- PAGE ROUTES ----------------

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/dashboard")
    def dashboard():

        stats = get_dashboard_stats(
            app.config["DATABASE_PATH"]
        )

        recent_reports = get_recent_reports(
            app.config["DATABASE_PATH"],
            limit=5
        )

        return render_template(
            "dashboard.html",
            stats=stats,
            recent_reports=recent_reports
        )

    @app.route("/verify")
    def verify():
        return render_template("verify.html")

    @app.route("/result/<int:report_id>")
    def result(report_id):

        report = get_report(
            app.config["DATABASE_PATH"],
            report_id
        )

        if report is None:
            abort(404)

        return render_template(
            "result.html",
            report=report,
            analysis=report["analysis"]
        )

    @app.route("/community")
    def community():

        reports = get_recent_reports(
            app.config["DATABASE_PATH"],
            limit=30
        )

        return render_template(
            "community.html",
            reports=reports
        )

    @app.route("/intelligence")
    def intelligence():

        stats = get_dashboard_stats(
            app.config["DATABASE_PATH"]
        )

        return render_template(
            "intelligence.html",
            stats=stats
        )

    @app.route("/about")
    def about():
        return render_template("about.html")

    # ---------------- API ROUTES ----------------

    @app.route("/api/health")
    def health():

        return jsonify({
            "status": "online",
            "application": "ProofMirror Shield",
            "message": "Backend is running."
        })

    @app.route("/api/analyze", methods=["POST"])
    def api_analyze():

        data = request.get_json(silent=True)

        if not isinstance(data, dict):

            return jsonify({
                "error": "Please send a valid JSON request."
            }), 400

        text = data.get("text", "")
        url = data.get("url", "")

        if not isinstance(text, str) or not isinstance(url, str):

            return jsonify({
                "error": "Text and URL inputs must be strings."
            }), 400

        if len(text) > 10000:

            return jsonify({
                "error": "Message text must be 10,000 characters or fewer."
            }), 400

        if len(url) > 2048:

            return jsonify({
                "error": "URL must be 2,048 characters or fewer."
            }), 400

        if not text.strip() and not url.strip():

            return jsonify({
                "error": "Enter a message or URL before analysing."
            }), 400

        try:

            analysis = analyze_content(
                text=text,
                url=url
            )

            report_id = save_report(
                app.config["DATABASE_PATH"],
                text,
                url,
                analysis
            )

            analysis["report_id"] = report_id

            return jsonify({
                "success": True,
                "report_id": report_id,
                "analysis": analysis,
                "result_url": f"/result/{report_id}"
            }), 200

        except ValueError as error:

            return jsonify({
                "error": str(error)
            }), 400

        except Exception:

            app.logger.exception("Analysis failed")

            return jsonify({
                "error": "An unexpected error occurred during analysis."
            }), 500

    @app.route("/api/reports")
    def api_reports():

        reports = get_recent_reports(
            app.config["DATABASE_PATH"],
            limit=50
        )

        return jsonify({
            "reports": reports
        })

    @app.route("/api/stats")
    def api_stats():

        stats = get_dashboard_stats(
            app.config["DATABASE_PATH"]
        )

        return jsonify(stats)

    @app.route("/api/report/<int:report_id>")
    def api_report(report_id):

        report = get_report(
            app.config["DATABASE_PATH"],
            report_id
        )

        if report is None:

            return jsonify({
                "error": "Report not found."
            }), 404

        return jsonify(report)

    # ---------------- PDF REPORT ----------------

    @app.route("/api/report/<int:report_id>/download-pdf")
    def download_report_pdf(report_id):

        report = get_report(
            app.config["DATABASE_PATH"],
            report_id
        )

        if report is None:

            return jsonify({
                "error": "Report not found."
            }), 404

        analysis = report["analysis"]

        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontSize=23,
            textColor=colors.HexColor("#29235C"),
            alignment=TA_CENTER,
            spaceAfter=8
        )

        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#5141A8"),
            spaceBefore=12,
            spaceAfter=7
        )

        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["BodyText"],
            fontSize=9,
            leading=14,
            spaceAfter=5,
            wordWrap="CJK"
        )

        story = []

        def add_value(value):

            if isinstance(value, dict):

                for key, item in value.items():

                    story.append(Paragraph(
                        escape(str(key).replace("_", " ").title()),
                        heading_style
                    ))

                    add_value(item)

            elif isinstance(value, list):

                for item in value:

                    if isinstance(item, (dict, list)):
                        add_value(item)

                    else:

                        story.append(Paragraph(
                            "• " + escape(str(item)),
                            body_style
                        ))

            elif value is not None:

                story.append(Paragraph(
                    escape(str(value)),
                    body_style
                ))

        story.append(Paragraph(
            "PROOFMIRROR SHIELD",
            title_style
        ))

        story.append(Paragraph(
            "Digital Content Risk Analysis Report",
            ParagraphStyle(
                "Subtitle",
                parent=body_style,
                alignment=TA_CENTER
            )
        ))

        story.append(Spacer(1, 15))

        story.append(HRFlowable(
            width="100%",
            color=colors.HexColor("#5141A8")
        ))

        story.append(Spacer(1, 12))

        story.append(Paragraph(
            f"Report ID: #{report_id}",
            body_style
        ))

        story.append(Paragraph(
            f"Generated: {escape(str(report.get('created_at', 'Not available')))}",
            body_style
        ))

        story.append(Spacer(1, 12))

        score = analysis.get("score", 0)
        verdict = analysis.get("verdict", "Not available")

        summary_data = [
            ["OVERALL RISK SCORE", "VERDICT"],
            [f"{score}/100", str(verdict)]
        ]

        summary_table = Table(
            summary_data,
            colWidths=[75 * mm, 75 * mm]
        )

        summary_table.setStyle(TableStyle([

            ("BACKGROUND", (0, 0), (-1, 0),
             colors.HexColor("#29235C")),

            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("BACKGROUND", (0, 1), (-1, 1),
             colors.HexColor("#F0EEFA")),

            ("TEXTCOLOR", (0, 1), (-1, 1),
             colors.HexColor("#29235C")),

            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),

            ("FONTSIZE", (0, 0), (-1, -1), 11),

            ("ALIGN", (0, 0), (-1, -1), "CENTER"),

            ("PADDING", (0, 0), (-1, -1), 12),

            ("GRID", (0, 0), (-1, -1), 0.5, colors.white)

        ]))

        story.append(summary_table)
        story.append(Spacer(1, 15))

        story.append(Paragraph(
            "ANALYSIS DETAILS",
            heading_style
        ))

        for key, value in analysis.items():

            if key in ("score", "verdict", "risk_level"):
                continue

            story.append(Paragraph(
                escape(str(key).replace("_", " ").title()),
                heading_style
            ))

            add_value(value)

        story.append(Spacer(1, 15))

        story.append(HRFlowable(
            width="100%",
            color=colors.HexColor("#CCCCCC")
        ))

        story.append(Spacer(1, 8))

        story.append(Paragraph(
            "Disclaimer: This report contains automated risk indicators. "
            "It is not a certificate of authenticity or a final fact-check.",
            body_style
        ))

        doc.build(story)

        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"proofmirror_report_{report_id}.pdf"
        )

    # ---------------- JSON REPORT ----------------

    @app.route("/api/report/<int:report_id>/download")
    def download_report(report_id):

        report = get_report(
            app.config["DATABASE_PATH"],
            report_id
        )

        if report is None:

            return jsonify({
                "error": "Report not found."
            }), 404

        export_data = generate_report(
            report["analysis"],
            report_id=report_id
        )

        file_data = io.BytesIO(
            json.dumps(
                export_data,
                indent=4,
                ensure_ascii=False
            ).encode("utf-8")
        )

        file_data.seek(0)

        return send_file(
            file_data,
            mimetype="application/json",
            as_attachment=True,
            download_name=f"proofmirror_report_{report_id}.json"
        )

    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )