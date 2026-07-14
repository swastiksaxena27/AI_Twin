"""Mouse behavioral collector."""

import statistics
import time
from collections import deque
from threading import Lock
from typing import Deque, Dict, Tuple

from behavioral_guardian.utils.logging_config import setup_logging

logger = setup_logging(__name__)


class MouseCollector:
    """Collect mouse speed, click rate, and idle ratio."""

    def __init__(self, window_size: int = 500) -> None:
        self._positions: Deque[Tuple[float, float, float]] = deque(maxlen=window_size)
        self._click_times: Deque[float] = deque(maxlen=window_size)
        self._last_move_time = time.time()
        self._idle_seconds = 0.0
        self._window_start = time.time()
        self._lock = Lock()

    def on_move(self, x: float, y: float) -> None:
        """Record mouse movement."""
        now = time.time()
        with self._lock:
            if self._positions:
                _, last_x, last_y = self._positions[-1]
                if x == last_x and y == last_y:
                    self._idle_seconds += now - self._last_move_time
            self._positions.append((now, x, y))
            self._last_move_time = now

    def on_click(self, x: float, y: float, button, pressed: bool) -> None:
        """Record click events."""
        if pressed:
            with self._lock:
                self._click_times.append(time.time())

    def snapshot(self) -> Dict[str, float]:
        """Return mouse metrics for feature extraction."""
        with self._lock:
            positions = list(self._positions)
            clicks = list(self._click_times)
            elapsed = max(time.time() - self._window_start, 0.01)

        speeds = []
        for idx in range(1, len(positions)):
            t0, x0, y0 = positions[idx - 1]
            t1, x1, y1 = positions[idx]
            dt = t1 - t0
            if dt > 0:
                distance = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
                speeds.append(distance / dt)

        click_rate = len(clicks) / elapsed
        idle_ratio = self._idle_seconds / elapsed

        return {
            "ms_speed_mean": statistics.mean(speeds) if speeds else 0.0,
            "ms_speed_std": statistics.pstdev(speeds) if len(speeds) > 1 else 0.0,
            "ms_click_rate": click_rate,
            "ms_idle_ratio": min(1.0, idle_ratio),
        }
