import { createRouter, createWebHistory } from 'vue-router';
import { api } from './api.js';

// 页面组件（动态导入）
const Login = () => import('./components/Login.vue');
const TaskList = () => import('./components/TaskList.vue');

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true },
  },
  {
    path: '/',
    name: 'TaskList',
    component: TaskList,
    meta: { requiresAuth: true },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = api.isLoggedIn();

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  } else if (to.meta.requiresGuest && isAuthenticated) {
    next('/');
  } else {
    next();
  }
});

export default router;
