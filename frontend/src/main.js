/**
 * 智能手写笔记转录系统 - 前端入口文件
 * 初始化Vue应用、路由、状态管理等
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElIcons from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import { useUserStore } from '@/stores/user'

// 创建Vue应用实例
const app = createApp(App)

// 使用状态管理
const pinia = createPinia()

// 全局挂载Element Plus图标
for (const [key, component] of Object.entries(ElIcons)) {
  app.component(key, component)
}

// 配置并使用插件
app.use(pinia)
app.use(router)
app.use(ElementPlus, { locale: zhCn })

// 在挂载前尝试从 token 恢复用户信息（如果有）
const userStore = useUserStore(pinia)
userStore.initFromToken().finally(() => {
  // 无论成功与否均继续挂载应用
  app.mount('#app')
})
