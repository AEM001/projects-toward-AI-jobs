// API 配置
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// 获取 token
function getToken() {
    return localStorage.getItem('token');
}

// 设置 token
function setToken(token) {
    localStorage.setItem('token', token);
}

// 清除 token
function clearToken() {
    localStorage.removeItem('token');
}

// 检查是否已登录
function isLoggedIn() {
    return !!getToken();
}

// 通用请求函数
async function request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const token = getToken();

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        clearToken();
        window.location.href = '/login';
        throw new Error('未授权，请重新登录');
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.detail || '请求失败');
    }

    return data;
}

// API 方法
export const api = {
    // 认证
    register: async (email, password) => {
        const data = await request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        return data;
    },

    login: async (email, password) => {
        const data = await request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        if (data.access_token) {
            setToken(data.access_token);
        }
        return data;
    },

    // 任务
    getTasks: async () => {
        return await request('/tasks');
    },

    createTask: async (title, description) => {
        return await request('/tasks', {
            method: 'POST',
            body: JSON.stringify({ title, description }),
        });
    },

    updateTask: async (taskId, updates) => {
        return await request(`/tasks/${taskId}`, {
            method: 'PUT',
            body: JSON.stringify(updates),
        });
    },

    deleteTask: async (taskId) => {
        return await request(`/tasks/${taskId}`, {
            method: 'DELETE',
        });
    },

    // 工具函数
    getToken,
    setToken,
    clearToken,
    isLoggedIn,
};
