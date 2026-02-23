# Frontend Learning Guide: Zero to Hero

## FastAPI Todo Application Frontend

> **A comprehensive guide to modern React/Next.js development**  
> Learn by exploring a production-ready todo application

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Architecture & Structure](#3-architecture--structure)
4. [Core Concepts](#4-core-concepts)
5. [Deep Dive: Code Analysis](#5-deep-dive-code-analysis)
6. [Knowledge Breakdown](#6-knowledge-breakdown)
7. [Learning Path](#7-learning-path)

---

## 1. Project Overview

### What This Application Does

A full-stack todo application with:

- **User Authentication** (register, login, logout)
- **Todo Management** (create, read, update, delete)
- **Real-time UI Updates** (optimistic updates, auto-refresh)
- **Modern Design** (responsive, dark mode support)

### Key Features

- JWT-based authentication
- Protected routes
- Form validation
- Loading states
- Error handling
- Persistent state management

---

## 2. Technology Stack

### Core Framework

- **Next.js 16** - React framework with App Router
- **React 19** - UI library with latest features
- **TypeScript** - Type-safe JavaScript

### State Management

- **Zustand** - Lightweight state management (auth)
- **TanStack Query** - Server state management (API data)

### Styling

- **Tailwind CSS v4** - Utility-first CSS framework
- **shadcn/ui** - Pre-built accessible components
- **class-variance-authority** - Component variant management

### HTTP & Data

- **Axios** - HTTP client with interceptors
- **React Query** - Async state management

### UI Components

- **Lucide React** - Icon library
- **Radix UI** - Headless UI primitives

---

## 3. Architecture & Structure

### Directory Tree

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx          # Root layout (wraps all pages)
│   │   ├── page.tsx            # Home page (redirects)
│   │   ├── providers.tsx       # React Query provider
│   │   ├── globals.css         # Global styles + Tailwind
│   │   ├── login/
│   │   │   └── page.tsx        # Login page
│   │   ├── register/
│   │   │   └── page.tsx        # Register page
│   │   └── todos/
│   │       └── page.tsx        # Todo list page
│   ├── components/
│   │   └── ui/                 # Reusable UI components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── input.tsx
│   │       └── label.tsx
│   ├── services/
│   │   └── api.ts              # API client & endpoints
│   ├── store/

│   │   └── authStore.ts        # Zustand auth state
│   ├── types/
│   │   └── index.ts            # TypeScript interfaces
│   └── utils/
│       └── cn.ts               # Utility functions
├── public/                     # Static assets
├── package.json                # Dependencies
├── tsconfig.json               # TypeScript config
├── next.config.ts              # Next.js config
└── tailwind.config.js          # Tailwind config
```

### Data Flow Architecture

```
User Action
    ↓
React Component (UI)
    ↓
Event Handler
    ↓
┌─────────────────────────────────┐
│  TanStack Query Mutation/Query  │ ← Server State
└─────────────────────────────────┘
    ↓
API Service (axios)
    ↓
HTTP Request → FastAPI Backend
    ↓
Response ← FastAPI Backend
    ↓
┌─────────────────────────────────┐
│  Query Cache Update             │ ← Auto re-render
└─────────────────────────────────┘
    ↓
UI Re-renders with New Data
```

---

## 4. Core Concepts

### 4.1 Next.js App Router

**What it is:** File-system based routing where folders = routes

**How it works:**

```
app/
├── page.tsx           → /
├── login/
│   └── page.tsx       → /login
└── todos/
    └── page.tsx       → /todos
```

**Key Files:**

- `layout.tsx` - Wraps all pages (persistent UI)
- `page.tsx` - Actual page content
- `providers.tsx` - Context providers

### 4.2 Client vs Server Components

**Server Components (default):**

- Render on server
- Can't use hooks or browser APIs
- Better performance

**Client Components (`'use client'`):**

- Render in browser
- Can use hooks (useState, useEffect)
- Interactive features

**This app uses:** Client components (all pages have `'use client'`)

### 4.3 State Management Strategy

**Two types of state:**

1. **Client State** (Zustand)
   
   - User authentication
   - UI preferences
   - Persisted to localStorage

2. **Server State** (TanStack Query)
   
   - Todo data from API
   - Cached automatically
   - Auto-refetch on mutations

### 4.4 TypeScript Benefits

**Type Safety:**

```typescript
interface Todo {
  id: number;
  title: string;
  done: boolean;
  ddl: string;
  owner_id: number;
}
```

**Autocomplete & Error Prevention:**

- IDE knows what properties exist
- Catches errors before runtime
- Self-documenting code

---

## 5. Deep Dive: Code Analysis

### 5.1 Entry Point: Root Layout

**File:** `@/Users/Mac/code/project/FastAPI/frontend/src/app/layout.tsx`

```typescript
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

**What happens:**

1. Defines HTML structure for entire app
2. Loads Inter font from Google Fonts
3. Wraps children in `<Providers>` for React Query
4. Applies global CSS classes

**Key Concepts:**

- **Layout composition** - Nested layouts
- **Font optimization** - Next.js auto-optimizes fonts
- **CSS variables** - `inter.variable` creates CSS custom property

---

### 5.2 Providers Setup

**File:** `@/Users/Mac/code/project/FastAPI/frontend/src/app/providers.tsx`

```typescript
export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () => new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: 60 * 1000,        // Data fresh for 60s
          refetchOnWindowFocus: false,  // Don't refetch on tab switch
        },
      },
    })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

**What it does:**

- Creates React Query client with configuration
- Wraps app to enable data fetching hooks

**Key Concepts:**

- **staleTime** - How long data is considered fresh
- **refetchOnWindowFocus** - Auto-refetch behavior
- **Provider pattern** - Context for child components

---

### 5.3 API Service Layer

**File:** `@/Users/Mac/code/project/FastAPI/frontend/src/services/api.ts`

```typescript
// Create axios instance
export const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Add JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**What it does:**

1. Creates reusable HTTP client
2. Automatically adds auth token to requests
3. Organizes API calls by feature

**Key Concepts:**

- **Axios interceptors** - Modify requests/responses globally
- **Bearer token** - JWT authentication standard
- **API organization** - Group related endpoints

**API Structure:**

```typescript
export const authAPI = {
  register: (email, password) => POST /api/v1/auth/register
  login: (email, password) => POST /api/v1/auth/login
  getCurrentUser: () => GET /api/v1/auth/me
}

export const todoAPI = {
  getTodos: (params) => GET /api/v1/todos
  createTodo: (data) => POST /api/v1/todos
  updateTodo: (id, data) => PUT /api/v1/todos/:id
  deleteTodo: (id) => DELETE /api/v1/todos/:id
}
```

---

### 5.4 Authentication Store

**File:** `@/Users/Mac/code/project/FastAPI/frontend/src/store/authStore.ts`

```typescript
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      setAuth: (user, token) => {
        localStorage.setItem('token', token);
        set({ user, token, isAuthenticated: true });
      },

      logout: () => {
        localStorage.removeItem('token');
        set({ user: null, token: null, isAuthenticated: false });
      },
    }),
    { name: 'auth-storage' }  // Persist to localStorage
  )
);
```

**What it does:**

- Global authentication state
- Persists to localStorage (survives page refresh)
- Simple API: `setAuth()`, `logout()`

**Usage in components:**

```typescript
const { user, isAuthenticated, logout } = useAuthStore();
```

**Key Concepts:**

- **Zustand** - Minimal boilerplate state management
- **Persist middleware** - Auto-save to localStorage
- **Selectors** - Only re-render when selected state changes

---

### 5.5 Login Page Deep Dive

**File:** `@/Users/Mac/code/project/FastAPI/frontend/src/app/login/page.tsx`

#### Component Structure

```typescript
export default function LoginPage() {
  // 1. Hooks
  const router = useRouter();                    // Navigation
  const setAuth = useAuthStore((state) => state.setAuth);  // Auth state
  const [email, setEmail] = useState('');        // Form state
  const [password, setPassword] = useState('');

  // 2. Mutation (API call)
  const loginMutation = useMutation({
    mutationFn: () => authAPI.login(email, password),
    onSuccess: async (data) => {
      localStorage.setItem('token', data.access_token);
      const user = await authAPI.getCurrentUser();
      setAuth(user, data.access_token);
      router.push('/todos');
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || 'Login failed');
    },
  });

  // 3. Event handler
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loginMutation.mutate();
  };

  // 4. JSX (UI)
  return (/* ... */);
}
```

#### Flow Breakdown

**Step 1: User fills form**

```typescript
<Input
  value={email}
  onChange={(e) => setEmail(e.target.value)}
/>
```

- Controlled input (React manages value)
- `onChange` updates state on every keystroke

**Step 2: User submits**

```typescript
<form onSubmit={handleSubmit}>
```

- `handleSubmit` prevents default form submission
- Triggers mutation

**Step 3: API call**

```typescript
mutationFn: () => authAPI.login(email, password)
```

- Calls backend `/api/v1/auth/login`
- Returns `{ access_token, token_type }`

**Step 4: Success handling**

```typescript
onSuccess: async (data) => {
  localStorage.setItem('token', data.access_token);  // Save token
  const user = await authAPI.getCurrentUser();       // Get user info
  setAuth(user, data.access_token);                  // Update store
  router.push('/todos');                             // Navigate
}
```

**Step 5: UI feedback**

```typescript
<Button disabled={loginMutation.isPending}>
  {loginMutation.isPending ? 'Logging in...' : 'Login'}
</Button>
```

- Shows loading state during API call
- Disables button to prevent double-submit

---

### 5.6 Todos Page Deep Dive

**File:** `@/Users/Mac/code/project/FastAPI/frontend/src/app/todos/page.tsx`

#### Data Fetching

```typescript
const { data: todosData, isLoading } = useQuery({
  queryKey: ['todos'],
  queryFn: () => todoAPI.getTodos(),
  enabled: isAuthenticated,
});
```

**Key Concepts:**

- **queryKey** - Unique identifier for cache
- **queryFn** - Function that fetches data
- **enabled** - Only fetch if authenticated
- **Auto-refetch** - Refetches on window focus, reconnect

#### Mutations (Create/Update/Delete)

**Create Todo:**

```typescript
const createMutation = useMutation({
  mutationFn: (title: string) => todoAPI.createTodo({ title }),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['todos'] });  // Refetch
    setNewTodoTitle('');  // Clear input
  },
});
```

**Update Todo (Toggle Done):**

```typescript
const updateMutation = useMutation({
  mutationFn: ({ id, done }: { id: number; done: boolean }) =>
    todoAPI.updateTodo(id, { done }),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['todos'] });
  },
});
```

**Delete Todo:**

```typescript
const deleteMutation = useMutation({
  mutationFn: (id: number) => todoAPI.deleteTodo(id),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['todos'] });
  },
});
```

**Pattern:**

1. Define mutation function
2. On success, invalidate query cache
3. React Query auto-refetches
4. UI updates automatically

#### Rendering Logic

**Loading State:**

```typescript
{isLoading ? (
  <Card>Loading todos...</Card>
) : /* ... */}
```

**Empty State:**

```typescript
{todosData?.items?.length === 0 ? (
  <Card>No todos yet. Create one above!</Card>
) : /* ... */}
```

**Todo List:**

```typescript
{todosData?.items?.map((todo: Todo) => (
  <Card key={todo.id}>
    <Button onClick={() => updateMutation.mutate({ id: todo.id, done: !todo.done })}>
      {todo.done ? <Check /> : <X />}
    </Button>
    <p className={todo.done ? 'line-through' : ''}>{todo.title}</p>
    <Button onClick={() => deleteMutation.mutate(todo.id)}>
      <Trash2 />
    </Button>
  </Card>
))}
```

**Key Concepts:**

- **Conditional rendering** - Show different UI based on state
- **List rendering** - `.map()` to render arrays
- **Key prop** - React optimization for lists
- **Inline handlers** - Pass data to mutations

---

### 5.7 UI Components (shadcn/ui)

#### Button Component

**File:** `@/Users/Mac/code/project/FastAPI/frontend/src/components/ui/button.tsx`

```typescript
const buttonVariants = cva(
  "base-classes",  // Always applied
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground",
        destructive: "bg-destructive text-destructive-foreground",
        outline: "border border-input bg-background",
        ghost: "hover:bg-accent",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 px-3",
        lg: "h-11 px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);
```

**Usage:**

```typescript
<Button variant="destructive" size="sm">Delete</Button>
<Button variant="outline">Cancel</Button>
<Button size="icon"><Plus /></Button>
```

**Key Concepts:**

- **CVA (Class Variance Authority)** - Type-safe variant management
- **Composition** - Combine base + variant classes
- **TypeScript inference** - Autocomplete for variants

#### Card Component

**File:** `@/Users/Mac/code/project/FastAPI/frontend/src/components/ui/card.tsx`

```typescript
const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("rounded-lg border bg-card text-card-foreground shadow-sm", className)}
      {...props}
    />
  )
);
```

**Composition Pattern:**

```typescript
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>Content here</CardContent>
  <CardFooter>Footer</CardFooter>
</Card>
```

**Key Concepts:**

- **forwardRef** - Pass refs to child components
- **Spread props** - Forward all HTML attributes
- **cn utility** - Merge Tailwind classes intelligently

---

### 5.8 Utility Functions

#### cn (Class Names)

**File:** `@/Users/Mac/code/project/FastAPI/frontend/src/utils/cn.ts`

```typescript
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

**What it does:**

1. **clsx** - Conditionally join classNames
2. **twMerge** - Merge Tailwind classes (handles conflicts)

**Usage:**

```typescript
cn("text-base", isActive && "font-bold", className)
// Output: "text-base font-bold custom-class"

cn("p-4", "p-6")  // twMerge resolves conflict
// Output: "p-6" (not "p-4 p-6")
```

---

## 6. Knowledge Breakdown

### 6.1 React Fundamentals

#### Hooks Used in This Project

**useState** - Local component state

```typescript
const [email, setEmail] = useState('');
setEmail('new@email.com');  // Update state
```

**useEffect** - Side effects (redirects, subscriptions)

```typescript
useEffect(() => {
  if (!isAuthenticated) {
    router.push('/login');
  }
}, [isAuthenticated, router]);  // Dependencies
```

**Custom Hooks** - Reusable logic

```typescript
const { user, logout } = useAuthStore();  // Zustand hook
const { data, isLoading } = useQuery({ ... });  // React Query hook
```

#### Component Patterns

**Controlled Components:**

```typescript
<Input
  value={email}
  onChange={(e) => setEmail(e.target.value)}
/>
```

- React controls input value
- Single source of truth

**Conditional Rendering:**

```typescript
{isLoading ? <Spinner /> : <Content />}
{error && <ErrorMessage />}
{items.map(item => <Item key={item.id} />)}
```

**Event Handling:**

```typescript
const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault();  // Stop default form behavior
  // Custom logic
};
```

---

### 6.2 Next.js Specific

#### App Router Concepts

**File-based Routing:**

- `app/page.tsx` → `/`
- `app/login/page.tsx` → `/login`
- `app/todos/page.tsx` → `/todos`

**Layouts:**

- Shared UI across routes
- Nested layouts possible
- Preserves state on navigation

**Navigation:**

```typescript
import { useRouter } from 'next/navigation';
const router = useRouter();
router.push('/todos');  // Client-side navigation
```

**Link Component:**

```typescript
import Link from 'next/link';
<Link href="/register">Register</Link>
```

- Prefetches on hover
- Client-side navigation
- Better than `<a>` tags

#### Metadata:**

```typescript
export const metadata: Metadata = {
  title: "Todo App",
  description: "A modern todo application",
};
```

---

### 6.3 TypeScript Essentials

#### Interfaces

```typescript
interface User {
  id: number;
  email: string;
}

interface Todo {
  id: number;
  title: string;
  done: boolean;
  ddl: string;
  owner_id: number;
}
```

#### Type Annotations

```typescript
const [email, setEmail] = useState<string>('');
const user: User | null = null;
const handleClick = (id: number): void => { ... };
```

#### Generic Types

```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  setAuth: (user: User, token: string) => void;
}
```

---

### 6.4 TanStack Query (React Query)

#### Core Concepts

**Queries** - Fetch data

```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['todos'],           // Cache key
  queryFn: () => todoAPI.getTodos(),  // Fetch function
  staleTime: 60000,              // Fresh for 60s
  enabled: isAuthenticated,      // Conditional fetch
});
```

**Mutations** - Modify data

```typescript
const mutation = useMutation({
  mutationFn: (newTodo) => todoAPI.createTodo(newTodo),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['todos'] });
  },
  onError: (error) => {
    console.error(error);
  },
});

