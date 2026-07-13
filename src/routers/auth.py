from fastapi import APIRouter, HTTPException, status
from src.schemas.user import AuthSignup, AuthLogin, AuthResponse
from src.core.config import settings
import httpx

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=AuthResponse)
async def signup(auth_in: AuthSignup):
    """
    Register a new user directly against the connected Supabase Auth service.
    """
    if not settings.SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="SUPABASE_ANON_KEY not configured")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.SUPABASE_URL}/auth/v1/signup",
            headers={
                "apikey": settings.SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            },
            json={
                "email": auth_in.email,
                "password": auth_in.password
            }
        )

        if response.status_code != 200:
            error_data = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=error_data.get("msg", "Signup failed")
            )
            
        data = response.json()
        
        return AuthResponse(
            access_token=data.get("access_token", ""),
            refresh_token=data.get("refresh_token", ""),
            user_id=data.get("user", {}).get("id")
        )

@router.post("/login", response_model=AuthResponse)
async def login(auth_in: AuthLogin):
    """
    Authenticate a user directly against the connected Supabase Auth service.
    """
    if not settings.SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="SUPABASE_ANON_KEY not configured")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={
                "apikey": settings.SUPABASE_ANON_KEY,
                "Content-Type": "application/json"
            },
            json={
                "email": auth_in.email,
                "password": auth_in.password
            }
        )

        if response.status_code != 200:
            error_data = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=error_data.get("error_description", "Login failed")
            )
            
        data = response.json()
        
        return AuthResponse(
            access_token=data.get("access_token", ""),
            refresh_token=data.get("refresh_token", ""),
            user_id=data.get("user", {}).get("id")
        )
