<template>
  <div class="admin-users-container">
    <el-container>
      <el-aside width="200px" class="sidebar">
        <div class="sidebar-header">
          <h3>智能手写笔记转录系统</h3>
        </div>
        <el-menu :default-active="activeMenu" router class="sidebar-menu">
          <el-menu-item index="/"><el-icon><HomeFilled /></el-icon><span>首页</span></el-menu-item>
          <el-menu-item index="/upload"><el-icon><Upload /></el-icon><span>上传识别</span></el-menu-item>
          <el-menu-item index="/profile"><el-icon><User /></el-icon><span>个人中心</span></el-menu-item>
          <el-sub-menu index="2" v-if="user.role === 'admin'">
            <template #title><el-icon><Setting /></el-icon><span>管理员后台</span></template>
            <el-menu-item index="/admin">系统统计</el-menu-item>
            <el-menu-item index="/admin/users">用户管理</el-menu-item>
            <el-menu-item index="/admin/records">记录管理</el-menu-item>
          </el-sub-menu>
          <el-menu-item index="logout" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon><span>退出登录</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main class="main-content">
        <div class="users-section">
          <h2>用户管理</h2>
          <el-card class="users-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>用户列表</span>
                <div class="search-box">
                  <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 120px" size="small">
                    <el-option label="正常" value="active" />
                    <el-option label="禁用" value="inactive" />
                  </el-select>
                  <el-select v-model="filterRole" placeholder="角色" clearable style="width: 120px" size="small">
                    <el-option label="管理员" value="admin" />
                    <el-option label="普通用户" value="user" />
                  </el-select>
                  <el-input v-model="searchText" placeholder="搜索用户名" clearable style="width: 200px" size="small" />
                </div>
              </div>
            </template>

            <!-- 表格支持纵向滚动 -->
            <el-table v-loading="loading" :data="usersData" stripe style="width: 100%" max-height="500">
              <el-table-column prop="username" label="用户名" width="150" />
              <el-table-column prop="email" label="邮箱" width="200" />
              <el-table-column prop="role" label="角色" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
                    {{ row.role === 'admin' ? '管理员' : '普通用户' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                    {{ row.status === 'active' ? '正常' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="180" />
              <el-table-column prop="last_login" label="最后登录" width="180" />
              <el-table-column prop="total_uploads" label="上传次数" width="100" />
              <el-table-column prop="total_characters" label="字符数" width="100" />
              <el-table-column label="操作" width="160" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link @click="toggleStatus(row)">
                    {{ row.status === 'active' ? '禁用' : '启用' }}
                  </el-button>
                  <el-button type="danger" link @click="deleteUser(row)">删除</el-button>
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
import { HomeFilled, Upload, User, Setting, SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const usersData = ref([])
const loading = ref(false)
const pagination = reactive({ page: 1, page_size: 10, total: 0 })
const filterStatus = ref('')
const filterRole = ref('')
const searchText = ref('')

const activeMenu = computed(() => router.currentRoute.value.path)
const user = computed(() => userStore.user)

const getUsers = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({ page: pagination.page, page_size: pagination.page_size })
    if (filterStatus.value) params.append('status', filterStatus.value)
    if (filterRole.value) params.append('role', filterRole.value)
    if (searchText.value) params.append('username', searchText.value)

    const response = await fetch(`/api/admin/users?${params.toString()}`)
    const data = await response.json()
    if (data.status === 'success') {
      usersData.value = data.data.users
      pagination.total = data.data.total
      pagination.page = data.data.page
      pagination.page_size = data.data.page_size
    }
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = () => { pagination.page = 1; getUsers() }
const handlePageChange = () => { getUsers() }

const toggleStatus = async (row) => {
  const newStatus = row.status === 'active' ? 'inactive' : 'active'
  try {
    const response = await fetch(`/api/admin/users/${row.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    })
    const data = await response.json()
    if (data.status === 'success') {
      row.status = newStatus
      ElMessage.success(`${newStatus === 'active' ? '启用' : '禁用'}成功`)
      getUsers()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const deleteUser = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该用户吗？', '警告', { type: 'warning' })
    const response = await fetch(`/api/admin/users/${row.id}`, { method: 'DELETE' })
    const data = await response.json()
    if (data.status === 'success') { ElMessage.success('删除成功'); getUsers() }
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

onMounted(() => { getUsers() })
</script>

<style scoped>
.admin-users-container { height: 100vh; overflow: hidden; }
.sidebar { background: #304156; color: #fff; }
.sidebar-header { padding: 20px; text-align: center; border-bottom: 1px solid #4b5d75; }
.sidebar-header h3 { font-size: 16px; font-weight: normal; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sidebar-menu { border-right: none; }
.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) { color: #bfcbd9; }
.sidebar-menu :deep(.el-menu-item.is-active),
.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) { background: #2b3a4e; color: #fff; }

/* 主内容区添加滚动条 */
.main-content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;   /* ← 垂直滚动条 */
  height: 100vh;
  box-sizing: border-box;
}

.users-section { max-width: 1200px; margin: 0 auto; }
.users-section h2 { font-size: 28px; color: #303133; margin-bottom: 20px; }
.users-card { margin-bottom: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-box { display: flex; gap: 10px; }
</style>