mutation.mutate({ title: 'New Todo' });
```

**Query Invalidation** - Refetch data

```typescript
queryClient.invalidateQueries({ queryKey: ['todos'] });
```

**Benefits:**

- Automatic caching
- Background refetching
- Deduplication
- Loading/error states
- Optimistic updates

---

### 6.5 Zustand State Management

#### Store Creation

```typescript
const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,

      // Actions
      setAuth: (user, token) => set({ user, token }),
      logout: () => set({ user: null, token: null }),
    }),
    { name: 'auth-storage' }  // localStorage key
  )
);
```

#### Usage in Components

```typescript
// Select specific state
const user = useAuthStore((state) => state.user);
const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

// Select multiple
const { user, logout } = useAuthStore();

// Call actions
const setAuth = useAuthStore((state) => state.setAuth);
setAuth(userData, token);
```

**Why Zustand?**

- Minimal boilerplate
- No providers needed
- TypeScript-first
- Middleware support (persist)

---

### 6.6 Tailwind CSS

#### Utility-First Approach

```typescript
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-md">
```

**Breakdown:**

- `flex` - display: flex
- `items-center` - align-items: center
- `justify-between` - justify-content: space-between
- `p-4` - padding: 1rem
- `bg-white` - background-color: white
- `rounded-lg` - border-radius: 0.5rem
- `shadow-md` - box-shadow: medium

#### Responsive Design

```typescript
<div className="w-full md:w-1/2 lg:w-1/3">
```

- `w-full` - width: 100% (mobile)
- `md:w-1/2` - width: 50% (tablet+)
- `lg:w-1/3` - width: 33.33% (desktop+)

#### Dark Mode

```typescript
<div className="bg-white dark:bg-slate-900">
```

#### Custom CSS Variables

```css
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
}
```

**Usage:**

```typescript
<div className="bg-background text-foreground">
```

---

### 6.7 Axios & HTTP

#### Instance Creation

```typescript
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});
```

#### Interceptors

```typescript
// Request interceptor (add auth token)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (handle errors globally)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
    }
    return Promise.reject(error);
  }
);
```

#### API Methods

```typescript
// GET
const response = await api.get('/api/v1/todos', { params: { limit: 10 } });

