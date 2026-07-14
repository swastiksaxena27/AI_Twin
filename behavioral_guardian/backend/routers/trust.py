"""Trust API router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from behavioral_guardian.backend.dependencies import get_db, get_trust_service, require_self_or_org_admin
from behavioral_guardian.backend.schemas.models import TrustResponse
from behavioral_guardian.backend.services.trust_service import TrustService
from behavioral_guardian.database.models import User

router = APIRouter(tags=["trust"])


@router.get("/trust/{user_id}", response_model=TrustResponse)
def get_trust(
    user_id: int,
    db: Session = Depends(get_db),
    service: TrustService = Depends(get_trust_service),
    _current_user: User = Depends(require_self_or_org_admin),
) -> TrustResponse:
    """Get identity trust for user. Requires a valid bearer token for this
    user (or an org admin's token)."""
    return service.get_trust(db, user_id)
