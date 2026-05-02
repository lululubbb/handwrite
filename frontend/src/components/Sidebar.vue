<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <div class="logo">
        <img src="@/assets/logo.png" alt="Logo" />
        <span>智能手写笔记转录系统</span>
      </div>
    </div>
    
    <el-menu
      :default-active="currentPath"
      class="sidebar-menu"
      :collapse="isCollapsed"
      router
    >
      <el-menu-item index="/">
        <el-icon><HomeFilled /></el-icon>
        <template #title>首页</template>
      </el-menu-item>
      <el-menu-item index="/upload">
        <el-icon><Upload /></el-icon>
        <template #title>上传识别</template>
      </el-menu-item>
      <el-menu-item index="/profile">
        <el-icon><User /></el-icon>
        <template #title>个人信息</template>
      </el-menu-item>
      <el-menu-item v-if="user?.role === 'admin'" index="/admin">
        <el-icon><Setting /></el-icon>
        <template #title>管理员面板</template>
      </el-menu-item>

      <!-- 修复在这里：加了 .prevent -->
    <el-menu-item @click="handleLogout">
        <el-icon><SwitchButton /></el-icon>
        <template #title>退出登录</template>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { HomeFilled, Upload, User, Setting, SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const user = computed(() => userStore.user)

const currentPath = computed(() => {
  return route.path
})

const handleLogout = (e) => {
  // 如果需要，可以手动失焦防止 CSS 状态残留
  if (e && e.currentTarget) {
    e.currentTarget.blur();
  }

  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }).catch(() => {
    // 这里不需要做任何操作，因为 currentPath 是响应式的
    // 由于没有设置 index="logout"，菜单的高亮会停留在之前的路由位置
    console.log('用户取消退出')
  })
}
</script>

<style scoped>
.sidebar {
  width: 250px;
  height: 100vh;
  background: #1f2429;
  color: #fff;
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid #30363d;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s;
}

.logo img {
  width: 32px;
  height: 32px;
}

.logo span {
  font-size: 16px;
  font-weight: 600;
  color: #e4e7ed;
}

.sidebar.collapsed .logo span {
  display: none;
}

.collapse-btn {
  color: #e4e7ed;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  transition: all 0.3s;
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.sidebar-menu {
  flex: 1;
  background: transparent !important;
  border-right: none !important;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  color: #e4e7ed;
  height: 50px;
  line-height: 50px;
  margin: 0 10px;
  border-radius: 6px;
  margin-bottom: 5px;
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background: rgba(255, 255, 255, 0.1) !important;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: #165dff !important;
  color: #fff !important;
}

.sidebar-menu :deep(.el-menu-item.is-active:hover) {
  background: #165dff !important;
  color: #fff !important;
}

.sidebar-menu :deep(.el-menu-item i) {
  margin-right: 10px;
}

.sidebar.collapsed .sidebar-menu :deep(.el-menu-item i) {
  margin-right: 0;
}

.sidebar.collapsed .sidebar-menu :deep(.el-menu-item__title) {
  display: none;
}

.sidebar.collapsed .sidebar-menu :deep(.el-sub-menu__title span) {
  display: none;
}

.sidebar.collapsed .sidebar-menu :deep(.el-sub-menu__title i) {
  margin-right: 0;
}
</style>