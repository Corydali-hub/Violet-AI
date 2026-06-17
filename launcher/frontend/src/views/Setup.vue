<template>
  <div class="setup-page">
    <h2 class="page-title">⚙️ 设置</h2>

    <div class="setup-card">
      <div class="card-header">🧠 LLM 配置</div>
      <el-form label-position="top" class="setup-form">
        <el-form-item label="API Key">
          <el-input v-model="form.llm_api_key" type="password" show-password placeholder="sk-..." />
        </el-form-item>
        <el-form-item label="API Base">
          <el-input v-model="form.llm_api_base" placeholder="https://api.deepseek.com/v1" />
        </el-form-item>
        <el-form-item label="模型">
          <el-input v-model="form.llm_model" placeholder="deepseek-chat" />
        </el-form-item>
      </el-form>
    </div>

    <div class="setup-card">
      <div class="card-header">🤖 机器人配置</div>
      <el-form label-position="top" class="setup-form">
        <el-form-item label="Bot 名称">
          <el-input v-model="form.bot_name" placeholder="我的Bot" />
        </el-form-item>
        <el-form-item label="主人 QQ">
          <el-input v-model="form.bot_owner" placeholder="123456789" />
        </el-form-item>
        <el-form-item label="主人称呼">
          <el-input v-model="form.bot_owner_title" placeholder="主人 / 姐姐 / 老大" />
        </el-form-item>
        <el-form-item label="NapCat 路径">
          <el-input v-model="form.napcat_path" placeholder="E:/path/to/napcat" />
        </el-form-item>
        <el-form-item label="OneBot WS 地址">
          <el-input v-model="form.bot_ws_url" placeholder="ws://localhost:8080" />
        </el-form-item>
      </el-form>
    </div>

    <div class="save-wrapper">
      <el-button class="save-btn" @click="save" :loading="saving">💾 保存配置</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const saving = ref(false)
const form = reactive({
  llm_api_key: '',
  llm_api_base: '',
  llm_model: '',
  bot_name: '',
  bot_owner: '',
  bot_owner_title: '',     // 新增：主人称呼
  napcat_path: '',
  bot_ws_url: '',
})

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/config')
    form.llm_api_key = data.llm?.api_key || ''
    form.llm_api_base = data.llm?.api_base || ''
    form.llm_model = data.llm?.model || ''
    form.bot_name = data.bot?.bot_name || ''
    form.bot_owner = data.bot?.owner || ''
    form.bot_owner_title = data.bot?.owner_title || ''   // 新增
    form.napcat_path = data.napcat?.path || ''
    form.bot_ws_url = data.bot?.ws_url || ''
  } catch {}
})

async function save() {
  saving.value = true
  const cfg = {
    llm: {
      api_key: form.llm_api_key,
      api_base: form.llm_api_base,
      model: form.llm_model,
      temperature: 0.7,
      max_tokens: 100,
    },
    bot: {
      owner: form.bot_owner,
      bot_name: form.bot_name,
      owner_title: form.bot_owner_title,   // 新增
      ws_url: form.bot_ws_url,
      whitelist: [],
    },
    napcat: { path: form.napcat_path },
  }
  try {
    await axios.put('/api/config', cfg)
    ElMessage.success('✅ 配置已保存')
  } catch {
    ElMessage.error('❌ 保存失败')
  }
  saving.value = false
}
</script>

<style scoped>
.setup-page {
  padding: 8px 4px;
  max-width: 680px;
  margin: 0 auto;
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
.setup-card {
  background: var(--bg-card, rgba(30, 41, 59, 0.7));
  backdrop-filter: blur(8px);
  border: 1px solid var(--border-color, #334155);
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 24px;
  transition: border-color 0.3s;
}
.setup-card:hover {
  border-color: var(--text-secondary, #64748b);
}
.card-header {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #e2e8f0);
  margin-bottom: 16px;
  letter-spacing: 0.3px;
}
.setup-form {
  margin-top: -6px;
}
.setup-form :deep(.el-form-item) {
  margin-bottom: 16px;
}
.setup-form :deep(.el-form-item__label) {
  color: var(--text-secondary, #94a3b8);
  font-weight: 500;
  font-size: 13px;
  padding-bottom: 4px;
}
.setup-form :deep(.el-input__wrapper) {
  background: var(--bg-primary, #0f172a);
  border-radius: 40px;
  box-shadow: none;
  border: 1px solid var(--border-color, #334155);
  transition: border-color 0.2s, box-shadow 0.2s;
}
.setup-form :deep(.el-input__wrapper:hover) {
  border-color: var(--text-secondary, #64748b);
}
.setup-form :deep(.el-input__wrapper.is-focus) {
  border-color: #8b5cf6;
  box-shadow: 0 0 0 2px #8b5cf644;
}
.setup-form :deep(.el-input__inner) {
  color: var(--text-primary, #e2e8f0);
}
.setup-form :deep(.el-input__inner::placeholder) {
  color: var(--text-secondary, #64748b);
}
.setup-form :deep(.el-input-group__append) {
  background: transparent;
  border: none;
}
.save-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}
.save-btn {
  border-radius: 60px;
  padding: 14px 48px;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  color: white;
  border: none;
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
  box-shadow: 0 6px 24px -6px #8b5cf688;
}
.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px -8px #8b5cf6bb;
}
.save-btn:active {
  transform: scale(0.96);
}
.save-btn.is-loading {
  background: #6d28d9;
}
</style>