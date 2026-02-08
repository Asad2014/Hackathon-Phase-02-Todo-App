# Quickstart Guide: Frontend Todo Web Application

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Git version control system
- Access to backend API (FastAPI server)

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd frontend
```

### 2. Install Dependencies
```bash
npm install
# or
yarn install
```

### 3. Environment Configuration
Create a `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-here
NEXT_PUBLIC_JWT_SECRET=your-jwt-secret-here
```

### 4. Initialize Shadcn/UI Components
```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input card dialog toast skeleton
```

### 5. Run Development Server
```bash
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:3000`

## Key Features

### Authentication
- Secure login/signup using Better Auth
- Automatic JWT token management
- Protected routes and private components

### Task Management
- Create, read, update, and delete tasks
- Optimistic UI updates for instant feedback
- Dark/light mode support
- Responsive design for all devices

### Development Tools
- TypeScript for type safety
- Tailwind CSS for styling
- ESLint and Prettier for code quality
- Husky for pre-commit hooks

## API Integration

### API Client
The centralized API client is located at `lib/api-client.ts`:
- Automatically attaches JWT tokens to requests
- Handles error responses
- Provides consistent request/response patterns

### Authentication Headers
All authenticated requests automatically include:
```
Authorization: Bearer <jwt-token>
```

## Folder Structure

```
frontend/
├── app/                 # Next.js App Router pages
│   ├── (auth)/         # Authentication pages
│   ├── (dashboard)/    # Main application pages
│   ├── globals.css     # Global styles
│   └── layout.tsx      # Root layout
├── components/         # Reusable UI components
│   ├── ui/            # Shadcn/UI components
│   └── auth/          # Authentication components
├── lib/               # Utility functions
│   └── api-client.ts  # API client with JWT integration
└── types/             # TypeScript type definitions
```

## Environment Variables

- `NEXT_PUBLIC_API_BASE_URL`: Base URL for backend API
- `NEXT_PUBLIC_BETTER_AUTH_URL`: Better Auth server URL
- `BETTER_AUTH_SECRET`: Secret for JWT signing
- `NEXT_PUBLIC_JWT_SECRET`: JWT secret for token validation