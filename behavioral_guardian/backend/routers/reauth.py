"""Reauth API router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from behavioral_guardian.backend.dependencies import get_current_user, get_db, get_reauth_service
from behavioral_guardian.backend.schemas.models import ReauthRequest, ReauthResponse
from behavioral_guardian.backend.services.reauth_service import ReauthService
from behavioral_guardian.database.models import User

router = APIRouter(tags=["reauth"])


@router.post("/reauth", response_model=ReauthResponse)
def reauth(
    payload: ReauthRequest,
    db: Session = Depends(get_db),
    service: ReauthService = Depends(get_reauth_service),
    current_user: User = Depends(get_current_user),
) -> ReauthResponse:
    """Submit reauthentication attempt. Token holder must match `payload.user_id`
    (or be an org admin)."""
    if current_user.id != payload.user_id and not current_user.is_org_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot submit reauthentication for another user",
        )
    return service.reauth(db, payload)
