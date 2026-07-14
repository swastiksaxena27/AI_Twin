"""Integration tests."""

from behavioral_guardian.backend.schemas.models import FeatureVector
from behavioral_guardian.engines.risk_engine import compute_activity_risk
from behavioral_guardian.engines.trust_engine import compute_identity_trust
from behavioral_guardian.engines.response_engine import execute_response
from behavioral_guardian.ml.inference import predict_anomaly


def test_ml_to_trust_to_response_pipeline():
    features = FeatureVector(user_id=100).to_feature_dict()
    anomaly = predict_anomaly(100, features, bootstrap_rows=[features] * 20)
    trust, status, trust_explanation = compute_identity_trust(anomaly)
    risk, rules, risk_explanations = compute_activity_risk({"powershell_detected": True})
    response = execute_response(100, trust, risk, status, {"process_name": "powershell.exe"})
    assert 0.0 <= anomaly <= 1.0
    assert 0.0 <= trust <= 100.0
    assert risk > 0
    assert response["level"] >= 1
    assert trust_explanation
    assert rules
    assert risk_explanations
