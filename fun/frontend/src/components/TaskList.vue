<template>
  <div class="task-list-container">
    <div class="header">
      <h1>📋 我的任务</h1>
      <button @click="logout" class="logout-btn">退出登录</button>
    </div>

    <!-- 创建任务表单 -->
    <div class="create-form">
      <input
        v-model="newTaskTitle"
        type="text"
        placeholder="任务标题..."
        @keyup.enter="createTask"
      />
      <input
        v-model="newTaskDescription"
        type="text"
        placeholder="任务描述（可选）..."
        @keyup.enter="createTask"
      />
      <button @click="createTask" :disabled="!newTaskTitle.trim()">
        添加任务
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      加载中...
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error">
      {{ error }}
    </div>

    <!-- 任务列表 -->
    <div v-if="!loading && tasks.length > 0" class="tasks">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="task-item"
        :class="task.status"
      >
        <div class="task-content">
          <div class="task-title">
            <span class="status-badge" :class="task.status">
              {{ getStatusLabel(task.status) }}
            </span>
            {{ task.title }}
          </div>
          <div v-if="task.description" class="task-description">
            {{ task.description }}
          </div>
          <div class="task-time">
            {{ formatDate(task.created_at) }}
          </div>
        </div>

        <div class="task-actions">
          <!-- 状态切换 -->
          <select
            v-model="task.status"
            @change="updateTaskStatus(task)"
            class="status-select"
          >
            <option value="pending">待办</option>
            <option value="in_progress">进行中</option>
            <option value="completed">已完成</option>
          </select>

          <!-- 删除按钮 -->
          <button @click="deleteTask(task.id)" class="delete-btn">
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && tasks.length === 0" class="empty-state">
      <div class="empty-icon">📝</div>
      <p>还没有任务，添加一个吧！</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../api.js';

const router = useRouter();
const tasks = ref([]);
const loading = ref(false);
const error = ref('');
const newTaskTitle = ref('');
const newTaskDescription = ref('');

// 加载任务列表
async function loadTasks() {
  loading.value = true;
  error.value = '';
  try {
    tasks.value = await api.getTasks();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

// 创建任务
async function createTask() {
  if (!newTaskTitle.value.trim()) return;

  try {
    const task = await api.createTask(
      newTaskTitle.value.trim(),
      newTaskDescription.value.trim()
    );
    tasks.value.unshift(task); // 添加到列表顶部
    newTaskTitle.value = '';
    newTaskDescription.value = '';
  } catch (err) {
    error.value = err.message;
  }
}

// 更新任务状态
async function updateTaskStatus(task) {
  try {
    await api.updateTask(task.id, { status: task.status });
  } catch (err) {
    error.value = err.message;
    // 恢复原状态
    await loadTasks();
  }
}

// 删除任务
async function deleteTask(taskId) {
  if (!confirm('确定要删除这个任务吗？')) return;

  try {
    await api.deleteTask(taskId);
    tasks.value = tasks.value.filter(t => t.id !== taskId);
  } catch (err) {
    error.value = err.message;
  }
}

// 退出登录
function logout() {
  api.clearToken();
  router.push('/login');
}

// 工具函数
function getStatusLabel(status) {
  const labels = {
    pending: '待办',
    in_progress: '进行中',
    completed: '已完成',
  };
  return labels[status] || status;
}

function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// 页面加载时获取任务
onMounted(() => {
  loadTasks();
});
</script>

<style scoped>
.task-list-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h1 {
  color: #333;
  font-size: 32px;
}

.logout-btn {
  padding: 8px 16px;
  background: #ff4757;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.logout-btn:hover {
  background: #ee5a6f;
}

/* 创建表单 */
.create-form {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.create-form input {
  flex: 1;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
}

.create-form input:focus {
  outline: none;
  border-color: #667eea;
}

.create-form button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.create-form button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 状态和错误提示 */
.loading, .error {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 12px;
  margin-bottom: 20px;
}

.error {
  background: #fee;
  color: #c33;
  border: 1px solid #fcc;
}

/* 任务列表 */
.tasks {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  transition: transform 0.2s, box-shadow 0.2s;
}

.task-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.task-item.completed {
  opacity: 0.7;
  background: #f8f9fa;
}

.task-item.in_progress {
  border-left: 4px solid #ffa502;
}

.task-item.pending {
  border-left: 4px solid #667eea;
}

.task-item.completed {
  border-left: 4px solid #2ed573;
}

.task-content {
  flex: 1;
}

.task-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.task-description {
  color: #666;
  margin-bottom: 8px;
  font-size: 14px;
}

.task-time {
  color: #999;
  font-size: 12px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.status-badge.pending {
  background: #667eea;
}

.status-badge.in_progress {
  background: #ffa502;
}

.status-badge.completed {
  background: #2ed573;
}

/* 任务操作 */
.task-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.status-select {
  padding: 8px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  background: white;
}

.status-select:focus {
  outline: none;
  border-color: #667eea;
}

.delete-btn {
  padding: 8px 16px;
  background: #ff4757;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.delete-btn:hover {
  background: #ee5a6f;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  color: #999;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 16px;
}

/* 响应式 */
@media (max-width: 768px) {
  .create-form {
    flex-direction: column;
  }

  .task-item {
    flex-direction: column;
    gap: 15px;
  }

  .task-actions {
    width: 100%;
    justify-content: space-between;
  }

  .header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
}
</style>
