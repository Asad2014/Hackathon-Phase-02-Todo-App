import pytest
import sys
import os
from datetime import datetime

# Add the backend directory to the path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models


@pytest.mark.asyncio
async def test_user_creation():
    """Test creating a user model."""
    user = models.User(
        id="test-user-id-123",
        email="test@example.com",
        name="Test User"
    )

    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.id == "test-user-id-123"
    assert isinstance(user.created_at, datetime)


@pytest.mark.asyncio
async def test_task_creation():
    """Test creating a task model."""
    task = models.Task(
        title="Test Task",
        description="Test Description",
        user_id="test-user-id-123"
    )

    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.user_id == "test-user-id-123"
    assert task.completed is False  # Default value
    assert isinstance(task.created_at, datetime)


@pytest.mark.asyncio
async def test_task_without_description():
    """Test creating a task without description."""
    task = models.Task(
        title="Test Task",
        user_id="test-user-id-123"
    )

    assert task.title == "Test Task"
    assert task.description is None
    assert task.user_id == "test-user-id-123"


@pytest.mark.asyncio
async def test_task_completion_toggle():
    """Test toggling task completion."""
    task = models.Task(
        title="Test Task",
        user_id="test-user-id-123"
    )

    assert task.completed is False

    task.completed = True
    assert task.completed is True

    task.completed = False
    assert task.completed is False