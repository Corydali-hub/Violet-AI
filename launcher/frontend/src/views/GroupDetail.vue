<template>
  <div class="detail-page">
    <div class="detail-header">
      <el-button class="back-btn" @click="router.push('/groups')" text>
        ← 返回群列表
      </el-button>
      <div class="group-info-wrap">
        <el-avatar
          :size="56"
          class="detail-avatar"
          :src="`https://p.qlogo.cn/gh/${gid}/${gid}/0`"
        >
          {{ group?.group_name?.charAt(0) || '群' }}
        </el-avatar>
        <div class="group-meta">
          <h2 class="detail-title">{{ group?.group_name || '群详情' }}</h2>
          <span class="group-id-label">群号：{{ gid }}</span>
        </div>
      </div>
    </div>

    <div class="setting-grid-flex">
      <div class="setting-item">
        <div class="setting-card">
          <div class="card-header"><span class="card-icon">🐱</span> 人格模式</div>
          <el-radio-group v-model="state.persona" @change="save" class="radio-group">
            <el-radio value="catgirl">乖巧猫娘</el-radio>
            <el-radio value="tsundere">毒舌傲娇 😈</el-radio>
          </el-radio-group>
        </div>
      </div>

      <div class="setting-item">
        <div class="setting-card">
          <div class="card-header"><span class="card-icon">📖</span> 博学模式</div>
          <div class="switch-wrapper">
            <el-switch v-model="state.scholar" @change="save" />
            <span class="switch-label" :class="{ 'is-active': state.scholar }">
              {{ state.scholar ? '已开启' : '已关闭' }}
            </span>
          </div>
        </div>
      </div>

      <div class="setting-item">
        <div class="setting-card">
          <div class="card-header"><span class="card-icon">🔇</span> 静音模式</div>
          <div class="switch-wrapper">
            <el-switch v-model="state.paused" @change="save" />
            <span class="switch-label" :class="{ 'is-active': state.paused }">
              {{ state.paused ? '已静音' : '正常运行' }}
            </span>
          </div>
        </div>
      </div>

      <div class="setting-item" v-if="state.persona === 'tsundere'">
        <div class="setting-card">
          <div class="card-header"><span class="card-icon">🎯</span> 毒舌目标</div>
          <div class="input-group">
            <el-input v-model="state.target" placeholder="输入目标 QQ 号" clearable />
            <el-button class="save-target-btn" @click="save">保存</el-button>
          </div>
        </div>
      </div>

      <div class="setting-item" v-if="state.persona !== 'tsundere'">
        <div class="setting-card placeholder-card">
          <div class="card-header"><span class="card-icon">✨</span> 更多功能</div>
          <div class="placeholder-text">切换「毒舌傲娇」人格解锁专属设置</div>
        </div>
      </div>
    </div>

    <div class="memory-card">
      <div class="memory-header">
        <span class="card-icon">🧠</span> 记忆管理
        <span class="memory-badge">{{ state.memory_count || 0 }} 条</span>
      </div>
      <div class="memory-body">
        <span class="memory-hint">记忆条数较多时，可清空以释放上下文空间</span>
        <el-button type="danger" size="small" @click="clearMemory">清空记忆</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const gid = route.params.gid as string
const group = ref<any>({})
const state = ref({
  persona: 'catgirl',
  target: '',
  scholar: false,
  paused: false,
  memory_count: 0,
})
let pollTimer = 0

async function load() {
  try {
    const { data } = await axios.get(`/api/groups/${gid}/state`)
    state.value = data
  } catch {}
  try {
    const { data: groups } = await axios.get('/api/groups')
    group.value = groups.find((g: any) => String(g.group_id) === gid) || {}
  } catch {}
}

async function save() {
  try {
    await axios.put(`/api/groups/${gid}/state`, state.value)
    ElMessage.success('已保存')
  } catch {
    ElMessage.error('保存失败')
  }
}

async function clearMemory() {
  try {
    await axios.post(`/api/groups/${gid}/state`, { ...state.value, memory_clear: true })
    ElMessage.success('已清空')
  } catch {
    ElMessage.error('清空失败')
  }
}

onMounted(() => {
  load()
  pollTimer = window.setInterval(load, 3000)  // 每3秒拉取最新状态
})
onUnmounted(() => clearInterval(pollTimer))
</script>

