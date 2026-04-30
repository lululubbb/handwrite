/**
 * API请求封装
 * 统一处理HTTP请求
 */

import axios from 'axios'

// 创建axios实例
const service = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 添加token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // 统一错误处理
    if (error.response) {
      const status = error.response.status
      switch (status) {
        case 400:
          // 请求参数错误
          console.error('请求参数错误:', error.response.data?.message)
          break
        case 401:
          // 未授权，跳转登录
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
        case 403:
          // 禁止访问
          console.error('禁止访问')
          break
        case 404:
          // 接口不存在
          console.error('接口不存在')
          break
        case 500:
          // 服务器错误
          console.error('服务器错误')
          break
      }
    }
    return Promise.reject(error)
  }
)

export default service
