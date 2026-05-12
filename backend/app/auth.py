from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import AdminUser

security = HTTPBearer(auto_error=True)


def hash_password(password: str, salt: str | None = None) -> str:
    salt_value = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_value.encode("utf-8"),
        390000,
    )
    return f"{salt_value}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_value, digest = stored_hash.split("$", maxsplit=1)
    except ValueError:
        return False
    expected_hash = hash_password(password, salt=salt_value)
    return hmac.compare_digest(expected_hash, f"{salt_value}${digest}")


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}".encode("utf-8"))


def create_access_token(username: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.token_expire_hours)
    payload = {
        "sub": username,
        "exp": int(expires_at.timestamp()),
    }
    payload_segment = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        payload_segment.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    signature_segment = _b64encode(signature)
    return f"{payload_segment}.{signature_segment}"


def decode_access_token(token: str) -> str:
    try:
        payload_segment, signature_segment = token.split(".", maxsplit=1)
        expected_signature = hmac.new(
            settings.secret_key.encode("utf-8"),
            payload_segment.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(_b64encode(expected_signature), signature_segment):
            raise ValueError("Invalid token signature.")
        payload = json.loads(_b64decode(payload_segment))
        if datetime.now(timezone.utc).timestamp() > payload["exp"]:
            raise ValueError("Token expired.")
        return payload["sub"]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Сессия истекла. Войдите заново.",
        ) from exc


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> AdminUser:
    username = decode_access_token(credentials.credentials)
    admin = db.scalar(select(AdminUser).where(AdminUser.username == username))
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Администратор не найден.",
        )
    return admin

