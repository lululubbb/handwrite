<template>
  <div class="admin-records-container">
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
          
          <el-menu-item index="logout" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-main class="main-content">
        <div class="records-section">
          <h2>历史记录管理</h2>
          
          <el-card class="records-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>历史记录列表</span>
                <el-select
                  v-model="filterStatus"
                  placeholder="状态"
                  clearable
                  style="width: 120px"
                  size="small"
                >
                  <el-option label="已完成" value="completed" />
                  <el-option label="处理中" value="processing" />
                  <el-option label="失败" value="failed" />
                </el-select>
                <el-input
                  v-model="searchText"
                  placeholder="搜索文件名"
                  clearable
                  style="width: 200px"
                  size="small"
                />
              </div>
            </template>
            
            <el-table
              v-loading="loading"
              :data="recordsData"
              stripe
              style="width: 100%"
            >
              <el-table-column prop="username" label="用户名" width="120" />
              <el-table-column prop="original_filename" label="文件名" width="250" />
              <el-table-column prop="upload_time" label="上传时间" width="180" />
              <el-table-column prop="character_count" label="字符数" width="100" />
              <el-table-column prop="confidence" label="置信度" width="100">
                <template #default="{ row }">
                  {{ (row.confidence * 100).toFixed(2) }}%
                </template>
              </el-table-column>
              <el-table-column prop="processing_time" label="处理时间" width="100">
                <template #default="{ row }">
                  {{ row.processing_time }}s
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'completed' ? 'success' : (row.status === 'failed' ? 'danger' : 'warning')">
                    {{ row.status === 'completed' ? '已完成' : (row.status === 'failed' ? '失败' : '处理中') }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200" fixed="right">
                <template #default="{ row }">
                  <el-button
                    type="primary"
                    link
                    @click="viewRecord(row.id)"
                  >
                    查看
                  </el-button>
                  <el-button
                    type="primary"
                    link
                    @click="downloadRecord(row)"
                  >
                    下载
                  </el-button>
                  <el-button
                    type="danger"
                    link
                    @click="deleteRecord(row)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.page_size"
              :total="pagination.total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handlePageChange"
              style="margin-top: 20px"
              background
            />
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  HomeFilled, 
  Upload, 
  User, 
  Setting, 
  SwitchButton 
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 记录列表
const recordsData = ref([])
const loading = ref(false)
const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

// 过滤条件
const filterStatus = ref('')
const searchText = ref('')

// 当前激活的菜单
const activeMenu = computed(() => router.currentRoute.value.path)

// 获取用户信息
const user = computed(() => userStore.user)

// 获取记录列表
const getRecords = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: pagination.page,
      page_size: pagination.page_size
    })
    
    if (filterStatus.value) params.append('status', filterStatus.value)
    if (searchText.value) params.append('filename', searchText.value)
    
    const response = await fetch(`/api/admin/records?${params.toString()}`)
    const data = await response.json()
    
    if (data.status === 'success') {
      recordsData.value = data.data.records
      pagination.total = data.data.total
      pagination.page = data.data.page
      pagination.page_size = data.data.page_size
    }
  } catch (error) {
    ElMessage.error('获取记录列表失败')
  } finally {
    loading.value = false
  }
}

// 分页变化
const handleSizeChange = () => {
  pagination.page = 1
  getRecords()
}

const handlePageChange = () => {
  getRecords()
}

// 查看记录
const viewRecord = (recordId) => {
  router.push(`/result/${recordId}`)
}

// 下载记录
const downloadRecord = (record) => {
  if (record.formatted_text) {
    const blob = new Blob([record.formatted_text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${record.original_filename}_识别结果.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } else {
    ElMessage.warning('没有可下载的文本')
  }
}

// 删除记录
const deleteRecord = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该记录吗？', '警告', {
      type: 'warning'
    })
    
    const response = await fetch(`/api/admin/records/${row.id}`, {
      method: 'DELETE'
    })
    
    const data = await response.json()
    
    if (data.status === 'success') {
      ElMessage.success('删除成功')
      getRecords()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 退出登录
const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

// 组件挂载时获取记录列表
onMounted(() => {
  getRecords()
})
</script>

<style scoped>
.admin-records-container {
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

.records-section {
  max-width: 1200px;
  margin: 0 auto;
}

.records-section h2 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 20px;
}

.records-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
