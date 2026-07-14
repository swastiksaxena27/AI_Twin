"""Trust engine status level mapping."""

from behavioral_guardian.config.settings import (
    TRUST_STATUS_CRITICAL,
    TRUST_STATUS_ELEVATED,
    TRUST_STATUS_HIGH_RISK,
    TRUST_STATUS_NORMAL,
    TRUST_STATUS_SUSPICIOUS,
    TRUST_THRESHOLD_ELEVATED,
    TRUST_THRESHOLD_HIGH_RISK,
    TRUST_THRESHOLD_NORMAL,
    TRUST_THRESHOLD_SUSPICIOUS,
)


def resolve_status_level(identity_trust: float) -> str:
    """Map identity_trust score to status level."""
    if identity_trust >= TRUST_THRESHOLD_NORMAL:
        return TRUST_STATUS_NORMAL
    if identity_trust >= TRUST_THRESHOLD_ELEVATED:
        return TRUST_STATUS_ELEVATED
    if identity_trust >= TRUST_THRESHOLD_SUSPICIOUS:
        return TRUST_STATUS_SUSPICIOUS
    if identity_trust >= TRUST_THRESHOLD_HIGH_RISK:
        return TRUST_STATUS_HIGH_RISK
    return TRUST_STATUS_CRITICAL
