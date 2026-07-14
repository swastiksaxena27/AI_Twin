"""Keyboard behavioral collector — timings only, no typed text."""

import statistics
import time
from collections import deque
from threading import Lock
from typing import Deque, Dict

from behavioral_guardian.utils.logging_config import setup_logging

logger = setup_logging(__name__)


class KeyboardCollector:
    """Collect keyboard dwell and flight timings."""

    def __init__(self, window_size: int = 200) -> None:
        self._dwell_times: Deque[float] = deque(maxlen=window_size)
        self._flight_times: Deque[float] = deque(maxlen=window_size)
        self._key_press_times: Dict[int, float] = {}
        self._last_release_time: float | None = None
        self._keystroke_count = 0
        self._error_count = 0
        self._window_start = time.time()
        self._lock = Lock()

    def on_press(self, key) -> None:
        """Record key press timestamp."""
        try:
            key_id = hash(key)
        except TypeError:
            return
        with self._lock:
            now = time.time()
            self._key_press_times[key_id] = now
            if self._last_release_time is not None:
                self._flight_times.append(now - self._last_release_time)

    def on_release(self, key) -> None:
        """Record dwell time on key release."""
        try:
            key_id = hash(key)
        except TypeError:
            return
        with self._lock:
            now = time.time()
            press_time = self._key_press_times.pop(key_id, None)
            if press_time is not None:
                self._dwell_times.append(now - press_time)
                self._keystroke_count += 1
            self._last_release_time = now

    def record_error(self) -> None:
        """Increment error counter (e.g., backspace bursts)."""
        with self._lock:
            self._error_count += 1

    def snapshot(self) -> Dict[str, float]:
        """Return keyboard metrics for feature extraction."""
        with self._lock:
            dwell = list(self._dwell_times)
            flight = list(self._flight_times)
            elapsed_minutes = max((time.time() - self._window_start) / 60.0, 0.01)
            wpm = self._keystroke_count / elapsed_minutes
            error_rate = self._error_count / max(self._keystroke_count, 1)

        return {
            "ks_dwell_mean": statistics.mean(dwell) if dwell else 0.0,
            "ks_dwell_std": statistics.pstdev(dwell) if len(dwell) > 1 else 0.0,
            "ks_flight_mean": statistics.mean(flight) if flight else 0.0,
            "ks_flight_std": statistics.pstdev(flight) if len(flight) > 1 else 0.0,
            "ks_wpm": wpm,
            "ks_error_rate": error_rate,
        }
