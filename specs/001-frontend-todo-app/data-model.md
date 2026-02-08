# Data Model: Frontend Todo Web Application

## Entities

### User
- **Fields**:
  - id: string (unique identifier)
  - email: string (email address, unique)
  - name: string (display name)
  - createdAt: Date (account creation timestamp)
  - updatedAt: Date (last updated timestamp)
  - preferences: object (theme preference, notification settings)

- **Validations**:
  - Email must be valid email format
  - Email must be unique
  - Name must not be empty

- **State Transitions**:
  - Unauthenticated → Authenticated (login)
  - Authenticated → Unauthenticated (logout)

### Task
- **Fields**:
  - id: string (unique identifier)
  - title: string (task title, required)
  - description: string (optional task description)
  - completed: boolean (completion status)
  - userId: string (foreign key to User)
  - createdAt: Date (creation timestamp)
  - updatedAt: Date (last updated timestamp)
  - dueDate: Date (optional due date)

- **Validations**:
  - Title must not be empty
  - UserId must correspond to valid user
  - Due date must be valid date if provided

- **Relationships**:
  - Belongs to one User
  - User has many Tasks

## Business Logic

### User Isolation
- All task queries must be filtered by the authenticated user's ID
- Cross-user data access must be prevented at the API level
- JWT token must be validated for all authenticated requests

### Task Operations
- Users can create tasks for themselves
- Users can only view, update, and delete their own tasks
- Task completion status can be toggled by the owner
- Task details can be edited by the owner