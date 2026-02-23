





Found the problem - there are TWO [app](cci:9://file:///Users/Mac/code/project/learn/nextjs/app:0:0-0:0) directories:
- [app/](cci:9://file:///Users/Mac/code/project/learn/nextjs/app:0:0-0:0) (original, with layout.tsx)
- `src/app/` (where I mistakenly created files)

Next.js can only use one. I'll fix this by moving everything to the root [app/](cci:9://file:///Users/Mac/code/project/learn/nextjs/app:0:0-0:0) directory.

The project already has a root [app/](cci:9://file:///Users/Mac/code/project/learn/nextjs/app:0:0-0:0) directory. I'll move my API route there, consolidate the types, and update the existing page.tsx with the todo app code.









Fixed! The duplicate `src/app` directory is removed. Now here's how everything works together:

## File Structure (Single [app/](cci:9://file:///Users/Mac/code/project/learn/nextjs/app:0:0-0:0) Directory)

```
learn/nextjs/
├── app/
│   ├── layout.tsx          # Root layout (wraps all pages)
│   ├── page.tsx            # Home page (todo app UI)
│   ├── globals.css         # Global styles
│   └── api/todos/
│       └── route.ts        # Backend API (GET/POST)
├── public/                 # Static files
├── package.json            # Dependencies
└── next.config.ts          # Next.js config
```

## How Files Connect (Execution Flow)

**1. Browser Request:**
```
Browser → http://localhost:3000
```

**2. Next.js Routing:**
```
GET /          →  app/page.tsx    (renders the todo UI)
GET /api/todos →  app/api/todos/route.ts  (API endpoint)
```

**3. Data Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│  Browser                                                    │
│  ┌──────────────────┐     ┌─────────────────────────────┐ │
│  │  User types      │────→│  page.tsx                   │ │
│  │  "Buy milk"      │     │  • React component            │ │
│  │  clicks Add      │     │  • Handles form submit        │ │
│  └──────────────────┘     │  • Calls fetch('/api/todos')  │ │
│         ↑                 └─────────────────────────────┘ │
│         │                            │                      │
│         │                            ↓ POST /api/todos      │
│  ┌──────────────────┐     ┌─────────────────────────────┐ │
│  │  UI updates      │←────│  route.ts                   │ │
│  │  shows new todo  │     │  • GET: returns todo[]      │ │
│  └──────────────────┘     │  • POST: creates new todo     │ │
│                           │  • In-memory array storage    │ │
│                           └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Key Logic in Each File

**[app/page.tsx](cci:7://file:///Users/Mac/code/project/nextjs/app/page.tsx:0:0-0:0)** - Frontend Component:
- `useEffect()` → calls [fetchTodos()](cci:1://file:///Users/Mac/code/project/learn/nextjs/app/page.tsx:15:2-25:3) on page load
- `fetch('/api/todos')` → GET request to backend
- [addTodo()](cci:1://file:///Users/Mac/code/project/learn/nextjs/app/page.tsx:27:2-48:3) → POST new todo to backend
- `setTodos([...todos, created])` → Update React state, triggers re-render

**[app/api/todos/route.ts](cci:7://file:///Users/Mac/code/project/learn/nextjs/app/api/todos/route.ts:0:0-0:0)** - Backend API:
- `let todos: Todo[] = [...]` → In-memory data store
- [GET()](cci:1://file:///Users/Mac/code/project/learn/nextjs/app/api/todos/route.ts:21:0-24:1) → Returns the todos array as JSON
- [POST()](cci:1://file:///Users/Mac/code/project/learn/nextjs/src/app/api/todos/route.ts:15:0-28:1) → Creates new todo, pushes to array, returns it

**[app/layout.tsx](cci:7://file:///Users/Mac/code/project/learn/nextjs/app/layout.tsx:0:0-0:0)** - Root Wrapper:
- Wraps ALL pages (including page.tsx)
- Provides common HTML structure (`<html>`, `<body>`)
- Loads fonts and global CSS

## Request Lifecycle

```
1. User opens localhost:3000
2. Next.js renders app/layout.tsx
   └─ layout.tsx renders {children} → page.tsx
3. page.tsx mounts, useEffect triggers
4. fetch('/api/todos') sends request
5. Next.js matches URL to app/api/todos/route.ts
6. route.ts GET() returns JSON
7. page.tsx receives data, setTodos() updates state
8. React re-renders, displays todo list

When user adds a todo:
1. Form submit → addTodo() function
2. fetch('/api/todos', {method: 'POST'})
3. route.ts POST() creates todo, saves to array
4. Returns new todo
5. page.tsx adds to state, UI updates
```