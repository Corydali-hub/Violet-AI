<template>
  <div class="logs-page">
    <h2 class="page-title">📋 实时日志</h2>

    <div class="log-container">
      <div class="log-toolbar">
        <el-button size="small" class="tool-btn" @click="paused = !paused">
          {{ paused ? '▶ 继续' : '⏸ 暂停' }}
        </el-button>
        <el-button size="small" class="tool-btn" @click="logs = []">清空</el-button>
        <span class="log-count">{{ logs.length }} 条</span>
      </div>

      <div ref="container" class="log-output">
        <div v-for="(l, i) in logs" :key="i" class="log-line">{{ l }}</div>
        <div v-if="!logs.length" class="log-empty">等待日志...</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
const logs = ref<string[]>([])
const paused = ref(false)
const container = ref<HTMLElement>()

let ws: WebSocket | null = null

function connect() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws'
  ws = new WebSocket(`${proto}://${location.host}/ws/logs`)
  ws.onmessage = (e) => {
    if (!paused.value) {
      logs.value.push(e.data)
      if (logs.value.length > 500) logs.value.shift()
    }
  }
  ws.onclose = () => setTimeout(connect, 3000)
}

watch(logs, async () => {
  await nextTick()
  if (container.value) container.value.scrollTop = container.value.scrollHeight
})

onMounted(connect)
onUnmounted(() => ws?.close())
</script>

<style scoped>
.logs-page {
  padding: 8px 4px;
}
.page-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 28px;
  background: linear-gradient(135deg, #f0f4ff 0%, #c7d2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.log-container {
  background: var(--bg-card, rgba(30, 41, 59, 0.8));
  backdrop-filter: blur(8px);
  border: 1px solid var(--border-color, #334155);
  border-radius: 16px;
  overflow: hidden;
}
.log-toolbar {
  display: flex;
  gap: 8px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-color, #334155);
  background: rgba(15, 23, 42, 0.4);
  flex-wrap: wrap;
}
.tool-btn {
  border-radius: 30px;
  border-color: var(--border-color, #334155);
  color: var(--text-secondary, #94a3b8);
  transition: all 0.2s;
}
.tool-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--text-secondary, #64748b);
  color: var(--text-primary, #e2e8f0);
}
.log-count {
  color: var(--text-secondary, #64748b);
  font-size: 13px;
  line-height: 32px;
  margin-left: auto;
}
.log-output {
  height: 500px;
  overflow-y: auto;
  background: var(--bg-primary, #0f172a);
  padding: 16px 20px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.7;
}
.log-line {
  color: var(--text-secondary, #94a3b8);
  white-space: pre-wrap;
  word-break: break-all;
  padding: 2px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.02);
}
.log-line:last-child {
  border-bottom: none;
}
.log-empty {
  color: var(--text-secondary, #64748b);
  text-align: center;
  padding: 40px 0;
}
.log-output::-webkit-scrollbar { width: 6px; }
.log-output::-webkit-scrollbar-track { background: transparent; }
.log-output::-webkit-scrollbar-thumb { background: var(--border-color, #334155); border-radius: 10px; }
.log-output::-webkit-scrollbar-thumb:hover { background: var(--text-secondary, #475569); }
</style>