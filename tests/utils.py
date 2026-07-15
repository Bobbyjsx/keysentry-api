import jwt
from datetime import datetime, timedelta


def create_test_token(user_id: str, secret="testsecret") -> str:
    payload = {"sub": user_id, "exp": datetime.utcnow() + timedelta(days=1)}
    return jwt.encode(payload, secret, algorithm="HS256")
