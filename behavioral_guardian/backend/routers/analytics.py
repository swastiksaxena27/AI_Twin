"""Analytics API router — real aggregates for the Risk Analytics dashboard."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from behavioral_guardian.backend.dependencies import get_analytics_service, get_db, require_self_or_org_admin
from behavioral_guardian.backend.schemas.models import AnalyticsResponse
from behavioral_guardian.backend.services.analytics_service import AnalyticsService
from behavioral_guardian.database.models import User

router = APIRouter(tags=["analytics"])


@router.get("/analytics/{user_id}", response_model=AnalyticsResponse)
def get_analytics(
    user_id: int,
    organization: str | None = None,
    days: int = 7,
    db: Session = Depends(get_db),
    service: AnalyticsService = Depends(get_analytics_service),
    _current_user: User = Depends(require_self_or_org_admin),
) -> AnalyticsResponse:
    """Real risk/trust/alert/response aggregates for the last N days.

    Pass `organization` to aggregate across every user in that org instead
    of just `user_id` (used by the Organization Overview's Risk Analytics page).
    Requires a valid bearer token for `user_id` (or an org admin's token).
    """
    return service.get_analytics(db, user_id, organization=organization, days=days)
