def build_evidence(text_result, url_result):
    findings = []

    for signal in text_result.get("signals", []):
        findings.append({
            "source": "Message content",
            "finding": signal["name"],
            "severity": signal["severity"],
            "explanation": signal["explanation"]
        })

    for signal in url_result.get("signals", []):
        findings.append({
            "source": "URL structure",
            "finding": signal["name"],
            "severity": signal["severity"],
            "explanation": signal["explanation"]
        })

    high = sum(1 for item in findings if item["severity"] == "high")
    medium = sum(1 for item in findings if item["severity"] == "medium")
    low = sum(1 for item in findings if item["severity"] == "low")

    if not findings:
        unknowns = [
            "No major warning signs were found by the current checks.",
            "The sender's identity and the original source have not been independently verified.",
            "The content may still be misleading or fraudulent."
        ]
        next_steps = [
            "Confirm the information through the organisation's official website.",
            "Contact the organisation using a phone number or email found independently.",
            "Do not share passwords, OTPs, PINs, or payment details."
        ]
    else:
        unknowns = [
            "The sender's identity has not been independently verified.",
            "The claims in the message have not been confirmed against an authoritative source.",
            "The URL has been inspected structurally but has not been visited or checked against a live threat database."
        ]
        next_steps = [
            "Do not click suspicious links or download unexpected attachments.",
            "Verify the claim through the organisation's official website or app.",
            "Never share OTPs, passwords, PINs, or banking details.",
            "Report suspected fraud to the relevant official channel."
        ]

    return {
        "findings": findings,
        "summary": {
            "total": len(findings),
            "high": high,
            "medium": medium,
            "low": low
        },
        "unknowns": unknowns,
        "next_steps": next_steps,
        "limitations": [
            "This prototype uses transparent rule-based checks.",
            "A risk score is not proof that content is fake or genuine.",
            "No live website reputation lookup or independent fact-checking is performed."
        ]
    }