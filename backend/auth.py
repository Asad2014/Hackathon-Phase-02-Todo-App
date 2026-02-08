from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from config import settings
from typing import Optional
import os

# Define the security scheme
security = HTTPBearer()

# Define the algorithm
ALGORITHM = "HS256"

def verify_token(token: str) -> Optional[str]:
    """
    Verify the JWT token and extract user_id
    Returns user_id if valid, None if invalid
    """
    try:
        # Decode the JWT token using the BETTER_AUTH_SECRET
        payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=[ALGORITHM])

        # Extract user_id from the payload
        user_id: str = payload.get("userId")

        if user_id is None:
            return None

        # Check if token has expired
        exp = payload.get("exp")
        if exp is not None:
            import time
            if time.time() > exp:
                return None

        return user_id
    except JWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency to get the current user from the JWT token
    """
    token = credentials.credentials

    user_id = verify_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id




# from fastapi import Depends, HTTPException, status, Request
# from jose import jwt, JWTError
# from config import settings
# from typing import Optional
# import time

# ALGORITHM = "HS256"


# def verify_token(token: str) -> Optional[str]:
#     """
#     Verify the JWT token and extract user_id
#     Returns user_id if valid, None if invalid
#     """
#     try:
#         payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=[ALGORITHM])

#         # Extract user_id
#         user_id: str = payload.get("userId")
#         if user_id is None:
#             return None

#         # Check expiration
#         exp = payload.get("exp")
#         if exp and time.time() > exp:
#             return None

#         return user_id
#     except JWTError:
#         return None


# async def get_current_user(request: Request) -> str:
#     """
#     Dependency to get the current user from JWT token stored in cookies.
#     Compatible with fetch(..., credentials: 'include') from Next.js.
#     """
#     # Get token from cookie
#     token = request.cookies.get("better-auth.session_token")

#     if not token:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="No authentication token provided",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     user_id = verify_token(token)
#     if not user_id:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     return user_id
