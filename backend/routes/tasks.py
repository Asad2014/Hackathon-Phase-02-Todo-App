# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlmodel import select
# from typing import List
# from uuid import UUID
# from models import Task, User
# from schemas import TaskCreate, TaskUpdate, TaskResponse
# from dependencies import get_db_session, CurrentUser
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import delete, update
# from datetime import datetime
# import re

# router = APIRouter()


# @router.get("/tasks", response_model=List[TaskResponse])
# async def get_tasks(
#     user_id: str,
#     current_user: str = Depends(CurrentUser),
#     session: AsyncSession = Depends(get_db_session)
# ):
#     """
#     Get all tasks for a specific user
#     """
#     # Verify that the requesting user is the same as the user_id in the path
#     if current_user != user_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to access these tasks"
#         )

#     # Validate user_id format
#     try:
#         UUID(user_id)
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid user ID format"
#         )

#     # Query tasks for the specific user
#     statement = select(Task).where(Task.user_id == user_id)
#     result = await session.execute(statement)
#     tasks = result.scalars().all()

#     return tasks


# @router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
# async def create_task(
#     user_id: str,
#     task_data: TaskCreate,
#     current_user: str = Depends(CurrentUser),
#     session: AsyncSession = Depends(get_db_session)
# ):
#     """
#     Create a new task for a user
#     """
#     # Verify that the requesting user is the same as the user_id in the path
#     if current_user != user_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to create tasks for this user"
#         )

#     # Validate user_id format
#     try:
#         UUID(user_id)
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid user ID format"
#         )

#     # Validate task title length
#     if not task_data.title or len(task_data.title.strip()) == 0:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Task title cannot be empty"
#         )

#     if len(task_data.title) > 255:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Task title cannot exceed 255 characters"
#         )

#     # Validate description length if provided
#     if task_data.description and len(task_data.description) > 1000:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Task description cannot exceed 1000 characters"
#         )

#     # Create new task instance
#     task = Task(
#         title=task_data.title.strip(),
#         description=task_data.description.strip() if task_data.description else None,
#         user_id=user_id
#     )

#     # Add to session and commit
#     session.add(task)
#     await session.commit()
#     await session.refresh(task)

#     return task


# @router.put("/tasks/{id}", response_model=TaskResponse)
# async def update_task(
#     user_id: str,
#     id: int,
#     task_data: TaskUpdate,
#     current_user: str = Depends(CurrentUser),
#     session: AsyncSession = Depends(get_db_session)
# ):
#     """
#     Update details of a specific task
#     """
#     # Verify that the requesting user is the same as the user_id in the path
#     if current_user != user_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to update this task"
#         )

#     # Validate user_id format
#     try:
#         UUID(user_id)
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid user ID format"
#         )

#     # Validate task ID
#     if id <= 0:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid task ID"
#         )

#     # Validate task data if provided
#     if task_data.title is not None:
#         if len(task_data.title.strip()) == 0:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Task title cannot be empty"
#             )

#         if len(task_data.title) > 255:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Task title cannot exceed 255 characters"
#             )

#     # Validate description length if provided
#     if task_data.description is not None and len(task_data.description) > 1000:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Task description cannot exceed 1000 characters"
#         )

#     # Get the task from database
#     statement = select(Task).where(Task.id == id).where(Task.user_id == user_id)
#     result = await session.execute(statement)
#     task = result.scalar_one_or_none()

#     if not task:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Task not found"
#         )

#     # Update task fields if provided
#     for field, value in task_data.model_dump(exclude_unset=True).items():
#         if field == "title" and value is not None:
#             setattr(task, field, value.strip())
#         elif field == "description" and value is not None:
#             setattr(task, field, value.strip() if value else None)
#         else:
#             setattr(task, field, value)

#     # Update timestamp
#     task.updated_at = datetime.utcnow()

#     # Commit changes
#     await session.commit()
#     await session.refresh(task)

#     return task


# @router.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_task(
#     user_id: str,
#     id: int,
#     current_user: str = Depends(CurrentUser),
#     session: AsyncSession = Depends(get_db_session)
# ):
#     """
#     Delete a specific task
#     """
#     # Verify that the requesting user is the same as the user_id in the path
#     if current_user != user_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to delete this task"
#         )

#     # Validate user_id format
#     try:
#         UUID(user_id)
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid user ID format"
#         )

