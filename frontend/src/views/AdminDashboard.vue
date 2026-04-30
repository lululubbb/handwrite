<template>
  <div class="admin-dashboard-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="200px" class="sidebar">
        <div class="sidebar-header">
          <h3>智能手写笔记转录系统</h3>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          router
          class="sidebar-menu"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          
          <el-menu-item index="/upload">
            <el-icon><Upload /></el-icon>
            <span>上传识别</span>
          </el-menu-item>
          
          <el-menu-item index="/profile">
            <el-icon><User /></el-icon>
            <span>个人中心</span>
          </el-menu-item>
          
          <el-sub-menu index="2" v-if="user.role === 'admin'">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>管理员后台</span>
            </template>
            <el-menu-item index="/admin">系统统计</el-menu-item>
            <el-menu-item index="/admin/users">用户管理</el-menu-item>
            <el-menu-item index="/admin/records">记录管理</el-menu-item>
          </el-sub-menu>
          
          <el-menu-item index="/login" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-main class="main-content">
        <div class="dashboard-section">
          <h2>系统统计</h2>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card class="stat-card" shadow="hover">
                <div class="stat-content">
                  <div class="stat-icon">
                    <el-icon><User /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ stats.users?.total || 0 }}</div>
                    <div class="stat-label">总用户数</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="8">
              <el-card class="stat-card" shadow="hover">
                <div class="stat-content">
                  <div class="stat-icon">
                    <el-icon><Upload /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ stats.total?.uploads || 0 }}</div>
                    <div class="stat-label">总上传次数</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="8">
              <el-card class="stat-card" shadow="hover">
                <div class="stat-content">
                  <div class="stat-icon">
                    <el-icon><Document /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ stats.total?.characters || 0 }}</div>
                    <div class="stat-label">总识别字符数</div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
          
          <el-row :gutter="20" style="margin-top: 20px">
            <el-col :span="12">
              <el-card class="stat-card" shadow="hover">
                <template #header>
                  <span>今日统计</span>
                </template>
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="今日上传">
                    {{ stats.today?.uploads || 0 }}
                  </el-descriptions-item>
                  <el-descriptions-item label="今日字符">
                    {{ stats.today?.characters || 0 }}
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
            
            <el-col :span="12">
              <el-card class="stat-card" shadow="hover">
                <template #header>
                  <span>本周统计</span>
                </template>
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="本周上传">
                    {{ stats.week?.uploads || 0 }}
                  </el-descriptions-item>
                  <el-descriptions-item label="本周字符">
                    {{ stats.week?.characters || 0 }}
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
          </el-row>
          
          <el-card class="top-users-card" shadow="hover" style="margin-top: 20px">
            <template #header>
              <span>活跃用户TOP 10</span>
            </template>
            
            <el-table
              v-loading="loading"
              :data="topUsers"
              stripe
              style="width: 100%"
            >
              <el-table-column prop="rank" label="排名" width="80">
                <template #default="{ $index }">
                  {{ $index + 1 }}
                </template>
              </el-table-column>
              <el-table-column prop="username" label="用户名" width="150" />
              <el-table-column prop="uploads" label="上传次数" width="120">
                <template #default="{ row }">
                  {{ row.uploads }}
                </template>
              </el-table-column>
              <el-table-column prop="characters" label="识别字符数" width="150">
                <template #default="{ row }">
                  {{ row.characters }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { 
  HomeFilled, 
  Upload, 
  User, 
  Setting, 
  SwitchButton,
  Document
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 系统统计
const stats = ref({})
const topUsers = ref([])
const loading = ref(false)

// 当前激活的菜单
const activeMenu = computed(() => router.currentRoute.value.path)

// 获取用户信息
const user = computed(() => userStore.user)

// 获取系统统计
const getStatistics = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/admin/stats')
    const data = await response.json()
    
    if (data.status === 'success') {
      stats.value = data.data
      topUsers.value = data.data.top_users || []
    }
  } catch (error) {
    ElMessage.error('获取统计信息失败')
  } finally {
    loading.value = false
  }
}

// 退出登录
const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

// 组件挂载时获取统计信息
onMounted(() => {
  getStatistics()
})
</script>

<style scoped>
.admin-dashboard-container {
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  background: #304156;
  color: #fff;
}

.sidebar-header {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #4b5d75;
}

.sidebar-header h3 {
  font-size: 16px;
  font-weight: normal;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-menu {
  border-right: none;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  color: #bfcbd9;
}

.sidebar-menu :deep(.el-menu-item.is-active),
.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background: #2b3a4e;
  color: #fff;
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

.dashboard-section {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-section h2 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  font-size: 48px;
  color: #667eea;
  margin-right: 20px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.top-users-card {
  margin-top: 20px;
}

.top-users-card :deep(.el-card__header) {
  padding: 15px 20px;
}
</style>
