from dataclasses import dataclass
from agents import function_tool, RunContextWrapper
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Task
from datetime import datetime
from typing import Optional


@dataclass
class AgentContext:
    user_id: str
    db_session: AsyncSession


@function_tool
async def add_task(
    ctx: RunContextWrapper[AgentContext],
    title: str,
    description: str = "",
) -> str:
    """Add a new task for the user. Use this when the user wants to create a new todo item."""
    session = ctx.context.db_session
    user_id = ctx.context.user_id

    task = Task(
        title=title.strip(),
        description=description.strip() if description else None,
        user_id=user_id,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return f"Task created successfully: '{task.title}' (ID: {task.id})"


@function_tool
async def list_tasks(
    ctx: RunContextWrapper[AgentContext],
    status: str = "all",
) -> str:
    """List the user's tasks. Filter by status: 'all', 'pending', or 'completed'."""
    session = ctx.context.db_session
    user_id = ctx.context.user_id

    statement = select(Task).where(Task.user_id == user_id)
    if status == "pending":
        statement = statement.where(Task.completed == False)
    elif status == "completed":
        statement = statement.where(Task.completed == True)

    result = await session.execute(statement)
    tasks = result.scalars().all()

    if not tasks:
        return f"No {status} tasks found." if status != "all" else "No tasks found."

    lines = []
    for t in tasks:
        check = "done" if t.completed else "pending"
        desc = f" - {t.description}" if t.description else ""
        lines.append(f"  [{check}] ID:{t.id} | {t.title}{desc}")

    return f"Found {len(tasks)} task(s):\n" + "\n".join(lines)


@function_tool
async def complete_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: int,
) -> str:
    """Mark a task as completed by its ID."""
    session = ctx.context.db_session
    user_id = ctx.context.user_id

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        return f"Task with ID {task_id} not found."

    task.completed = True
    task.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(task)
    return f"Task '{task.title}' (ID: {task.id}) marked as completed."


@function_tool
async def delete_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: int,
) -> str:
    """Delete a task by its ID."""
    session = ctx.context.db_session
    user_id = ctx.context.user_id

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        return f"Task with ID {task_id} not found."

    title = task.title
    await session.delete(task)
    await session.commit()
    return f"Task '{title}' (ID: {task_id}) deleted successfully."


@function_tool
async def update_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """Update a task's title or description by its ID."""
    session = ctx.context.db_session
    user_id = ctx.context.user_id

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        return f"Task with ID {task_id} not found."

    if title is not None:
        task.title = title.strip()
    if description is not None:
        task.description = description.strip() if description else None

    task.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(task)
    return f"Task '{task.title}' (ID: {task.id}) updated successfully."


ALL_TOOLS = [add_task, list_tasks, complete_task, delete_task, update_task]
