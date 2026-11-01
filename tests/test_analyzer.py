
import pytest

from backend.analyzer import analyze_content, classify_risk
from backend.text_analyzer import analyze_text
from backend.url_analyzer import analyze_url


def test_empty_text():
    result = analyze_text("")

    assert result["score"] == 0
    assert result["signals"] == []


def test_suspicious_text():
    result = analyze_text("Please send your OTP immediately.")

    assert result["score"] == 42
    assert len(result["signals"]) == 2


def test_safe_text():
    result = analyze_text(
        "The college library will remain open until 5 PM."
    )

    assert result["score"] == 0
    assert result["signals"] == []


def test_empty_url():
    result = analyze_url("")

    assert result["score"] == 0
    assert result["signals"] == []


def test_http_url():
    result = analyze_url("http://example.com")

    assert result["score"] == 12
    assert result["signals"][0]["name"] == "Unencrypted connection"


def test_url_shortener():
    result = analyze_url("https://bit.ly/example")

    assert result["score"] == 10
    assert result["signals"][0]["name"] == "URL shortener"


def test_url_is_not_visited():
    result = analyze_url("https://example.com/login")

    assert result["normalized_url"] == "https://example.com/login"


def test_classify_risk():
    assert classify_risk(10) == ("LOWER RISK", "low")
    assert classify_risk(25) == ("NEEDS REVIEW", "medium")
    assert classify_risk(60) == ("HIGH RISK", "high")


def test_analyze_content_with_text():
    result = analyze_content(
        text="Please send your OTP."
    )

    assert result["score"] == 30
    assert result["risk_level"] == "medium"
    assert result["verdict"] == "NEEDS REVIEW"


def test_analyze_content_with_url():
    result = analyze_content(
        url="http://example.com"
    )

    assert result["score"] == 12
    assert result["risk_level"] == "low"


def test_analyze_content_with_both():
    result = analyze_content(
        text="Please send your OTP.",
        url="http://example.com"
    )

    assert result["score"] == 23
    assert result["input_summary"]["text_provided"] is True
    assert result["input_summary"]["url_provided"] is True


def test_analyze_content_without_input():
    with pytest.raises(ValueError):
        analyze_content()
