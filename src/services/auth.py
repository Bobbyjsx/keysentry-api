import httpx
from fastapi import HTTPException

from src.core.config import settings
from src.schemas.user import AuthLogin, AuthResponse, AuthSignup


class AuthService:
    def __init__(self):
        if not settings.SUPABASE_ANON_KEY:
            raise HTTPException(
                status_code=500, detail="SUPABASE_ANON_KEY not configured"
            )

        self.headers = {
            "apikey": settings.SUPABASE_ANON_KEY,
            "Content-Type": "application/json",
        }
        self.admin_headers = {
            "apikey": settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
        }
        self.base_url = settings.SUPABASE_URL

    async def signup(self, auth_in: AuthSignup) -> AuthResponse:
        # Use the admin API to create the user and bypass email confirmation
        if not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise HTTPException(
                status_code=500,
                detail="SUPABASE_SERVICE_ROLE_KEY not configured for admin signup",
            )

        async with httpx.AsyncClient() as client:
            # Create user via Admin API
            admin_response = await client.post(
                f"{self.base_url}/auth/v1/admin/users",
                headers=self.admin_headers,
                json={
                    "email": auth_in.email,
                    "password": auth_in.password,
                    "email_confirm": True,
                    "user_metadata": {"full_name": auth_in.full_name},
                },
            )

            if admin_response.status_code != 200:
                try:
                    error_data = admin_response.json()
                    detail = error_data.get("msg", error_data.get("message", error_data.get("error_description", "Signup failed")))
                except Exception:
                    detail = admin_response.text or "Signup failed"
                raise HTTPException(
                    status_code=admin_response.status_code,
                    detail=detail,
                )
            
            user_data = admin_response.json()
            user_id_str = user_data.get("id")
            
            if user_id_str:
                from src.core.events import event_bus
                await event_bus.publish("USER_SIGNED_UP", user_id_str=user_id_str, email=auth_in.email, full_name=auth_in.full_name)

            # Automatically login to get the token since Admin API doesn't return a session
            return await self.login(
                AuthLogin(email=auth_in.email, password=auth_in.password)
            )

    async def login(self, auth_in: AuthLogin) -> AuthResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/v1/token?grant_type=password",
                headers=self.headers,
                json={"email": auth_in.email, "password": auth_in.password},
            )

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    detail = error_data.get("error_description", error_data.get("message", error_data.get("msg", "Login failed")))
                except Exception:
                    detail = response.text or "Login failed"
                raise HTTPException(
                    status_code=response.status_code,
                    detail=detail,
                )

            data = response.json()
            return AuthResponse(
                access_token=data.get("access_token", ""),
                refresh_token=data.get("refresh_token", ""),
                user_id=data.get("user", {}).get("id"),
            )
