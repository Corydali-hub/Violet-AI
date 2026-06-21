<h1 align="center">
  <img src="launcher/static/logo.png" alt="logo" width="48" align="top">
  Violet-AI — 一个 WebUI 可视化管理的 QQ 机器人
</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Vue-3.4-4FC08D?style=flat&logo=vue.js&logoColor=white" alt="Vue">
  <img src="https://img.shields.io/badge/LLM-DeepSeek-536DFE?style=flat" alt="DeepSeek">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows-0078D6?style=flat&logo=windows&logoColor=white" alt="Windows">
</p>

<p align="center">
  <b>基于 NapCat + DeepSeek 的智能 QQ 群聊机器人</b><br>
  双人格 · 流式长文 · 联网搜索 · 点歌 · WebUI 可视化管理
</p>

---

## 📖 目录

- [✨ 功能特性](#-功能特性)
- [🏗 架构概览](#-架构概览)
- [🚀 快速开始](#-快速开始)
- [📖 命令大全](#-命令大全)
- [⚙ 配置说明](#-配置说明)
- [📁 目录结构](#-目录结构)
- [🖥 WebUI 管理面板](#-webui-管理面板)
- [🔧 常见问题](#-常见问题)
- [📝 更新日志](#-更新日志)
- [🙏 致谢](#-致谢)
- [📄 许可证](#-许可证)

---

## ✨ 功能特性

| 功能 | 说明 |
|:---|:---|
| 🐱 **双人格切换** | 乖猫娘 / 毒舌傲娇，群内随时切换 |
| 📚 **博学模式** | 开启后调用 Tavily 联网搜索，8192 token 长回复 |
| 🌊 **流式分段输出** | 长文本按句子自动切分，防刷屏、不超时 |
| 🎵 **点歌** | @Bot 点歌 歌名，自动搜索网易云并发送音乐卡片 |
| 🖼️ **智能图片** | 博学模式下自动筛选国内可达的图片发送 |
| 🔇 **全局静音/活跃** | 主人一键控制所有群响应 |
| 👑 **主人特权** | 免 @ 专属命令，精准控制机器人 |
| ⚡ **关键词触发** | 预设短语秒回，无需 AI 调用 |
| 🔁 **复读检测** | 群内 30s 内重复消息自动复读 |
| 🖥 **WebUI 管理面板** | 可视化配置、群状态管理、实时日志、扫码登录 |

---

## 🏗 架构概览

```
┌──────────────────────────────────────────────────────┐
│                    QQ 客户端                          │
│              (NapCat DLL 注入)                        │
└──────────────┬───────────────────────────────────────┘
               │  OneBot v11 WebSocket (ws://127.0.0.1:6700)
               ▼
┌──────────────────────────────┐     ┌────────────────┐
│      qq-ghost-bot (Python)    │────▶│  DeepSeek API   │
│   · 消息解析 · 命令路由        │     │  deepseek-chat  │
│   · 流式分段 · 状态管理        │     └────────────────┘
│   · 点歌 · 联网搜索 · 图片过滤 │
└──────────────┬───────────────┘     ┌────────────────┐
               │                     │   Tavily API    │
               │                     │  联网搜索 + 图片 │
               │                     └────────────────┘
               │  JSON (config.json)
               ▼
┌──────────────────────────────┐
│    launcher WebUI (FastAPI)   │
│   · 配置管理 · 进程控制        │
│   · 实时日志 · QR 扫码登录     │
│   · Vue 3 + Element Plus 前端 │
└──────────────────────────────┘
```

| 组件 | 技术栈 | 端口 |
|:---|:---|:---|
| QQ 连接 | NapCat (Node.js, OneBot v11) | `6700` (WebSocket) |
| Bot 核心 | Python 3.10+, aiohttp, openai | — |
| WebUI 后端 | FastAPI + uvicorn | `8000` |
| WebUI 前端 | Vue 3 + Element Plus + Vite | 已预构建 |
| LLM | DeepSeek (`deepseek-chat`) | HTTPS API |
| 搜索 | Tavily Search API | HTTPS API |

---

## 🚀 快速开始

### 📋 环境要求

- **操作系统**：Windows 10 / 11
- **Python**：3.10 及以上
- **QQ**：一个可正常登录的 QQ 账号
- **DeepSeek API Key**：[platform.deepseek.com](https://platform.deepseek.com) 获取
- **Tavily API Key**（可选）：[tavily.com](https://tavily.com) 获取，用于博学模式的联网搜索

> Node.js / npm 仅在二次开发前端时需要。本项目已预构建前端产物。

### 📥 安装

```powershell
pip install -r qq-ghost-bot/requirements.txt -r launcher/requirements.txt
```

> 💡 详细说明见 [SETUP.md](SETUP.md)。

### ⚙ 首次配置

**推荐方式：启动后在 WebUI 面板中填写配置。**

1. 双击 `start.bat` 启动
2. 浏览器打开 `http://localhost:8000`，进入「系统设置」
3. 填入 **API Key**、**主人 QQ**、**Bot QQ** 等
4. 点击保存

> Bot QQ 填写后保存，系统自动生成 NapCat 配置，无需手动编辑 JSON。

### 🟢 启动

| 模式 | 操作 | 说明 |
|:---|:---|:---|
| **生产模式** | 双击 `start.bat` | 浏览器打开 `http://localhost:8000` |
| **调试模式** | 双击 `dev.bat` | 前端 `:5173`，后端 `:8000`，热重载 |
| **仅启动 Bot** | `cd qq-ghost-bot && python main.py` | 纯命令行，不含 WebUI |

### 📱 扫码登录

1. NapCat 启动后弹出控制台，显示二维码或登录链接
2. 使用手机 QQ 扫码授权登录
3. 控制台显示"登录成功"后，Bot 自动连接
4. WebUI 中可查看实时日志确认状态

> ⚠️ 第一次扫码可能提示失败，关闭窗口重新扫描第二次即可。

---

## 📖 命令大全

### 👑 主人命令（无需 @，仅在主人所在群生效）

| 命令 | 效果 |
|:---|:---|
| `不许吵了` / `闭嘴` | 当前群静音 |
| `猫猫可以说话了哦` / `在哪鬼混呢` | 当前群恢复响应 |
| `全局静音` | 所有群静音 |
| `全局活跃` | 所有群恢复响应 |
| `博学猫猫启动` / `乖乖回答一些问题` | 开启博学模式（联网搜索 + 长回复） |
| `傻傻猫娘` / `变笨` | 关闭博学模式 |

### 🐱 @机器人 命令

| 命令 | 效果 |
|:---|:---|
| `@Bot 乖` | 切换为乖猫娘人格 |
| `@Bot 坏` | 切换为毒舌傲娇人格 |
| `@Bot 攻击 @某人` | 设置毒舌目标 |
| `@Bot 停止攻击` | 取消毒舌目标 |
| `@Bot 清记忆` | 清除当前群聊天记录 |
| `@Bot 点歌 歌名` | 搜索网易云音乐并发送音乐卡片 |

### 🔑 关键词触发（无需 @）

| 关键词 | 回复 |
|:---|:---|
| `谁玩` / `有没有玩的` / `吸血` / `八角笼` | 游戏组队相关 |
| `啵啵` | TD |
| `哦对了` | 是我点的举报 |
| `小团体` / `标志` / `彪子` / `糖拌番茄` 等 | 梗图回复 |

> 💡 可在 `qq-ghost-bot/handlers.py` 的 `TRIGGERS` 字典中自定义。

---

## ⚙ 配置说明

### 主配置文件 (`launcher/data/config.json`)

| 配置项 | 类型 | 说明 |
|:---|:---|:---|
| `llm.api_key` | string | DeepSeek API 密钥 |
| `llm.api_base` | string | API 地址（默认 `https://api.deepseek.com`） |
| `llm.model` | string | 模型名（默认 `deepseek-chat`） |
| `llm.temperature` | float | 生成温度 0~1（默认 `0.7`） |
| `llm.max_tokens` | int | 最大 token 数（默认 `100`） |
| `bot.owner` | string | 主人 QQ 号 |
| `bot.qq` | string | Bot 登录的 QQ 号 |
| `bot.bot_name` | string | 机器人昵称 |
| `bot.owner_title` | string | 主人称呼 |
| `bot.ws_url` | string | OneBot WebSocket 地址 |
| `bot.whitelist` | string[] | 群号白名单（空 = 所有群） |
| `tavily.api_key` | string | Tavily 搜索 API Key（博学模式可选） |
| `background.url` | string | WebUI 背景图 URL |
| `background.theme` | string | WebUI 主题 `light` / `dark` |

> 📌 优先级：WebUI (`config.json`) > `.env` 文件 > 代码默认值。群状态由系统自动管理。

---

## 📁 目录结构

```
Violet-AI/
├── start.bat                  # 🟢 生产模式一键启动
├── dev.bat                    # 🔧 调试模式一键启动
├── SETUP.md                   # 📖 安装说明书
├── README.md
├── LICENSE
│
├── NapCat.Shell/              # 🔌 QQ 连接框架
│   ├── NapCatWinBootMain.exe  #   QQ 启动引导（DLL 注入）
│   ├── napcat.mjs             #   NapCat 核心
│   ├── launcher-win10.bat     #   NapCat 启动（需管理员）
│   └── config/
│       ├── napcat.json        #   框架默认配置
│       └── plugins.json       #   插件列表
│
├── qq-ghost-bot/              # 🤖 Bot 核心
│   ├── main.py                #   入口：WebSocket → 消息分发 → LLM
│   ├── handlers.py            #   消息处理：命令/触发词/流式分段
│   ├── llm.py                 #   DeepSeek 流式调用 + 图片过滤
│   ├── prompts.py             #   系统提示词
│   ├── state_manager.py       #   群状态管理
│   ├── config.py              #   统一配置（WebUI 优先）
│   ├── netease.py             #   网易云音乐搜索
│   ├── tavily_search.py       #   联网搜索 API
│   ├── napcat_config_fixer.py #   NapCat 配置自动修复
│   └── requirements.txt       #   Python 依赖
│
├── launcher/                  # 🖥 WebUI 管理面板
│   ├── app.py                 #   FastAPI 后端
│   ├── manager.py             #   进程管理
│   ├── config_manager.py      #   配置读写
│   ├── requirements.txt       #   Python 依赖
│   ├── data/                  #   配置数据目录
│   ├── static/                #   前端构建产物（已预构建）
│   └── frontend/              #   Vue 3 前端源码（仅开发用）
│       └── src/
```

---

## 🖥 WebUI 管理面板

启动后访问 `http://127.0.0.1:8000`。

| 页面 | 功能 |
|:---|:---|
| 🏠 **仪表盘** | 运行状态概览，进程启动/停止/重启 |
| 👥 **群组管理** | 查看所有群状态，按群修改人格/静音/博学 |
| 📋 **实时日志** | WebSocket 推送的实时运行日志 |
| ⚙ **系统设置** | API Key、主人 QQ、白名单等全局配置 |
| 📱 **扫码登录** | 查看 NapCat 登录二维码 |

### 前端二次开发

```powershell
cd launcher/frontend
npm install        # 安装依赖（仅一次）
npm run dev        # 启动 Vite 开发服务器 (localhost:5173)
npm run build      # 构建生产版本 → launcher/static/
```

---

## 🔧 常见问题

### Q1：机器人没反应？

1. 确认 NapCat 已登录（黑窗口显示"登录成功"）
2. 确认 Bot 已连接（日志中有"已连接成功"）
3. 检查 DeepSeek API Key 是否有效、余额是否充足

### Q2：主人命令不生效？

- 确认 `config.json` 中 `bot.owner` 填写正确
- 修改配置后需重启 Bot

### Q3：点歌失败？

点歌依赖网易云公开 API，如遇失败可能是 API 限流，稍后重试即可。

### Q4：博学模式图片发不出来？

已内置国内可达性检测，只发送无需代理的图片。境外 CDN 图片会被自动过滤。

### Q5：复制到另一台电脑能用吗？

可以。项目全部使用相对路径，复制到任意位置即可运行。只需确保那台电脑已安装 Python 3.10+，然后 `pip install -r` 安装依赖。NapCat 和前端均已预置，无需额外安装 Node.js。

### Q6：NapCat 需要管理员权限？

NapCat 通过 DLL 注入与 QQ 通信，需要管理员权限。右键 `launcher-win10.bat` → "以管理员身份运行"。

---

## 📝 更新日志

### v2.2
- 🎵 新增点歌功能：@Bot 点歌 歌名，搜索网易云并发送音乐卡片
- 🔍 新增 Tavily 联网搜索（博学模式）
- 🖼 智能图片过滤：自动检测国内可达性，过滤境外 CDN
- 🧹 精简分发：移除 node_modules（123MB），移除个人信息和缓存
- 📦 前端预构建：普通用户无需安装 Node.js / npm
- 📖 更新 SETUP.md 和 README

### v2.1
- 🚀 统一起动器：`run.py`，解决路径兼容问题
- 🔍 NapCat 路径自动检测
- 📦 Bot QQ 自动配置
- 🛡 全相对路径硬化

### v2.0
- 🖥 WebUI 管理面板（Vue 3 + Element Plus）
- 🐱 双人格系统 + 博学模式
- 🌊 流式分段输出
- 👥 群组独立状态管理

---

## 🙏 致谢

| 项目 | 用途 |
|:---|:---|
| [NapCat](https://github.com/NapNeko/NapCatQQ) | QQ 机器人框架（OneBot v11） |
| [DeepSeek](https://deepseek.com) | 大语言模型 API |
| [Tavily](https://tavily.com) | 联网搜索 API |
| [FastAPI](https://fastapi.tiangolo.com) | WebUI 后端框架 |
| [Vue 3](https://vuejs.org) | 前端框架 |
| [Element Plus](https://element-plus.org) | UI 组件库 |
| [Vite](https://vitejs.dev) | 前端构建工具 |
| [aiohttp](https://docs.aiohttp.org) | 异步 HTTP / WebSocket 客户端 |

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

<p align="center">
  <b>🐱 祝使用愉快！有问题欢迎提 Issue~</b>
</p>