// POST
const response = await api.post('/api/v1/todos', { title: 'New Todo' });

// PUT
const response = await api.put('/api/v1/todos/1', { done: true });

// DELETE
const response = await api.delete('/api/v1/todos/1');
```

---

## 7. Learning Path

### Phase 1: Foundations (Beginner)

**Week 1-2: JavaScript/TypeScript Basics**

- [ ] Variables, functions, arrays, objects
- [ ] Promises, async/await
- [ ] ES6+ features (destructuring, spread, arrow functions)
- [ ] TypeScript basics (types, interfaces)

**Week 3-4: React Fundamentals**

- [ ] JSX syntax
- [ ] Components (functional)
- [ ] Props and state
- [ ] Hooks (useState, useEffect)
- [ ] Event handling
- [ ] Conditional rendering
- [ ] Lists and keys

**Practice Project:** Build a simple counter app with React

---

### Phase 2: Intermediate (Building Skills)

**Week 5-6: Next.js Basics**

- [ ] App Router vs Pages Router
- [ ] File-based routing
- [ ] Layouts and nested routes
- [ ] Client vs Server Components
- [ ] Navigation (Link, useRouter)
- [ ] Image optimization

**Week 7-8: State Management**

- [ ] Context API
- [ ] Zustand basics
- [ ] When to use global vs local state
- [ ] Persist middleware

**Week 9-10: Data Fetching**

- [ ] Fetch API
- [ ] Axios basics
- [ ] TanStack Query (useQuery, useMutation)
- [ ] Cache management
- [ ] Loading and error states

**Practice Project:** Build a weather app with API integration

---

### Phase 3: Advanced (Production Ready)

**Week 11-12: Styling**

- [ ] Tailwind CSS fundamentals
- [ ] Responsive design
- [ ] Dark mode
- [ ] Component libraries (shadcn/ui)
- [ ] CSS-in-JS vs utility-first

**Week 13-14: Forms & Validation**

- [ ] Controlled vs uncontrolled inputs
- [ ] Form libraries (React Hook Form)
- [ ] Validation (Zod, Yup)
- [ ] Error handling

**Week 15-16: Authentication**

- [ ] JWT basics
- [ ] Login/register flows
- [ ] Protected routes
- [ ] Token refresh
- [ ] Secure storage

**Practice Project:** Build this todo app from scratch

---

### Phase 4: Expert (Optimization & Best Practices)

**Week 17-18: Performance**

- [ ] React.memo, useMemo, useCallback
- [ ] Code splitting
- [ ] Lazy loading
- [ ] Image optimization
- [ ] Bundle analysis

**Week 19-20: Testing**

- [ ] Jest basics
- [ ] React Testing Library
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests (Playwright)

**Week 21-22: Deployment**

- [ ] Environment variables
- [ ] Build optimization
- [ ] Vercel deployment
- [ ] CI/CD basics
- [ ] Monitoring and analytics

**Final Project:** Deploy a full-stack application

---

## Key Takeaways

### Architecture Patterns

1. **Separation of Concerns** - API, state, UI separated
2. **Component Composition** - Small, reusable components
3. **Type Safety** - TypeScript prevents runtime errors
4. **Declarative UI** - Describe what, not how

### Best Practices

1. **Use TypeScript** - Catch errors early
2. **Server State ≠ Client State** - Use right tool for each
3. **Optimize Renders** - Only re-render when needed
4. **Error Handling** - Always handle loading/error states
5. **Accessibility** - Use semantic HTML, ARIA labels

### Common Pitfalls to Avoid

1. ❌ Prop drilling (use context/state management)
2. ❌ Fetching in useEffect (use React Query)
3. ❌ Inline object/function definitions in JSX (causes re-renders)
4. ❌ Missing keys in lists
5. ❌ Not handling loading/error states

---

## Next Steps

1. **Read the code** - Start with `layout.tsx`, then `login/page.tsx`
2. **Run the app** - `npm install && npm run dev`
3. **Make changes** - Modify UI, add features
4. **Break things** - Best way to learn
5. **Build your own** - Apply concepts to new project

---

## Resources

### Official Docs

- [React](https://react.dev)
- [Next.js](https://nextjs.org/docs)
- [TypeScript](https://www.typescriptlang.org/docs)
- [TanStack Query](https://tanstack.com/query)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com)

### Learning Platforms

- [Frontend Masters](https://frontendmasters.com)
- [Egghead.io](https://egghead.io)
- [React.gg](https://react.gg)

### Community

- [Next.js Discord](https://nextjs.org/discord)
- [Reactiflux Discord](https://www.reactiflux.com)
- [r/reactjs](https://reddit.com/r/reactjs)

---

**Happy Learning! 🚀**
