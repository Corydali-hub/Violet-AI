<template>
  <div class="dashboard">
    <!-- 头部区域 -->
    <div class="dashboard-header">
      <div class="header-left">
        <h2 class="page-title">🐱 控制台</h2>
        <span class="status-badge" :class="statusClass">
          <span class="dot"></span>
          {{ statusText }}
        </span>
      </div>
      <div class="header-right">
        <el-tag size="large" type="info" hit>v2.0.0</el-tag>
      </div>
    </div>

    <!-- 状态卡片 -->
    <el-row :gutter="20" class="card-row">
      <el-col :xs="24" :sm="8" v-for="c in cards" :key="c.label">
        <div class="stat-card" :style="{'--card-color': c.color}">
          <div class="card-icon">{{ c.icon }}</div>
          <div class="card-content">
            <div class="card-label">{{ c.label }}</div>
            <div class="card-value" :style="{color: c.color}">{{ c.value }}</div>
          </div>
          <div class="card-glow"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 控制面板 -->
    <el-card class="control-panel" shadow="never">
      <template #header>
        <div class="panel-header">
          <span class="panel-title">⚙️ 机器人控制</span>
          <el-tag size="small" :type="status.bot_running ? 'success' : 'danger'" effect="plain">
            {{ status.bot_running ? '在线' : '离线' }}
          </el-tag>
        </div>
      </template>
      <div class="control-buttons">
        <el-button
          type="primary"
          size="large"
          class="ctrl-btn start-btn"
          @click="act('start')"
          :loading="loading==='start'"
          :disabled="loading!==''"
        >
          <el-icon><VideoPlay /></el-icon> 启动
        </el-button>
        <el-button
          size="large"
          class="ctrl-btn restart-btn"
          @click="act('restart')"
          :loading="loading==='restart'"
          :disabled="loading!==''"
        >
          <el-icon><Refresh /></el-icon> 重启
        </el-button>
        <el-button
          type="danger"
          size="large"
          class="ctrl-btn stop-btn"
          @click="act('stop')"
          :loading="loading==='stop'"
          :disabled="loading!==''"
        >
          <el-icon><VideoPause /></el-icon> 停止
        </el-button>
      </div>
      <div class="panel-footer">
        <span class="hint">💡 系统将自动检测 QQ 登录状态并尝试启动 Bot</span>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import axios from 'axios'
import { VideoPlay, Refresh, VideoPause } from '@element-plus/icons-vue'

// ===== Bot 状态 =====
const status = ref({ bot_running: false, napcat_running: false, napcat_logged: false })
const loading = ref('')
let timer = 0

const cards = computed(() => [
  {
    icon: '🐱',
    label: 'Bot 状态',
    value: status.value.bot_running ? '运行中' : '已停止',
    color: status.value.bot_running ? '#4ade80' : '#f87171'
  },
  {
    icon: '🔌',
    label: 'QQ 连接',
    value: status.value.napcat_logged ? 'QQ状态' : status.value.napcat_running ? '等待扫码' : '未启动',
    color: status.value.napcat_logged ? '#4ade80' : status.value.napcat_running ? '#fbbf24' : '#64748b'
  },
  {
    icon: '🧠',
    label: 'LLM 大脑',
    value: '已配置',
    color: '#c084fc'
  },
])

const statusClass = computed(() => ({
  online: status.value.bot_running,
  offline: !status.value.bot_running
}))

const statusText = computed(() => status.value.bot_running ? '运行中' : '已停止')

// ===== Bot 控制 =====
async function refresh() {
  try {
    const { data } = await axios.get('/api/status')
    status.value = data
  } catch {}
  if (status.value.napcat_logged && !status.value.bot_running && !loading.value) {
    try {
      await axios.post('/api/bot/start')
    } catch {}
  }
}

async function act(type: string) {
  loading.value = type
  await axios.post(`/api/bot/${type}`).catch(() => {})
  for (let i = 0; i < 15; i++) {
    await new Promise(r => setTimeout(r, 1000))
    await refresh()
    if (status.value.napcat_running) break
  }
  loading.value = ''
}

