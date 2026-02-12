from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List
import json
import os

from openai import AsyncOpenAI
from agents import Agent, Runner, set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

# Disable tracing (requires OPENAI_API_KEY which we don't have when using Gemini)
set_tracing_disabled(True)

from dependencies import get_db_session, CurrentUser
from models import Conversation, Message
from schemas import ChatRequest, ChatResponse, ToolCallInfo, MessageResponse
from agent_tools import AgentContext, ALL_TOOLS
from config import settings

router = APIRouter()

SYSTEM_PROMPT = """You are a Todo assistant that manages tasks using ONLY the provided tools.

CRITICAL RULES:
1. You MUST call the appropriate tool for EVERY task action. NEVER just say you did something - actually call the tool.
2. When the user asks to add a task, IMMEDIATELY call add_task. Do NOT ask follow-up questions unless the title is completely unclear.
3. When the user asks to list tasks, IMMEDIATELY call list_tasks.
4. When the user asks to complete a task, IMMEDIATELY call complete_task.
5. When the user asks to delete a task, IMMEDIATELY call delete_task.
6. When the user asks to update a task, IMMEDIATELY call update_task.
7. NEVER pretend you performed an action without calling a tool. If you didn't call a tool, you didn't do the action.

After calling a tool, briefly confirm the result to the user.
Keep responses short and action-oriented."""


def _check_user_authorization(path_user_id: str, current_user: str):
    if current_user != path_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource",
        )


async def _get_or_create_conversation(
    user_id: str, session: AsyncSession, conversation_id: int | None = None
) -> Conversation:
    if conversation_id:
        stmt = select(Conversation).where(
            Conversation.id == conversation_id, Conversation.user_id == user_id
        )
        result = await session.execute(stmt)
        conv = result.scalar_one_or_none()
        if conv:
            return conv

    # Get the user's most recent conversation or create one
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    result = await session.execute(stmt)
    conv = result.scalar_one_or_none()

    if conv:
        return conv

    conv = Conversation(user_id=user_id)
    session.add(conv)
    await session.commit()
    await session.refresh(conv)
    return conv


async def _get_history_messages(
    conversation_id: int, user_id: str, session: AsyncSession, limit: int = 10
) -> list[dict]:
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id, Message.user_id == user_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    messages = list(reversed(result.scalars().all()))

    history = []
    for msg in messages:
        history.append({"role": msg.role, "content": msg.content})
    return history


@router.post("/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: str = Depends(CurrentUser),
    session: AsyncSession = Depends(get_db_session),
):
    _check_user_authorization(user_id, current_user)

    # Get or create conversation
    conversation = await _get_or_create_conversation(
        user_id, session, request.conversation_id
    )

    # Fetch history
    history = await _get_history_messages(conversation.id, user_id, session)

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=request.message,
    )
    session.add(user_msg)
    await session.commit()

    # Build input messages for the agent
    input_messages = history + [{"role": "user", "content": request.message}]

    # Configure OpenRouter API
    openrouter_client = AsyncOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )

    # Create agent with OpenRouter model
    agent = Agent(
        name="TodoAssistant",
        instructions=SYSTEM_PROMPT,
        tools=ALL_TOOLS,
        model=OpenAIChatCompletionsModel(
            model="google/gemini-2.0-flash-001",
            openai_client=openrouter_client,
        ),
    )

    context = AgentContext(user_id=user_id, db_session=session)

    try:
        result = await Runner.run(agent, input=input_messages, context=context)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI agent error: {str(e)}",
        )

    # Extract response text
    response_text = result.final_output or "I'm sorry, I couldn't process that request."

    # Extract tool calls from result.new_items
    tool_calls_info: list[ToolCallInfo] = []
    try:
        for item in result.new_items:
            item_type = getattr(item, "type", None)
            if item_type == "tool_call_item":
                raw_call = getattr(item, "raw_item", item)
                tool_name = getattr(raw_call, "name", None) or "unknown"
                arguments_str = getattr(raw_call, "arguments", "{}")
                try:
                    arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
                except (json.JSONDecodeError, TypeError):
                    arguments = {}
                tool_calls_info.append(
                    ToolCallInfo(tool_name=tool_name, arguments=arguments, result="")
                )
            elif item_type == "tool_call_output_item":
                raw_output = getattr(item, "output", "")
                if tool_calls_info and not tool_calls_info[-1].result:
                    tool_calls_info[-1].result = str(raw_output)
    except Exception:
        pass

    # Save assistant message
    tool_calls_json = (
        json.dumps([tc.model_dump() for tc in tool_calls_info]) if tool_calls_info else None
    )
    assistant_msg = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="assistant",
        content=response_text,
        tool_calls=tool_calls_json,
    )
    session.add(assistant_msg)

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    await session.commit()

    return ChatResponse(
        response=response_text,
        conversation_id=conversation.id,
        tool_calls=tool_calls_info,
        created_at=assistant_msg.created_at,
    )


@router.get("/chat/history")
async def get_chat_history(
    user_id: str,
    current_user: str = Depends(CurrentUser),
    session: AsyncSession = Depends(get_db_session),
):
    _check_user_authorization(user_id, current_user)

    # Get user's conversation
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    result = await session.execute(stmt)
    conv = result.scalar_one_or_none()

    if not conv:
        return {"conversation_id": None, "messages": []}

    # Get all messages
    stmt = (
        select(Message)
        .where(Message.conversation_id == conv.id, Message.user_id == user_id)
        .order_by(Message.created_at.asc())
    )
    result = await session.execute(stmt)
    messages = result.scalars().all()

    message_list = []
    for msg in messages:
        tool_calls = None
        if msg.tool_calls:
            try:
                tool_calls = json.loads(msg.tool_calls)
            except (json.JSONDecodeError, TypeError):
                tool_calls = None

        message_list.append(
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                tool_calls=tool_calls,
                created_at=msg.created_at,
            )
        )

    return {"conversation_id": conv.id, "messages": message_list}
