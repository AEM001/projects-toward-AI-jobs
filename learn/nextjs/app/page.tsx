'use client';

import { useEffect, useState } from 'react';
import { Todo, CreateTodoRequest } from './api/todos/route';

export default function Home(): React.ReactElement {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTodo, setNewTodo] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  // Fetch todos on page load
  useEffect(() => {
    fetchTodos();
  }, []);

  async function fetchTodos(): Promise<void> {
    try {
      const response = await fetch('/api/todos');
      const data: Todo[] = await response.json();
      setTodos(data);
    } catch (error) {
      console.error('Failed to fetch todos:', error);
    } finally {
      setLoading(false);
    }
  }

  async function addTodo(e: React.FormEvent): Promise<void> {
    e.preventDefault();
    if (!newTodo.trim()) return;

    const request: CreateTodoRequest = { title: newTodo };
    
    try {
      const response = await fetch('/api/todos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      
      if (response.ok) {
        const created: Todo = await response.json();
        setTodos([...todos, created]);
        setNewTodo('');
      }
    } catch (error) {
      console.error('Failed to add todo:', error);
    }
  }

  return (
    <main style={{ maxWidth: '600px', margin: '40px auto', padding: '0 20px' }}>
      <h1>📝 Next.js + TypeScript Todo App</h1>
      
      <form onSubmit={addTodo} style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={newTodo}
          onChange={(e) => setNewTodo(e.target.value)}
          placeholder="Add a new todo..."
          style={{ padding: '8px', width: '300px', marginRight: '8px' }}
        />
        <button type="submit" style={{ padding: '8px 16px' }}>
          Add
        </button>
      </form>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {todos.map((todo) => (
            <li
              key={todo.id}
              style={{
                padding: '12px',
                marginBottom: '8px',
                backgroundColor: todo.completed ? '#e8f5e9' : '#fff3e0',
                borderRadius: '4px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <span>{todo.completed ? '✅' : '⭕'}</span>
              <span style={{ textDecoration: todo.completed ? 'line-through' : 'none' }}>
                {todo.title}
              </span>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
