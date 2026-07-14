"""Response level definitions."""

from behavioral_guardian.config.settings import (
    RESPONSE_ACTION_KILL_PROCESS,
    RESPONSE_ACTION_LOCK_WORKSTATION,
    RESPONSE_ACTION_MONITOR,
    RESPONSE_ACTION_REAUTH,
    RESPONSE_ACTION_WARN,
    RESPONSE_LEVEL_1_MAX_RISK,
    RESPONSE_LEVEL_2_MAX_RISK,
    RESPONSE_LEVEL_3_MAX_RISK,
    RESPONSE_LEVEL_4_MAX_RISK,
    TRUST_STATUS_CRITICAL,
    TRUST_STATUS_HIGH_RISK,
)

RESPONSE_LEVELS = {
    1: {"actions": [RESPONSE_ACTION_MONITOR], "description": "Monitor only"},
    2: {"actions": [RESPONSE_ACTION_WARN], "description": "Issue warning"},
    3: {"actions": [RESPONSE_ACTION_REAUTH], "description": "Reauthentication and screenshot"},
    4: {"actions": [RESPONSE_ACTION_KILL_PROCESS], "description": "Kill suspicious process and alert owner"},
    5: {"actions": [RESPONSE_ACTION_LOCK_WORKSTATION], "description": "Lock workstation and critical alert"},
}


def determine_response_level(identity_trust: float, activity_risk: float, status_level: str) -> int:
    """Determine response level from trust, risk, and status."""
    if status_level == TRUST_STATUS_CRITICAL or activity_risk > RESPONSE_LEVEL_4_MAX_RISK:
        return 5
    if status_level == TRUST_STATUS_HIGH_RISK or activity_risk > RESPONSE_LEVEL_3_MAX_RISK:
        return 4
    if activity_risk > RESPONSE_LEVEL_2_MAX_RISK or identity_trust < 40:
        return 3
    if activity_risk > RESPONSE_LEVEL_1_MAX_RISK or identity_trust < 60:
        return 2
    return 1
