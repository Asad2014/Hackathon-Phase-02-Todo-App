import pytest
import sys
import os
from httpx import AsyncClient

# Add the backend directory to the path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Task
import models
import json


@pytest.mark.asyncio
async def test_create_task_success(async_client, mock_jwt_token):
    """Test successfully creating a task."""
    user_id = "test-user-id-123"

    # Create a task
    response = await async_client.post(
        f"/api/{user_id}/tasks",
        json={
            "title": "Test Task",
            "description": "Test Description"
        },
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["user_id"] == user_id
    assert data["completed"] is False


@pytest.mark.asyncio
async def test_create_task_missing_title(async_client, mock_jwt_token):
    """Test creating a task with missing title (should fail validation)."""
    user_id = "test-user-id-123"

    # Try to create a task without title
    response = await async_client.post(
        f"/api/{user_id}/tasks",
        json={
            "description": "Test Description without title"
        },
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_tasks_empty(async_client, mock_jwt_token):
    """Test getting tasks when none exist."""
    user_id = "test-user-id-123"

    response = await async_client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_get_tasks_with_data(async_client, mock_jwt_token):
    """Test getting tasks when they exist."""
    user_id = "test-user-id-123"

    # First create a task
    create_response = await async_client.post(
        f"/api/{user_id}/tasks",
        json={
            "title": "Test Task",
            "description": "Test Description"
        },
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert create_response.status_code == 201

    # Now get the tasks
    response = await async_client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Task"


@pytest.mark.asyncio
async def test_update_task_success(async_client, mock_jwt_token):
    """Test successfully updating a task."""
    user_id = "test-user-id-123"

    # First create a task
    create_response = await async_client.post(
        f"/api/{user_id}/tasks",
        json={
            "title": "Original Title",
            "description": "Original Description"
        },
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert create_response.status_code == 201
    created_task = create_response.json()
    task_id = created_task["id"]

    # Now update the task
    update_response = await async_client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={
            "title": "Updated Title",
            "description": "Updated Description"
        },
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["title"] == "Updated Title"
    assert updated_task["description"] == "Updated Description"


@pytest.mark.asyncio
async def test_update_nonexistent_task(async_client, mock_jwt_token):
    """Test updating a task that doesn't exist."""
    user_id = "test-user-id-123"
    nonexistent_task_id = 999999

    # Try to update a non-existent task
    response = await async_client.put(
        f"/api/{user_id}/tasks/{nonexistent_task_id}",
        json={
            "title": "Updated Title",
            "description": "Updated Description"
        },
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert "Task not found" in data["detail"]


@pytest.mark.asyncio
async def test_delete_task_success(async_client, mock_jwt_token):
    """Test successfully deleting a task."""
    user_id = "test-user-id-123"

    # First create a task
    create_response = await async_client.post(
        f"/api/{user_id}/tasks",
        json={
            "title": "Task to Delete",
            "description": "Will be deleted"
        },
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert create_response.status_code == 201
    created_task = create_response.json()
    task_id = created_task["id"]

    # Now delete the task
    response = await async_client.delete(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert response.status_code == 204  # No content

    # Verify the task is gone
    get_response = await async_client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert get_response.status_code == 200
    data = get_response.json()
    assert len(data) == 0


@pytest.mark.asyncio
async def test_delete_nonexistent_task(async_client, mock_jwt_token):
    """Test deleting a task that doesn't exist."""
    user_id = "test-user-id-123"
    nonexistent_task_id = 999999

    # Try to delete a non-existent task
    response = await async_client.delete(
        f"/api/{user_id}/tasks/{nonexistent_task_id}",
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert "Task not found" in data["detail"]


@pytest.mark.asyncio
async def test_toggle_task_completion(async_client, mock_jwt_token):
    """Test toggling task completion status."""
    user_id = "test-user-id-123"

    # First create a task (default should be not completed)
    create_response = await async_client.post(
        f"/api/{user_id}/tasks",
        json={
            "title": "Toggle Completion Task",
            "description": "Task for testing completion toggle"
        },
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert create_response.status_code == 201
    created_task = create_response.json()
    task_id = created_task["id"]
    assert created_task["completed"] is False  # Default value

    # Toggle the task completion status
    toggle_response = await async_client.patch(
        f"/api/{user_id}/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert toggle_response.status_code == 200
    toggled_task = toggle_response.json()
    assert toggled_task["completed"] is True  # Should now be completed

    # Toggle again to make sure it goes back to False
    toggle_response2 = await async_client.patch(
        f"/api/{user_id}/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert toggle_response2.status_code == 200
    toggled_task2 = toggle_response2.json()
    assert toggled_task2["completed"] is False  # Should now be not completed


@pytest.mark.asyncio
async def test_toggle_nonexistent_task_completion(async_client, mock_jwt_token):
    """Test toggling completion status of a task that doesn't exist."""
    user_id = "test-user-id-123"
    nonexistent_task_id = 999999

    # Try to toggle completion of a non-existent task
    response = await async_client.patch(
        f"/api/{user_id}/tasks/{nonexistent_task_id}/complete",
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert "Task not found" in data["detail"]


@pytest.mark.asyncio
async def test_user_isolation_get_tasks(async_client, mock_jwt_token):
    """Test that users can only access their own tasks."""
    user_id_1 = "test-user-id-1"
    user_id_2 = "test-user-id-2"

    # Create a task for user 1
    create_response_1 = await async_client.post(
        f"/api/{user_id_1}/tasks",
        json={
            "title": "User 1 Task",
            "description": "Task for user 1"
        },
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert create_response_1.status_code == 201

    # Create a task for user 2
    create_response_2 = await async_client.post(
        f"/api/{user_id_2}/tasks",
        json={
            "title": "User 2 Task",
            "description": "Task for user 2"
        },
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert create_response_2.status_code == 201

    # User 1 should only see their own task
    get_response_1 = await async_client.get(
        f"/api/{user_id_1}/tasks",
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert get_response_1.status_code == 200
    user1_tasks = get_response_1.json()
    assert len(user1_tasks) == 1
    assert user1_tasks[0]["title"] == "User 1 Task"

    # User 2 should only see their own task
    get_response_2 = await async_client.get(
        f"/api/{user_id_2}/tasks",
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert get_response_2.status_code == 200
    user2_tasks = get_response_2.json()
    assert len(user2_tasks) == 1
    assert user2_tasks[0]["title"] == "User 2 Task"


@pytest.mark.asyncio
async def test_user_isolation_access_other_users_task(async_client, mock_jwt_token):
    """Test that users cannot access other users' tasks."""
    user_id_1 = "test-user-id-1"
    user_id_2 = "test-user-id-2"

    # Create a task for user 1
    create_response = await async_client.post(
        f"/api/{user_id_1}/tasks",
        json={
            "title": "User 1 Task",
            "description": "Task for user 1"
        },
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    assert create_response.status_code == 201
    created_task = create_response.json()
    task_id = created_task["id"]

    # User 2 should not be able to access user 1's task
    # Try to get user 1's task with user 2's ID
    get_response = await async_client.get(
        f"/api/{user_id_2}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {mock_jwt_token}"}
    )

    # This should fail with 403 Forbidden since the user_id in the path doesn't match the token
    assert get_response.status_code == 403