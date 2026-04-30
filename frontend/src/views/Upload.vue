<template>
  <div class="upload-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="250px" class="sidebar">
        <Sidebar />
      </el-aside>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <div class="upload-section">
          <div class="page-header">
            <h2 class="page-title">上传手写笔记</h2>
            <p class="page-subtitle">支持 JPG、PNG 格式，最大 16MB，上传后自动预处理并进行 OCR 识别</p>
          </div>

          <el-row :gutter="20">
            <!-- 左：上传区 -->
            <el-col :span="14">
              <el-card shadow="never" class="upload-card">
                <!-- 上传区域 -->
                <div
                  class="drop-zone"
                  :class="{ 'drag-over': isDragOver, 'has-file': selectedFile }"
                  @dragover.prevent="isDragOver = true"
                  @dragleave.prevent="isDragOver = false"
                  @drop.prevent="handleDrop"
                  @click="triggerFileInput"
                >
                  <input
                    ref="fileInputRef"
                    type="file"
                    accept="image/jpeg,image/jpg,image/png"
                    style="display:none"
                    @change="handleFileInputChange"
                  />

                  <!-- 预览图片 -->
                  <div v-if="previewUrl" class="preview-wrapper">
                    <img :src="previewUrl" class="preview-img" alt="预览" />
                    <div class="preview-overlay">
                      <el-button type="primary" size="small" circle @click.stop="clearFile">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  </div>

                  <!-- 默认提示 -->
                  <div v-else class="drop-hint">
                    <el-icon class="drop-icon" :size="64"><UploadFilled /></el-icon>
                    <p class="drop-text">点击选择图片，或将图片拖拽到此处</p>
                    <p class="drop-sub">支持 JPG、PNG 格式，最大 16MB</p>
                  </div>
                </div>

                <!-- 文件信息 -->
                <div v-if="selectedFile" class="file-info-bar">
                  <el-icon><Document /></el-icon>
                  <!-- 修复：显示原始文件名 -->
                  <span class="file-name">{{ selectedFile.name }}</span>
                  <el-tag size="small" type="info">{{ formatFileSize(selectedFile.size) }}</el-tag>
                  <el-button text size="small" type="danger" @click="clearFile">移除</el-button>
                </div>

                <!-- 操作按钮 -->
                <div class="upload-actions">
                  <el-button
                    type="primary"
                    size="large"
                    :disabled="!selectedFile || uploading"
                    :loading="uploading"
                    @click="handleUpload"
                    class="start-btn"
                  >
                    <el-icon v-if="!uploading"><Search /></el-icon>
                    {{ uploading ? currentStepLabel : '开始识别' }}
                  </el-button>
                  <el-button size="large" @click="clearFile" :disabled="!selectedFile || uploading">
                    取消
                  </el-button>
                </div>

                <!-- 进度条 -->
                <div v-if="uploading" class="progress-area">
                  <el-steps :active="currentStep" align-center finish-status="success" size="small">
                    <el-step title="上传图片" />
                    <el-step title="预处理" />
                    <el-step title="OCR识别" />
                    <el-step title="保存记录" />
                  </el-steps>
                </div>
              </el-card>

              <!-- 批量搜索卡片 -->
              <el-card shadow="never" class="search-card" style="margin-top: 16px;">
                <template #header>
                  <div class="search-header">
                    <el-icon><Search /></el-icon>
                    <span>全文搜索历史记录</span>
                  </div>
                </template>
                <div class="search-area">
                  <el-input
                    v-model="searchKeyword"
                    placeholder="输入关键词搜索所有历史识别内容..."
                    clearable
                    @keyup.enter="doSearch"
                  >
                    <template #append>
                      <el-button @click="doSearch" :loading="searching">搜索</el-button>
                    </template>
                  </el-input>
                  <div v-if="searchResults.length > 0" class="search-results">
                    <div class="search-result-title">
                      找到 <strong>{{ searchResults.length }}</strong> 条相关记录
                    </div>
                    <div
                      v-for="result in searchResults"
                      :key="result.record_id"
                      class="search-result-item"
                      @click="goToResult(result.record_id)"
                    >
                      <div class="result-filename">
                        <el-icon><Document /></el-icon>
                        {{ result.filename }}
                      </div>
                      <div class="result-context">{{ result.context }}</div>
                      <div class="result-meta">
                        <el-tag size="small" type="info">{{ result.upload_time }}</el-tag>
                        <el-tag size="small" type="success">{{ result.character_count }} 字</el-tag>
                      </div>
                    </div>
                  </div>
                  <el-empty
                    v-else-if="searchDone && searchResults.length === 0"
                    description="未找到相关内容"
                    :image-size="60"
                  />
                </div>
              </el-card>
            </el-col>

            <!-- 右：结果预览 / 使用说明 -->
            <el-col :span="10">
              <!-- 识别结果预览卡 -->
              <el-card v-if="uploadResult" shadow="never" class="result-preview-card">
                <template #header>
                  <div class="result-preview-header">
                    <span>识别完成</span>
                    <el-tag type="success" size="small">✓ 成功</el-tag>
                  </div>
                </template>

                <el-descriptions :column="1" border size="small">
                  <el-descriptions-item label="文件名">
                    <!-- 修复：显示用户原始上传文件名，与上传区域保持一致 -->
                    {{ uploadResult.display_filename }}
                  </el-descriptions-item>
                  <el-descriptions-item label="识别字符">
                    <strong style="color:#409eff">{{ uploadResult.total_characters }}</strong> 个字符
                  </el-descriptions-item>
                  <el-descriptions-item label="平均置信度">
                    <el-progress
                      :percentage="Math.round(uploadResult.average_confidence * 100)"
                      :color="uploadResult.average_confidence >= 0.85 ? '#67c23a' : '#e6a23c'"
                      :stroke-width="8"
                    />
                  </el-descriptions-item>
                  <el-descriptions-item label="处理耗时">
                    {{ uploadResult.processed_time }} 秒
                  </el-descriptions-item>
                </el-descriptions>

                <!-- 文本摘要 -->
                <div v-if="uploadResult.text_preview" class="text-preview">
                  <div class="text-preview-label">文本摘要</div>
                  <div class="text-preview-content">{{ uploadResult.text_preview }}</div>
                </div>

                <div class="result-actions">
                  <el-button
                    type="primary"
                    class="view-result-btn"
                    @click="goToResult(uploadResult.record_id)"
                  >
                    查看完整识别结果 →
                  </el-button>
                  <el-button
                    class="view-result-btn"
                    style="margin-top: 8px;"
                    @click="quickDownload(uploadResult)"
                  >
                    <el-icon><Download /></el-icon> 快速下载 TXT
                  </el-button>
                </div>
              </el-card>

              <!-- 使用说明卡 -->
              <el-card v-else shadow="never" class="guide-card">
                <template #header><span>使用说明</span></template>
                <div class="guide-list">
                  <div class="guide-item">
                    <div class="guide-num">1</div>
                    <div class="guide-text">
                      <strong>上传图片</strong>
                      <p>点击上传区域或拖拽手写笔记图片（JPG/PNG，≤16MB）</p>
                    </div>
                  </div>
                  <div class="guide-item">
                    <div class="guide-num">2</div>
                    <div class="guide-text">
                      <strong>自动预处理</strong>
                      <p>系统自动进行亮度增强、清晰度优化、倾斜校正</p>
                    </div>
                  </div>
                  <div class="guide-item">
                    <div class="guide-num">3</div>
                    <div class="guide-text">
                      <strong>OCR识别</strong>
                      <p>基于 PaddleOCR 模型进行高精度中文手写识别，自动转换为简体中文</p>
                    </div>
                  </div>
                  <div class="guide-item">
                    <div class="guide-num">4</div>
                    <div class="guide-text">
                      <strong>查看&编辑结果</strong>
                      <p>查看排版还原文本，支持手动修正、下载和全文搜索</p>
                    </div>
                  </div>
                </div>
              </el-card>

              <!-- 最近记录卡 -->
              <el-card shadow="never" class="recent-card" style="margin-top: 16px;">
                <template #header>
                  <div class="recent-header">
                    <span>最近识别记录</span>
                    <el-button
                      v-if="selectedForExport.length > 0"
                      type="success"
                      size="small"
                      @click="batchExport"
                      :loading="exporting"
                    >
                      导出选中 ({{ selectedForExport.length }})
                    </el-button>
                  </div>
                </template>
                <div v-if="recentRecords.length === 0" style="text-align:center; color:#909399; padding:20px 0;">
                  暂无记录
                </div>
                <div v-else class="recent-list">
                  <div
                    v-for="record in recentRecords"
                    :key="record.id"
                    class="recent-item"
                    :class="{ selected: selectedForExport.includes(record.id) }"
                  >
                    <el-checkbox
                      :model-value="selectedForExport.includes(record.id)"
                      @change="toggleExportSelect(record.id)"
                      class="record-checkbox"
                    />
                    <div class="recent-info" @click="goToResult(record.id)">
                      <div class="recent-filename">{{ record.original_filename }}</div>
                      <div class="recent-meta">
                        <span>{{ record.upload_time }}</span>
                        <el-tag size="small" type="info">{{ record.character_count }} 字</el-tag>
                      </div>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { UploadFilled, Document, Search, Delete, Download } from '@element-plus/icons-vue'
