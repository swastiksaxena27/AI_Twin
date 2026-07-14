"""Response action implementations — lightweight, no kernel drivers."""

import platform
import subprocess
from pathlib import Path
from typing import Optional

from behavioral_guardian.config.settings import (
    DATA_DIR,
    RESPONSE_ACTION_KILL_PROCESS,
    RESPONSE_ACTION_LOCK_WORKSTATION,
    RESPONSE_ACTION_MONITOR,
    RESPONSE_ACTION_REAUTH,
    RESPONSE_ACTION_WARN,
)
from behavioral_guardian.utils.logging_config import ensure_directory, setup_logging

logger = setup_logging(__name__)


def action_monitor(user_id: int) -> str:
    """Log monitoring action."""
    message = f"Monitoring user_id={user_id}"
    logger.info(message)
    return message


def action_warn(user_id: int) -> str:
    """Log warning action."""
    message = f"Warning issued for user_id={user_id}"
    logger.warning(message)
    return message


def action_reauth(user_id: int) -> str:
    """Trigger reauthentication workflow."""
    screenshot_dir = ensure_directory(DATA_DIR / "screenshots")
    screenshot_path = screenshot_dir / f"user_{user_id}_reauth.png"
    message = f"Reauthentication required for user_id={user_id}; screenshot path={screenshot_path}"
    logger.warning(message)
    return message


def action_kill_process(process_name: Optional[str]) -> str:
    """Attempt to terminate suspicious process."""
    if not process_name:
        message = "Kill process requested but no process name provided"
        logger.error(message)
        return message
    try:
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/F", "/IM", process_name], check=False, capture_output=True)
        else:
            subprocess.run(["pkill", "-f", process_name], check=False, capture_output=True)
        message = f"Attempted to kill process: {process_name}"
        logger.warning(message)
        return message
    except OSError as exc:
        message = f"Failed to kill process {process_name}: {exc}"
        logger.exception(message)
        return message


def action_lock_workstation() -> str:
    """Lock workstation using OS-native command."""
    try:
        if platform.system() == "Windows":
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=False)
        elif platform.system() == "Darwin":
            subprocess.run(
                ["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"],
                check=False,
            )
        else:
            subprocess.run(["loginctl", "lock-session"], check=False)
        message = "Workstation lock initiated"
        logger.critical(message)
        return message
    except OSError as exc:
        message = f"Failed to lock workstation: {exc}"
        logger.exception(message)
        return message


ACTION_HANDLERS = {
    RESPONSE_ACTION_MONITOR: lambda user_id, **_: action_monitor(user_id),
    RESPONSE_ACTION_WARN: lambda user_id, **_: action_warn(user_id),
    RESPONSE_ACTION_REAUTH: lambda user_id, **_: action_reauth(user_id),
    RESPONSE_ACTION_KILL_PROCESS: lambda user_id, process_name=None, **_: action_kill_process(process_name),
    RESPONSE_ACTION_LOCK_WORKSTATION: lambda user_id, **_: action_lock_workstation(),
}
