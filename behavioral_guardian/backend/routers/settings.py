"""Settings API router — security policy + threshold configuration per user."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from behavioral_guardian.backend.dependencies import get_db, get_settings_service, require_self_or_org_admin
from behavioral_guardian.backend.schemas.models import SettingsResponse, SettingsUpdateRequest
from behavioral_guardian.backend.services.settings_service import SettingsService
from behavioral_guardian.database.models import User

router = APIRouter(tags=["settings"])


@router.get("/settings/{user_id}", response_model=SettingsResponse)
def get_settings(
    user_id: int,
    db: Session = Depends(get_db),
    service: SettingsService = Depends(get_settings_service),
    _current_user: User = Depends(require_self_or_org_admin),
) -> SettingsResponse:
    """Get the stored security policy / threshold configuration for a user."""
    return service.get_settings(db, user_id)


@router.put("/settings/{user_id}", response_model=SettingsResponse)
def update_settings(
    user_id: int,
    payload: SettingsUpdateRequest,
    db: Session = Depends(get_db),
    service: SettingsService = Depends(get_settings_service),
    _current_user: User = Depends(require_self_or_org_admin),
) -> SettingsResponse:
    """Update one or more settings fields for a user."""
    return service.update_settings(db, user_id, payload)
