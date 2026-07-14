"""Network activity monitoring."""

from typing import Any, Dict

import psutil

from behavioral_guardian.utils.logging_config import setup_logging

logger = setup_logging(__name__)


class NetworkMonitor:
    """Track network upload volume between snapshots."""

    def __init__(self) -> None:
        counters = psutil.net_io_counters()
        self._last_bytes_sent = counters.bytes_sent if counters else 0

    def snapshot(self) -> Dict[str, Any]:
        """Return upload delta since last snapshot."""
        counters = psutil.net_io_counters()
        current_sent = counters.bytes_sent if counters else self._last_bytes_sent
        delta = max(0, current_sent - self._last_bytes_sent)
        self._last_bytes_sent = current_sent
        return {"network_upload_bytes": float(delta)}
