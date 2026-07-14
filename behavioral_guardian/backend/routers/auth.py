"""Auth API router — register / login / device-token exchange."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from behavioral_guardian.backend.dependencies import get_auth_service, get_current_user, get_db
from behavioral_guardian.backend.schemas.models import AuthResponse, DeviceTokenResponse, LoginRequest, RegisterRequest
from behavioral_guardian.backend.services.auth_service import AuthService
from behavioral_guardian.database.models import User
from behavioral_guardian.utils.security import create_device_token

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=AuthResponse)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """Create a new account."""
    return service.register(db, payload)


@router.post("/auth/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """Authenticate with a username/email + password."""
    return service.login(db, payload)


@router.post("/auth/device-token", response_model=DeviceTokenResponse)
def issue_device_token(current_user: User = Depends(get_current_user)) -> DeviceTokenResponse:
    """Exchange a normal (24h) login token for a long-lived (30 day) device
    token, meant to be cached locally by the background agent so it never
    has to ask for a password again until this expires.

    Call this once, right after logging in, with the login token in the
    Authorization header — the agent's one-time setup step does exactly
    this automatically.
    """
    token = create_device_token(current_user.id)
    return DeviceTokenResponse(access_token=token, user_id=current_user.id)
