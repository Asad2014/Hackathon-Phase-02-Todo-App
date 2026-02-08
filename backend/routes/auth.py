from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
import uuid
from jose import jwt
from passlib.context import CryptContext
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from models import User
from dependencies import get_db_session
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

# Helper functions
def _truncate_password(password: str) -> str:
    """
    Helper to truncate password to 72 bytes for bcrypt compatibility.
    """
    passwd_bytes = password.encode('utf-8')
    if len(passwd_bytes) > 72:
        passwd_bytes = passwd_bytes[:72]
        return passwd_bytes.decode('utf-8', errors='ignore')
    return password

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # We must truncate the plain password before verifying, 
    # because the hash was created from a truncated password.
    # Also passlib will raise ValueError if we pass > 72 bytes.
    safe_password = _truncate_password(plain_password)
    try:
        return pwd_context.verify(safe_password, hashed_password)
    except ValueError:
        # Fallback: try raw just in case, or handle validation error
        return False

def get_password_hash(password: str) -> str:
    safe_password = _truncate_password(password)
    return pwd_context.hash(safe_password)

router = APIRouter(prefix="/auth", tags=["auth"])

# Pydantic models
class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1)  # Remove max_length limit, we handle truncation

class RegisterRequest(BaseModel):
    email: str
    name: Optional[str] = None
    password: str = Field(min_length=1)  # Remove max_length limit, we handle truncation


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]


# Helper functions


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, settings.BETTER_AUTH_SECRET, algorithm="HS256")
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("userId")
        if user_id is None:
            return None
        return user_id
    except jwt.JWTError:
        return None


@router.post("/login", response_model=TokenResponse)
async def login(login_request: LoginRequest, session: AsyncSession = Depends(get_db_session)):
    # Find user by email
    statement = select(User).where(User.email == login_request.email)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={"userId": user.id},
        expires_delta=timedelta(hours=24)
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=TokenResponse)
async def register(register_request: RegisterRequest, session: AsyncSession = Depends(get_db_session)):
    try:
        # Check if user already exists
        statement = select(User).where(User.email == register_request.email)
        result = await session.execute(statement)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user with hashed password
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(register_request.password)

        # Ensure name is not None
        user_name = register_request.name
        if not user_name:
            user_name = register_request.email.split('@')[0]

        user = User(
            id=user_id,
            email=register_request.email,
            name=user_name,
            password=hashed_password  # Store hashed password (field named password in DB)
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Create access token
        access_token = create_access_token(
            data={"userId": user.id},
            expires_delta=timedelta(hours=24)
        )

        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error during registration: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session: AsyncSession = Depends(get_db_session)):
    token = credentials.credentials

    # Check if token is blacklisted
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_access_token(token)
    print(f"Decoded user_id: {user_id}")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Retrieve user from database
    try:
        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement)
        user = result.scalar_one_or_none()
    except Exception as e:
        print(f"Database error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserResponse(id=user.id, email=user.email, name=user.name)


from auth_utils import blacklist_token, is_token_blacklisted

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout endpoint that adds the current token to a blacklist
    """
    token = credentials.credentials

    # Add the token to the blacklist
    blacklist_token(token)

    return {"message": "Successfully logged out"}