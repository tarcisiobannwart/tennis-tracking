"""
Simple test authentication for development
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from jose import jwt
from pydantic import BaseModel

router = APIRouter()

# Test credentials
TEST_USER = {
    "email": "test@tennis.com",
    "password": "test123",
    "name": "Test User"
}

SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def test_login(request: LoginRequest):
    """Simple test login - accepts test@tennis.com / test123"""

    if request.email == TEST_USER["email"] and request.password == TEST_USER["password"]:
        # Create token
        payload = {
            "sub": request.email,
            "name": TEST_USER["name"],
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return TokenResponse(access_token=token)

    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/test-token")
async def get_test_token():
    """Get a test token directly for development"""
    payload = {
        "sub": TEST_USER["email"],
        "name": TEST_USER["name"],
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "message": "Use this token for testing",
        "token": token,
        "usage": f"Authorization: Bearer {token}"
    }