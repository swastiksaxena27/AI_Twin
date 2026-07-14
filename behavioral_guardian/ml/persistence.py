"""ML model persistence using joblib."""

import json
from pathlib import Path
from typing import Any, Tuple

import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from behavioral_guardian.config.settings import (
    MODEL_FILENAME_BASELINE,
    MODEL_FILENAME_ISOLATION_FOREST,
    MODEL_FILENAME_SCALER,
    MODELS_DIR,
)
from behavioral_guardian.utils.logging_config import ensure_directory, setup_logging

logger = setup_logging(__name__)


def user_model_dir(user_id: int) -> Path:
    """Return per-user model directory."""
    return ensure_directory(MODELS_DIR / str(user_id))


def save_model_artifacts(
    user_id: int,
    model: IsolationForest,
    scaler: StandardScaler,
    baseline: dict,
) -> None:
    """Persist model, scaler, and baseline for a user."""
    directory = user_model_dir(user_id)
    joblib.dump(model, directory / MODEL_FILENAME_ISOLATION_FOREST)
    joblib.dump(scaler, directory / MODEL_FILENAME_SCALER)
    with open(directory / MODEL_FILENAME_BASELINE, "w", encoding="utf-8") as handle:
        json.dump(baseline, handle, indent=2)
    logger.info("Saved model artifacts for user_id=%d", user_id)


def load_model_artifacts(user_id: int) -> Tuple[IsolationForest, StandardScaler, dict]:
    """Load model artifacts for a user."""
    directory = user_model_dir(user_id)
    model = joblib.load(directory / MODEL_FILENAME_ISOLATION_FOREST)
    scaler = joblib.load(directory / MODEL_FILENAME_SCALER)
    with open(directory / MODEL_FILENAME_BASELINE, "r", encoding="utf-8") as handle:
        baseline = json.load(handle)
    return model, scaler, baseline


def model_exists(user_id: int) -> bool:
    """Check whether all model artifacts exist."""
    directory = user_model_dir(user_id)
    return all((directory / name).exists() for name in (
        MODEL_FILENAME_ISOLATION_FOREST,
        MODEL_FILENAME_SCALER,
        MODEL_FILENAME_BASELINE,
    ))
