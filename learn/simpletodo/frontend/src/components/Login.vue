<template>
  <div class="login-container">
    <div class="login-box">
      <h1>{{ isRegister ? '注册' : '登录' }}</h1>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>邮箱</label>
          <input
            type="email"
            v-model="email"
            required
            placeholder="your@email.com"
          />
        </div>

        <div class="form-group">
          <label>密码</label>
          <input
            type="password"
            v-model="password"
            required
            placeholder="••••••••"
          />
        </div>

        <div class="form-group" v-if="isRegister">
          <label>确认密码</label>
          <input
            type="password"
            v-model="confirmPassword"
            required
            placeholder="••••••••"
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div v-if="success" class="success-message">
          {{ success }}
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? '处理中...' : (isRegister ? '注册' : '登录') }}
        </button>
      </form>

      <div class="toggle">
        {{ isRegister ? '已有账号？' : '没有账号？' }}
        <button @click="toggleMode" class="link-btn">
          {{ isRegister ? '登录' : '注册' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { api } from '../api.js';
import { useRouter } from 'vue-router';

const router = useRouter();
const isRegister = ref(false);
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const loading = ref(false);
const error = ref('');
const success = ref('');

function toggleMode() {
  isRegister.value = !isRegister.value;
  error.value = '';
  success.value = '';
}

async function handleSubmit() {
  loading.value = true;
  error.value = '';
  success.value = '';

  try {
    if (isRegister.value) {
      if (password.value !== confirmPassword.value) {
        error.value = '两次密码不一致';
        loading.value = false;
        return;
      }
      await api.register(email.value, password.value);
      success.value = '注册成功！请登录';
      isRegister.value = false;
      password.value = '';
      confirmPassword.value = '';
    } else {
      await api.login(email.value, password.value);
      router.push('/');
    }
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-box {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 28px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #667eea;
}

button[type="submit"] {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, opacity 0.2s;
  margin-top: 10px;
}

button[type="submit"]:hover:not(:disabled) {
  transform: translateY(-2px);
  opacity: 0.9;
}

button[type="submit"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.link-btn {
  background: none;
  border: none;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  font-size: 14px;
}

.link-btn:hover {
  text-decoration: underline;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 15px;
  border: 1px solid #fcc;
}

.success-message {
  background: #efe;
  color: #3c3;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 15px;
  border: 1px solid #cfc;
}
</style>
