"""Isolation Forest training."""

from typing import Dict, List, Tuple

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from behavioral_guardian.config.settings import FROZEN_FEATURE_NAMES


def train_isolation_forest(feature_rows: List[Dict[str, float]]) -> Tuple[IsolationForest, StandardScaler]:
    """Train Isolation Forest and scaler on feature rows."""
    matrix = np.array([[row[name] for name in FROZEN_FEATURE_NAMES] for row in feature_rows])
    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
    )
    model.fit(scaled)
    return model, scaler
