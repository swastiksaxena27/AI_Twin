"""Session API router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from behavioral_guardian.backend.dependencies import get_db, get_session_service, require_self_or_org_admin
from behavioral_guardian.backend.schemas.models import SessionResponse
from behavioral_guardian.backend.services.session_service import SessionService
from behavioral_guardian.database.models import User

router = APIRouter(tags=["session"])


@router.get("/session/{user_id}", response_model=SessionResponse)
def get_session(
    user_id: int,
    db: Session = Depends(get_db),
    service: SessionService = Depends(get_session_service),
    _current_user: User = Depends(require_self_or_org_admin),
) -> SessionResponse:
    """Get current session information."""
    return service.get_session(db, user_id)
