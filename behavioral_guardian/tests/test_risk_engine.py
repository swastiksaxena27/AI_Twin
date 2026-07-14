"""Risk engine tests."""

from behavioral_guardian.engines.risk_engine import compute_activity_risk
from behavioral_guardian.config.settings import RISK_WEIGHT_POWERSHELL, RISK_WEIGHT_USB_INSERTION


def test_risk_starts_at_zero():
    score, rules, explanations = compute_activity_risk({})
    assert score == 0
    assert rules == []
    assert explanations == []


def test_powershell_rule():
    score, rules, _ = compute_activity_risk({"powershell_detected": True})
    assert score == RISK_WEIGHT_POWERSHELL
    assert rules[0]["rule_name"] == "powershell"


def test_risk_capped_at_100():
    score, _, _ = compute_activity_risk(
        {
            "powershell_detected": True,
            "usb_insertion": True,
            "credential_tools": True,
            "registry_persistence": True,
            "download_bytes": 100_000_000,
        }
    )
    assert score == 100
