<template>
  <div class="floating-menu">
    <el-button
      class="menu-toggle"
      :class="{ 'is-active': menuVisible }"
      @click="menuVisible = !menuVisible"
      circle
    >
      <el-icon><Setting /></el-icon>
    </el-button>

    <div v-show="menuVisible" class="menu-panel">
      <div class="menu-panel-inner">
        <div class="menu-title">🎨 界面定制</div>

        <div class="menu-item theme-toggle">
          <span class="item-label"><span class="icon">🌙</span> 夜间模式</span>
          <el-switch v-model="isDarkTheme" @change="toggleTheme" />
        </div>

        <div class="menu-item">
          <span class="item-label"><span class="icon">🖼️</span> 背景图</span>
          <el-upload class="bg-upload" :show-file-list="false" :before-upload="handleBeforeUpload" accept="image/*" action="#">
            <el-button size="small" type="primary" plain>{{ bgConfig.url ? '更换图片' : '选择图片' }}</el-button>
          </el-upload>
          <el-button v-if="bgConfig.url" size="small" type="danger" plain @click="removeBg">移除</el-button>
        </div>

        <div class="menu-item slider-item">
          <span class="item-label">🌫️ 模糊度</span>
          <el-slider v-model="bgConfig.blur" :min="0" :max="20" :step="0.5" :marks="{ '0': '0', '10': '10', '20': '20' }" @change="saveBgConfig" />
        </div>

        <div class="menu-item slider-item">
          <span class="item-label">↔️ X 偏移</span>
          <el-slider v-model="bgConfig.offsetX" :min="-100" :max="100" :step="1" :marks="{ '-100': '-100%', '0': '0%', '100': '100%' }" @change="saveBgConfig" />
        </div>

        <div class="menu-item slider-item">
          <span class="item-label">↕️ Y 偏移</span>
          <el-slider v-model="bgConfig.offsetY" :min="-100" :max="100" :step="1" :marks="{ '-100': '-100%', '0': '0%', '100': '100%' }" @change="saveBgConfig" />
        </div>

        <el-divider />

        <div class="menu-item github-link">
          <a href="https://github.com/your-repo" target="_blank" rel="noopener noreferrer" class="github-btn">
            <el-icon><Link /></el-icon> 访问作者 GitHub
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, inject, watch, onMounted } from 'vue'
import { Setting, Link } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const bgConfig: any = inject('bgConfig', reactive({ url: '', blur: 0, offsetX: 0, offsetY: 0, theme: 'dark' }))
const menuVisible = ref(false)
const isDarkTheme = ref(true)

function toggleTheme(val: boolean) {
  const theme = val ? 'dark' : 'light'
  bgConfig.theme = theme
  saveBgConfig()
  const el = document.documentElement
  if (theme === 'light') {
    el.style.setProperty('--bg-primary', '#f1f5f9')
    el.style.setProperty('--bg-card', 'rgba(255,255,255,0.75)')
    el.style.setProperty('--text-primary', '#1e293b')
    el.style.setProperty('--text-secondary', '#475569')
    el.style.setProperty('--border-color', 'rgba(203, 213, 225, 0.6)')
    el.style.setProperty('--sidebar-bg', 'rgba(255, 255, 255, 0.85)')
  } else {
    el.style.setProperty('--bg-primary', '#0f172a')
    el.style.setProperty('--bg-card', 'rgba(30, 41, 59, 0.8)')
    el.style.setProperty('--text-primary', '#e2e8f0')
    el.style.setProperty('--text-secondary', '#94a3b8')
    el.style.setProperty('--border-color', '#334155')
    el.style.setProperty('--sidebar-bg', 'rgba(30, 41, 59, 0.85)')
  }
}

function handleBeforeUpload(file: File) {
  const reader = new FileReader()
  reader.onload = async (e) => {
    const base64 = e.target?.result as string
    try {
      const fd = new FormData()
      fd.append('image', file)
      const { data } = await axios.post('/api/background/upload', fd)
      bgConfig.url = data.url
      await saveBgConfig()
      ElMessage.success('背景图已更新')
    } catch {
      bgConfig.url = base64
      await saveBgConfig()
      ElMessage.success('背景图已更新（本地）')
    }
  }
  reader.readAsDataURL(file)
  return false
}

async function removeBg() {
  bgConfig.url = ''
  await saveBgConfig()
  ElMessage.info('背景图已移除')
}

async function saveBgConfig() {
  try {
    await axios.put('/api/background/config', {
      url: bgConfig.url,
      blur: bgConfig.blur,
      offsetX: bgConfig.offsetX,
      offsetY: bgConfig.offsetY,
      theme: bgConfig.theme,
    })
  } catch {}
}

function handleClickOutside(e: MouseEvent) {
  if (!(e.target as HTMLElement).closest('.floating-menu')) menuVisible.value = false
}
watch(menuVisible, (val) => {
  if (val) document.addEventListener('click', handleClickOutside)
  else document.removeEventListener('click', handleClickOutside)
})

onMounted(() => {
  isDarkTheme.value = bgConfig.theme !== 'light'
})
</script>

<style scoped>
/* 样式与之前完全相同，无需改动（保持原样） */
.floating-menu {
  position: fixed;
  bottom: 28px;
  left: 28px;
  z-index: 1000;
}
.menu-toggle {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  color: white;
  border: none;
  box-shadow: 0 8px 30px -6px #8b5cf6aa;
  font-size: 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
}
.menu-toggle:hover {
  transform: scale(1.08);
  box-shadow: 0 12px 40px -6px #8b5cf6dd;
}
.menu-toggle.is-active {
  transform: rotate(90deg);
}
.menu-panel {
  position: absolute;
  bottom: 68px;
  left: 0;
  width: 340px;
  max-height: 560px;
  overflow-y: auto;
  background: rgba(15, 23, 42, 0.92);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 92, 246, 0.25);
  border-radius: 20px;
  box-shadow: 0 20px 60px -12px rgba(0, 0, 0, 0.8);
  padding: 4px;
  animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(16px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.menu-panel-inner {
  padding: 20px 22px 18px;
}
.menu-title {
  font-size: 18px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 18px;
  letter-spacing: 0.5px;
}
.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid rgba(51, 65, 85, 0.4);
}
.menu-item:last-of-type {
  border-bottom: none;
}
.item-label {
  color: #cbd5e1;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}
.item-label .icon {
  font-size: 16px;
}
.slider-item {
  flex-direction: column;
  align-items: stretch;
  gap: 6px;
  padding: 12px 0;
}
.slider-item .item-label {
  margin-bottom: 2px;
}
.bg-upload {
  display: inline-block;
}
.bg-upload :deep(.el-upload) {
  display: inline-block;
}
.theme-toggle {
  border-bottom: 1px solid rgba(51, 65, 85, 0.4);
}
.github-link {
  padding-top: 12px;
  border: none;
}
.github-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #94a3b8;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s;
  padding: 6px 12px;
  border-radius: 40px;
  background: rgba(255, 255, 255, 0.04);
  width: 100%;
  justify-content: center;
}
.github-btn:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.08);
}
.menu-panel::-webkit-scrollbar {
  width: 4px;
}
.menu-panel::-webkit-scrollbar-track {
  background: transparent;
}
.menu-panel::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 10px;
}
@media (max-width: 768px) {
  .menu-panel {
    width: 290px;
    left: -10px;
  }
  .floating-menu {
    bottom: 16px;
    left: 16px;
  }
  .menu-toggle {
    width: 44px;
    height: 44px;
    font-size: 20px;
  }
}
</style>