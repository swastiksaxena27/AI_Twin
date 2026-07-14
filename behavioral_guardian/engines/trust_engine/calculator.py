"""Identity trust calculator."""

from typing import Optional, Tuple

from behavioral_guardian.config.settings import (
    TRUST_ANOMALY_WEIGHT,
    TRUST_HISTORY_WEIGHT,
    TRUST_SCORE_MAX,
)
from behavioral_guardian.engines.trust_engine.decay import apply_decay, clamp_trust
from behavioral_guardian.engines.trust_engine.recovery import apply_recovery
from behavioral_guardian.engines.trust_engine.status import resolve_status_level
from behavioral_guardian.utils.logging_config import setup_logging

logger = setup_logging(__name__)


def anomaly_to_trust(anomaly_score: float) -> float:
    """Convert anomaly score (0-1) to instantaneous trust contribution."""
    return (1.0 - anomaly_score) * TRUST_SCORE_MAX


def compute_identity_trust(anomaly_score: float, previous_trust: Optional[float] = None) -> Tuple[float, str, str]:
    """
    Compute identity_trust using weighted averaging, decay, and recovery.

    Returns:
        identity_trust, status_level, explanation
    """
    instantaneous = anomaly_to_trust(anomaly_score)

    if previous_trust is None:
        identity_trust = instantaneous
        explanation = "Initial trust score derived from current behavioral baseline."
    else:
        weighted = (instantaneous * TRUST_ANOMALY_WEIGHT) + (previous_trust * TRUST_HISTORY_WEIGHT)
        if anomaly_score >= 0.5:
            adjusted = apply_decay(weighted, anomaly_score)
            explanation = f"Trust decay applied due to elevated anomaly score ({anomaly_score:.2f})."
        else:
            adjusted = apply_recovery(weighted, anomaly_score)
            explanation = f"Trust recovery applied; behavior within expected range ({anomaly_score:.2f})."
        identity_trust = clamp_trust(adjusted)

    status_level = resolve_status_level(identity_trust)
    logger.info("Computed identity_trust=%.2f status=%s", identity_trust, status_level)
    return identity_trust, status_level, explanation