#     # Validate task ID
#     if id <= 0:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid task ID"
#         )

#     # Get the task from database
#     statement = select(Task).where(Task.id == id).where(Task.user_id == user_id)
#     result = await session.execute(statement)
#     task = result.scalar_one_or_none()

#     if not task:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Task not found"
#         )

#     # Delete the task
#     await session.delete(task)
#     await session.commit()

#     return


# @router.patch("/tasks/{id}/complete", response_model=TaskResponse)
# async def toggle_task_completion(
#     user_id: str,
#     id: int,
#     current_user: str = Depends(CurrentUser),
#     session: AsyncSession = Depends(get_db_session)
# ):
#     """
#     Toggle the completion status of a specific task
#     """
#     # Verify that the requesting user is the same as the user_id in the path
#     if current_user != user_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to update this task"
#         )

#     # Validate user_id format
#     try:
#         UUID(user_id)
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid user ID format"
#         )

#     # Validate task ID
#     if id <= 0:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid task ID"
#         )

#     # Get the task from database
#     statement = select(Task).where(Task.id == id).where(Task.user_id == user_id)
#     result = await session.execute(statement)
#     task = result.scalar_one_or_none()

#     if not task:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Task not found"
#         )

#     # Toggle the completed status
#     task.completed = not task.completed
#     task.updated_at = datetime.utcnow()

#     # Commit changes
#     await session.commit()
#     await session.refresh(task)

#     return task







from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from typing import List
from uuid import UUID
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskResponse
from dependencies import get_db_session, CurrentUser
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

router = APIRouter()

# Helper function to validate user_id (only allow real UUIDs)
def validate_user_id(user_id: str):
    try:
        UUID(user_id)
        return True
    except ValueError:
        return False

# Helper function to check if user is authorized
def check_user_authorization(path_user_id: str, current_user: str):
    """
    Check if the authenticated user is authorized to access the specified user_id
    Only allow access to the authenticated user's own tasks
    """
    return current_user == path_user_id

# ======================================================
# GET all tasks
# ======================================================
@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    user_id: str,
    current_user: str = Depends(CurrentUser),
    session: AsyncSession = Depends(get_db_session)
):
    if not check_user_authorization(user_id, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to access these tasks")

    if not validate_user_id(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid user ID format")

    statement = select(Task).where(Task.user_id == user_id)
    result = await session.execute(statement)
    tasks = result.scalars().all()
    return tasks

# ======================================================
# CREATE a task
# ======================================================
@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: str = Depends(CurrentUser),
    session: AsyncSession = Depends(get_db_session)
):
    if not check_user_authorization(user_id, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to create tasks for this user")

    if not validate_user_id(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid user ID format")

    if not task_data.title.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Task title cannot be empty")

    task = Task(
        title=task_data.title.strip(),
        description=(task_data.description.strip() if task_data.description else None),
        user_id=user_id
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

# ======================================================
# UPDATE a task
# ======================================================
@router.put("/tasks/{id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    id: int,
    task_data: TaskUpdate,
    current_user: str = Depends(CurrentUser),
    session: AsyncSession = Depends(get_db_session)
):
    if not check_user_authorization(user_id, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to update this task")

    if not validate_user_id(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid user ID format")

    statement = select(Task).where(Task.id == id).where(Task.user_id == user_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Update only provided fields
    for field, value in task_data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(task, field, value.strip() if isinstance(value, str) else value)

    task.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(task)
    return task

# ======================================================
# DELETE a task
# ======================================================
@router.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    id: int,
    current_user: str = Depends(CurrentUser),
    session: AsyncSession = Depends(get_db_session)
):
    if not check_user_authorization(user_id, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to delete this task")

    if not validate_user_id(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid user ID format")

    statement = select(Task).where(Task.id == id).where(Task.user_id == user_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    await session.delete(task)
    await session.commit()
    return

# ======================================================
# TOGGLE completion
# ======================================================
@router.patch("/tasks/{id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    id: int,
    current_user: str = Depends(CurrentUser),
    session: AsyncSession = Depends(get_db_session)
):
    if not check_user_authorization(user_id, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to update this task")

    if not validate_user_id(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid user ID format")

    statement = select(Task).where(Task.id == id).where(Task.user_id == user_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)
    return task
