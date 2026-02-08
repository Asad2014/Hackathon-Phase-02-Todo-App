from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class TaskNotFoundException(HTTPException):
    """Raised when a task is not found"""
    def __init__(self, task_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )


class UnauthorizedAccessException(HTTPException):
    """Raised when a user tries to access resources they don't own"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )


class InvalidTokenException(HTTPException):
    """Raised when a JWT token is invalid"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ValidationException(HTTPException):
    """Raised for validation errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "validation_error",
                "message": message,
                "details": details or {}
            }
        )