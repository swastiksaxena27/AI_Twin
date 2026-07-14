"""Feature vector assembly."""

from typing import Any, Dict

from behavioral_guardian.config.settings import FROZEN_FEATURE_NAMES
from behavioral_guardian.utils.logging_config import setup_logging

logger = setup_logging(__name__)


class FeatureExtractor:
    """Combine collector snapshots into a frozen feature vector."""

    def build_vector(
        self,
        keyboard: Dict[str, float],
        mouse: Dict[str, float],
        process: Dict[str, Any],
    ) -> Dict[str, float]:
        """Merge behavioral features using frozen names."""
        vector = {
            "ks_dwell_mean": keyboard.get("ks_dwell_mean", 0.0),
            "ks_dwell_std": keyboard.get("ks_dwell_std", 0.0),
            "ks_flight_mean": keyboard.get("ks_flight_mean", 0.0),
            "ks_flight_std": keyboard.get("ks_flight_std", 0.0),
            "ks_wpm": keyboard.get("ks_wpm", 0.0),
            "ks_error_rate": keyboard.get("ks_error_rate", 0.0),
            "ms_speed_mean": mouse.get("ms_speed_mean", 0.0),
            "ms_speed_std": mouse.get("ms_speed_std", 0.0),
            "ms_click_rate": mouse.get("ms_click_rate", 0.0),
            "ms_idle_ratio": mouse.get("ms_idle_ratio", 0.0),
            "ap_unique_count": float(process.get("ap_unique_count", 0.0)),
            "ap_unknown_flag": float(process.get("ap_unknown_flag", 0.0)),
        }
        for name in FROZEN_FEATURE_NAMES:
            vector.setdefault(name, 0.0)
        return vector

    def build_activity_signals(
        self,
        process: Dict[str, Any],
        usb: Dict[str, Any],
        download: Dict[str, Any],
        network: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge activity signals for risk engine."""
        signals = {}
        signals.update(process)
        signals.update(usb)
        signals.update(download)
        signals.update(network)
        signals.setdefault("registry_persistence", False)
        return signals
