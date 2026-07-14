import httpx
from fastapi import HTTPException
import jwt
from datetime import datetime, timezone, timedelta

from src.core.config import settings
from src.core.events import EventType
from src.schemas.user import AuthLogin, AuthResponse, AuthSignup


class AuthService:
    def __init__(self):
        if not settings.GOTRUE_URL:
            raise HTTPException(
                status_code=500, detail="GOTRUE_URL not configured"
            )
        self.base_url = settings.GOTRUE_URL.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
        }

    async def signup(self, auth_in: AuthSignup) -> AuthResponse:
        # Use the standard public signup API since GOTRUE_MAILER_AUTOCONFIRM is true
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/signup",
                headers=self.headers,
                json={
                    "email": auth_in.email,
                    "password": auth_in.password,
                    "data": {"full_name": auth_in.full_name},
                },
            )

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    detail = error_data.get(
                        "msg",
                        error_data.get(
                            "message",
                            error_data.get("error_description", "Signup failed"),
                        ),
                    )
                except Exception:
                    detail = response.text or "Signup failed"
                raise HTTPException(
                    status_code=response.status_code,
                    detail=detail,
                )

            data = response.json()
            user_id_str = data.get("user", {}).get("id") or data.get("id")

            if user_id_str:
                from src.core.events import event_bus

                await event_bus.publish(
                    EventType.USER_SIGNED_UP,
                    user_id_str=user_id_str,
                    email=auth_in.email,
                    full_name=auth_in.full_name,
                )

            # GoTrue /signup returns a session (access_token, refresh_token) if autoconfirm is true
            return AuthResponse(
                access_token=data.get("access_token", ""),
                refresh_token=data.get("refresh_token", ""),
                user_id=user_id_str,
            )

    async def login(self, auth_in: AuthLogin) -> AuthResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/token?grant_type=password",
                headers=self.headers,
                json={"email": auth_in.email, "password": auth_in.password},
            )

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    detail = error_data.get(
                        "error_description",
                        error_data.get(
                            "message", error_data.get("msg", "Login failed")
                        ),
                    )
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

    async def refresh(self, refresh_token: str) -> AuthResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/token?grant_type=refresh_token",
                headers=self.headers,
                json={"refresh_token": refresh_token},
            )

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    detail = error_data.get(
                        "error_description",
                        error_data.get(
                            "message", error_data.get("msg", "Token refresh failed")
                        ),
                    )
                except Exception:
                    detail = response.text or "Token refresh failed"
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
