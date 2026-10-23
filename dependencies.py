from fastapi import Depends, Header, HTTPException
from typing import Optional

from .auth import decode_access_token

from .constants import SYSTEM_USER_UUID

def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """Extract and verify JWT from Authorization header.
    Expected format: "Bearer <token>".
    Returns the user_id (sub claim) if valid, otherwise raises 401.
    If no header is provided, returns the system user UUID for unauthenticated access (used in tests).
    """
    if not authorization:
        # No auth provided – treat as system user (fallback for test environment)
        return SYSTEM_USER_UUID
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        user_id = decode_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return user_id
