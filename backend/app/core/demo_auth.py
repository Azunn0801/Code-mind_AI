"""Short-lived, signed demo access tokens for the MVP.

This is deliberately not a replacement for production OAuth.  It prevents a
demo link or a copied local token from being valid forever while keeping the
judge-facing demo self-contained and free of passwords.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta


class DemoTokenError(ValueError):
    """Raised when a token is malformed or its signature cannot be trusted."""


class DemoTokenExpired(DemoTokenError):
    """Raised when a correctly signed demo token has expired."""


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def issue_demo_token(
    user_id: str,
    secret: str,
    ttl_seconds: int,
    *,
    now: datetime | None = None,
) -> str:
    issued_at = now or datetime.now(UTC)
    payload = {
        "sub": user_id,
        "exp": int((issued_at + timedelta(seconds=ttl_seconds)).timestamp()),
    }
    encoded_payload = _encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"demo.{encoded_payload}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"demo.{encoded_payload}.{_encode(signature)}"


def verify_demo_token(token: str, secret: str, *, now: datetime | None = None) -> str:
    try:
        prefix, encoded_payload, encoded_signature = token.split(".")
        if prefix != "demo":
            raise DemoTokenError("unsupported token type")
        signing_input = f"demo.{encoded_payload}".encode("ascii")
        expected_signature = hmac.new(
            secret.encode("utf-8"), signing_input, hashlib.sha256
        ).digest()
        if not hmac.compare_digest(_decode(encoded_signature), expected_signature):
            raise DemoTokenError("invalid token signature")
        payload = json.loads(_decode(encoded_payload))
        subject = payload.get("sub")
        expiry = payload.get("exp")
        if not isinstance(subject, str) or not subject or not isinstance(expiry, int):
            raise DemoTokenError("invalid token payload")
    except (UnicodeDecodeError, ValueError, TypeError, json.JSONDecodeError) as exc:
        if isinstance(exc, DemoTokenError):
            raise
        raise DemoTokenError("malformed token") from exc

    current_time = now or datetime.now(UTC)
    if expiry <= int(current_time.timestamp()):
        raise DemoTokenExpired("token expired")
    return subject
