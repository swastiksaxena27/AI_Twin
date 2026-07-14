"""Users API router — roster listing, single profile, profile update."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from behavioral_guardian.backend.dependencies import get_current_user, get_db, get_user_service, require_self_or_org_admin
from behavioral_guardian.backend.schemas.models import UserProfile, UserUpdateRequest
from behavioral_guardian.backend.services.user_service import UserService
from behavioral_guardian.database.models import User

router = APIRouter(tags=["users"])


@router.get("/users", response_model=List[UserProfile])
def list_users(
    organization: Optional[str] = None,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> List[UserProfile]:
    """List registered users, optionally filtered by organization.

    Requires a valid bearer token. Non-admins are limited to their own
    organization's roster regardless of what `organization` they pass.
    """
    if not current_user.is_org_admin:
        organization = current_user.organization
    return service.list_users(db, organization=organization)


@router.get("/users/{user_id}", response_model=UserProfile)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
    _current_user: User = Depends(require_self_or_org_admin),
) -> UserProfile:
    """Get a single user's profile + latest trust/risk snapshot."""
    profile = service.get_user(db, user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="User not found")
    return profile


@router.patch("/users/{user_id}", response_model=UserProfile)
def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
    _current_user: User = Depends(require_self_or_org_admin),
) -> UserProfile:
    """Update profile fields (full name, organization, role, device name, email)."""
    profile = service.update_user(db, user_id, payload)
    if profile is None:
        raise HTTPException(status_code=404, detail="User not found")
    return profile
