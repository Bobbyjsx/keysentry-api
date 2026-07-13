from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.user import AuthLogin, AuthResponse, AuthSignup
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


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
