"""Risk API router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from behavioral_guardian.backend.dependencies import get_db, get_risk_service, require_self_or_org_admin
from behavioral_guardian.backend.schemas.models import RiskResponse
from behavioral_guardian.backend.services.risk_service import RiskService
from behavioral_guardian.database.models import User

router = APIRouter(tags=["risk"])


@router.get("/risk/{user_id}", response_model=RiskResponse)
def get_risk(
    user_id: int,
    db: Session = Depends(get_db),
    service: RiskService = Depends(get_risk_service),
    _current_user: User = Depends(require_self_or_org_admin),
) -> RiskResponse:
    """Get activity risk for user. Requires a valid bearer token."""
    return service.get_risk(db, user_id)
