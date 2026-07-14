"""Response engine tests."""

from behavioral_guardian.engines.response_engine import execute_response
from behavioral_guardian.config.settings import RESPONSE_ACTION_MONITOR, RESPONSE_ACTION_WARN


def test_low_risk_monitor_only():
    result = execute_response(1, 95.0, 10.0, "NORMAL", {})
    assert result["level"] == 1
    assert RESPONSE_ACTION_MONITOR in result["actions"]


def test_high_risk_triggers_stronger_response():
    result = execute_response(1, 15.0, 90.0, "CRITICAL", {"process_name": "unknown.exe"})
    assert result["level"] >= 4
