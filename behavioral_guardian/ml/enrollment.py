"""Digital Twin enrollment."""

from datetime import datetime, timezone
from typing import Dict, List

from sqlalchemy.orm import Session

from behavioral_guardian.config.settings import FROZEN_FEATURE_NAMES, TRAINING_PERIOD_DAYS_MIN
from behavioral_guardian.database.models import ModelMetadata
from behavioral_guardian.ml.baseline import generate_baseline
from behavioral_guardian.ml.persistence import save_model_artifacts
from behavioral_guardian.ml.trainer import train_isolation_forest
from behavioral_guardian.utils.logging_config import setup_logging

logger = setup_logging(__name__)


def enroll_user(db: Session, user_id: int, feature_rows: List[Dict[str, float]]) -> ModelMetadata:
    """
    Train static Isolation Forest model from enrollment data.

    Expects 7–10 days of feature vectors in production; uses provided rows for bootstrap.
    """
    if len(feature_rows) < 10:
        logger.warning("Enrollment for user_id=%d has only %d samples", user_id, len(feature_rows))

    started_at = datetime.now(timezone.utc)
    model, scaler = train_isolation_forest(feature_rows)
    baseline = generate_baseline(feature_rows, FROZEN_FEATURE_NAMES)
    save_model_artifacts(user_id, model, scaler, baseline)

    metadata = ModelMetadata(
        user_id=user_id,
        model_version="1.0.0",
        training_samples=len(feature_rows),
        training_started_at=started_at,
        training_completed_at=datetime.now(timezone.utc),
        is_active=True,
    )
    db.add(metadata)
    db.flush()
    logger.info(
        "Enrolled user_id=%d with %d samples (target period %d days)",
        user_id,
        len(feature_rows),
        TRAINING_PERIOD_DAYS_MIN,
    )
    return metadata