import Sidebar from '@/components/Sidebar.vue'

const router = useRouter()
const userStore = useUserStore()
const user = computed(() => userStore.user)

// 文件相关
const fileInputRef = ref(null)
const selectedFile = ref(null)
const previewUrl = ref('')
const isDragOver = ref(false)

// 上传状态
const uploading = ref(false)
const currentStep = ref(0)
const uploadResult = ref(null)

// 搜索相关
const searchKeyword = ref('')
const searchResults = ref([])
const searching = ref(false)
const searchDone = ref(false)

// 批量导出相关
const recentRecords = ref([])
const selectedForExport = ref([])
const exporting = ref(false)

// 步骤标签
const stepLabels = ['上传中...', '预处理中...', '识别中...', '保存中...']
const currentStepLabel = computed(() => stepLabels[currentStep.value] || '处理中...')

// 触发文件选择
const triggerFileInput = () => {
  if (!uploading.value) fileInputRef.value?.click()
}

// 文件input变化
const handleFileInputChange = (e) => {
  const file = e.target.files?.[0]
  if (file) setFile(file)
  e.target.value = ''
}

// 拖拽释放
const handleDrop = (e) => {
  isDragOver.value = false
  const file = e.dataTransfer.files?.[0]
  if (file) setFile(file)
}

