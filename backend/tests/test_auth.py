import pytest
import sys
import os
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException

# Add the backend directory to the path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import verify_token, get_current_user
from config import settings


@pytest.mark.asyncio
async def test_verify_valid_token():
    """Test verifying a valid JWT token."""
    # Create a valid token
    payload = {
        "userId": "test-user-id-123",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "aud": "better-auth"
    }

    token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm="HS256")

    # Verify the token
    user_id = verify_token(token)

    assert user_id == "test-user-id-123"


@pytest.mark.asyncio
async def test_verify_expired_token():
    """Test verifying an expired JWT token."""
    # Create an expired token
    payload = {
        "userId": "test-user-id-123",
        "exp": datetime.utcnow() - timedelta(hours=1),  # Already expired
        "iat": datetime.utcnow() - timedelta(hours=2),
        "aud": "better-auth"
    }

    token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm="HS256")

    # Verify the token (should return None for expired token)
    user_id = verify_token(token)

    assert user_id is None


@pytest.mark.asyncio
async def test_verify_invalid_token():
    """Test verifying an invalid JWT token."""
    # Use an invalid token (not properly encoded)
    invalid_token = "invalid.token.string"

    # Verify the token (should return None for invalid token)
    user_id = verify_token(invalid_token)

    assert user_id is None


@pytest.mark.asyncio
async def test_verify_token_without_user_id():
    """Test verifying a token without userId claim."""
    # Create a token without userId
    payload = {
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "aud": "better-auth"
    }

    token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm="HS256")

    # Verify the token (should return None for missing userId)
    user_id = verify_token(token)

    assert user_id is None


@pytest.mark.asyncio
async def test_verify_token_with_wrong_secret():
    """Test verifying a token with wrong secret."""
    # Create a token with a different secret
    wrong_secret = "wrong-secret-key-different-from-config"
    payload = {
        "userId": "test-user-id-123",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "aud": "better-auth"
    }

    token = jwt.encode(payload, wrong_secret, algorithm="HS256")

    # Verify the token (should return None for wrong secret)
    user_id = verify_token(token)

    assert user_id is None