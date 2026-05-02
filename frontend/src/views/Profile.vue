<template>
  <div class="profile-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="250px" class="sidebar">
        <Sidebar />
      </el-aside>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <div class="profile-section">
          <h2>个人中心</h2>

          <el-tabs v-model="activeTab">
            <!-- 个人信息 -->
            <el-tab-pane label="个人信息" name="info">
              <el-card class="profile-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>用户信息</span>
                  </div>
                </template>

                <el-descriptions :column="2" border>
                  <el-descriptions-item label="用户名">
                    {{ user?.username || '未知' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="邮箱">
                    {{ user?.email || '未知' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="角色">
                    <el-tag :type="user?.role === 'admin' ? 'danger' : 'primary'">
                      {{ user?.role === 'admin' ? '管理员' : '普通用户' }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="状态">
                    <el-tag :type="user?.status === 'active' ? 'success' : 'danger'">
                      {{ user?.status === 'active' ? '正常' : '禁用' }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="创建时间">
                    {{ formatDate(user?.created_at) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="最后登录">
                    {{ formatDate(user?.last_login) }}
                  </el-descriptions-item>
                </el-descriptions>

                <div class="profile-actions">
                  <el-button type="primary" @click="editInfo">编辑信息</el-button>
                  <el-button @click="showChangePassword">修改密码</el-button>
                </div>
              </el-card>
            </el-tab-pane>

            <!-- 历史记录 -->
            <el-tab-pane label="历史记录" name="history">
              <el-card class="history-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>历史识别记录</span>
                    <el-input
                      v-model="searchText"
                      placeholder="搜索文件名"
                      clearable
                      style="width: 200px"
                      size="small"
                    />
                  </div>
                </template>

                <!-- 表格本身支持滚动 -->
                <el-table
                  v-loading="loading"
                  :data="historyData"
                  stripe
                  style="width: 100%"
                  max-height="460"
                >
                  <el-table-column prop="original_filename" label="文件名" width="250" show-overflow-tooltip />
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
                  <el-table-column label="操作" width="200" fixed="right">
                    <template #default="{ row }">
                      <el-button type="primary" link @click="viewRecord(row.id)">查看</el-button>
                      <el-button type="primary" link @click="downloadRecord(row)">下载</el-button>
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
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-main>
    </el-container>

    <!-- 编辑信息对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑信息"
      width="500px"
      @close="handleEditClose"
    >
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="500px"
      @close="handlePasswordClose"
    >
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item label="原密码">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePassword">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { formatDate } from '@/utils/common'
import Sidebar from '@/components/Sidebar.vue'

const userStore = useUserStore()
const router = useRouter()

const activeTab = ref('info')
const user = computed(() => userStore.user)

const editDialogVisible = ref(false)
const editForm = reactive({ username: '', email: '' })

const passwordDialogVisible = ref(false)
const passwordForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })

const historyData = ref([])
const loading = ref(false)
const pagination = reactive({ page: 1, page_size: 10, total: 0 })
const searchText = ref('')

const getHistory = async () => {
  if (!user.value?.id) { ElMessage.error('请先登录'); router.push('/login'); return }
  loading.value = true
  try {
    const response = await fetch(
      `/api/user/history?page=${pagination.page}&page_size=${pagination.page_size}`,
      { headers: { 'X-User-ID': user.value.id, 'Authorization': userStore.token || '' } }
    )
    const data = await response.json()
    if (data.status === 'success') {
      historyData.value = data.data.records
      pagination.total = data.data.total
    } else {
      ElMessage.error(data.message || '获取记录失败')
    }
  } catch (error) {
    ElMessage.error('获取历史记录失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = () => { pagination.page = 1; getHistory() }
const handlePageChange = () => { getHistory() }

const editInfo = () => {
  if (!user.value) return
  editForm.username = user.value.username || ''
  editForm.email = user.value.email || ''
  editDialogVisible.value = true
}
const handleEditClose = () => { editForm.username = ''; editForm.email = '' }
const saveEdit = async () => {
  try {
    await userStore.updateProfile({ email: editForm.email })
    editDialogVisible.value = false
    ElMessage.success('信息更新成功')
  } catch (error) {
    ElMessage.error(error.message || '更新失败')
  }
}

const showChangePassword = () => { passwordDialogVisible.value = true }
const handlePasswordClose = () => {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}
const savePassword = async () => {
  if (!passwordForm.oldPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
    ElMessage.error('请填写完整密码信息'); return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.error('两次输入的密码不一致'); return
  }
  try {
    await userStore.changePassword(passwordForm.oldPassword, passwordForm.newPassword)
    passwordDialogVisible.value = false
    ElMessage.success('密码修改成功')
  } catch (error) {
    ElMessage.error(error.message || '修改失败')
  }
}

const viewRecord = (recordId) => router.push(`/result/${recordId}`)
const downloadRecord = (record) => {
  try {
    if (!record?.formatted_text) { ElMessage.warning('没有可下载的文本'); return }
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
  } catch (e) {
    ElMessage.error('下载失败')
  }
}

onMounted(() => {
  if (!user.value) { ElMessage.error('请先登录'); router.push('/login'); return }
  getHistory()
})
</script>

<style scoped>
.profile-container {
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  background: #304156;
  color: #fff;
}

/* 主内容区添加滚动条 */
.main-content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;   /* ← 垂直滚动条 */
  height: 100vh;
  box-sizing: border-box;
}

.profile-section {
  max-width: 1000px;
  margin: 0 auto;
}

.profile-section h2 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 20px;
}

.profile-card,
.history-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}
</style>