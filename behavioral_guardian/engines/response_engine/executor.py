"""Response engine executor."""

from typing import Any, Dict, List

from behavioral_guardian.engines.response_engine.actions import ACTION_HANDLERS
from behavioral_guardian.engines.response_engine.levels import RESPONSE_LEVELS, determine_response_level
from behavioral_guardian.utils.logging_config import setup_logging

logger = setup_logging(__name__)


def execute_response(
    user_id: int,
    identity_trust: float,
    activity_risk: float,
    status_level: str,
    activity_signals: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Determine and execute response actions.

    Returns level, actions taken, and execution details.
    """
    level = determine_response_level(identity_trust, activity_risk, status_level)
    level_config = RESPONSE_LEVELS[level]
    actions_taken: List[str] = []
    details: List[str] = []

    process_name = activity_signals.get("process_name")

    for action in level_config["actions"]:
        handler = ACTION_HANDLERS.get(action)
        if handler is None:
            logger.error("Unknown response action: %s", action)
            continue
        detail = handler(user_id=user_id, process_name=process_name)
        actions_taken.append(action)
        details.append(detail)

    logger.info("Response level=%d actions=%s user_id=%d", level, actions_taken, user_id)
    return {
        "level": level,
        "actions": actions_taken,
        "description": level_config["description"],
        "details": details,
    }
