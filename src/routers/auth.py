from fastapi import APIRouter, HTTPException
from src.schemas.user import AuthSignup, AuthLogin, AuthResponse
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=AuthResponse)
async def signup(auth_in: AuthSignup):
    """
    Register a new user. 
    Note: In production, this would integrate with Supabase Auth or proxy the request.
    """
    # Mock response
    return AuthResponse(
        access_token="mock_access_token",
        refresh_token="mock_refresh_token",
        user_id=uuid.uuid4()
    )

@router.post("/login", response_model=AuthResponse)
async def login(auth_in: AuthLogin):
    """
    Authenticate a user.
    Note: In production, this would integrate with Supabase Auth or proxy the request.
    """
    # Mock response
    return AuthResponse(
        access_token="mock_access_token",
        refresh_token="mock_refresh_token",
        user_id=uuid.uuid4()
    )
