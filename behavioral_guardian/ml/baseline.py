"""Baseline statistics generation."""

from typing import Dict, List

import numpy as np


def generate_baseline(feature_rows: List[Dict[str, float]], feature_names: tuple) -> dict:
    """Compute mean and std baseline from enrollment feature rows."""
    if not feature_rows:
        return {"feature_names": list(feature_names), "mean": {}, "std": {}}

    matrix = np.array([[row[name] for name in feature_names] for row in feature_rows])
    means = matrix.mean(axis=0)
    stds = matrix.std(axis=0)
    return {
        "feature_names": list(feature_names),
        "mean": {name: float(means[i]) for i, name in enumerate(feature_names)},
        "std": {name: float(stds[i]) for i, name in enumerate(feature_names)},
        "sample_count": len(feature_rows),
    }
