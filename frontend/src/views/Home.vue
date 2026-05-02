<template>
  <div class="home-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="250px" class="sidebar">
        <Sidebar/>
      </el-aside>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <div class="welcome-section">
          <h2>欢迎使用智能手写笔记转录系统</h2>
          <p class="subtitle">Handwritten Note Transcription System</p>

          <el-card class="stats-card" shadow="hover">
            <template #header>
              <div class="stats-header">
                <span>系统统计</span>
              </div>
            </template>

            <el-row :gutter="20">
              <el-col :span="8">
                <div class="stat-item">
                  <div class="stat-value">{{ user?.total_uploads || 0 }}</div>
                  <div class="stat-label">总上传次数</div>
                </div>
              </el-col>

              <el-col :span="8">
                <div class="stat-item">
                  <div class="stat-value">{{ user?.total_characters || 0 }}</div>
                  <div class="stat-label">总识别字符数</div>
                </div>
              </el-col>

              <el-col :span="8">
                <div class="stat-item">
                  <div class="stat-value">{{ formatDate(user?.last_login) }}</div>
                  <div class="stat-label">最后登录</div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </div>

        <div class="features-section">
          <h3>系统功能</h3>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-card class="feature-card" shadow="hover">
                <div class="feature-icon">
                  <el-icon><Picture /></el-icon>
                </div>
                <h4>图像上传</h4>
                <p>支持JPG/PNG格式图片上传，自动预处理</p>
              </el-card>
            </el-col>

            <el-col :span="8">
              <el-card class="feature-card" shadow="hover">
                <div class="feature-icon">
                  <el-icon><Search /></el-icon>
                </div>
                <h4>智能识别</h4>
                <p>基于PaddleOCR-VL模型，高精度中文手写识别</p>
              </el-card>
            </el-col>

            <el-col :span="8">
              <el-card class="feature-card" shadow="hover">
                <div class="feature-icon">
                  <el-icon><Document /></el-icon>
                </div>
                <h4>排版还原</h4>
                <p>自动还原笔记段落、标题、换行等结构</p>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import {
  Picture,
  Search,
  Document
} from '@element-plus/icons-vue'
import { formatDate } from '@/utils/common'
import Sidebar from '@/components/Sidebar.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)
</script>

<style scoped>
.home-container {
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

.welcome-section {
  margin-bottom: 30px;
}

.welcome-section h2 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  color: #909399;
  margin-bottom: 20px;
}

.stats-card {
  margin-bottom: 20px;
}

.stats-header {
  font-weight: bold;
  color: #303133;
}

.stat-item {
  text-align: center;
  padding: 15px 0;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.features-section {
  margin-top: 30px;
}

.features-section h3 {
  font-size: 20px;
  color: #303133;
  margin-bottom: 20px;
}

.feature-card {
  text-align: center;
  padding: 30px 20px;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  font-size: 48px;
  color: #667eea;
  margin-bottom: 15px;
}

.feature-card h4 {
  font-size: 18px;
  color: #303133;
  margin-bottom: 10px;
}

.feature-card p {
  font-size: 14px;
  color: #909399;
  line-height: 1.6;
}
</style>