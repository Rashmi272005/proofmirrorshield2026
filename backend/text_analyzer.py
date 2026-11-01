
import re

RULES = [
    {
        "name": "Urgent action",
        "pattern": r"\b(act now|immediately|urgent|within \d+ hours?|limited time|expires today)\b",
        "weight": 12,
        "severity": "medium",
        "explanation": "The message pressures the reader to act quickly."
    },
    {
        "name": "Sensitive information request",
        "pattern": r"\b(share|send|provide|enter|confirm)\b.{0,35}\b(otp|password|pin|cvv|bank details|card details)\b",
        "weight": 30,
        "severity": "high",
        "explanation": "The message may be requesting sensitive account or payment information."
    },
    {
        "name": "Upfront payment request",
        "pattern": r"\b(registration fee|processing fee|advance payment|pay first|security deposit|upfront fee)\b",
        "weight": 25,
        "severity": "high",
        "explanation": "The message mentions paying money before receiving a service or benefit."
    },
    {
        "name": "Unrealistic reward",
        "pattern": r"\b(guaranteed income|free money|won a prize|winner|huge reward)\b",
        "weight": 18,
        "severity": "medium",
        "explanation": "The message advertises a reward that needs independent verification."
    },
    {
        "name": "Threatening language",
        "pattern": r"\b(account blocked|account suspended|legal action|police case|permanent closure)\b",
        "weight": 18,
        "severity": "medium",
        "explanation": "The message uses threatening language to influence the reader."
    },
    {
        "name": "Remote access request",
        "pattern": r"\b(anydesk|teamviewer|remote access|screen sharing app)\b",
        "weight": 25,
        "severity": "high",
        "explanation": "The message mentions remote access or screen-sharing software."
    },
    {
        "name": "Suspicious contact instruction",
        "pattern": r"\b(contact only on whatsapp|message this number|call this private number)\b",
        "weight": 12,
        "severity": "medium",
        "explanation": "The message directs the reader to an alternative contact channel."
    },
    {
        "name": "Credential verification pressure",
        "pattern": r"\b(verify your account|confirm your identity|update your kyc|reactivate your account)\b",
        "weight": 15,
        "severity": "medium",
        "explanation": "The message asks the reader to verify or reactivate an account."
    }
]


def analyze_text(text):
    """Identify possible warning signs in message content."""

    if not isinstance(text, str):
        text = ""

    cleaned_text = text.strip()

    if not cleaned_text:
        return {
            "score": 0,
            "signals": [],
            "message": "No message text was provided."
        }

    signals = []
    total_score = 0

    for rule in RULES:
        matches = re.findall(
            rule["pattern"],
            cleaned_text,
            flags=re.IGNORECASE
        )

        if matches:
            total_score += rule["weight"]

            signals.append({
                "name": rule["name"],
                "severity": rule["severity"],
                "weight": rule["weight"],
                "explanation": rule["explanation"],
                "matched_count": len(matches)
            })

    score = min(total_score, 100)

    return {
        "score": score,
        "signals": signals,
        "message": (
            "Potential warning signs were identified."
            if signals
            else "No major warning signs were identified by the current rules."
        )
    }
