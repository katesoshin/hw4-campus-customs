"""Password hashing (pbkdf2_sha256) and signed session tokens.

New hashes use a self-describing 4-part format:
    pbkdf2_sha256$<iterations>$<salt>$<hex>
The seeded users use a legacy 3-part format without an iteration count:
    pbkdf2_sha256$<salt>$<hex>
Legacy hashes are verified using config.LEGACY_PBKDF2_ITERATIONS.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time

from config import (
    LEGACY_PBKDF2_ITERATIONS,
    PBKDF2_ITERATIONS,
    SECRET_KEY,
    TOKEN_TTL_HOURS,
)

ALGO = "pbkdf2_sha256"


def _pbkdf2(password: str, salt: str, iterations: int) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations).hex()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = _pbkdf2(password, salt, PBKDF2_ITERATIONS)
    return f"{ALGO}${PBKDF2_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    """Constant-time check of a password against a stored hash (new or legacy format)."""
    parts = stored.split("$")
    try:
        if len(parts) == 4:  # pbkdf2_sha256$iterations$salt$hex
            _, iters, salt, digest = parts
            iterations = int(iters)
        elif len(parts) == 3:  # legacy: pbkdf2_sha256$salt$hex
            _, salt, digest = parts
            iterations = LEGACY_PBKDF2_ITERATIONS
        else:
            return False
    except (ValueError, IndexError):
        return False
    candidate = _pbkdf2(password, salt, iterations)
    return hmac.compare_digest(candidate, digest)


# ---- Signed tokens (stateless, HMAC-signed; no external JWT dependency) ----
def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _unb64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def create_token(user_id: int) -> str:
    payload = {"uid": user_id, "exp": int(time.time()) + TOKEN_TTL_HOURS * 3600}
    body = _b64(json.dumps(payload, separators=(",", ":")).encode())
    sig = _b64(hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest())
    return f"{body}.{sig}"


def verify_token(token: str) -> int | None:
    """Return the user id for a valid, unexpired token, else None."""
    try:
        body, sig = token.split(".")
    except ValueError:
        return None
    expected = _b64(hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(sig, expected):
        return None
    try:
        payload = json.loads(_unb64(body))
    except (ValueError, json.JSONDecodeError):
        return None
    if payload.get("exp", 0) < int(time.time()):
        return None
    return payload.get("uid")
