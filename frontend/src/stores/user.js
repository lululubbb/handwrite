/**
 * 用户状态管理
 * 管理用户登录状态、个人信息等
 */

import { defineStore } from 'pinia'
import axios from 'axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || '',
    isAuthenticated: !!localStorage.getItem('token'),
    loading: false,
    error: null
  }),
  
  actions: {
    // 设置用户信息
    setUser(user) {
      this.user = user
      if (user) {
        this.isAuthenticated = true
      }
    },
    
    // 设置token
    setToken(token) {
      this.token = token
      localStorage.setItem('token', token)
    },
    
    // 清除用户信息
    clearUser() {
      this.user = null
      this.token = ''
      this.isAuthenticated = false
      localStorage.removeItem('token')
    },
    
    // 登录
    async login(username, password) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/user/login', {
          username,
          password
        })
        
        const { data } = response.data
        
        this.setUser(data)
        this.setToken(data.token)
        
        return data
      } catch (error) {
        this.error = error.response?.data?.message || '登录失败'
        throw new Error(this.error)
      } finally {
        this.loading = false
      }
    },
    
    // 注册
    async register(username, email, password) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/user/register', {
          username,
          email,
          password
        })
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || '注册失败'
        throw new Error(this.error)
      } finally {
        this.loading = false
      }
    },
    
    // 获取用户信息
    async getProfile() {
      this.loading = true
      
      try {
        const response = await axios.get('/api/user/profile', {
          headers: {
            'X-User-ID': this.user?.id
          }
        })
        
        this.setUser(response.data.data)
        return response.data.data
      } catch (error) {
        this.error = error.response?.data?.message || '获取用户信息失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 更新用户信息
    async updateProfile(data) {
      try {
        const response = await axios.put('/api/user/profile', data, {
          headers: {
            'X-User-ID': this.user?.id
          }
        })
        
        this.setUser(response.data.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || '更新信息失败'
        throw error
      }
    },
    
    // 修改密码
    async changePassword(oldPassword, newPassword) {
      try {
        const response = await axios.put('/api/user/change-password', {
          old_password: oldPassword,
          new_password: newPassword
        }, {
          headers: {
            'X-User-ID': this.user?.id
          }
        })
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || '修改密码失败'
        throw error
      }
    },
    
    // 登出
    logout() {
      this.clearUser()
    }
  }
})
