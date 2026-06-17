<template>
  <div class="groups-page">
    <div class="page-header">
      <h2 class="page-title">💬 群管理</h2>
      <div class="header-actions">
        <el-button type="warning" @click="pauseAll" :loading="pausingAll" plain>
          🔇 全部静音
        </el-button>
        <el-button type="success" @click="activeAll" :loading="activingAll" plain>
          🔊 全部活跃
        </el-button>
        <el-button class="refresh-btn" @click="load" :loading="loading" plain>
          <span v-if="!loading">⟳ 刷新</span>
          <span v-else>加载中...</span>
        </el-button>
      </div>
    </div>

    <!-- 搜索框 -->
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="输入群名或群号查找"
        clearable
        prefix-icon="Search"
        style="max-width: 360px;"
      />
    </div>

    <el-row :gutter="20" class="group-grid">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="g in filteredGroups" :key="g.group_id">
        <div class="group-card" @click="router.push(`/groups/${g.group_id}`)">
          <div class="card-top">
            <el-avatar
              :size="48"
              class="group-avatar"
              :src="`https://p.qlogo.cn/gh/${g.group_id}/${g.group_id}/0`"
            >
              {{ g.group_name?.charAt(0) || '群' }}
            </el-avatar>
            <div class="group-info">
              <div class="group-name">{{ g.group_name || '未知群' }}</div>
              <div class="group-id">{{ g.group_id }}</div>
            </div>
          </div>
          <div class="card-bottom">
            <span class="tag" :class="stateCache[g.group_id]?.paused ? 'tag-off' : 'tag-on'">
              {{ stateCache[g.group_id]?.paused ? '🔇 静音' : '🟢 活跃' }}
            </span>
            <span class="tag">
              🐱 {{ stateCache[g.group_id]?.persona === 'tsundere' ? '傲娇' : '猫娘' }}
            </span>
            <span class="tag" v-if="stateCache[g.group_id]?.scholar">
              📖 博学
            </span>
          </div>
          <div class="card-glow"></div>
        </div>
      </el-col>
    </el-row>

    <el-empty v-if="!loading && !filteredGroups.length" :description="searchKeyword ? '未找到匹配的群' : '暂无群数据，请确认机器人已启动'">
      <el-button @click="load">重试</el-button>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const groups = ref<any[]>([])
const stateCache = ref<Record<string, any>>({})
const loading = ref(false)
const searchKeyword = ref('')
const pausingAll = ref(false)
const activingAll = ref(false)
let pollTimer = 0

// 计算过滤后的群列表
const filteredGroups = computed(() => {
  const kw = searchKeyword.value.trim().toLowerCase()
  if (!kw) return groups.value
  return groups.value.filter(g => {
    const name = (g.group_name || '').toLowerCase()
    const id = String(g.group_id)
    return name.includes(kw) || id.includes(kw)
  })
})

async function load() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/groups')
    groups.value = data
    for (const g of data) {
      try {
        const { data: s } = await axios.get(`/api/groups/${g.group_id}/state`)
        stateCache.value[g.group_id] = s
      } catch {}
    }
  } catch {}
  loading.value = false
}

// 全部静音
async function pauseAll() {
  pausingAll.value = true
  try {
    const { data } = await axios.post('/api/groups/all/pause')
    ElMessage.success(`已静音 ${data.count} 个群`)
    await load()
  } catch {
    ElMessage.error('操作失败')
  } finally {
    pausingAll.value = false
  }
}

// 全部活跃
async function activeAll() {
  activingAll.value = true
  try {
    const { data } = await axios.post('/api/groups/all/active')
    ElMessage.success(`已激活 ${data.count} 个群`)
    await load()
  } catch {
    ElMessage.error('操作失败')
  } finally {
    activingAll.value = false
  }
}

onMounted(() => {
  load()
  pollTimer = window.setInterval(load, 5000)  // 每5秒刷新群状态
})
onUnmounted(() => clearInterval(pollTimer))
</script>

<style scoped>
.groups-page {
  padding: 8px 4px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
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
.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.refresh-btn,
.header-actions .el-button {
  border-radius: 40px;
  border-color: var(--border-color, #334155);
  color: var(--text-secondary, #94a3b8);
  transition: all 0.25s;
}
.refresh-btn:hover,
.header-actions .el-button:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--text-secondary, #64748b);
  color: var(--text-primary, #e2e8f0);
}
.header-actions .el-button--warning {
  border-color: #f59e0b66;
  color: #fbbf24;
}
.header-actions .el-button--warning:hover {
  background: #f59e0b22;
  border-color: #f59e0b;
}
.header-actions .el-button--success {
  border-color: #4ade8066;
  color: #4ade80;
}
.header-actions .el-button--success:hover {
  background: #4ade8022;
  border-color: #4ade80;
}
.search-bar {
  margin-bottom: 20px;
}
.group-grid {
  margin: -10px;
}
.group-card {
  position: relative;
  background: var(--bg-card, rgba(30, 41, 59, 0.8));
  backdrop-filter: blur(8px);
  border: 1px solid var(--border-color, #334155);
  border-radius: 16px;
  padding: 18px 16px;
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  height: 130px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.group-card:hover {
  transform: translateY(-4px);
  border-color: #4ade8066;
  box-shadow: 0 12px 30px -8px rgba(0, 0, 0, 0.6);
}
.group-card .card-glow {
  position: absolute;
  top: -40%;
  right: -20%;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, #4ade8033 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.5s;
}
.group-card:hover .card-glow {
  opacity: 1;
}
.card-top {
  display: flex;
  align-items: center;
  gap: 14px;
}
.group-avatar {
  flex-shrink: 0;
  background: linear-gradient(135deg, #f472b6, #c084fc) !important;
  color: #fff;
  font-weight: 700;
  font-size: 18px;
}
.group-avatar :deep(img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}
.group-info {
  flex: 1;
  min-width: 0;
}
.group-name {
  color: var(--text-primary, #e2e8f0);
  font-weight: 600;
  font-size: 16px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.group-id {
  color: var(--text-secondary, #64748b);
  font-size: 12px;
  margin-top: 2px;
}
.card-bottom {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}
.tag {
  font-size: 12px;
  padding: 2px 12px;
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--border-color, #334155);
  color: var(--text-secondary, #94a3b8);
  line-height: 24px;
  transition: all 0.2s;
}
.tag-on {
  color: #4ade80;
  border-color: #4ade8066;
}
.tag-off {
  color: #f87171;
  border-color: #f8717166;
}
</style>