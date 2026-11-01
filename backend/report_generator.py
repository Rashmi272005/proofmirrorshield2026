from datetime import datetime, timezone


def generate_report(analysis, report_id=None):
    return {
        "application": "ProofMirror Shield",
        "report_id": report_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "result": analysis,
        "report_note": (
            "This report contains automated risk indicators. "
            "It is not a certificate of authenticity or a final fact-check."
        )
    }