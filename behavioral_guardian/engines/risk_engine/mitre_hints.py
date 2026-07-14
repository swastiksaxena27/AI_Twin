"""MITRE ATT&CK expansion hints for future rule mapping."""

from behavioral_guardian.engines.risk_engine.rules import RISK_RULES


def get_mitre_hints() -> dict:
    """Return rule name to MITRE technique hint mapping."""
    return {name: meta["mitre_hint"] for name, meta in RISK_RULES.items()}
