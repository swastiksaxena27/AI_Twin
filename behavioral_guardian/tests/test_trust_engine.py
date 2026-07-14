"""Trust engine tests."""

from behavioral_guardian.engines.trust_engine import compute_identity_trust
from behavioral_guardian.config.settings import TRUST_STATUS_NORMAL, TRUST_STATUS_SUSPICIOUS


def test_initial_trust_from_low_anomaly():
    trust, status, explanation = compute_identity_trust(0.1)
    assert trust >= 80
    assert status == TRUST_STATUS_NORMAL
    assert explanation


def test_trust_decays_with_high_anomaly():
    trust, status, _ = compute_identity_trust(0.9, previous_trust=90.0)
    assert trust < 90
    assert status in {TRUST_STATUS_SUSPICIOUS, "HIGH_RISK", "CRITICAL", "ELEVATED"}
