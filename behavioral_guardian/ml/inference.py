"""Isolation Forest inference."""

from typing import Dict, List

import numpy as np

from behavioral_guardian.config.settings import ANOMALY_SCORE_MAX, ANOMALY_SCORE_MIN, FROZEN_FEATURE_NAMES
from behavioral_guardian.ml.persistence import load_model_artifacts, model_exists
from behavioral_guardian.ml.trainer import train_isolation_forest
from behavioral_guardian.utils.logging_config import setup_logging

logger = setup_logging(__name__)


def _score_from_decision(decision: float) -> float:
    """Map Isolation Forest decision function to 0-1 anomaly score."""
    normalized = max(ANOMALY_SCORE_MIN, min(ANOMALY_SCORE_MAX, 0.5 - decision))
    return float(normalized)


def predict_anomaly(user_id: int, features: Dict[str, float], bootstrap_rows: List[Dict[str, float]] | None = None) -> float:
    """
    Run inference for a user.

    If no model exists, optionally bootstrap from provided rows.
    """
    if not model_exists(user_id):
        if bootstrap_rows:
            logger.warning("Bootstrapping model for user_id=%d", user_id)
            from behavioral_guardian.ml.persistence import save_model_artifacts
            from behavioral_guardian.ml.baseline import generate_baseline

            model, scaler = train_isolation_forest(bootstrap_rows)
            baseline = generate_baseline(bootstrap_rows, FROZEN_FEATURE_NAMES)
            save_model_artifacts(user_id, model, scaler, baseline)
        else:
            logger.warning("No model for user_id=%d; returning neutral anomaly", user_id)
            return 0.0

    model, scaler, _ = load_model_artifacts(user_id)
    vector = np.array([[features[name] for name in FROZEN_FEATURE_NAMES]])
    scaled = scaler.transform(vector)
    decision = model.decision_function(scaled)[0]
    anomaly_score = _score_from_decision(decision)
    logger.info("Anomaly score for user_id=%d: %.4f", user_id, anomaly_score)
    return anomaly_score
