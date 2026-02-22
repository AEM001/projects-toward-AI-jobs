# Next.js + TypeScript + Tailwind CSS + shadcn/ui - Complete Frontend Guide

## 📚 Table of Contents
1. [What is This Stack?](#what-is-this-stack)
2. [Technology Overview](#technology-overview)
3. [Project Structure](#project-structure)
4. [Core Concepts Explained](#core-concepts-explained)
5. [How Everything Works Together](#how-everything-works-together)
6. [Common Patterns & Examples](#common-patterns--examples)
7. [Running the Project](#running-the-project)
8. [Troubleshooting](#troubleshooting)

---

## What is This Stack?

Your frontend is now built with a **modern, production-ready stack** that's used by companies like Vercel, Netflix, and thousands of startups. Here's what each technology does:

- **Next.js**: The React framework that handles routing, rendering, and optimization
- **TypeScript**: Adds type safety to JavaScript (catches bugs before they happen)
- **Tailwind CSS**: Utility-first CSS framework (style directly in your HTML)
- **shadcn/ui**: Beautiful, accessible UI components built on Radix UI

---

## Technology Overview

### 1. Next.js - The React Framework

**What is it?**
Next.js is a framework built on top of React that makes building web applications easier and faster.

**Why use it?**
- **File-based routing**: Create a file in `app/login/page.tsx` → automatically get `/login` route
- **Server & Client components**: Render on server for speed, or client for interactivity
- **Built-in optimization**: Automatic code splitting, image optimization, font optimization
- **API routes**: Build your backend API right in the same project (we're using FastAPI instead)

**Key Concepts:**

#### App Router (Next.js 13+)
```
app/
├── page.tsx          → Homepage (/)
├── login/
│   └── page.tsx      → Login page (/login)
├── todos/
│   └── page.tsx      → Todos page (/todos)
└── layout.tsx        → Wraps all pages (navbar, footer, etc.)
```

#### Server vs Client Components
```tsx
// Server Component (default) - Runs on server, faster, SEO-friendly
export default function Page() {
  return <div>Hello</div>
}

// Client Component - Runs in browser, can use hooks, state, events
'use client';
export default function Page() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

**When to use 'use client':**
- Using React hooks (`useState`, `useEffect`, etc.)
- Using browser APIs (`localStorage`, `window`, etc.)
- Event handlers (`onClick`, `onChange`, etc.)
- Using context or state management (Zustand)

---

### 2. TypeScript - Type Safety for JavaScript

**What is it?**
TypeScript is JavaScript with types. It catches errors while you're writing code, not when users are using your app.

**Example:**
```typescript
// JavaScript - No error until runtime
function greet(name) {
  return "Hello " + name.toUpperCase(); // Crashes if name is undefined
}
greet(); // Oops! Forgot to pass name

// TypeScript - Error immediately in your editor
function greet(name: string) {
  return "Hello " + name.toUpperCase();
}
greet(); // ❌ Error: Expected 1 argument, but got 0
```

**Common Types in This Project:**

```typescript
// Interface - Defines shape of an object
interface User {
  id: number;
  email: string;
}

// Type - Similar to interface
type Todo = {
  id: number;
  title: string;
  done: boolean;
  ddl: string;
  owner_id: number;
}

// Function with types
function createTodo(title: string): Promise<Todo> {
  return todoAPI.createTodo({ title });
}

// React component props
interface ButtonProps {
  onClick: () => void;
  children: React.ReactNode;
  disabled?: boolean; // ? means optional
}
```

**Benefits:**
- Autocomplete in your editor (knows what properties exist)
- Catches typos and bugs before running code
- Self-documenting code (types explain what data looks like)

---

### 3. Tailwind CSS - Utility-First Styling

**What is it?**
Instead of writing CSS files, you apply pre-made utility classes directly to your HTML.

**Traditional CSS vs Tailwind:**

```html
<!-- Traditional CSS -->
<style>
  .button {
    background-color: blue;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
  }
</style>
<button class="button">Click me</button>

<!-- Tailwind CSS -->
<button class="bg-blue-500 text-white px-4 py-2 rounded-md">
  Click me
</button>
```

**Common Tailwind Classes:**

```tsx
// Layout
<div className="flex">              // display: flex
<div className="grid">              // display: grid
<div className="block">             // display: block

// Spacing
<div className="p-4">               // padding: 1rem (all sides)
<div className="px-4 py-2">         // padding-x: 1rem, padding-y: 0.5rem
<div className="m-4">               // margin: 1rem
<div className="gap-2">             // gap: 0.5rem (for flex/grid)

// Sizing
<div className="w-full">            // width: 100%
<div className="h-screen">          // height: 100vh
<div className="max-w-md">          // max-width: 28rem

// Colors
<div className="bg-blue-500">       // background-color: blue
<div className="text-white">        // color: white
<div className="border-gray-200">   // border-color: gray

// Typography
<div className="text-xl">           // font-size: 1.25rem
<div className="font-bold">         // font-weight: 700
<div className="text-center">       // text-align: center

// Flexbox
<div className="flex items-center justify-between">
// display: flex; align-items: center; justify-content: space-between

// Responsive Design
<div className="md:flex lg:grid">
// flex on medium screens, grid on large screens

// Hover/Focus States
<button className="hover:bg-blue-600 focus:ring-2">
// Changes on hover and focus
```

**Responsive Design:**
```tsx
<div className="
  w-full          // Full width on mobile
  md:w-1/2        // Half width on tablets (768px+)
  lg:w-1/3        // Third width on desktop (1024px+)
">
```

---

### 4. shadcn/ui - Beautiful UI Components

**What is it?**
A collection of copy-paste components built with Radix UI and Tailwind CSS. Unlike component libraries you `npm install`, shadcn/ui copies the actual code into your project so you own it.

**Components in This Project:**

#### Button
```tsx
import { Button } from '@/components/ui/button';

<Button>Default</Button>
<Button variant="outline">Outline</Button>
<Button variant="destructive">Delete</Button>
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
<Button disabled>Disabled</Button>
```

#### Card
```tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
  </CardHeader>
  <CardContent>
    Card content goes here
  </CardContent>
</Card>
```

#### Input & Label
```tsx
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

<div>
  <Label htmlFor="email">Email</Label>
  <Input 
    id="email" 
    type="email" 
    placeholder="you@example.com"
    value={email}
    onChange={(e) => setEmail(e.target.value)}
  />
</div>
```

---

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout (wraps all pages)
│   │   ├── page.tsx            # Homepage (redirects to login/todos)
│   │   ├── providers.tsx       # React Query provider
│   │   ├── login/
│   │   │   └── page.tsx        # Login page
│   │   ├── register/
│   │   │   └── page.tsx        # Register page
│   │   └── todos/
│   │       └── page.tsx        # Todos page
│   │
│   ├── components/
│   │   └── ui/                 # shadcn/ui components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── input.tsx
│   │       └── label.tsx
│   │
│   ├── services/
│   │   └── api.ts              # API client (axios)
│   │
│   ├── store/
│   │   └── authStore.ts        # Zustand state management
│   │
│   ├── types/
│   │   └── index.ts            # TypeScript types
│   │
│   └── utils/
│       └── cn.ts               # Utility function for className merging
│
├── .env.local                  # Environment variables (API URL)
├── .env.example                # Example env file
├── next.config.ts              # Next.js configuration
├── tailwind.config.ts          # Tailwind CSS configuration
├── tsconfig.json               # TypeScript configuration
└── package.json                # Dependencies
```

---

## Core Concepts Explained

### 1. State Management with Zustand

**What is state?**
State is data that changes over time (like user info, todos, form inputs).

**Why Zustand?**
- Simpler than Redux
- No boilerplate code
- Works with TypeScript
- Persistent storage built-in

**Example: Auth Store**
```typescript
// src/store/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      // Action to set user and token
      setAuth: (user, token) => {
        localStorage.setItem('token', token);
        set({ user, token, isAuthenticated: true });
      },
      
      // Action to logout
      logout: () => {
        localStorage.removeItem('token');
        set({ user: null, token: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage', // localStorage key
    }
  )
);

// Usage in components
function MyComponent() {
  const { user, logout } = useAuthStore();
  
  return (
    <div>
      <p>Welcome, {user?.email}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

---

### 2. Data Fetching with React Query

**What is React Query?**
A library for fetching, caching, and updating server data.

**Why use it?**
- Automatic caching (don't re-fetch data you already have)
- Loading and error states built-in
- Automatic refetching when data is stale
- Optimistic updates

**Example: Fetching Todos**
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function TodosPage() {
  const queryClient = useQueryClient();
  
  // Fetch todos
  const { data, isLoading, error } = useQuery({
    queryKey: ['todos'],           // Unique key for this query
    queryFn: () => todoAPI.getTodos(), // Function that fetches data
  });
  
  // Create todo mutation
  const createMutation = useMutation({
    mutationFn: (title: string) => todoAPI.createTodo({ title }),
    onSuccess: () => {
      // Refetch todos after creating one
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });
  
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      <button onClick={() => createMutation.mutate('New Todo')}>
        Add Todo
      </button>
      {data?.items.map(todo => (
        <div key={todo.id}>{todo.title}</div>
      ))}
    </div>
  );
}
```

**Query vs Mutation:**
- **Query**: Fetching data (GET requests)
- **Mutation**: Changing data (POST, PUT, DELETE requests)

---

### 3. API Client with Axios

**What is Axios?**
A library for making HTTP requests (like `fetch` but better).

**Our API Client:**
```typescript
// src/services/api.ts
import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await api.post('/api/v1/auth/login', { email, password });
    return response.data;
  },
  // ... more methods
};

// Todo API
export const todoAPI = {
  getTodos: async () => {
    const response = await api.get('/api/v1/todos');
    return response.data;
  },
  createTodo: async (data: { title: string }) => {
    const response = await api.post('/api/v1/todos', data);
    return response.data;
  },
  // ... more methods
};
```

**Usage:**
```typescript
// In a component
const handleLogin = async () => {
  try {
    const data = await authAPI.login(email, password);
    console.log('Logged in:', data);
  } catch (error) {
    console.error('Login failed:', error);
  }
};
```

---

### 4. Routing in Next.js

**File-based Routing:**
```
app/
├── page.tsx              → /
├── login/
│   └── page.tsx          → /login
├── register/
│   └── page.tsx          → /register
└── todos/
    └── page.tsx          → /todos
```

**Navigation:**
```typescript
import { useRouter } from 'next/navigation';
import Link from 'next/link';

function MyComponent() {
  const router = useRouter();
  
  // Programmatic navigation
  const goToTodos = () => {
    router.push('/todos');
  };
  
  return (
    <div>
      {/* Link component (preferred for navigation) */}
      <Link href="/login">Go to Login</Link>
      
      {/* Button with onClick */}
      <button onClick={goToTodos}>Go to Todos</button>
    </div>
  );
}
```

---

## How Everything Works Together

### Login Flow Example

1. **User visits `/login`**
   - Next.js renders `app/login/page.tsx`
   - Component is marked `'use client'` (needs interactivity)

2. **User enters email/password**
   - React state (`useState`) stores form values
   - TypeScript ensures email is a string

3. **User clicks "Login"**
   - React Query mutation is triggered
   - Axios sends POST request to FastAPI backend
   - Request includes email/password in JSON body

4. **Backend responds with token**
   - Mutation `onSuccess` callback runs
   - Zustand store saves user and token
   - Token is also saved to localStorage
   - Router redirects to `/todos`

5. **User sees todos page**
   - Next.js renders `app/todos/page.tsx`
   - React Query fetches todos from API
   - Axios automatically adds token to request headers
   - shadcn/ui Card components display todos
   - Tailwind CSS styles everything

### Creating a Todo Flow

1. **User types in input**
   - React state updates on every keystroke
   - Input component from shadcn/ui

2. **User clicks "Add"**
   - Form `onSubmit` prevents page reload
   - React Query mutation is triggered
   - Axios sends POST request with todo title

3. **Backend creates todo**
   - Mutation `onSuccess` callback runs
   - React Query invalidates todos cache
   - Todos are automatically refetched
   - UI updates with new todo

---

## Common Patterns & Examples

### Pattern 1: Protected Route

```typescript
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';

export default function ProtectedPage() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);
  
  if (!isAuthenticated) {
    return null; // or loading spinner
  }
  
  return <div>Protected content</div>;
}
```

### Pattern 2: Form with Validation

```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function MyForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const validate = () => {
    const newErrors: Record<string, string> = {};
    
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      // Submit form
      console.log('Form is valid');
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        {errors.email && (
          <p className="text-sm text-red-500">{errors.email}</p>
        )}
      </div>
      
      <div>
        <Label htmlFor="password">Password</Label>
        <Input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {errors.password && (
          <p className="text-sm text-red-500">{errors.password}</p>
        )}
      </div>
      
      <Button type="submit">Submit</Button>
    </form>
  );
}
```

### Pattern 3: Loading States

```typescript
'use client';

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';

export default function DataPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['data'],
    queryFn: fetchData,
  });
  
  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto" />
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </CardContent>
      </Card>
    );
  }
  
  if (error) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-red-500">
          Error: {error.message}
        </CardContent>
      </Card>
    );
  }
  
  return (
    <div>
      {data.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
}
```

### Pattern 4: Conditional Rendering

```typescript
// Show different UI based on state
{isLoading ? (
  <div>Loading...</div>
) : error ? (
  <div>Error: {error.message}</div>
) : data.length === 0 ? (
  <div>No items found</div>
) : (
  <div>
    {data.map(item => <div key={item.id}>{item.name}</div>)}
  </div>
)}

// Show/hide based on condition
{user && <div>Welcome, {user.email}</div>}
{!isAuthenticated && <Link href="/login">Login</Link>}

// Conditional className
<div className={`base-class ${isActive ? 'active' : 'inactive'}`}>
```

---

## Running the Project

### 1. Install Dependencies
```bash
cd /Users/Mac/code/project/FastAPI/frontend
npm install
```

### 2. Set Up Environment Variables
```bash
# Copy example env file
cp .env.example .env.local

# Edit .env.local if needed
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Development Server
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### 4. Build for Production
```bash
npm run build
npm start
```

---

## Troubleshooting

### Common Errors

#### 1. "Cannot find module '@/...'"
**Problem:** TypeScript can't resolve the `@/` import alias

**Solution:** Check `tsconfig.json` has:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

#### 2. "localStorage is not defined"
**Problem:** Trying to use localStorage in a Server Component

**Solution:** Add `'use client'` at the top of the file:
```typescript
'use client';

import { useEffect } from 'react';

export default function MyComponent() {
  useEffect(() => {
    const token = localStorage.getItem('token');
  }, []);
}
```

#### 3. "Hydration failed"
**Problem:** Server-rendered HTML doesn't match client-rendered HTML

**Solution:** 
- Don't use `localStorage` or `window` during initial render
- Use `useEffect` for client-only code
- Make sure server and client render the same initial HTML

```typescript
'use client';

import { useState, useEffect } from 'react';

export default function MyComponent() {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);
  
  if (!mounted) {
    return null; // or loading state
  }
  
  return <div>{localStorage.getItem('token')}</div>;
}
```

#### 4. API Requests Failing
**Problem:** CORS errors or 404s

**Solution:**
- Make sure FastAPI backend is running on port 8000
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
- Verify API endpoints match backend routes

#### 5. Styles Not Applying
**Problem:** Tailwind classes not working

**Solution:**
- Make sure `tailwind.config.ts` includes your files:
```typescript
export default {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
}
```
- Restart dev server after changing Tailwind config

---

## Key Takeaways

### What You Should Understand

1. **Next.js App Router**: Files in `app/` folder become routes
2. **'use client' directive**: Needed for interactivity (hooks, events, state)
3. **TypeScript types**: Define shapes of data (User, Todo, etc.)
4. **Tailwind classes**: Style directly in JSX with utility classes
5. **React Query**: Handles data fetching, caching, and mutations
6. **Zustand**: Simple state management for global state (auth)
7. **shadcn/ui**: Pre-built components you can customize

### Development Workflow

1. **Create a new page**: Add file in `app/your-page/page.tsx`
2. **Add interactivity**: Add `'use client'` and use hooks
3. **Style it**: Use Tailwind classes
4. **Fetch data**: Use React Query's `useQuery`
5. **Mutate data**: Use React Query's `useMutation`
6. **Manage state**: Use Zustand for global state, `useState` for local

### Resources for Learning More

- **Next.js**: https://nextjs.org/docs
- **TypeScript**: https://www.typescriptlang.org/docs/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **shadcn/ui**: https://ui.shadcn.com
- **React Query**: https://tanstack.com/query/latest/docs/react/overview
- **Zustand**: https://github.com/pmndrs/zustand

---

## Summary

You now have a **modern, type-safe, production-ready** frontend built with:

✅ **Next.js** - Fast, SEO-friendly React framework with file-based routing
✅ **TypeScript** - Catches bugs before they happen with type safety
✅ **Tailwind CSS** - Rapid styling with utility classes
✅ **shadcn/ui** - Beautiful, accessible UI components
✅ **React Query** - Smart data fetching and caching
✅ **Zustand** - Simple state management

This stack is used by thousands of companies and is considered industry best practice for modern web development in 2024-2026.

**Happy coding! 🚀**
