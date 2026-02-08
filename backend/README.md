# FastAPI Todo Backend

A robust, secure FastAPI backend for the Todo application with JWT-based authentication compatible with Better Auth, Neon PostgreSQL database using SQLModel ORM, and full user isolation.

## Features

- **Secure Task Management**: Create, read, update, and delete tasks with proper authentication and authorization
- **User Isolation**: Each user can only access their own tasks
- **JWT Authentication**: Secure token-based authentication with Better Auth compatibility
- **RESTful API**: Clean, intuitive API endpoints for task management
- **Task Completion Toggle**: Mark tasks as completed/incomplete with a single endpoint
- **Input Validation**: Comprehensive validation for all API inputs
- **Consistent Error Handling**: Standardized error response format

## Prerequisites

- Python 3.11+
- pip package manager
- Access to Neon PostgreSQL database
- Environment variables configured

## Setup Instructions

### 1. Clone and Navigate to Backend Directory

```bash
cd /path/to/project/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If requirements.txt doesn't exist yet, install the core dependencies:

```bash
pip install fastapi uvicorn sqlmodel python-jose[cryptography] psycopg2-binary python-multipart python-dotenv
```

### 4. Environment Configuration

Create a `.env` file in the backend root with the following variables:

```env
DATABASE_URL=postgresql://your_username:your_password@your_host:your_port/your_database
BETTER_AUTH_SECRET=your_better_auth_secret
BETTER_AUTH_URL=http://localhost:3000/
```

### 5. Initialize Database Tables

The application will automatically create tables on startup. Alternatively, you can create them manually:

```bash
python -c "from main import create_db_and_tables; create_db_and_tables()"
```

### 6. Start the Development Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or if using the app in main.py differently:

```bash
cd backend
python -m uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation will be available at `http://localhost:8000/docs`

## API Endpoints

### Task Management

- `GET /api/{user_id}/tasks` - Get all tasks for a specific user
- `POST /api/{user_id}/tasks` - Create a new task for a user
- `PUT /api/{user_id}/tasks/{id}` - Update a specific task
- `DELETE /api/{user_id}/tasks/{id}` - Delete a specific task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion status

### Authentication

All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token_here>
```

## Error Response Format

The API returns standardized error responses:

```json
{
  "error": "error_type",
  "message": "Human-readable error message",
  "details": {
    "additional_details": "as needed"
  }
}
```

## Development Commands

### Run Tests

```bash
pytest tests/
```

### Format Code

```bash
black .
```

### Lint Code

```bash
flake8 .
```

## Security Features

- **JWT Token Validation**: All requests are authenticated using JWT tokens
- **User Isolation**: Users can only access their own tasks
- **Input Validation**: All inputs are validated to prevent injection and other attacks
- **Proper Error Handling**: Generic error messages to avoid information leakage

## Architecture

- **Database**: Neon PostgreSQL with SQLModel ORM
- **Authentication**: JWT-based with Better Auth compatibility
- **Framework**: FastAPI with async support
- **Validation**: Pydantic models for request/response validation