// 设置选中文件
const setFile = (file) => {
  if (!validateFile(file)) return
  selectedFile.value = file
  uploadResult.value = null
  const reader = new FileReader()
  reader.onload = (e) => { previewUrl.value = e.target.result }
  reader.readAsDataURL(file)
}

// 校验文件
const validateFile = (file) => {
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png']
  if (!validTypes.includes(file.type)) {
    ElMessage.error('只支持 JPG、PNG 格式的图片')
    return false
  }
  if (file.size > 16 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 16MB')
    return false
  }
  return true
}

// 清除文件
const clearFile = () => {
  selectedFile.value = null
  previewUrl.value = ''
  uploadResult.value = null
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / (1024 * 1024)).toFixed(1) + ' MB'
}

// 认证请求头
const getAuthHeaders = () => ({
  'X-User-ID': String(user.value?.id || ''),
  'Authorization': userStore.token || ''
})

// 上传与识别主流程
const handleUpload = async () => {
  if (!selectedFile.value) { ElMessage.warning('请先选择文件'); return }
  if (!user.value?.id) { ElMessage.error('请先登录'); router.push('/login'); return }

  uploading.value = true
  currentStep.value = 0
  uploadResult.value = null

  // 保存用户原始文件名（用于前后端保持一致）
  const userOriginalFilename = selectedFile.value.name

  try {
    // ---- Step 1: 上传并预处理 ----
    currentStep.value = 0
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const uploadResp = await fetch('/api/upload/preprocess', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData
    })
    const uploadData = await uploadResp.json()

    if (uploadData.status !== 'success') {
      throw new Error(uploadData.message || '上传失败')
    }

    // ---- Step 2: OCR识别 ----
    currentStep.value = 2
    const ocrResp = await fetch('/api/ocr/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({
        image_path: uploadData.data.processed_path,
        // 传递原始文件名，保持一致性
        image_filename: userOriginalFilename
      })
    })
    const ocrData = await ocrResp.json()

    if (ocrData.status !== 'success') {
      throw new Error(ocrData.message || 'OCR识别失败')
    }

    const ocrResult = ocrData.data

    // ---- Step 3: 保存记录 ----
    currentStep.value = 3

    // 构造 text_lines 数组（兼容新旧格式）
    const textLines = ocrResult.raw_ocr_result?.text_lines || []
    const normalizedLines = textLines.map(item =>
      typeof item === 'string'
        ? { text: item, confidence: 0.96 }
        : item
    )

    const saveResp = await fetch('/api/upload/save-record', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({
        user_id: user.value.id,
        // 修复：使用用户原始文件名，而非 secure_filename 处理过的名字
        original_filename: userOriginalFilename,
        processed_filename: uploadData.data.processed_filename,
        ocr_result: JSON.stringify({
          text_lines: normalizedLines,
          boxes: ocrResult.visual_coordinates || [],
          layout_detection: ocrResult.layout_detection || {},
          total_characters: ocrResult.statistics?.total_characters || 0,
          average_confidence: ocrResult.statistics?.average_confidence || 0
        }),
        formatted_text: ocrResult.processed_text || '',
        character_count: ocrResult.statistics?.total_characters || 0,
        confidence: ocrResult.statistics?.average_confidence || 0,
        processing_time: ocrResult.statistics?.processing_time || 0
      })
    })
    const saveData = await saveResp.json()

    if (saveData.status !== 'success') {
      throw new Error(saveData.message || '保存记录失败')
    }

    // 文本摘要（取前100字符）
    const fullText = ocrResult.processed_text || ''
    const preview = fullText.length > 100 ? fullText.slice(0, 100) + '...' : fullText

    uploadResult.value = {
      // 修复：始终使用用户原始文件名
      display_filename: userOriginalFilename,
      original_filename: userOriginalFilename,
      processed_time: ocrResult.statistics?.processing_time || 0,
      total_characters: ocrResult.statistics?.total_characters || 0,
      average_confidence: ocrResult.statistics?.average_confidence || 0,
      record_id: saveData.data.record_id,
      text_preview: preview,
      formatted_text: ocrResult.processed_text || ''
    }

    currentStep.value = 4
    ElMessage.success('识别完成！')

    // 刷新最近记录
    await loadRecentRecords()

  } catch (error) {
    ElMessage.error(error.message || '操作失败，请重试')
    console.error('[Upload] 错误:', error)
  } finally {
    uploading.value = false
  }
}

