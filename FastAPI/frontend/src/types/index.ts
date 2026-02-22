export interface User {
  id: number;
  email: string;
}

export interface Todo {
  id: number;
  title: string;
  done: boolean;
  ddl: string;
  owner_id: number;
}

export interface TodoListResponse {
  total: number;
  skip: number;
  limit: number;
  page: number;
  pages: number;
  items: Todo[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}
