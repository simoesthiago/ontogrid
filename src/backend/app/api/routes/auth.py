from fastapi import APIRouter, HTTPException, status

from app.core.auth import create_access_token
from app.core.config import settings
from app.schemas.auth import LoginRequest, LoginResponse, UserSummary

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    if payload.email != settings.demo_user_email or payload.password != settings.demo_user_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(
        user_id=settings.demo_user_id,
        tenant_id=settings.demo_tenant_id,
        role=settings.demo_user_role,
    )
    return LoginResponse(
        access_token=token,
        expires_in=settings.token_expiration_seconds,
        user=UserSummary(
            id=settings.demo_user_id,
            tenant_id=settings.demo_tenant_id,
            email=settings.demo_user_email,
            role=settings.demo_user_role,
        ),
    )
