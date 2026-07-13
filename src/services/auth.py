from fastapi import HTTPException
import httpx
from src.core.config import settings
from src.schemas.user import AuthSignup, AuthLogin, AuthResponse

class AuthService:
    def __init__(self):
        if not settings.SUPABASE_ANON_KEY:
            raise HTTPException(status_code=500, detail="SUPABASE_ANON_KEY not configured")
        
        self.headers = {
            "apikey": settings.SUPABASE_ANON_KEY,
            "Content-Type": "application/json"
        }
        self.base_url = settings.SUPABASE_URL

    async def signup(self, auth_in: AuthSignup) -> AuthResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/v1/signup",
                headers=self.headers,
                json={"email": auth_in.email, "password": auth_in.password}
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

    async def login(self, auth_in: AuthLogin) -> AuthResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/v1/token?grant_type=password",
                headers=self.headers,
                json={"email": auth_in.email, "password": auth_in.password}
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
