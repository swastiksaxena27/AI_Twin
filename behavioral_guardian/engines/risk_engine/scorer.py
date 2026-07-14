"""Activity risk scorer."""

from typing import Any, Dict, List, Tuple

from behavioral_guardian.config.settings import (
    CHILD_PROCESS_EXPLOSION_THRESHOLD,
    DOWNLOAD_SPIKE_THRESHOLD_BYTES,
    NETWORK_UPLOAD_SPIKE_THRESHOLD_BYTES,
    RISK_SCORE_MAX,
)
from behavioral_guardian.engines.risk_engine.rules import CREDENTIAL_TOOL_NAMES, KNOWN_PROCESS_ALLOWLIST, RISK_RULES
from behavioral_guardian.utils.logging_config import setup_logging

logger = setup_logging(__name__)


def _append_rule(
    triggered: List[Dict[str, Any]],
    explanations: List[str],
    rule_name: str,
    detail: str,
) -> int:
    """Append triggered rule and return its weight."""
    rule = RISK_RULES[rule_name]
    triggered.append({"rule_name": rule_name, "weight": rule["weight"], "detail": detail})
    explanations.append(f"{rule_name}: {detail} (+{rule['weight']})")
    return rule["weight"]


def compute_activity_risk(activity_signals: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]], List[str]]:
    """
    Evaluate activity signals against frozen risk rules.

    Returns:
        activity_risk, triggered_rules, explanations
    """
    risk = 0
    triggered: List[Dict[str, Any]] = []
    explanations: List[str] = []

    process_name = str(activity_signals.get("process_name", "")).lower()
    if process_name and process_name not in KNOWN_PROCESS_ALLOWLIST:
        risk += _append_rule(triggered, explanations, "unknown_process", process_name)

    if activity_signals.get("powershell_detected"):
        risk += _append_rule(triggered, explanations, "powershell", "PowerShell activity detected")

    if activity_signals.get("cmd_detected"):
        risk += _append_rule(triggered, explanations, "cmd", "cmd.exe activity detected")

    if activity_signals.get("usb_insertion"):
        risk += _append_rule(triggered, explanations, "usb_insertion", "USB device inserted")

    download_bytes = float(activity_signals.get("download_bytes", 0))
    if download_bytes >= DOWNLOAD_SPIKE_THRESHOLD_BYTES:
        risk += _append_rule(triggered, explanations, "download_spike", f"{download_bytes:.0f} bytes downloaded")

    if activity_signals.get("zip_creation"):
        risk += _append_rule(triggered, explanations, "zip_creation", "Archive creation detected")

    upload_bytes = float(activity_signals.get("network_upload_bytes", 0))
    if upload_bytes >= NETWORK_UPLOAD_SPIKE_THRESHOLD_BYTES:
        risk += _append_rule(triggered, explanations, "network_upload_spike", f"{upload_bytes:.0f} bytes uploaded")

    child_count = int(activity_signals.get("child_process_count", 0))
    if child_count >= CHILD_PROCESS_EXPLOSION_THRESHOLD:
        risk += _append_rule(triggered, explanations, "child_process_explosion", f"{child_count} child processes")

    if activity_signals.get("credential_tools") or process_name in CREDENTIAL_TOOL_NAMES:
        risk += _append_rule(triggered, explanations, "credential_tools", "Credential access tool detected")

    if activity_signals.get("registry_persistence"):
        risk += _append_rule(triggered, explanations, "registry_persistence", "Registry persistence behavior detected")

    activity_risk = min(float(RISK_SCORE_MAX), float(risk))
    logger.info("Computed activity_risk=%.2f rules=%d", activity_risk, len(triggered))
    return activity_risk, triggered, explanations