onMounted(() => {
  refresh()
  timer = window.setInterval(refresh, 5000)
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.dashboard {
  padding: 8px 4px;
  position: relative;
}

/* ---- 头部 ---- */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 12px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 18px;
}
.page-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #f0f4ff 0%, #c7d2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.5px;
}
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 14px 4px 10px;
  border-radius: 30px;
  font-size: 13px;
  font-weight: 500;
  background: var(--bg-card, rgba(30, 41, 59, 0.7));
  backdrop-filter: blur(4px);
  border: 1px solid var(--border-color, #334155);
  color: var(--text-secondary, #94a3b8);
}
.status-badge .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}
.status-badge.online .dot {
  background: #4ade80;
  box-shadow: 0 0 8px #4ade80;
}
.status-badge.offline .dot {
  background: #f87171;
  box-shadow: 0 0 8px #f87171;
}
.status-badge.online {
  border-color: #4ade8066;
  color: #4ade80;
}
.status-badge.offline {
  border-color: #f8717166;
  color: #f87171;
}
.header-right .el-tag {
  background: var(--bg-card, rgba(30, 41, 59, 0.6));
  border-color: var(--border-color, #334155);
  color: var(--text-secondary, #94a3b8);
}

/* ---- 卡片 ---- */
.card-row {
  margin-bottom: 28px;
}
.stat-card {
  position: relative;
  background: var(--bg-card, #1e293b);
  backdrop-filter: blur(8px);
  border-radius: 16px;
  padding: 20px 18px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid var(--border-color, #334155);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  height: 110px;
}
.stat-card:hover {
  transform: translateY(-3px);
  border-color: v-bind('cards[0].color + "66"');
  box-shadow: 0 12px 30px -10px rgba(0,0,0,0.5);
}
.stat-card .card-glow {
  position: absolute;
  top: -50%;
  right: -20%;
  width: 120px;
  height: 120px;
  background: radial-gradient(circle, var(--card-color) 0%, transparent 70%);
  opacity: 0.08;
  border-radius: 50%;
  pointer-events: none;
  transition: opacity 0.4s;
}
.stat-card:hover .card-glow {
  opacity: 0.18;
}
.card-icon {
  font-size: 38px;
  line-height: 1;
  flex-shrink: 0;
  width: 56px;
  text-align: center;
}
.card-content {
  flex: 1;
  min-width: 0;
}
.card-label {
  font-size: 14px;
  color: var(--text-secondary, #94a3b8);
  font-weight: 500;
  letter-spacing: 0.3px;
  margin-bottom: 4px;
}
.card-value {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
  text-shadow: 0 0 20px var(--card-color);
  letter-spacing: 0.3px;
}

/* ---- 控制面板 ---- */
.control-panel {
  background: var(--bg-card, #1e293b);
  backdrop-filter: blur(8px);
  border: 1px solid var(--border-color, #334155);
  border-radius: 16px;
  overflow: hidden;
}
.control-panel :deep(.el-card__header) {
  border-bottom: 1px solid var(--border-color, #334155);
  padding: 16px 24px;
  background: rgba(15, 23, 42, 0.3);
}
.control-panel :deep(.el-card__body) {
  padding: 24px;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #e2e8f0);
  letter-spacing: 0.5px;
}
.control-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 16px;
}
.ctrl-btn {
  flex: 1 1 auto;
  min-width: 120px;
  border-radius: 60px;
  font-weight: 600;
  font-size: 16px;
  padding: 14px 28px;
  transition: all 0.25s ease;
  border: none;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  letter-spacing: 0.5px;
}
.ctrl-btn .el-icon {
  margin-right: 6px;
  font-size: 18px;
}
.ctrl-btn:active {
  transform: scale(0.96);
}
.start-btn {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
}
.start-btn:hover {
  box-shadow: 0 8px 25px -5px #22c55e80;
  transform: translateY(-2px);
}
.restart-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}
.restart-btn:hover {
  box-shadow: 0 8px 25px -5px #f59e0b80;
  transform: translateY(-2px);
}
.stop-btn {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}
.stop-btn:hover {
  box-shadow: 0 8px 25px -5px #ef444480;
  transform: translateY(-2px);
}
.ctrl-btn:disabled {
  opacity: 0.5;
  transform: none !important;
  box-shadow: none !important;
}
.panel-footer {
  padding-top: 12px;
  border-top: 1px solid var(--border-color, #334155);
  display: flex;
  justify-content: flex-end;
}
.hint {
  font-size: 13px;
  color: var(--text-secondary, #64748b);
  letter-spacing: 0.3px;
}

/* ---- 响应式 ---- */
@media (max-width: 768px) {
  .stat-card {
    height: 100px;
    padding: 16px;
  }
  .card-icon {
    font-size: 30px;
    width: 44px;
  }
  .card-value {
    font-size: 20px;
  }
  .ctrl-btn {
    min-width: 100px;
    padding: 12px 18px;
    font-size: 14px;
  }
}
</style>