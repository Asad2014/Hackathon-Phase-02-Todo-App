from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routes
from routes import tasks, auth, chat
from exceptions import ValidationException

app = FastAPI(title="FastAPI Todo Backend", version="1.0.0")

# Configure CORS properly - only allow http://localhost:3000
# DO NOT use "*" with allow_credentials=True
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8007"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# Exception Handlers
# ======================================================
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "details": {"status_code": exc.status_code},
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "details": exc.errors(),
        },
    )


@app.exception_handler(ValidationException)
async def custom_validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "validation_error",
            "message": exc.detail.get("message", "Validation error occurred"),
            "details": exc.detail.get("details", {}),
        }
        if isinstance(exc.detail, dict)
        else {
            "error": "validation_error",
            "message": exc.detail,
            "details": {},
        },
    )


# ======================================================
# Routes
# ======================================================
app.include_router(tasks.router, prefix="/api/{user_id}", tags=["tasks"])
app.include_router(chat.router, prefix="/api/{user_id}", tags=["chat"])
app.include_router(auth.router, tags=["auth"])  # auth routes already have /auth prefix in the router definition


# ======================================================
# Startup
# ======================================================
@app.on_event("startup")
async def startup_event():
    from db import create_db_and_tables

    try:
        await create_db_and_tables()
    except Exception as e:
        print(f"Database initialization failed: {e}")


# ======================================================
# Health Check
# ======================================================
@app.get("/")
def read_root():
    return {"message": "FastAPI Todo Backend is running!"}


# ======================================================
# Run Server
# ======================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)






# from fastapi import APIRouter, Depends, HTTPException, status, Cookie
# from pydantic import BaseModel
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlmodel import select
# from datetime import datetime, timedelta
# import uuid
# from jose import jwt
# from passlib.context import CryptContext
# from db import get_db_session
# from models import User
# from config import settings

# router = APIRouter(prefix="/auth", tags=["auth"])

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # -------------------------
# # Pydantic Models
# # -------------------------
# class RegisterRequest(BaseModel):
#     email: str
#     name: str
#     password: str

# class LoginRequest(BaseModel):
#     email: str
#     password: str

# class TokenResponse(BaseModel):
#     access_token: str
#     token_type: str = "bearer"

# class UserResponse(BaseModel):
#     id: str
#     email: str
#     name: str

# # -------------------------
# # Helper functions
# # -------------------------
# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)

# def verify_password(plain: str, hashed: str) -> bool:
#     return pwd_context.verify(plain, hashed)

# def create_access_token(user_id: str, expires_minutes: int = 1440):
#     expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
#     to_encode = {"userId": user_id, "exp": expire.timestamp()}
#     token = jwt.encode(to_encode, settings.BETTER_AUTH_SECRET, algorithm="HS256")
#     return token

# def decode_access_token(token: str):
#     try:
#         payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"])
#         return payload.get("userId")
#     except jwt.JWTError:
#         return None

# # -------------------------
# # Register
# # -------------------------
# @router.post("/register", response_model=TokenResponse)
# async def register(data: RegisterRequest, session: AsyncSession = Depends(get_db_session)):
#     # Check existing user
#     statement = select(User).where(User.email == data.email)
#     result = await session.execute(statement)
#     existing = result.scalar_one_or_none()
#     if existing:
#         raise HTTPException(status_code=400, detail="Email already registered")

#     # Create user
#     user = User(
#         id=str(uuid.uuid4()),
#         email=data.email,
#         name=data.name,
#         hashed_password=get_password_hash(data.password)
#     )
#     session.add(user)
#     await session.commit()
#     await session.refresh(user)

#     token = create_access_token(user.id)
#     return {"access_token": token, "token_type": "bearer"}

# # -------------------------
# # Login
# # -------------------------
# @router.post("/login", response_model=TokenResponse)
# async def login(data: LoginRequest, session: AsyncSession = Depends(get_db_session)):
#     statement = select(User).where(User.email == data.email)
#     result = await session.execute(statement)
#     user = result.scalar_one_or_none()

#     if not user or not verify_password(data.password, user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid email or password")

#     token = create_access_token(user.id)
#     return {"access_token": token, "token_type": "bearer"}

# # -------------------------
# # Get Current User
# # -------------------------
# @router.get("/me", response_model=UserResponse)
# async def get_current_user(session_token: str = Cookie(None), session: AsyncSession = Depends(get_db_session)):
#     if not session_token:
#         raise HTTPException(status_code=401, detail="No session token")

#     user_id = decode_access_token(session_token)
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Invalid session token")

#     statement = select(User).where(User.id == user_id)
#     result = await session.execute(statement)
#     user = result.scalar_one_or_none()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     return UserResponse(id=user.id, email=user.email, name=user.name)
