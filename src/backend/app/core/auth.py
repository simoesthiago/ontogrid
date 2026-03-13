from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import get_settings
from app.schemas.auth import RequestContext

bearer_scheme = HTTPBearer(auto_error=False)
DEMO_USER_FALLBACK = "demo-user"


def create_access_token(user_id: str, tenant_id: str, role: str) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.token_expiration_seconds)
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_request_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> RequestContext:
    settings = get_settings()
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    return RequestContext(
        user_id=str(payload["sub"]),
        tenant_id=str(payload["tenant_id"]),
        role=str(payload["role"]),
    )


def get_demo_user_id(
    x_demo_user_id: str | None = Header(default=None, alias="X-Demo-User-Id"),
) -> str:
    candidate = (x_demo_user_id or DEMO_USER_FALLBACK).strip()
    return candidate or DEMO_USER_FALLBACK
