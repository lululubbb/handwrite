<template>
  <div class="stats-container">
    <el-container>
      <el-aside width="250px" class="sidebar">
        <Sidebar />
      </el-aside>

      <el-main class="main-content">
        <div class="stats-section">
          <div class="page-header">
            <h2 class="page-title">识别数据统计</h2>
            <p class="page-subtitle">查看您的手写识别使用情况与数据分析</p>
          </div>

          <!-- 概览卡片 -->
          <el-row :gutter="16" class="summary-row" v-if="summary">
            <el-col :span="8">
              <div class="summary-card blue">
                <div class="summary-icon"><el-icon :size="28"><Document /></el-icon></div>
                <div class="summary-body">
                  <div class="summary-num">{{ summary.total_records }}</div>
                  <div class="summary-lbl">累计识别次数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="summary-card green">
                <div class="summary-icon"><el-icon :size="28"><Edit /></el-icon></div>
                <div class="summary-body">
                  <div class="summary-num">{{ summary.total_characters.toLocaleString() }}</div>
                  <div class="summary-lbl">累计识别字符数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="summary-card orange">
                <div class="summary-icon"><el-icon :size="28"><TrendCharts /></el-icon></div>
                <div class="summary-body">
                  <div class="summary-num">{{ (summary.average_confidence * 100).toFixed(1) }}%</div>
                  <div class="summary-lbl">平均识别置信度</div>
                </div>
              </div>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 20px;">
            <!-- 每日识别趋势 -->
            <el-col :span="16">
              <el-card shadow="never" class="chart-card">
                <template #header>
                  <span>近30天识别趋势</span>
                </template>
                <div v-if="loadingStats" class="chart-loading">
                  <el-skeleton :rows="5" animated />
                </div>
                <div v-else-if="dailyStats.length === 0" class="chart-empty">
                  <el-empty description="暂无数据" :image-size="80" />
                </div>
                <div v-else class="chart-wrapper">
                  <!-- 简单 SVG 柱状图 -->
                  <svg :width="chartWidth" height="200" class="bar-chart">
                    <g v-for="(item, idx) in chartBars" :key="idx">
                      <!-- 柱体 -->
                      <rect
                        :x="item.x"
                        :y="item.y"
                        :width="item.w"
                        :height="item.h"
                        :fill="item.h > 0 ? '#409eff' : '#f0f0f0'"
                        rx="3"
                      />
                      <!-- 数值标签 -->
                      <text
                        v-if="item.h > 0"
                        :x="item.x + item.w / 2"
                        :y="item.y - 4"
                        text-anchor="middle"
                        font-size="10"
                        fill="#606266"
                      >{{ item.count }}</text>
                      <!-- 日期标签（每5天显示一次） -->
                      <text
                        v-if="idx % 5 === 0"
                        :x="item.x + item.w / 2"
                        y="195"
                        text-anchor="middle"
                        font-size="9"
                        fill="#909399"
                      >{{ item.dateLabel }}</text>
                    </g>
                    <!-- X 轴线 -->
                    <line x1="0" y1="170" :x2="chartWidth" y2="170" stroke="#e4e7ed" stroke-width="1" />
                  </svg>
                </div>
              </el-card>
            </el-col>

            <!-- 置信度分布 -->
            <el-col :span="8">
              <el-card shadow="never" class="chart-card">
                <template #header>
                  <span>置信度分布</span>
                </template>
                <div v-if="loadingStats" class="chart-loading">
                  <el-skeleton :rows="4" animated />
                </div>
                <div v-else class="conf-dist">
                  <div class="conf-item high">
                    <div class="conf-label">高置信度 ≥90%</div>
                    <el-progress
                      :percentage="confHighPct"
                      color="#67c23a"
                      :stroke-width="14"
                    />
                    <div class="conf-count">{{ confDist.high }} 次</div>
                  </div>
                  <div class="conf-item mid">
                    <div class="conf-label">中置信度 70-90%</div>
                    <el-progress
                      :percentage="confMidPct"
                      color="#e6a23c"
                      :stroke-width="14"
                    />
                    <div class="conf-count">{{ confDist.mid }} 次</div>
                  </div>
                  <div class="conf-item low">
                    <div class="conf-label">低置信度 &lt;70%</div>
                    <el-progress
                      :percentage="confLowPct"
                      color="#f56c6c"
                      :stroke-width="14"
                    />
                    <div class="conf-count">{{ confDist.low }} 次</div>
                  </div>

                  <!-- 置信度说明 -->
                  <div class="conf-note">
                    <el-icon><InfoFilled /></el-icon>
                    置信度反映模型对识别结果的把握程度，高置信度表示结果更可靠。
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 使用习惯分析 -->
          <el-card shadow="never" class="habit-card" style="margin-top: 20px;">
            <template #header>
              <span>使用习惯分析</span>
            </template>
            <div v-if="loadingStats">
              <el-skeleton :rows="3" animated />
            </div>
            <el-row :gutter="20" v-else>
              <el-col :span="8">
                <div class="habit-item">
                  <div class="habit-icon" style="background:#e8f4fd; color:#409eff;">
                    <el-icon :size="22"><Calendar /></el-icon>
                  </div>
                  <div class="habit-body">
                    <div class="habit-value">{{ activeDays }}</div>
                    <div class="habit-label">近30天活跃天数</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="habit-item">
                  <div class="habit-icon" style="background:#fdf0e8; color:#e6a23c;">
                    <el-icon :size="22"><TrendCharts /></el-icon>
                  </div>
                  <div class="habit-body">
                    <div class="habit-value">{{ avgDailyUploads }}</div>
                    <div class="habit-label">日均识别次数</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="habit-item">
                  <div class="habit-icon" style="background:#e8fdf0; color:#67c23a;">
                    <el-icon :size="22"><Edit /></el-icon>
                  </div>
                  <div class="habit-body">
                    <div class="habit-value">{{ avgCharsPerUpload }}</div>
                    <div class="habit-label">每次平均字符数</div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </el-card>

          <!-- 最近识别记录表 -->
          <el-card shadow="never" class="recent-table-card" style="margin-top: 20px;">
            <template #header>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span>识别记录明细</span>
                <el-button size="small" @click="$router.push('/profile')">
                  查看全部
                </el-button>
              </div>
            </template>
            <el-table
              v-loading="loadingRecords"
              :data="recentRecords"
              stripe
              size="small"
              style="width:100%"
            >
              <el-table-column prop="original_filename" label="文件名" min-width="200" show-overflow-tooltip />
              <el-table-column prop="upload_time" label="识别时间" width="170" />
              <el-table-column prop="character_count" label="字符数" width="90" align="center" />
              <el-table-column label="置信度" width="120" align="center">
                <template #default="{ row }">
                  <el-tag
                    :type="row.confidence >= 0.9 ? 'success' : row.confidence >= 0.7 ? 'warning' : 'danger'"
                    size="small"
                  >
                    {{ (row.confidence * 100).toFixed(1) }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="processing_time" label="耗时" width="80" align="center">
                <template #default="{ row }">{{ row.processing_time }}s</template>
              </el-table-column>
              <el-table-column label="操作" width="80" align="center">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="$router.push(`/result/${row.id}`)">
                    查看
                  </el-button>
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
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { Document, Edit, TrendCharts, Calendar, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import Sidebar from '@/components/Sidebar.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

const loadingStats = ref(false)
const loadingRecords = ref(false)

const summary = ref(null)
const dailyStats = ref([])
const confDist = ref({ high: 0, mid: 0, low: 0 })
const recentRecords = ref([])

const chartWidth = 560

// 计算柱状图数据
const chartBars = computed(() => {
  if (dailyStats.value.length === 0) return []

  // 补全近30天的日期
  const today = new Date()
  const days = []
  for (let i = 29; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().split('T')[0]
    days.push(dateStr)
  }

  const countMap = {}
  dailyStats.value.forEach(s => { countMap[s.date] = s.count })

  const counts = days.map(d => countMap[d] || 0)
  const maxCount = Math.max(...counts, 1)
  const barMaxH = 150
  const barW = Math.floor(chartWidth / 30) - 2
  const gap = 2

  return days.map((d, i) => {
    const count = counts[i]
    const h = Math.round((count / maxCount) * barMaxH)
    return {
      x: i * (barW + gap),
      y: 170 - h,
      w: barW,
      h,
      count,
      dateLabel: d.slice(5) // MM-DD
    }
  })
})

// 置信度百分比
const confTotal = computed(() => confDist.value.high + confDist.value.mid + confDist.value.low || 1)
const confHighPct = computed(() => Math.round((confDist.value.high / confTotal.value) * 100))
const confMidPct = computed(() => Math.round((confDist.value.mid / confTotal.value) * 100))
const confLowPct = computed(() => Math.round((confDist.value.low / confTotal.value) * 100))

// 使用习惯
const activeDays = computed(() => {
  return dailyStats.value.filter(s => s.count > 0).length
})
const avgDailyUploads = computed(() => {
  if (activeDays.value === 0) return 0
  const total = dailyStats.value.reduce((sum, s) => sum + s.count, 0)
  return (total / Math.max(activeDays.value, 1)).toFixed(1)
})
const avgCharsPerUpload = computed(() => {
  if (!summary.value || summary.value.total_records === 0) return 0
  return Math.round(summary.value.total_characters / summary.value.total_records)
})

const getAuthHeaders = () => ({
  'X-User-ID': String(user.value?.id || ''),
  'Authorization': userStore.token || ''
})

const loadStats = async () => {
  if (!user.value?.id) return
  loadingStats.value = true
  try {
    const resp = await fetch(`/api/ocr/stats/user/${user.value.id}`, {
      headers: getAuthHeaders()
    })
    const data = await resp.json()
    if (data.status === 'success') {
      dailyStats.value = data.data.daily_stats || []
      confDist.value = data.data.confidence_distribution || { high: 0, mid: 0, low: 0 }
      summary.value = data.data.summary
    }
  } catch (e) {
    ElMessage.error('加载统计数据失败')
  } finally {
    loadingStats.value = false
  }
}

const loadRecentRecords = async () => {
  if (!user.value?.id) return
  loadingRecords.value = true
  try {
    const resp = await fetch('/api/user/history?page=1&page_size=10', {
      headers: getAuthHeaders()
    })
    const data = await resp.json()
    if (data.status === 'success') {
      recentRecords.value = data.data.records
    }
  } catch (e) {
    // 静默失败
  } finally {
    loadingRecords.value = false
  }
}

onMounted(() => {
  loadStats()
  loadRecentRecords()
})
</script>

<style scoped>
.stats-container { height: 100vh; overflow: hidden; }
.sidebar { background: #304156; }
.main-content {
  background: #f0f2f5;
  padding: 24px;
  overflow-y: auto;
}
.stats-section { max-width: 1100px; margin: 0 auto; }
.page-header { margin-bottom: 24px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin: 0 0 6px; }
.page-subtitle { font-size: 14px; color: #909399; margin: 0; }

/* 概览卡 */
.summary-card {
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.summary-card.blue { background: linear-gradient(135deg, #e8f4fd, #d0e9f9); }
.summary-card.green { background: linear-gradient(135deg, #e8fdf0, #d0f0e0); }
.summary-card.orange { background: linear-gradient(135deg, #fdf6e8, #f9e8c8); }
.summary-icon { font-size: 28px; color: #409eff; opacity: 0.8; }
.summary-card.green .summary-icon { color: #67c23a; }
.summary-card.orange .summary-icon { color: #e6a23c; }
.summary-num { font-size: 26px; font-weight: 700; color: #303133; }
.summary-lbl { font-size: 13px; color: #606266; margin-top: 4px; }

/* 图表卡 */
.chart-card { border-radius: 12px; }
.chart-loading { padding: 20px; }
.chart-empty { padding: 20px; text-align: center; }
.chart-wrapper { overflow-x: auto; }
.bar-chart { display: block; }

/* 置信度分布 */
.conf-dist { padding: 8px 0; }
.conf-item { margin-bottom: 16px; }
.conf-label { font-size: 13px; color: #606266; margin-bottom: 6px; }
.conf-count { font-size: 12px; color: #909399; margin-top: 4px; text-align: right; }
.conf-note {
  display: flex; align-items: flex-start; gap: 6px;
  font-size: 12px; color: #909399;
  background: #f5f7fa; border-radius: 6px;
  padding: 8px 10px; margin-top: 12px;
  line-height: 1.5;
}

/* 使用习惯 */
.habit-card { border-radius: 12px; }
.habit-item {
  display: flex; align-items: center; gap: 14px;
  padding: 16px; background: #fafafa; border-radius: 10px;
}
.habit-icon {
  width: 44px; height: 44px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.habit-value { font-size: 22px; font-weight: 700; color: #303133; }
.habit-label { font-size: 12px; color: #909399; margin-top: 4px; }

/* 记录表 */
.recent-table-card { border-radius: 12px; }
</style>