// 加载最近5条记录
const loadRecentRecords = async () => {
  if (!user.value?.id) return
  try {
    const resp = await fetch('/api/user/history?page=1&page_size=5', {
      headers: getAuthHeaders()
    })
    const data = await resp.json()
    if (data.status === 'success') {
      recentRecords.value = data.data.records
    }
  } catch (e) {
    // 静默失败
  }
}

// 全文搜索
const doSearch = async () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  searching.value = true
  searchDone.value = false
  try {
    const resp = await fetch('/api/ocr/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({
        keyword: searchKeyword.value.trim(),
        user_id: user.value?.id
      })
    })
    const data = await resp.json()
    if (data.status === 'success') {
      searchResults.value = data.data.results
    }
  } catch (e) {
    ElMessage.error('搜索失败')
  } finally {
    searching.value = false
    searchDone.value = true
  }
}

// 切换批量导出选中
const toggleExportSelect = (id) => {
  const idx = selectedForExport.value.indexOf(id)
  if (idx === -1) {
    selectedForExport.value.push(id)
  } else {
    selectedForExport.value.splice(idx, 1)
  }
}

// 批量导出
const batchExport = async () => {
  if (selectedForExport.value.length === 0) return
  exporting.value = true
  try {
    const resp = await fetch('/api/ocr/batch-export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({
        record_ids: selectedForExport.value,
        format: 'txt'
      })
    })
    if (resp.ok) {
      const blob = await resp.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `批量导出_${Date.now()}.zip`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      ElMessage.success('批量导出成功')
      selectedForExport.value = []
    } else {
      ElMessage.error('导出失败')
    }
  } catch (e) {
    ElMessage.error('导出失败: ' + e.message)
  } finally {
    exporting.value = false
  }
}

