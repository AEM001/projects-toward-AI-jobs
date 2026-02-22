'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { todoAPI } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LogOut, Plus, Trash2, Check, X } from 'lucide-react';
import type { Todo } from '@/types';

export default function TodosPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, logout, isAuthenticated } = useAuthStore();
  const [newTodoTitle, setNewTodoTitle] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  const { data: todosData, isLoading } = useQuery({
    queryKey: ['todos'],
    queryFn: () => todoAPI.getTodos(),
    enabled: isAuthenticated,
  });

  const createMutation = useMutation({
    mutationFn: (title: string) => todoAPI.createTodo({ title }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
      setNewTodoTitle('');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, done }: { id: number; done: boolean }) =>
      todoAPI.updateTodo(id, { done }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => todoAPI.deleteTodo(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });

  const handleCreateTodo = (e: React.FormEvent) => {
    e.preventDefault();
    if (newTodoTitle.trim()) {
      createMutation.mutate(newTodoTitle);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto max-w-4xl p-4 py-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">My Todos</h1>
            <p className="text-sm text-muted-foreground">Welcome, {user?.email}</p>
          </div>
          <Button variant="outline" onClick={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </div>

        {/* Create Todo Form */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <form onSubmit={handleCreateTodo} className="flex gap-2">
              <Input
                placeholder="What needs to be done?"
                value={newTodoTitle}
                onChange={(e) => setNewTodoTitle(e.target.value)}
                className="flex-1"
              />
              <Button type="submit" disabled={createMutation.isPending}>
                <Plus className="mr-2 h-4 w-4" />
                Add
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Todos List */}
        <div className="space-y-3">
          {isLoading ? (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                Loading todos...
              </CardContent>
            </Card>
          ) : todosData?.items?.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                No todos yet. Create one above!
              </CardContent>
            </Card>
          ) : (
            todosData?.items?.map((todo: Todo) => (
              <Card key={todo.id} className="transition-all hover:shadow-md">
                <CardContent className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-3 flex-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() =>
                        updateMutation.mutate({ id: todo.id, done: !todo.done })
                      }
                      className="h-8 w-8"
                    >
                      {todo.done ? (
                        <Check className="h-5 w-5 text-green-600" />
                      ) : (
                        <X className="h-5 w-5 text-gray-400" />
                      )}
                    </Button>
                    <div className="flex-1">
                      <p
                        className={`text-base ${
                          todo.done
                            ? 'text-muted-foreground line-through'
                            : 'text-foreground'
                        }`}
                      >
                        {todo.title}
                      </p>
                      {todo.ddl && (
                        <p className="text-xs text-muted-foreground">
                          Due: {todo.ddl}
                        </p>
                      )}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => deleteMutation.mutate(todo.id)}
                    className="h-8 w-8 text-destructive hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Stats */}
        {todosData?.items && todosData.items.length > 0 && (
          <Card className="mt-6">
            <CardContent className="py-4">
              <div className="flex justify-around text-center">
                <div>
                  <p className="text-2xl font-bold">{todosData.total}</p>
                  <p className="text-xs text-muted-foreground">Total</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-green-600">
                    {todosData.items.filter((t: Todo) => t.done).length}
                  </p>
                  <p className="text-xs text-muted-foreground">Completed</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-orange-600">
                    {todosData.items.filter((t: Todo) => !t.done).length}
                  </p>
                  <p className="text-xs text-muted-foreground">Pending</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
