"""Password hashing (stdlib PBKDF2-HMAC-SHA256) and JWT session tokens (PyJWT)."""

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from behavioral_guardian.config.settings import (
    JWT_ALGORITHM,
    JWT_DEVICE_TOKEN_EXPIRE_DAYS,
    JWT_EXPIRE_HOURS,
    JWT_SECRET_KEY,
)

_ITERATIONS = 200_000


def hash_password(plain: str) -> str:
    """Return 'salt$hash' hex string."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt, _ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(plain: str, stored: str) -> bool:
    """Constant-time compare against a 'salt$hash' string."""
    try:
        salt_hex, digest_hex = stored.split("$", 1)
    except (ValueError, AttributeError):
        return False
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(digest_hex)
    actual = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt, _ITERATIONS)
    return hmac.compare_digest(actual, expected)


# ── JWT session tokens ───────────────────────────────────────────────
# Ported over from the guardian-v2 backend: every authenticated request now
# carries a bearer token instead of a bare user_id, so routes can verify the
# caller actually owns the account (or is an org admin) they're asking about.

def create_access_token(user_id: int) -> str:
    """Issue a signed JWT for `user_id`, valid for JWT_EXPIRE_HOURS."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_device_token(user_id: int) -> str:
    """Issue a long-lived JWT for a background device/agent, valid for
    JWT_DEVICE_TOKEN_EXPIRE_DAYS. Same shape as an access token — just a
    longer expiry — so `decode_access_token` can read either one."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(days=JWT_DEVICE_TOKEN_EXPIRE_DAYS),
        "device": True,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[int]:
    """Return the user_id embedded in `token`, or None if invalid/expired."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        return None
