<template>
  <div class="qr-page">
    <h2 class="page-title">📱 QQ 登录二维码</h2>

    <div class="qr-card">
      <div class="qr-image-wrapper">
        <img :src="'/api/qrcode?' + ts" alt="QR Code" class="qr-image" />
        <div class="qr-status">
          <span class="status-dot" :class="statusClass"></span>
          {{ statusText }}
        </div>
      </div>
      <el-button class="refresh-qr-btn" @click="refresh" :loading="refreshing" plain>
        ⟳ 刷新二维码
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import axios from 'axios'

const ts = ref(Date.now())
const status = ref({ napcat_running: false, napcat_logged: false })
const refreshing = ref(false)
let timer = 0

const statusClass = computed(() => ({
  'status-on': status.value.napcat_logged,
  'status-wait': status.value.napcat_running && !status.value.napcat_logged,
  'status-off': !status.value.napcat_running,
}))
const statusText = computed(() => {
  if (status.value.napcat_logged) return '已登录'
  if (status.value.napcat_running) return '等待扫码...'
  return 'NapCat 未运行'
})

async function loadStatus() {
  try {
    const { data } = await axios.get('/api/status')
    status.value = data
  } catch {}
}

function refresh() {
  refreshing.value = true
  ts.value = Date.now()
  setTimeout(() => (refreshing.value = false), 500)
}

onMounted(() => {
  loadStatus()
  timer = window.setInterval(loadStatus, 3000)
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.qr-page {
  padding: 8px 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.page-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 28px;
  background: linear-gradient(135deg, #f0f4ff 0%, #c7d2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-align: center;
}
.qr-card {
  background: var(--bg-card, rgba(30, 41, 59, 0.8));
  backdrop-filter: blur(8px);
  border: 1px solid var(--border-color, #334155);
  border-radius: 24px;
  padding: 30px 40px 40px;
  max-width: 360px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: border-color 0.3s;
  box-shadow: 0 12px 40px -12px rgba(0, 0, 0, 0.6);
}
.qr-card:hover {
  border-color: var(--text-secondary, #64748b);
}
.qr-image-wrapper {
  position: relative;
  margin-bottom: 24px;
}
.qr-image {
  width: 220px;
  height: 220px;
  border-radius: 16px;
  background: var(--bg-primary, #0f172a);
  border: 2px solid var(--border-color, #334155);
  transition: border-color 0.3s;
}
.qr-image:hover {
  border-color: #8b5cf6;
}
.qr-status {
  margin-top: 16px;
  font-size: 14px;
  color: var(--text-secondary, #94a3b8);
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}
.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}
.status-on {
  background: #4ade80;
  box-shadow: 0 0 12px #4ade80aa;
}
.status-wait {
  background: #fbbf24;
  box-shadow: 0 0 12px #fbbf24aa;
}
.status-off {
  background: #64748b;
}
.refresh-qr-btn {
  border-radius: 40px;
  border-color: var(--border-color, #334155);
  color: var(--text-secondary, #94a3b8);
  padding: 10px 30px;
  transition: all 0.25s;
}
.refresh-qr-btn:hover {
  border-color: #8b5cf6;
  color: var(--text-primary, #e2e8f0);
  background: rgba(139, 92, 246, 0.1);
}
</style>