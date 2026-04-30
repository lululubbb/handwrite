/**
 * 路由配置
 * 定义系统所有页面路由
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

// 页面组件
const Login = () => import('@/views/Login.vue')
const Register = () => import('@/views/Register.vue')
const Home = () => import('@/views/Home.vue')
const Upload = () => import('@/views/Upload.vue')
const Result = () => import('@/views/Result.vue')
const Profile = () => import('@/views/Profile.vue')
const Statistics = () => import('@/views/Statistics.vue')
const AdminDashboard = () => import('@/views/AdminDashboard.vue')
const AdminUsers = () => import('@/views/AdminUsers.vue')
const AdminRecords = () => import('@/views/AdminRecords.vue')

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/',
    name: 'home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/upload',
    name: 'upload',
    component: Upload,
    meta: { requiresAuth: true }
  },
  {
    path: '/result/:recordId?',
    name: 'result',
    component: Result,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/profile',
    name: 'profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/statistics',
    name: 'statistics',
    component: Statistics,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'adminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'adminUsers',
    component: AdminUsers,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/records',
    name: 'adminRecords',
    component: AdminRecords,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const token = localStorage.getItem('token')
  
  // 检查是否需要登录
  if (to.meta.requiresAuth && !token) {
    return next({ name: 'login' })
  }
  
  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin && userStore.user?.role !== 'admin') {
    return next({ name: 'home' })
  }
  
  // 检查是否已登录（访问登录/注册页面）
  if (to.meta.requiresGuest && token) {
    return next({ name: 'home' })
  }
  
  next()
})

export default router