<style scoped>
.detail-page {
  padding: 8px 4px;
  max-width: 960px;
  margin: 0 auto;
}
.detail-header {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}
.back-btn {
  color: var(--text-secondary, #94a3b8) !important;
  font-weight: 500;
  font-size: 14px;
  padding: 0 4px;
  transition: color 0.2s;
}
.back-btn:hover {
  color: var(--text-primary, #e2e8f0) !important;
}
.group-info-wrap {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}
.detail-avatar {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #f472b6, #c084fc) !important;
  color: #fff;
  font-weight: 700;
  font-size: 20px;
}
.detail-avatar :deep(img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}
.group-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.detail-title {
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #f0f4ff 0%, #c7d2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.3;
}
.group-id-label {
  color: var(--text-secondary, #64748b);
  font-size: 13px;
  letter-spacing: 0.3px;
}
.setting-grid-flex {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
}
.setting-item {
  flex: 1 1 calc(50% - 10px);
  min-width: 200px;
  display: flex;
}
.setting-card {
  width: 100%;
  background: var(--bg-card, rgba(30, 41, 59, 0.7));
  backdrop-filter: blur(8px);
  border: 1px solid var(--border-color, #334155);
  border-radius: 16px;
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  transition: border-color 0.3s, box-shadow 0.3s;
}
.setting-card:hover {
  border-color: var(--text-secondary, #64748b);
  box-shadow: 0 4px 20px -8px rgba(0, 0, 0, 0.4);
}
.card-header {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #e2e8f0);
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 0.3px;
}
.card-icon {
  font-size: 18px;
  line-height: 1;
}
.radio-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  justify-content: center;
}
.radio-group :deep(.el-radio) {
  color: var(--text-secondary, #cbd5e1) !important;
  height: 32px;
  display: flex;
  align-items: center;
}
.radio-group :deep(.el-radio__input.is-checked .el-radio__inner) {
  background: #8b5cf6;
  border-color: #8b5cf6;
}
.radio-group :deep(.el-radio__input.is-checked + .el-radio__label) {
  color: var(--text-primary, #e2e8f0) !important;
}
.switch-wrapper {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
}
.switch-wrapper :deep(.el-switch) {
  --el-switch-on-color: #4ade80;
  --el-switch-off-color: #475569;
}
.switch-wrapper :deep(.el-switch__core) {
  border-radius: 40px;
  height: 22px;
  width: 44px;
}
.switch-wrapper :deep(.el-switch__core .el-switch__action) {
  width: 18px;
  height: 18px;
}
.switch-label {
  font-size: 14px;
  color: var(--text-secondary, #64748b);
  transition: color 0.25s;
}
.switch-label.is-active {
  color: #4ade80;
  font-weight: 500;
}
.input-group {
  display: flex;
  gap: 10px;
  align-items: center;
  flex: 1;
}
.input-group :deep(.el-input__wrapper) {
  background: var(--bg-primary, #0f172a);
  border-radius: 40px;
  box-shadow: none;
  border: 1px solid var(--border-color, #334155);
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input-group :deep(.el-input__wrapper:hover) {
  border-color: var(--text-secondary, #64748b);
}
.input-group :deep(.el-input__wrapper.is-focus) {
  border-color: #8b5cf6;
  box-shadow: 0 0 0 2px #8b5cf644;
}
.input-group :deep(.el-input__inner) {
  color: var(--text-primary, #e2e8f0);
}
.input-group :deep(.el-input__inner::placeholder) {
  color: var(--text-secondary, #64748b);
}
.save-target-btn {
  border-radius: 30px;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  color: white;
  border: none;
  padding: 0 22px;
  height: 36px;
  font-weight: 500;
  transition: all 0.25s;
  flex-shrink: 0;
}
.save-target-btn:hover {
  transform: scale(1.04);
  box-shadow: 0 6px 20px -4px #8b5cf6aa;
}
.placeholder-card {
  border-style: dashed;
  border-color: var(--border-color, #33415566);
  opacity: 0.7;
  justify-content: center;
}
.placeholder-text {
  color: var(--text-secondary, #64748b);
  font-size: 13px;
  line-height: 1.5;
}
.memory-card {
  background: var(--bg-card, rgba(30, 41, 59, 0.7));
  backdrop-filter: blur(8px);
  border: 1px solid var(--border-color, #334155);
  border-radius: 16px;
  padding: 18px 22px;
  margin-top: 10px;
  transition: border-color 0.3s;
}
.memory-card:hover {
  border-color: var(--text-secondary, #64748b);
}
.memory-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #e2e8f0);
  margin-bottom: 12px;
}
.memory-badge {
  margin-left: auto;
  background: rgba(100, 116, 139, 0.25);
  padding: 2px 14px;
  border-radius: 30px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary, #94a3b8);
}
.memory-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.memory-hint {
  color: var(--text-secondary, #94a3b8);
  font-size: 13px;
}
.memory-card .el-button--danger {
  border-radius: 30px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  border: none;
  padding: 8px 24px;
  font-weight: 500;
  transition: all 0.25s;
}
.memory-card .el-button--danger:hover {
  transform: scale(1.04);
  box-shadow: 0 6px 20px -4px #ef4444aa;
}
@media (max-width: 640px) {
  .detail-header { gap: 12px; }
  .group-info-wrap { gap: 12px; }
  .detail-avatar { width: 44px; height: 44px; font-size: 16px; }
  .detail-title { font-size: 18px; }
  .setting-item { flex: 1 1 100%; }
  .setting-card { padding: 16px 18px; }
  .memory-body { flex-direction: column; align-items: stretch; }
  .memory-card .el-button--danger { width: 100%; justify-content: center; }
}
</style>