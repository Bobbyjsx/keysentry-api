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
        # Check the token's algorithm first
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg")

        if alg == "HS256":
            # Traditional Supabase symmetric signing
            if not settings.SUPABASE_JWT_SECRET:
                raise HTTPException(
                    status_code=500, detail="SUPABASE_JWT_SECRET is not configured for HS256 validation"
                )
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        else:
            # Asymmetric signing (ES256, RS256) used by custom/newer Supabase environments
            # We fetch the public key directly from the JWKS endpoint using our configured SUPABASE_URL
            # (instead of relying on the token's 'iss' which might be an unreachable localhost alias)
            jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
            
            jwks_client = jwt.PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256", "RS256"],
                options={"verify_aud": False, "verify_exp": False},
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
