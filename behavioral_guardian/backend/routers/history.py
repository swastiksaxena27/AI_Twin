"""History API router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from behavioral_guardian.backend.dependencies import get_db, get_history_service, require_self_or_org_admin
from behavioral_guardian.backend.schemas.models import HistoryResponse
from behavioral_guardian.backend.services.history_service import HistoryService
from behavioral_guardian.database.models import User

router = APIRouter(tags=["history"])


@router.get("/history/{user_id}", response_model=HistoryResponse)
def get_history(
    user_id: int,
    db: Session = Depends(get_db),
    service: HistoryService = Depends(get_history_service),
    _current_user: User = Depends(require_self_or_org_admin),
) -> HistoryResponse:
    """Get trust and risk history."""
    return service.get_history(db, user_id)
