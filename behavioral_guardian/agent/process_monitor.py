"""Process monitoring."""

from typing import Any, Dict, List, Set

import psutil

from behavioral_guardian.engines.risk_engine.rules import KNOWN_PROCESS_ALLOWLIST
from behavioral_guardian.utils.logging_config import setup_logging

logger = setup_logging(__name__)


class ProcessMonitor:
    """Monitor running processes and child process counts."""

    def snapshot(self) -> Dict[str, Any]:
        """Return process-related activity signals."""
        process_names: List[str] = []
        child_counts: List[int] = []

        for proc in psutil.process_iter(["name", "ppid"]):
            try:
                info = proc.info
                name = (info.get("name") or "").lower()
                if name:
                    process_names.append(name)
                children = proc.children(recursive=False)
                child_counts.append(len(children))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        unique_names: Set[str] = set(process_names)
        foreground = process_names[0] if process_names else ""
        unknown_flag = 1.0 if foreground and foreground not in KNOWN_PROCESS_ALLOWLIST else 0.0

        return {
            "process_name": foreground,
            "ap_unique_count": float(len(unique_names)),
            "ap_unknown_flag": unknown_flag,
            "child_process_count": max(child_counts) if child_counts else 0,
            "powershell_detected": any("powershell" in name for name in unique_names),
            "cmd_detected": any(name in {"cmd.exe", "cmd"} for name in unique_names),
            "credential_tools": any(name.split(".")[0] in {"mimikatz", "lazagne"} for name in unique_names),
        }
