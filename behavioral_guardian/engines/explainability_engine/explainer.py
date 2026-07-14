"""Explainability engine — human-readable decision summaries."""

from typing import Any, Dict, List


def build_explanations(
    trust_explanation: str,
    risk_explanations: List[str],
    response_result: Dict[str, Any],
    anomaly_score: float,
    identity_trust: float,
    activity_risk: float,
    status_level: str,
) -> List[str]:
    """Combine trust, risk, and response outputs into explanation list."""
    explanations = [
        f"Anomaly score: {anomaly_score:.2f}",
        f"Identity trust: {identity_trust:.1f} ({status_level})",
        trust_explanation,
        f"Activity risk: {activity_risk:.1f}",
    ]
    explanations.extend(risk_explanations)
    explanations.append(
        f"Response level {response_result['level']}: {response_result['description']}"
    )
    for detail in response_result.get("details", []):
        explanations.append(detail)
    return explanations
