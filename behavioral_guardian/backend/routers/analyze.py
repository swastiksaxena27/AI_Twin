"""Analyze API router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from behavioral_guardian.backend.dependencies import get_analyze_service, get_current_user, get_db
from behavioral_guardian.backend.schemas.models import AnalyzeResponse, FeatureVector
from behavioral_guardian.backend.services.analyze_service import AnalyzeService
from behavioral_guardian.database.models import User

router = APIRouter(tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(
    payload: FeatureVector,
    db: Session = Depends(get_db),
    service: AnalyzeService = Depends(get_analyze_service),
    current_user: User = Depends(get_current_user),
) -> AnalyzeResponse:
    """Analyze behavioral feature vector. The token holder must match
    `payload.user_id` (or be an org admin) — the agent can only submit
    data for the account it authenticated as."""
    if current_user.id != payload.user_id and not current_user.is_org_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot submit behavioral data for another user",
        )
    return service.analyze(db, payload)
