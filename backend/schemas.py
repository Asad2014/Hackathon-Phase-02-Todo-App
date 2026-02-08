from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class TaskCreate(TaskBase):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskResponse(TaskBase):
    id: int
    user_id: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """
    Standard error response format for the API
    """
    error: str
    message: Optional[str] = None
    details: Optional[dict] = None


class ValidationErrorResponse(ErrorResponse):
    """
    Error response for validation errors
    """
    error: str = "validation_error"
    message: str
    details: dict