// 快速下载当前识别结果
const quickDownload = (result) => {
  if (!result?.formatted_text) {
    ElMessage.warning('没有可下载的内容')
    return
  }
  const blob = new Blob([result.formatted_text], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  const baseName = result.display_filename.replace(/\.[^.]+$/, '')
  a.download = `${baseName}_识别结果.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  ElMessage.success('下载成功')
}

// 跳转结果页
const goToResult = (recordId) => router.push(`/result/${recordId}`)

onMounted(() => {
  loadRecentRecords()
})
</script>

<style scoped>
.upload-container { height: 100vh; overflow: hidden; }
.sidebar {
  background: #304156;
  color: #fff;
}
.main-content {
  background: #f0f2f5;
  padding: 24px;
  overflow-y: auto;
}

.upload-section { max-width: 1100px; margin: 0 auto; }

.page-header { margin-bottom: 24px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin: 0 0 6px; }
.page-subtitle { font-size: 14px; color: #909399; margin: 0; }

/* ===== 上传卡 ===== */
.upload-card { border-radius: 12px; }

.drop-zone {
  border: 2px dashed #dcdfe6;
  border-radius: 10px;
  min-height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s;
  position: relative;
  overflow: hidden;
  background: #fafafa;
}

.drop-zone:hover, .drop-zone.drag-over {
  border-color: #409eff;
  background: #ecf5ff;
}

.drop-zone.has-file { border-color: #67c23a; }

.drop-hint { text-align: center; padding: 30px; }
.drop-icon { color: #c0c4cc; margin-bottom: 12px; }
.drop-text { font-size: 16px; color: #606266; margin: 0 0 6px; }
.drop-sub { font-size: 13px; color: #c0c4cc; margin: 0; }

/* 预览 */
.preview-wrapper {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  position: relative;
}

.preview-img {
  max-width: 100%; max-height: 240px;
  object-fit: contain; border-radius: 6px;
}

.preview-overlay {
  position: absolute; top: 8px; right: 8px;
  opacity: 0; transition: opacity 0.2s;
}

.preview-wrapper:hover .preview-overlay { opacity: 1; }

/* 文件信息栏 */
.file-info-bar {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; background: #f5f7fa;
  border-radius: 8px; margin-top: 12px;
  font-size: 14px; color: #606266;
}

.file-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* 操作按钮 */
.upload-actions {
  display: flex; gap: 12px; margin-top: 16px;
}

.start-btn { flex: 1; }

/* 进度步骤 */
.progress-area { margin-top: 20px; }

/* ===== 搜索卡 ===== */
.search-card { border-radius: 12px; }
.search-header {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 600; color: #303133;
}

.search-area { padding: 0; }

.search-results { margin-top: 16px; }
.search-result-title {
  font-size: 13px; color: #606266; margin-bottom: 10px;
}

.search-result-item {
  padding: 10px 12px;
  border-radius: 8px;
  background: #fafafa;
  border: 1px solid #f0f0f0;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.search-result-item:hover {
  background: #ecf5ff;
  border-color: #409eff;
}

.result-filename {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; font-weight: 600; color: #303133;
  margin-bottom: 4px;
}

.result-context {
  font-size: 12px; color: #606266;
  background: #fff; border-radius: 4px;
  padding: 4px 8px; margin-bottom: 6px;
  border-left: 3px solid #409eff;
}

.result-meta { display: flex; gap: 6px; }

/* ===== 结果预览卡 ===== */
.result-preview-card { border-radius: 12px; }
.result-preview-header { display: flex; justify-content: space-between; align-items: center; }

.text-preview {
  margin-top: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.text-preview-label { font-size: 12px; color: #909399; margin-bottom: 6px; }
.text-preview-content {
  font-size: 14px; color: #303133;
  line-height: 1.8; white-space: pre-wrap;
  max-height: 120px; overflow: hidden;
}

.result-actions { margin-top: 16px; }
.view-result-btn { width: 100%; }

/* ===== 使用说明卡 ===== */
.guide-card { border-radius: 12px; }
.guide-list { display: flex; flex-direction: column; gap: 16px; }

.guide-item { display: flex; gap: 14px; align-items: flex-start; }

.guide-num {
  width: 28px; height: 28px; border-radius: 50%;
  background: #409eff; color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; flex-shrink: 0;
}

.guide-text strong { font-size: 14px; color: #303133; }
.guide-text p { font-size: 13px; color: #909399; margin: 4px 0 0; }

/* ===== 最近记录卡 ===== */
.recent-card { border-radius: 12px; }
.recent-header {
  display: flex; justify-content: space-between; align-items: center;
}

.recent-list { display: flex; flex-direction: column; gap: 6px; }

.recent-item {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  background: #fafafa;
  transition: background 0.2s;
}

.recent-item:hover { background: #f0f2f5; }
.recent-item.selected { background: #ecf5ff; border: 1px solid #409eff; }

.record-checkbox { flex-shrink: 0; }

.recent-info {
  flex: 1; cursor: pointer;
  overflow: hidden;
}

.recent-filename {
  font-size: 13px; font-weight: 500; color: #303133;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.recent-meta {
  display: flex; align-items: center; gap: 8px;
  margin-top: 4px; font-size: 12px; color: #909399;
}
</style>