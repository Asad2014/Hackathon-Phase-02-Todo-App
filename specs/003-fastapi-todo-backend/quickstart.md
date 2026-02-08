# Quickstart Guide: FastAPI Todo Backend

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
DATABASE_URL=postgresql://neondb_owner:npg_oesqnFNCt12u@ep-billowing-lab-a13iu7ll-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=5mhHToIaFowGOPHmN7LJcgW4xE9fM05E
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

## Troubleshooting

### Database Connection Issues
- Verify DATABASE_URL is correct in your environment
- Check that your network allows connections to Neon PostgreSQL
- Ensure SSL mode is properly configured

### Authentication Failures
- Confirm BETTER_AUTH_SECRET matches the one used by the frontend auth system
- Verify JWT tokens are properly formatted and not expired
- Check that the Authorization header follows the "Bearer <token>" format

### CORS Errors
- Ensure frontend URL (http://localhost:3000) is allowed in CORS configuration
- Check that the backend is running when accessing from frontend