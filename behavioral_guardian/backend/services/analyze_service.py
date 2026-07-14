"""Analyze pipeline service."""

from sqlalchemy.orm import Session

from behavioral_guardian.backend.schemas.models import AnalyzeResponse, FeatureVector
from behavioral_guardian.database import repositories as repo
from behavioral_guardian.engines.explainability_engine import build_explanations
from behavioral_guardian.engines.risk_engine import compute_activity_risk
from behavioral_guardian.engines.response_engine import execute_response
from behavioral_guardian.engines.trust_engine import compute_identity_trust
from behavioral_guardian.ml.inference import predict_anomaly
from behavioral_guardian.utils.logging_config import setup_logging

logger = setup_logging(__name__)


class AnalyzeService:
    """Orchestrate ML, trust, risk, response, and persistence."""

    def analyze(self, db: Session, payload: FeatureVector) -> AnalyzeResponse:
        """Run full analyze pipeline."""
        repo.get_or_create_user(db, payload.user_id)
        repo.touch_session(db, payload.user_id, payload.device_id)

        features = payload.to_feature_dict()
        repo.save_feature_vector(db, payload.user_id, features, payload.device_id)

        anomaly_score = predict_anomaly(payload.user_id, features)
        previous_trust = repo.get_latest_trust(db, payload.user_id)
        previous_value = previous_trust.identity_trust if previous_trust else None
        identity_trust, status_level, trust_explanation = compute_identity_trust(anomaly_score, previous_value)

        activity_risk, triggered_rules, risk_explanations = compute_activity_risk(payload.activity_signals)
        response_result = execute_response(
            payload.user_id,
            identity_trust,
            activity_risk,
            status_level,
            payload.activity_signals,
        )

        explanations = build_explanations(
            trust_explanation,
            risk_explanations,
            response_result,
            anomaly_score,
            identity_trust,
            activity_risk,
            status_level,
        )

        repo.save_trust_event(db, payload.user_id, identity_trust, status_level, anomaly_score, trust_explanation)
        repo.save_risk_event(db, payload.user_id, activity_risk, triggered_rules, risk_explanations)

        for action in response_result["actions"]:
            repo.save_response_event(
                db,
                payload.user_id,
                action,
                response_result["level"],
                detail="; ".join(response_result.get("details", [])),
            )

        if response_result["level"] >= 2:
            repo.save_alert(
                db,
                payload.user_id,
                severity=status_level,
                title=f"Response level {response_result['level']}",
                message=response_result["description"],
            )

        db.commit()
        logger.info("Analyze complete user_id=%d trust=%.1f risk=%.1f", payload.user_id, identity_trust, activity_risk)

        return AnalyzeResponse(
            user_id=payload.user_id,
            anomaly_score=anomaly_score,
            identity_trust=identity_trust,
            status_level=status_level,
            activity_risk=activity_risk,
            triggered_rules=triggered_rules,
            response_actions=response_result["actions"],
            explanations=explanations,
        )
