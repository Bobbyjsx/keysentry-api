from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.config import settings

# HTTPBearer automatically looks for the Authorization header
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    """
    Validates the Supabase JWT access token and extracts the user ID.
    Returns the user's UUID.
    Raises 401 Unauthorized if the token is missing, invalid, or expired.
    """
    token = credentials.credentials

    try:
        if not settings.GOTRUE_JWT_SECRET:
            raise HTTPException(
                status_code=500,
                detail="GOTRUE_JWT_SECRET is not configured for validation",
            )

        payload = jwt.decode(
            token,
            settings.GOTRUE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )

        # The 'sub' claim contains the user ID
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=401, detail="Invalid authentication token payload"
            )

        return UUID(user_id_str)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")
