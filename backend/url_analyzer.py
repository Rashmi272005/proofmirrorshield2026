import ipaddress
import re
from urllib.parse import urlparse


SHORTENERS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "is.gd",
    "cutt.ly",
    "rb.gy",
    "shorturl.at"
}

SUSPICIOUS_TERMS = {
    "verify",
    "login",
    "secure",
    "update",
    "account",
    "wallet",
    "claim",
    "free",
    "reward"
}


def analyze_url(raw_url):
    """Check URL structure for possible warning signs without visiting it."""

    if not isinstance(raw_url, str) or not raw_url.strip():
        return {
            "score": 0,
            "signals": [],
            "normalized_url": None,
            "message": "No URL was provided."
        }

    raw_url = raw_url.strip()

    if len(raw_url) > 2048:
        return {
            "score": 0,
            "signals": [],
            "normalized_url": None,
            "message": "The URL is too long to analyse."
        }

    candidate = raw_url

    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", candidate):
        candidate = "https://" + candidate

    try:
        parsed = urlparse(candidate)
        hostname = parsed.hostname
    except ValueError:
        hostname = None
        parsed = None

    if not parsed or not hostname or not parsed.scheme:
        return {
            "score": 0,
            "signals": [],
            "normalized_url": None,
            "message": "The supplied URL could not be parsed."
        }

    if parsed.scheme not in ("http", "https"):
        return {
            "score": 0,
            "signals": [],
            "normalized_url": None,
            "message": "Only HTTP and HTTPS URLs are supported."
        }

    signals = []
    score = 0

    def add_signal(name, weight, severity, explanation):
        nonlocal score

        score += weight
        signals.append({
            "name": name,
            "weight": weight,
            "severity": severity,
            "explanation": explanation
        })

    if parsed.scheme == "http":
        add_signal(
            "Unencrypted connection",
            12,
            "medium",
            "The URL uses HTTP instead of HTTPS. Data may not be encrypted in transit."
        )

    if hostname.lower() in SHORTENERS:
        add_signal(
            "URL shortener",
            10,
            "medium",
            "The shortened URL hides the final destination."
        )

    try:
        ipaddress.ip_address(hostname)
        add_signal(
            "IP address used as domain",
            20,
            "high",
            "The URL uses a direct IP address instead of a conventional domain name."
        )
    except ValueError:
        pass

    if "xn--" in hostname.lower():
        add_signal(
            "Internationalized domain encoding",
            15,
            "medium",
            "The domain contains encoded characters. Check carefully for lookalike characters."
        )

    if hostname.count(".") >= 4:
        add_signal(
            "Many domain sublevels",
            8,
            "low",
            "The hostname contains several subdomains. This is worth checking, but is not proof of fraud."
        )

    if "@" in parsed.netloc:
        add_signal(
            "Misleading URL structure",
            25,
            "high",
            "The URL contains an @ symbol in its network location, which can make the actual destination confusing."
        )

    domain_terms = set(re.findall(r"[a-zA-Z]+", hostname.lower()))
    matched_terms = domain_terms.intersection(SUSPICIOUS_TERMS)

    if matched_terms:
        add_signal(
            "Sensitive-looking domain wording",
            8,
            "low",
            "The domain includes words commonly used in account or reward-related messages: "
            + ", ".join(sorted(matched_terms))
            + "."
        )

    score = min(score, 100)

    return {
        "score": score,
        "signals": signals,
        "normalized_url": candidate,
        "hostname": hostname,
        "message": (
            "Potential URL warning signs were identified."
            if signals
            else "No major structural warning signs were identified."
        )
    }