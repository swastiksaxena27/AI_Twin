"""Alerts API router."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from behavioral_guardian.backend.dependencies import get_alert_service, get_db, require_self_or_org_admin
from behavioral_guardian.backend.schemas.models import AlertResponse
from behavioral_guardian.backend.services.alert_service import AlertService
from behavioral_guardian.database.models import User

router = APIRouter(tags=["alerts"])


@router.get("/alerts/{user_id}", response_model=List[AlertResponse])
def get_alerts(
    user_id: int,
    db: Session = Depends(get_db),
    service: AlertService = Depends(get_alert_service),
    _current_user: User = Depends(require_self_or_org_admin),
) -> List[AlertResponse]:
    """Get alerts for user."""
    return service.get_alerts(db, user_id)
