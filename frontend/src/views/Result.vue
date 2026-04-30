<template>
  <div class="result-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="250px" class="sidebar">
        <Sidebar />
      </el-aside>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <div class="result-section">

          <!-- 顶部标题栏 -->
          <div class="result-topbar">
            <div class="topbar-left">
              <el-button text @click="goBack">
                <el-icon><ArrowLeft /></el-icon> 返回
              </el-button>
              <h2 class="page-title">识别结果</h2>
              <el-tag v-if="recordInfo" type="success" size="small" class="file-tag">
                <!-- 修复：显示原始文件名 -->
                {{ recordInfo.original_filename }}
              </el-tag>
            </div>
            <div class="topbar-actions">
              <el-button type="primary" size="small" :icon="CopyDocument" @click="copyText">
                复制文本
              </el-button>
              <!-- 下载下拉框 -->
              <el-dropdown @command="handleDownload">
                <el-button size="small" :icon="Download">
                  下载
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="markdown">Markdown (.md)</el-dropdown-item>
                    <el-dropdown-item command="txt">纯文本 (.txt)</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-button
                size="small"
                :icon="editMode ? Check : Edit"
                :type="editMode ? 'success' : 'default'"
                @click="toggleEdit"
              >
                {{ editMode ? '保存编辑' : '手动编辑' }}
              </el-button>
              <el-button size="small" :icon="Refresh" @click="goToUpload">
                重新识别
              </el-button>
            </div>
          </div>

          <!-- 统计卡片行 -->
          <el-row :gutter="16" class="stats-row" v-if="recordInfo">
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon chars-icon"><el-icon><Document /></el-icon></div>
                <div class="stat-body">
                  <div class="stat-num">{{ statsData.total_characters || 0 }}</div>
                  <div class="stat-lbl">识别字符数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon lines-icon"><el-icon><List /></el-icon></div>
                <div class="stat-body">
                  <div class="stat-num">{{ ocrLines.length }}</div>
                  <div class="stat-lbl">文本行数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon conf-icon"><el-icon><TrendCharts /></el-icon></div>
                <div class="stat-body">
                  <div class="stat-num">{{ confPercent }}%</div>
                  <div class="stat-lbl">平均置信度</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon time-icon"><el-icon><Timer /></el-icon></div>
                <div class="stat-body">
                  <div class="stat-num">{{ statsData.processing_time || 0 }}s</div>
                  <div class="stat-lbl">处理耗时</div>
                </div>
              </div>
            </el-col>
          </el-row>

          <!-- 加载中 -->
          <div v-if="loading" class="loading-area">
            <el-skeleton :rows="8" animated />
          </div>

          <!-- 无数据 -->
          <div v-else-if="!recordInfo" class="empty-area">
            <el-empty description="暂无识别数据，请先上传图片进行识别">
              <el-button type="primary" @click="goToUpload">去上传</el-button>
            </el-empty>
          </div>

          <!-- 主内容Tabs -->
          <el-tabs v-else v-model="activeTab" class="result-tabs" type="border-card">

            <!-- ===== Tab1: 排版还原结果 ===== -->
            <el-tab-pane name="formatted" label="📄 排版还原文本">
              <div class="tab-inner">
                <div class="tab-desc">
                  根据识别文字的位置与段落关系自动还原原始笔记排版，支持手动编辑修正。
                </div>

                <!-- 编辑模式 -->
                <div v-if="editMode" class="edit-area">
                  <div class="edit-toolbar">
                    <span class="edit-hint"><el-icon><EditPen /></el-icon> 编辑模式已开启，直接修改文本</span>
                    <el-button size="small" type="danger" plain @click="cancelEdit">取消编辑</el-button>
                  </div>
                  <el-input
                    v-model="editableText"
                    type="textarea"
                    :autosize="{ minRows: 16, maxRows: 36 }"
                    class="edit-textarea"
                    placeholder="识别文本将在此处显示，可直接修改..."
                  />
                  <div class="edit-footer">
                    <span class="char-count">字符数：{{ editableText.length }}</span>
                    <el-button type="success" @click="saveEdit">
                      <el-icon><Check /></el-icon> 保存修改
                    </el-button>
                  </div>
                </div>

                <!-- 展示模式 -->
                <div v-else class="formatted-display">
                  <div class="formatted-header">
                    <el-tag size="small" type="success">格式化文本</el-tag>
                    <el-tag size="small" type="info" class="ml-8">共 {{ formattedText.length }} 字符</el-tag>
                  </div>
                  <div class="formatted-content" v-if="formattedText">
                    <div class="formatted-pre markdown-body" v-html="renderMarkdown(formattedText)"></div>
                  </div>
                  <el-empty v-else description="暂无排版文本" />

                  <!-- 布局检测信息 -->
                  <div v-if="layoutData && hasLayoutInfo" class="layout-summary">
                    <div class="layout-title">检测到的排版元素</div>
                    <el-row :gutter="12">
                      <el-col :span="8" v-if="layoutData.headings && layoutData.headings.length">
                        <el-tag type="warning" size="small">
                          标题：{{ layoutData.headings.length }} 处
                        </el-tag>
                      </el-col>
                      <el-col :span="8" v-if="layoutData.paragraphs && layoutData.paragraphs.length">
                        <el-tag type="primary" size="small">
                          段落：{{ layoutData.paragraphs.length }} 段
                        </el-tag>
                      </el-col>
                      <el-col :span="8" v-if="layoutData.lists && layoutData.lists.length">
                        <el-tag type="success" size="small">
                          列表：{{ layoutData.lists.length }} 项
                        </el-tag>
                      </el-col>
                    </el-row>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <!-- ===== Tab2: OCR逐行识别结果 ===== -->
            <el-tab-pane name="raw" label="🔍 逐行识别详情">
              <div class="tab-inner">
                <div class="tab-desc">
                  展示每行文字的识别内容及置信度，置信度越高表示识别越准确。
                  <span class="conf-legend">
                    <span class="conf-dot high"></span>高 (≥90%)
                    <span class="conf-dot mid"></span>中 (70-90%)
                    <span class="conf-dot low"></span>低 (&lt;70%)
                  </span>
                </div>

                <div v-if="ocrLines.length === 0">
                  <el-empty description="无识别行数据" />
                </div>

                <div v-else class="lines-list">
                  <div
                    v-for="(line, idx) in ocrLines"
                    :key="idx"
                    class="line-item"
                    :class="getConfClass(line.confidence)"
                  >
                    <div class="line-num">{{ idx + 1 }}</div>
                    <div class="line-text">{{ line.text }}</div>
                    <div class="line-meta">
                      <el-progress
                        :percentage="Math.round(line.confidence * 100)"
                        :color="getConfColor(line.confidence)"
                        :stroke-width="6"
                        style="width: 100px"
                        :show-text="false"
                      />
                      <span class="conf-value" :style="{ color: getConfColor(line.confidence) }">
                        {{ (line.confidence * 100).toFixed(1) }}%
                      </span>
                    </div>
                  </div>
                </div>

                <!-- 置信度分布 -->
                <div v-if="ocrLines.length > 0" class="conf-distribution">
                  <div class="dist-title">置信度分布</div>
                  <el-row :gutter="12">
                    <el-col :span="8">
                      <div class="dist-item high-bg">
                        <div class="dist-count">{{ highConfCount }}</div>
                        <div class="dist-label">高置信度行 (≥90%)</div>
                      </div>
                    </el-col>
                    <el-col :span="8">
                      <div class="dist-item mid-bg">
                        <div class="dist-count">{{ midConfCount }}</div>
                        <div class="dist-label">中置信度行 (70-90%)</div>
                      </div>
                    </el-col>
                    <el-col :span="8">
                      <div class="dist-item low-bg">
                        <div class="dist-count">{{ lowConfCount }}</div>
                        <div class="dist-label">低置信度行 (&lt;70%)</div>
                      </div>
                    </el-col>
                  </el-row>
                </div>
              </div>
            </el-tab-pane>

            <!-- ===== Tab3: 坐标可视化 ===== -->
            <el-tab-pane name="coordinates" label="📍 坐标可视化">
              <div class="tab-inner">
                <div class="tab-desc">
                  展示每段文字在图像中的位置坐标，可用于复核识别区域。
                </div>
                <div v-if="coordinatesData.length === 0">
                  <el-empty description="无坐标数据" />
                </div>
                <el-table
                  v-else
                  :data="coordinatesData"
                  stripe
                  border
                  size="small"
                  max-height="520"
                >
                  <el-table-column type="index" label="#" width="50" />
                  <el-table-column prop="text" label="识别文本" min-width="160" show-overflow-tooltip />
                  <el-table-column label="置信度" width="110">
                    <template #default="{ row }">
                      <el-tag
                        :type="row.confidence >= 0.9 ? 'success' : row.confidence >= 0.7 ? 'warning' : 'danger'"
                        size="small"
                      >
                        {{ (row.confidence * 100).toFixed(1) }}%
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="左上角坐标" width="130">
                    <template #default="{ row }">
                      <span class="coord-text" v-if="row.coordinates && row.coordinates[0]">
                        ({{ row.coordinates[0][0] }}, {{ row.coordinates[0][1] }})
                      </span>
                    </template>
                  </el-table-column>
                  <el-table-column label="右下角坐标" width="130">
                    <template #default="{ row }">
                      <span class="coord-text" v-if="row.coordinates && row.coordinates[2]">
                        ({{ row.coordinates[2][0] }}, {{ row.coordinates[2][1] }})
                      </span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-tab-pane>

            <!-- ===== Tab4: 记录信息 ===== -->
            <el-tab-pane name="info" label="ℹ️ 记录信息">
              <div class="tab-inner">
                <el-descriptions
                  v-if="recordInfo"
                  :column="2"
                  border
                  class="record-desc"
                >
                  <el-descriptions-item label="原始文件名">
                    {{ recordInfo.original_filename }}
                  </el-descriptions-item>
                  <el-descriptions-item label="处理文件名">
                    {{ recordInfo.processed_filename }}
                  </el-descriptions-item>
                  <el-descriptions-item label="上传时间">
                    {{ recordInfo.upload_time }}
                  </el-descriptions-item>
                  <el-descriptions-item label="识别状态">
                    <el-tag :type="recordInfo.status === 'completed' ? 'success' : 'danger'">
                      {{ recordInfo.status === 'completed' ? '已完成' : recordInfo.status }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="识别字符数">
                    {{ recordInfo.character_count }}
                  </el-descriptions-item>
                  <el-descriptions-item label="平均置信度">
                    {{ (recordInfo.confidence * 100).toFixed(2) }}%
                  </el-descriptions-item>
                  <el-descriptions-item label="处理耗时">
                    {{ recordInfo.processing_time }} 秒
                  </el-descriptions-item>
                  <el-descriptions-item label="备注" v-if="recordInfo.notes">
                    {{ recordInfo.notes }}
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </el-tab-pane>

          </el-tabs>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { marked } from 'marked'
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, CopyDocument, Download, Edit, Check, Refresh,
  Document, List, TrendCharts, Timer, EditPen
} from '@element-plus/icons-vue'
import Sidebar from '@/components/Sidebar.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// ---- 状态 ----
const loading = ref(false)
const activeTab = ref('formatted')
const editMode = ref(false)

