from fastapi import APIRouter, Depends
from src.schemas.user import AuthSignup, AuthLogin, AuthResponse
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
