"""Trust recovery mechanism."""

from behavioral_guardian.config.settings import TRUST_RECOVERY_RATE, TRUST_SCORE_MAX


def apply_recovery(previous_trust: float, anomaly_score: float) -> float:
    """Increase trust when behavior is normal."""
    if anomaly_score > 0.3:
        return previous_trust
    recovery = TRUST_RECOVERY_RATE * (1.0 - anomaly_score) * 100
    return min(float(TRUST_SCORE_MAX), previous_trust + recovery)
