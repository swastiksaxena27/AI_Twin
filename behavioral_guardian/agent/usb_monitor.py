"""USB device monitoring."""

from typing import Any, Dict

from behavioral_guardian.utils.logging_config import setup_logging

logger = setup_logging(__name__)


class USBMonitor:
    """Detect USB insertion events."""

    def __init__(self) -> None:
        self._usb_insertion = False

    def mark_insertion(self) -> None:
        """Record a USB insertion event."""
        self._usb_insertion = True
        logger.info("USB insertion detected")

    def snapshot(self) -> Dict[str, Any]:
        """Return USB activity signals and reset latch."""
        detected = self._usb_insertion
        self._usb_insertion = False
        return {"usb_insertion": detected}
