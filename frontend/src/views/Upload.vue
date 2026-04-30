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
                    {{ uploadResult.original_filename }}
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

                <el-button
                  type="primary"
                  class="view-result-btn"
                  @click="goToResult(uploadResult.record_id)"
                >
                  查看完整识别结果 →
                </el-button>
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
                      <p>基于 PaddleOCR 模型进行高精度中文手写识别</p>
                    </div>
                  </div>
                  <div class="guide-item">
                    <div class="guide-num">4</div>
                    <div class="guide-text">
                      <strong>查看&编辑结果</strong>
                      <p>查看排版还原文本，支持手动修正和下载</p>
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { UploadFilled, Document, Search, Delete } from '@element-plus/icons-vue'
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

// ---- 上传 ----
const uploadFile = async () => {
  if (!selectedFile) {
    ElMessage.warning('请先选择文件')
    return
  }

  const formData = new FormData()
  formData.append('file', selectedFile)
  formData.append('original_filename', selectedFile.name) // 传递原始文件名

  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    })
    const data = await response.json()
    if (data.status === 'success') {
      ElMessage.success('文件上传成功')
      router.push(`/result/${data.recordId}`)
    } else {
      ElMessage.error(data.message || '文件上传失败')
    }
  } catch (error) {
    ElMessage.error('文件上传失败: ' + error.message)
  }
}

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
        image_filename: uploadData.data.processed_filename
      })
    })
    const ocrData = await ocrResp.json()

    if (ocrData.status !== 'success') {
      throw new Error(ocrData.message || 'OCR识别失败')
    }

    const ocrResult = ocrData.data

    // ---- Step 3: 保存记录 ----
    currentStep.value = 3
    const saveResp = await fetch('/api/upload/save-record', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify({
        user_id: user.value.id,
        original_filename: uploadData.data.original_filename,
        processed_filename: uploadData.data.processed_filename,
        ocr_result: JSON.stringify({
          text_lines: ocrResult.raw_ocr_result?.text_lines || [],
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
      original_filename: uploadData.data.original_filename,
      processed_time: ocrResult.statistics?.processing_time || 0,
      total_characters: ocrResult.statistics?.total_characters || 0,
      average_confidence: ocrResult.statistics?.average_confidence || 0,
      record_id: saveData.data.record_id,
      text_preview: preview
    }

    currentStep.value = 4
    ElMessage.success('识别完成！')

  } catch (error) {
    ElMessage.error(error.message || '操作失败，请重试')
    console.error('[Upload] 错误:', error)
  } finally {
    uploading.value = false
  }
}

// 跳转结果页
const goToResult = (recordId) => router.push(`/result/${recordId}`)
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

.view-result-btn { width: 100%; margin-top: 16px; }

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
</style>