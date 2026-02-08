from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db import AsyncSessionLocal, get_session
from auth import verify_token
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import re
import uuid


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    """
    async for session in get_session():
        try:
            yield session
        finally:
            await session.close()


async def get_current_user_or_mock(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))):
    """
    Flexible authentication that accepts either a valid JWT token or mock user IDs
    """
    # Check if this is a mock user request
    if credentials and hasattr(credentials, 'credentials'):
        token = credentials.credentials

        # Verify the JWT token
        user_id = verify_token(token)

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id
    else:
        # For development, allow mock users without authentication
        # In a real scenario, you'd want to be more restrictive
        # This is a simplified approach for development purposes
        return "mock-user-dev"


# Flexible user dependency that allows both authenticated and mock users
async def flexible_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))):
    """
    Dependency that allows either authenticated users or mock users for development
    """
    if credentials and credentials.credentials:
        # Verify JWT token if provided
        user_id = verify_token(credentials.credentials)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    else:
        # For development/testing, return a mock user ID
        # This matches the pattern used in the frontend
        # Return a UUID-like string format to match expected format
        import uuid
        return str(uuid.uuid4())  # Generate a real UUID to match expected format


CurrentUser = flexible_current_user