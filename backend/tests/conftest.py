import pytest
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from fastapi.testclient import TestClient
from httpx import AsyncClient
import asyncio
from unittest.mock import patch
from datetime import datetime, timedelta

# Add the backend directory to the path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
import models
from db import engine, get_session


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    """Create a test database session."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

        async with AsyncSession(bind=conn) as session:
            yield session

        await conn.rollback()


@pytest.fixture(scope="function")
async def async_client(db_session):
    """Create an async test client."""
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def mock_jwt_token():
    """Create a mock JWT token for testing."""
    import jwt
    from ..config import settings

    # Create a simple payload with user_id
    payload = {
        "userId": "test-user-id-123",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "aud": "better-auth"
    }

    token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm="HS256")
    return token