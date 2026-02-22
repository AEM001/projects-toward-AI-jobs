# Todo Frontend

Modern React + Vite + TypeScript + Tailwind CSS frontend for your FastAPI Todo API.

## Features

- ⚡ **Vite** - Lightning fast HMR and build
- ⚛️ **React 18** - Latest React with hooks
- 🔷 **TypeScript** - Type-safe code
- 🎨 **Tailwind CSS** - Modern utility-first styling
- 🔄 **React Query** - Powerful data fetching and caching
- 🗂️ **Zustand** - Simple state management
- 🛣️ **React Router** - Client-side routing
- 🔐 **JWT Auth** - Secure authentication flow

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:5173
```

## Configuration

The API URL is configured in `src/config/api.ts`:
- Default: `http://49.234.57.210:9000`
- Change it to your local backend if needed: `http://localhost:8000`

## API Connection

Your FastAPI backend provides:
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /todos/` - List todos
- `POST /todos/` - Create todo
- `PATCH /todos/{id}` - Update todo
- `DELETE /todos/{id}` - Delete todo

## Build for Production

```bash
npm run build
```

Output will be in `dist/` folder.
