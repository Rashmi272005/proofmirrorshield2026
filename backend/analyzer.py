from backend.text_analyzer import analyze_text
from backend.url_analyzer import analyze_url
from backend.evidence_engine import build_evidence


def classify_risk(score):
    if score >= 60:
        return "HIGH RISK", "high"

    if score >= 25:
        return "NEEDS REVIEW", "medium"

    return "LOWER RISK", "low"


def analyze_content(text="", url=""):
    text_result = analyze_text(text)
    url_result = analyze_url(url)

    has_text = bool(text and text.strip())
    has_url = bool(url and url.strip())

    if has_text and has_url:
        score = round(
            (text_result["score"] * 0.6) +
            (url_result["score"] * 0.4)
        )
    elif has_text:
        score = text_result["score"]
    elif has_url:
        score = url_result["score"]
    else:
        raise ValueError("Please enter a message or a URL to analyse.")

    verdict, risk_level = classify_risk(score)

    evidence = build_evidence(text_result, url_result)

    return {
        "score": score,
        "verdict": verdict,
        "risk_level": risk_level,
        "text_analysis": text_result,
        "url_analysis": url_result,
        "evidence": evidence,
        "input_summary": {
            "text_provided": has_text,
            "url_provided": has_url
        },
        "disclaimer": (
            "This result indicates potential risk, not verified truth. "
            "Always confirm important claims through official sources."
        )
    }