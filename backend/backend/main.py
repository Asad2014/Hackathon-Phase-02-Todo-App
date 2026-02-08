from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routes
from routes import tasks, auth
from exceptions import ValidationException

app = FastAPI(title="FastAPI Todo Backend", version="1.0.0")

# Configure CORS properly - only allow http://localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Only allow Next.js frontend
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
app.include_router(auth.router, tags=["auth"])


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