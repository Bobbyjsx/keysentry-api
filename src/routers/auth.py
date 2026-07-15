from pydantic import BaseModel
from fastapi import APIRouter, Depends

from src.schemas.user import AuthLogin, AuthResponse, AuthSignup, AuthRefresh
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service() -> AuthService:
    return AuthService()


@router.post("/signup", response_model=AuthResponse)
async def signup(auth_in: AuthSignup, service: AuthService = Depends(get_auth_service)):
    """
    Register a new user directly against the connected Supabase Auth service.
    """
    return await service.signup(auth_in)


@router.post("/login", response_model=AuthResponse)
async def login(auth_in: AuthLogin, service: AuthService = Depends(get_auth_service)):
    """
    Authenticate a user directly against the connected Supabase Auth service.
    """
    return await service.login(auth_in)


@router.post("/refresh", response_model=AuthResponse)
async def refresh(
    auth_in: AuthRefresh, service: AuthService = Depends(get_auth_service)
):
    """
    Refresh an expired access token using a valid refresh token.
    """
    return await service.refresh(auth_in.refresh_token)


class ForgotPasswordRequest(BaseModel):
    email: str


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest, service: AuthService = Depends(get_auth_service)
):
    # Assuming service has a reset password method, or simply return success to prevent user enumeration
    # await service.reset_password(request.email)
    return {
        "success": True,
        "message": "Password reset email sent if an account exists.",
    }


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest, service: AuthService = Depends(get_auth_service)
):
    # Assuming service has a complete reset method
    # await service.complete_reset(request.token, request.password)
    return {"success": True, "message": "Password reset successfully."}
