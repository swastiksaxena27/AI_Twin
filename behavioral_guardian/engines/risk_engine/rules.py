"""Risk rule definitions — frozen weights."""

from behavioral_guardian.config.settings import (
    RISK_WEIGHT_CHILD_PROCESS_EXPLOSION,
    RISK_WEIGHT_CMD,
    RISK_WEIGHT_CREDENTIAL_TOOLS,
    RISK_WEIGHT_DOWNLOAD_SPIKE,
    RISK_WEIGHT_NETWORK_UPLOAD_SPIKE,
    RISK_WEIGHT_POWERSHELL,
    RISK_WEIGHT_REGISTRY_PERSISTENCE,
    RISK_WEIGHT_UNKNOWN_PROCESS,
    RISK_WEIGHT_USB_INSERTION,
    RISK_WEIGHT_ZIP_CREATION,
)

RISK_RULES = {
    "unknown_process": {"weight": RISK_WEIGHT_UNKNOWN_PROCESS, "mitre_hint": "T1204"},
    "powershell": {"weight": RISK_WEIGHT_POWERSHELL, "mitre_hint": "T1059.001"},
    "cmd": {"weight": RISK_WEIGHT_CMD, "mitre_hint": "T1059.003"},
    "usb_insertion": {"weight": RISK_WEIGHT_USB_INSERTION, "mitre_hint": "T1091"},
    "download_spike": {"weight": RISK_WEIGHT_DOWNLOAD_SPIKE, "mitre_hint": "T1105"},
    "zip_creation": {"weight": RISK_WEIGHT_ZIP_CREATION, "mitre_hint": "T1560"},
    "network_upload_spike": {"weight": RISK_WEIGHT_NETWORK_UPLOAD_SPIKE, "mitre_hint": "T1048"},
    "child_process_explosion": {"weight": RISK_WEIGHT_CHILD_PROCESS_EXPLOSION, "mitre_hint": "T1055"},
    "credential_tools": {"weight": RISK_WEIGHT_CREDENTIAL_TOOLS, "mitre_hint": "T1003"},
    "registry_persistence": {"weight": RISK_WEIGHT_REGISTRY_PERSISTENCE, "mitre_hint": "T1547.001"},
}

CREDENTIAL_TOOL_NAMES = {"mimikatz", "lazagne", "procdump", "secretsdump"}
KNOWN_PROCESS_ALLOWLIST = {"explorer.exe", "chrome.exe", "code.exe", "python.exe", "streamlit.exe"}
