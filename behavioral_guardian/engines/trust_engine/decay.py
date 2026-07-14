"""Trust decay mechanism."""

from behavioral_guardian.config.settings import TRUST_DECAY_RATE, TRUST_SCORE_MAX


def apply_decay(previous_trust: float, anomaly_score: float) -> float:
    """Reduce trust when anomaly score is elevated."""
    decay = TRUST_DECAY_RATE * anomaly_score * 100
    return max(0.0, previous_trust - decay)


def clamp_trust(value: float) -> float:
    """Clamp trust to valid range."""
    return max(0.0, min(float(TRUST_SCORE_MAX), value))
