import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Todos from './pages/Todos'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route 
            index 
            element={
              isAuthenticated ? <Navigate to="/todos" replace /> : <Navigate to="/login" replace />
            } 
          />
          <Route 
            path="login" 
            element={isAuthenticated ? <Navigate to="/todos" replace /> : <Login />} 
          />
          <Route 
            path="register" 
            element={isAuthenticated ? <Navigate to="/todos" replace /> : <Register />} 
          />
          <Route 
            path="todos" 
            element={isAuthenticated ? <Todos /> : <Navigate to="/login" replace />} 
          />
        </Route>
      </Routes>
    </div>
  )
}

export default App
