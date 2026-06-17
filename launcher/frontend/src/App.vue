<template>
  <div class="app-wrapper" :class="themeClass">
    <!-- 全局背景层 -->
    <div class="global-background" :style="backgroundStyle"></div>

    <!-- 主布局 -->
    <el-container class="main-container" style="min-height: 100vh; color: #e2e8f0">
      <el-aside width="220px" class="app-sidebar">
        <div class="brand">
          <img src="/logo.png" alt="堇言AI" class="brand-logo" />
          <h2 class="brand-title">堇言AI</h2>
          <p style="color: var(--text-secondary, #94a3b8); font-size: 12px">AI 猫娘管理后台</p>
        </div>
        <el-menu
          :default-active="route.path"
          router
          background-color="transparent"
          text-color="var(--text-secondary, #cbd5e1)"
          active-text-color="#f472b6"
        >
          <el-menu-item index="/"><el-icon><Monitor /></el-icon> 控制台</el-menu-item>
          <el-menu-item index="/qr"><el-icon><Picture /></el-icon> QQ 二维码</el-menu-item>
          <el-menu-item index="/groups"><el-icon><ChatDotRound /></el-icon> 群管理</el-menu-item>
          <el-menu-item index="/logs"><el-icon><Document /></el-icon> 实时日志</el-menu-item>
          <el-menu-item index="/setup"><el-icon><Setting /></el-icon> 设置</el-menu-item>
        </el-menu>
      </el-aside>

      <el-main style="padding: 24px; position: relative; z-index: 10">
        <router-view />
        <!-- 全局浮动菜单 -->
        <BackgroundMenu />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed, ref, reactive, onMounted, provide, watch } from 'vue'
import axios from 'axios'
import BackgroundMenu from './components/BackgroundMenu.vue'
import { Monitor, Picture, ChatDotRound, Document, Setting } from '@element-plus/icons-vue'

// ===== 背景配置 =====
const bgConfig = reactive({
  url: '',
  blur: 0,
  offsetX: 0,
  offsetY: 0,
  theme: 'dark',
})

// 加载已保存的配置
async function loadBgConfig() {
  try {
    const { data } = await axios.get('/api/background/config')
    bgConfig.url = data.url || ''
    bgConfig.blur = data.blur ?? 0
    bgConfig.offsetX = data.offsetX ?? 0
    bgConfig.offsetY = data.offsetY ?? 0
    bgConfig.theme = data.theme || 'dark'
    applyTheme(bgConfig.theme)
  } catch {}
}

// 应用主题
function applyTheme(theme: string) {
  const el = document.documentElement
  if (theme === 'light') {
    el.style.setProperty('--bg-primary', '#f1f5f9')
    el.style.setProperty('--bg-card', 'rgba(255,255,255,0.75)')
    el.style.setProperty('--text-primary', '#1e293b')
    el.style.setProperty('--text-secondary', '#475569')
    el.style.setProperty('--border-color', 'rgba(203, 213, 225, 0.6)')
    el.style.setProperty('--sidebar-bg', 'rgba(255, 255, 255, 0.85)')  // ← 新增
  } else {
    el.style.setProperty('--bg-primary', '#0f172a')
    el.style.setProperty('--bg-card', 'rgba(30, 41, 59, 0.8)')
    el.style.setProperty('--text-primary', '#e2e8f0')
    el.style.setProperty('--text-secondary', '#94a3b8')
    el.style.setProperty('--border-color', '#334155')
    el.style.setProperty('--sidebar-bg', 'rgba(30, 41, 59, 0.85)')  // ← 新增
  }
}

const route = useRoute()
const themeClass = computed(() => bgConfig.theme === 'light' ? 'theme-light' : 'theme-dark')

// 背景样式（使用更大的偏移范围）
const backgroundStyle = computed(() => {
  const url = bgConfig.url
  if (!url) return { background: 'var(--bg-primary)' }
  return {
    backgroundImage: `url(${url})`,
    backgroundSize: 'cover',
    backgroundPosition: `calc(50% + ${bgConfig.offsetX}%) calc(50% + ${bgConfig.offsetY}%)`,
    filter: `blur(${bgConfig.blur}px)`,
  }
})

// 提供给子组件
provide('bgConfig', bgConfig)
provide('reloadBgConfig', loadBgConfig)

onMounted(() => {
  loadBgConfig()
})
</script>

<style>
/* ===== 全局 CSS 变量 ===== */
:root {
  --bg-primary: #0f172a;
  --bg-card: rgba(30, 41, 59, 0.8);
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --border-color: #334155;
  --sidebar-bg: rgba(30, 41, 59, 0.85);
}
.theme-light {
  --bg-primary: #f1f5f9;
  --bg-card: rgba(255, 255, 255, 0.75);
  --text-primary: #1e293b;
  --text-secondary: #475569;
  --border-color: rgba(203, 213, 225, 0.6);
  --sidebar-bg: rgba(255, 255, 255, 0.85);
}
* {
  transition: background-color 0.4s ease, color 0.3s ease, border-color 0.3s ease;
}
</style>

<style scoped>
.app-wrapper {
  position: relative;
  min-height: 100vh;
  background: var(--bg-primary);
}

/* ===== 全局背景层 ===== */
.global-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  background-color: var(--bg-primary);
  background-size: cover;
  background-position: center;
  transition: filter 0.3s ease, background-position 0.3s ease;
}

/* ===== 主容器 ===== */
.main-container {
  position: relative;
  z-index: 1;
  min-height: 100vh;
}

/* ===== 侧边栏 ===== */
.app-sidebar {
  background: var(--sidebar-bg) !important;
  backdrop-filter: blur(12px);
  border-right: 1px solid var(--border-color) !important;
  transition: background 0.4s ease, border-color 0.3s ease;
}

/* ===== 左侧品牌 ===== */
.brand {
  padding: 20px;
  text-align: center;
}
.brand-logo {
  width: 112px;
  height: 112px;
  border-radius: 14px;
  margin-bottom: 8px;
}
.brand-title {
  margin: 10px 0 0;
  font-size: 30px;
  font-weight: 800;
  background: linear-gradient(135deg, #8b5cf6, #a78bfa, #c084fc, #8b5cf6);
  background-size: 300% 300%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradient-shift 3s ease infinite;
}
@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* ===== 菜单透明化 ===== */
:deep(.el-menu) {
  border-right: none !important;
}
:deep(.el-menu-item) {
  border-radius: 8px;
  margin: 0 8px 2px;
}
:deep(.el-menu-item.is-active) {
  background: rgba(244, 114, 182, 0.15) !important;
}
</style>