// 数据
const recordInfo = ref(null)
const ocrLines = ref([])      // 始终是 [{text, confidence}] 格式
const formattedText = ref('')
const editableText = ref('')
const layoutData = ref(null)
const coordinatesData = ref([])
const statsData = ref({})

// 渲染 Markdown
const renderMarkdown = (text) => {
  if (!text) return ''
  return marked.parse(text)
}

// 记录ID
const recordId = computed(() => route.params.recordId)

// 置信度百分比
const confPercent = computed(() => {
  const v = statsData.value.average_confidence || 0
  return (v * 100).toFixed(1)
})

// 置信度分布计数
const highConfCount = computed(() => ocrLines.value.filter(l => l.confidence >= 0.9).length)
const midConfCount = computed(() => ocrLines.value.filter(l => l.confidence >= 0.7 && l.confidence < 0.9).length)
const lowConfCount = computed(() => ocrLines.value.filter(l => l.confidence < 0.7).length)

// 是否有布局信息
const hasLayoutInfo = computed(() => {
  if (!layoutData.value) return false
  const ld = layoutData.value
  return (ld.headings?.length || 0) + (ld.paragraphs?.length || 0) + (ld.lists?.length || 0) > 0
})

// ---- 获取数据 ----
const getResultData = async () => {
  if (!recordId.value) return
  loading.value = true
  try {
    const userId = userStore.user?.id
    const response = await fetch(`/api/user/history/${recordId.value}`, {
      headers: {
        'X-User-ID': userId,
        'Authorization': userStore.token || ''
      }
    })
    const data = await response.json()

    if (data.status === 'success') {
      const record = data.data
      recordInfo.value = record
      formattedText.value = record.formatted_text || ''
      editableText.value = record.formatted_text || ''

      // 解析 OCR JSON
      let ocrObj = null
      if (record.ocr_result) {
        try {
          ocrObj = typeof record.ocr_result === 'string'
            ? JSON.parse(record.ocr_result)
            : record.ocr_result
        } catch (e) {
          console.warn('OCR结果JSON解析失败:', e)
        }
      }

      if (ocrObj) {
        // 兼容两种格式：旧格式(string[]) 和 新格式({text, confidence}[])
        const rawLines = ocrObj.text_lines || []
        ocrLines.value = rawLines.map(item => {
          if (typeof item === 'string') {
            return { text: item, confidence: 0.96 }
          }
          return { text: item.text || '', confidence: item.confidence ?? 0.96 }
        }).filter(l => l.text.trim())

        coordinatesData.value = ocrObj.boxes || []
        layoutData.value = ocrObj.layout_detection || null

        statsData.value = {
          total_characters: record.character_count || ocrObj.total_characters || 0,
          text_lines_count: ocrLines.value.length,
          average_confidence: record.confidence || ocrObj.average_confidence || 0,
          processing_time: record.processing_time || 0
        }
      } else {
        statsData.value = {
          total_characters: record.character_count || 0,
          text_lines_count: 0,
          average_confidence: record.confidence || 0,
          processing_time: record.processing_time || 0
        }
      }
    } else {
      ElMessage.error(data.message || '获取识别结果失败')
    }
  } catch (error) {
    ElMessage.error('获取识别结果失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// ---- 编辑 ----
const toggleEdit = () => {
  if (editMode.value) {
    saveEdit()
  } else {
    editableText.value = formattedText.value
    editMode.value = true
    activeTab.value = 'formatted'
  }
}

const cancelEdit = () => {
  editableText.value = formattedText.value
  editMode.value = false
}

const saveEdit = async () => {
  formattedText.value = editableText.value
  editMode.value = false
  try {
    await fetch(`/api/user/history/${recordId.value}/update-text`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': userStore.user?.id,
        'Authorization': userStore.token || ''
      },
      body: JSON.stringify({ formatted_text: editableText.value })
    })
  } catch (_) { /* 静默失败，本地已更新 */ }
  ElMessage.success('编辑已保存')
}

// ---- 工具 ----
const getConfClass = (conf) => {
  if (conf >= 0.9) return 'conf-high'
  if (conf >= 0.7) return 'conf-mid'
  return 'conf-low'
}

const getConfColor = (conf) => {
  if (conf >= 0.9) return '#67c23a'
  if (conf >= 0.7) return '#e6a23c'
  return '#f56c6c'
}

const copyText = () => {
  const txt = editMode.value ? editableText.value : formattedText.value
  if (!txt) { ElMessage.warning('没有可复制的文本'); return }
  navigator.clipboard.writeText(txt).then(() => ElMessage.success('复制成功'))
}

// 下载
const handleDownload = (type) => {
  const content = editMode.value ? editableText.value : formattedText.value
  if (!content) {
    ElMessage.warning('没有可下载的内容')
    return
  }

  const fullName = recordInfo.value?.original_filename || '未命名文件'
  const fileName = fullName.substring(0, fullName.lastIndexOf('.')) || fullName
  const saveName = `${fileName}_识别结果`

  if (type === 'txt') {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    triggerDownload(blob, saveName + '.txt')
    ElMessage.success('TXT 下载成功')
  } else if (type === 'markdown') {
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
    triggerDownload(blob, saveName + '.md')
    ElMessage.success('Markdown 下载成功')
  }
}

const triggerDownload = (blob, filename) => {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const goToUpload = () => router.push('/upload')
const goBack = () => router.back()

onMounted(() => { getResultData() })
</script>

<style scoped>
/* ===== 容器 ===== */
.result-container {
  height: 100vh;
  overflow: hidden;
  background: #f0f2f5;
}

.sidebar { background: #1f2429; }

.main-content {
  background: #f0f2f5;
  padding: 20px 24px;
  overflow-y: auto;
}

.result-section {
  max-width: 1200px;
  margin: 0 auto;
}

/* ===== 顶部栏 ===== */
.result-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
}

.file-tag { max-width: 240px; overflow: hidden; text-overflow: ellipsis; }

.topbar-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* ===== 统计卡片 ===== */
.stats-row { margin-bottom: 20px; }

.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s;
}

.stat-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); }

