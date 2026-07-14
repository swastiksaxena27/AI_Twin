"""Authentication service — register and login."""

from sqlalchemy.orm import Session

from behavioral_guardian.backend.schemas.models import (
    AuthResponse,
    AuthUser,
    LoginRequest,
    RegisterRequest,
)
from behavioral_guardian.database import repositories as repo
from behavioral_guardian.utils.security import (
    create_access_token,
    hash_password,
    verify_password,
)


def _to_auth_user(user) -> AuthUser:
    return AuthUser(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        organization=user.organization,
        role=user.role,
        device_name=user.device_name,
        is_org_admin=user.is_org_admin,
    )


class AuthService:
    """Register and authenticate users."""

    def register(self, db: Session, payload: RegisterRequest) -> AuthResponse:

        print("\n========== REGISTER ==========")
        print(f"Username: {payload.username}")

        existing = repo.get_user_by_username_or_email(db, payload.username)

        if existing:
            print(f"Existing User ID: {existing.id}")
            print(f"Password Hash: {existing.password_hash}")

            # User created during enrollment
            if existing.password_hash is None:

                print("Enrollment user found. Updating password...")

                existing.password_hash = hash_password(payload.password)
                existing.email = payload.email
                existing.full_name = payload.full_name
                existing.organization = payload.organization
                existing.role = payload.role
                existing.is_org_admin = payload.is_org_admin

                db.commit()
                db.refresh(existing)

                print("Password successfully saved!")

                token = create_access_token(existing.id)

                return AuthResponse(
                    success=True,
                    message="Account linked successfully.",
                    user=_to_auth_user(existing),
                    access_token=token,
                )

            print("Username already has a password.")

            return AuthResponse(
                success=False,
                message="Username already taken.",
            )

        # Check email duplication
        if payload.email:
            email_user = repo.get_user_by_username_or_email(db, payload.email)

            if email_user:
                return AuthResponse(
                    success=False,
                    message="Email already registered.",
                )

        print("Creating completely new user...")

        user = repo.create_user(
            db=db,
            username=payload.username,
            password_hash=hash_password(payload.password),
            email=payload.email,
            full_name=payload.full_name,
            organization=payload.organization,
            role=payload.role,
            is_org_admin=payload.is_org_admin,
        )

        db.commit()
        db.refresh(user)

        print(f"Created User ID: {user.id}")

        token = create_access_token(user.id)

        return AuthResponse(
            success=True,
            message="Account created.",
            user=_to_auth_user(user),
            access_token=token,
        )

    def login(self, db: Session, payload: LoginRequest) -> AuthResponse:

        print("\n========== LOGIN ==========")

        user = repo.get_user_by_username_or_email(db, payload.identifier)

        if user is None:
            print("User not found")
            return AuthResponse(
                success=False,
                message="Invalid username/email or password.",
            )

        print(f"User ID: {user.id}")
        print(f"Password Hash: {user.password_hash}")

        if not user.password_hash:
            print("No password set")
            return AuthResponse(
                success=False,
                message="Invalid username/email or password.",
            )

        if not verify_password(payload.password, user.password_hash):
            print("Password mismatch")
            return AuthResponse(
                success=False,
                message="Invalid username/email or password.",
            )

        if not user.is_active:
            return AuthResponse(
                success=False,
                message="This account is deactivated.",
            )

        print("Login successful")

        token = create_access_token(user.id)

        return AuthResponse(
            success=True,
            message="Signed in.",
            user=_to_auth_user(user),
            access_token=token,
        )