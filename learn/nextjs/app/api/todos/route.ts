import { NextRequest, NextResponse } from 'next/server';

// TypeScript interfaces
export interface Todo {
  id: number;
  title: string;
  completed: boolean;
  createdAt: string;
}

export interface CreateTodoRequest {
  title: string;
}

// Simple in-memory storage (resets on server restart)
let todos: Todo[] = [
  { id: 1, title: 'Learn Next.js', completed: false, createdAt: new Date().toISOString() },
  { id: 2, title: 'Build a todo app', completed: true, createdAt: new Date().toISOString() },
];
let nextId = 3;

// GET /api/todos - List all todos
export async function GET(): Promise<NextResponse> {
  return NextResponse.json(todos);
}

// POST /api/todos - Create a new todo
export async function POST(request: NextRequest): Promise<NextResponse> {
  const body: CreateTodoRequest = await request.json();
  
  const newTodo: Todo = {
    id: nextId++,
    title: body.title,
    completed: false,
    createdAt: new Date().toISOString(),
  };
  
  todos.push(newTodo);
  return NextResponse.json(newTodo, { status: 201 });
}