.stat-icon {
  width: 44px; height: 44px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.chars-icon { background: #e8f4fd; color: #409eff; }
.lines-icon { background: #fdf0e8; color: #e6a23c; }
.conf-icon  { background: #e8fdf0; color: #67c23a; }
.time-icon  { background: #fde8f4; color: #f56c6c; }

.stat-num {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
}

.stat-lbl {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* ===== 加载/空状态 ===== */
.loading-area, .empty-area {
  background: #fff;
  border-radius: 10px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* ===== Tabs ===== */
.result-tabs { background: #fff; border-radius: 10px; overflow: hidden; }

.result-tabs :deep(.el-tabs__header) {
  background: #fafafa;
  margin: 0;
}

.result-tabs :deep(.el-tabs__nav-wrap) { padding: 0 20px; }

.tab-inner { padding: 20px; }

.tab-desc {
  font-size: 13px;
  color: #909399;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

/* ===== 排版还原 ===== */
.formatted-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.ml-8 { margin-left: 8px; }

.formatted-content {
  background: #fafafa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px 24px;
  min-height: 200px;
}

.formatted-pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Microsoft YaHei', 'PingFang SC', '思源黑体', sans-serif;
  font-size: 15px;
  line-height: 2;
  color: #303133;
  margin: 0;
  max-height: calc(100vh - 350px);
  overflow-y: auto;
  padding-right: 8px;
}

.formatted-pre::-webkit-scrollbar { width: 6px; }
.formatted-pre::-webkit-scrollbar-thumb { background: #c0c4cc; border-radius: 3px; }

.layout-summary {
  margin-top: 16px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.layout-title {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 600;
}

/* 表格样式 */
.markdown-body { line-height: 1.8; }
.markdown-body table {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}
.markdown-body th, .markdown-body td {
  border: 1px solid #e5e7eb;
  padding: 8px 12px;
  text-align: center;
}
.markdown-body th {
  background: #f9fafb;
  font-weight: bold;
}

/* ===== 编辑模式 ===== */
.edit-area {
  border: 2px solid #409eff;
  border-radius: 8px;
  overflow: hidden;
}

.edit-toolbar {
  background: #ecf5ff;
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #409eff;
}

.edit-hint { display: flex; align-items: center; gap: 6px; }

.edit-textarea :deep(.el-textarea__inner) {
  border-radius: 0;
  border: none;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  font-size: 15px;
  line-height: 2;
  padding: 16px;
}

.edit-footer {
  background: #f5f7fa;
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #e4e7ed;
}

.char-count { font-size: 13px; color: #909399; }

/* ===== 逐行识别 ===== */
.conf-legend {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
}

.conf-dot {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-right: 2px;
}

.conf-dot.high { background: #67c23a; }
.conf-dot.mid  { background: #e6a23c; }
.conf-dot.low  { background: #f56c6c; }

.lines-list { display: flex; flex-direction: column; gap: 8px; }

.line-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  border-left: 4px solid transparent;
  background: #fafafa;
  transition: background 0.15s;
}

.line-item:hover { background: #f0f2f5; }

.conf-high { border-left-color: #67c23a; }
.conf-mid  { border-left-color: #e6a23c; }
.conf-low  { border-left-color: #f56c6c; }

.line-num {
  font-size: 12px;
  color: #c0c4cc;
  width: 28px;
  text-align: center;
  flex-shrink: 0;
}

.line-text {
  flex: 1;
  font-size: 14px;
  color: #303133;
  word-break: break-all;
}

.line-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.conf-value { font-size: 12px; font-weight: 600; width: 42px; text-align: right; }

/* 置信度分布 */
.conf-distribution { margin-top: 20px; }
.dist-title { font-size: 14px; font-weight: 600; color: #606266; margin-bottom: 10px; }

.dist-item {
  border-radius: 8px;
  padding: 14px;
  text-align: center;
}

.high-bg { background: #f0f9eb; }
.mid-bg  { background: #fdf6ec; }
.low-bg  { background: #fef0f0; }

.dist-count { font-size: 24px; font-weight: 700; color: #303133; }
.dist-label { font-size: 12px; color: #909399; margin-top: 4px; }

/* ===== 坐标表格 ===== */
.coord-text { font-family: monospace; font-size: 12px; color: #606266; }

/* ===== 记录信息 ===== */
.record-desc { margin-top: 8px; }
</style>