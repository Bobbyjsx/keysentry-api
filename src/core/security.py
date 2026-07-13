import jwt
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.core.config import settings

# HTTPBearer automatically looks for the Authorization header
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UUID:
    """
    Validates the Supabase JWT access token and extracts the user ID.
    Returns the user's UUID.
    Raises 401 Unauthorized if the token is missing, invalid, or expired.
    """
    token = credentials.credentials

    if not settings.SUPABASE_JWT_SECRET:
        raise HTTPException(status_code=500, detail="SUPABASE_JWT_SECRET is not configured")

    try:
        # Supabase uses HS256 algorithm and signs with the JWT secret
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}  # audience check is often unnecessary unless specified
        )
        
        # The 'sub' claim contains the user ID
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Invalid authentication token payload")
            
        return UUID(user_id_str)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")
