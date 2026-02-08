# Data Model: FastAPI Todo Backend

## Entities

### User
**Description**: Represents an authenticated user in the system

**Fields**:
- `id` (UUID/String): Unique identifier for the user (primary key)
- `email` (String): User's email address
- `name` (String): User's display name
- `created_at` (DateTime): Timestamp when user was created
- `updated_at` (DateTime): Timestamp when user was last updated

**Relationships**:
- One-to-Many: User has many Tasks (via user_id foreign key)

### Task
**Description**: Represents a todo item created by a user

**Fields**:
- `id` (UUID/Integer): Unique identifier for the task (primary key)
- `user_id` (String/UUID): Foreign key linking to the user who owns this task
- `title` (String): Title/name of the task (required)
- `description` (String): Optional detailed description of the task
- `completed` (Boolean): Status indicating if the task is completed (default: False)
- `created_at` (DateTime): Timestamp when task was created
- `updated_at` (DateTime): Timestamp when task was last updated

**Relationships**:
- Many-to-One: Task belongs to one User (via user_id foreign key)

## Database Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Validation Rules

### User Validation
- Email must be a valid email format
- Name must be between 1-255 characters
- Email must be unique across all users

### Task Validation
- Title must be between 1-255 characters
- User_id must reference an existing user
- Completed status defaults to False
- Description is optional, max length 1000 characters

## State Transitions

### Task State Transitions
- `created` → `active`: When a new task is created (default: completed=False)
- `active` → `completed`: When user marks task as completed (completed=True)
- `completed` → `active`: When user unmarks task as completed (completed=False)

## Constraints

### Data Integrity
- Foreign key constraint ensures task.user_id references valid user.id
- Cascade delete: When a user is deleted, all their tasks are also deleted
- Non-null constraints on required fields
- Unique constraint on user email

### Business Logic
- Each task must belong to exactly one user
- Users can only view, create, update, or delete their own tasks
- Task titles must be provided (cannot be empty)