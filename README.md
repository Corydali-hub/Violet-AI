<h1 align="center">
  <img src="launcher/static/logo.png" alt="logo" width="48" align="top">
  堇言AI — 一个 WebUI可视化管理的 QQ 机器人
</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Vue-3.4-4FC08D?style=flat&logo=vue.js&logoColor=white" alt="Vue">
  <img src="https://img.shields.io/badge/Node.js-18+-339933?style=flat&logo=node.js&logoColor=white" alt="Node.js">
  <img src="https://img.shields.io/badge/LLM-DeepSeek-536DFE?style=flat" alt="DeepSeek">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows-0078D6?style=flat&logo=windows&logoColor=white" alt="Windows">
</p>

<p align="center">
  <b>基于 NapCat + DeepSeek 的智能 QQ 群聊机器人</b><br>
  双人格 · 流式长文 · 关键词触发 · WebUI 可视化管理
</p>

---

## 📖 目录

- [✨ 功能特性](#-功能特性)
- [🏗️ 架构概览](#️-架构概览)
- [🚀 快速开始](#-快速开始)
- [📖 命令大全](#-命令大全)
- [⚙️ 配置说明](#️-配置说明)
- [📁 目录结构](#-目录结构)
- [🖥️ WebUI 管理面板](#️-webui-管理面板)
- [🔧 常见问题](#-常见问题)
- [📝 更新日志](#-更新日志)
- [🙏 致谢](#-致谢)
- [📄 许可证](#-许可证)

---

## ✨ 功能特性

| 功能 | 说明 |
|:---|:---|
| 🐱 **双人格切换** | 乖猫娘 (`catgirl`) / 毒舌傲娇 (`tsundere`)，群内随时切换 |
| 📚 **博学模式** | 开启后 8192 token 长回复，深度问答不截断 |
| 🌊 **流式分段输出** | 长文本按句子自动切分（200~400 字/段），防刷屏、不超时 |
| 🔇 **全局静音/活跃** | 主人一键控制所有群响应 |
| 👑 **主人特权** | 免 @ 专属命令，精准控制机器人 |
| ⚡ **关键词触发** | 预设短语秒回，无需 AI 调用 |
| 🔁 **复读检测** | 群内 30s 内重复消息自动复读 |
| 🖥️ **WebUI 管理面板** | 可视化配置、群状态管理、实时日志、扫码登录 |
---

## 🏗️ 架构概览

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
└──────────────┬───────────────┘
               │  JSON 文件 (config.json / state_overrides.json)
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
| WebUI 前端 | Vue 3 + Element Plus + Vite | `5173` (dev) |
| LLM | DeepSeek (`deepseek-chat`) | HTTPS API |

---

## 🚀 快速开始

### 📋 环境要求

- **操作系统**：Windows 10 / 11
- **Python**：3.10 及以上
- **Node.js**：18 及以上（NapCat 运行依赖）
- **QQ**：一个可正常登录的 QQ 账号
- **DeepSeek API Key**：[platform.deepseek.com](https://platform.deepseek.com) 获取

### 📥 安装依赖

```powershell
# Python 依赖（Bot + Launcher）
pip install -r qq-ghost-bot/requirements.txt -r launcher/requirements.txt

# 前端依赖（仅需构建一次）
cd launcher/frontend
npm install
npm run build
cd ../..
```

> 💡 详细说明见 [`SETUP.md`](SETUP.md)（依赖安装说明书）。

### ⚙️ 首次配置

**推荐方式：启动后在 WebUI 面板中填写配置。**

1. 双击 `start.bat` 启动
2. 浏览器打开 `http://localhost:8000`，进入「系统设置」
3. 填入 **API Key**、**主人 QQ**、**Bot QQ** 等
4. 点击保存 —— 系统会自动在 `NapCat.Shell/config/` 下生成 Bot QQ 对应的三个配置文件

> Bot QQ 填写后保存，无需手动碰 NapCat 的 JSON 配置。

### 🟢 启动机器人

| 模式 | 操作 | 说明 |
|:---|:---|:---|
| **生产模式** | 双击 `start.bat` | 浏览器打开 `http://localhost:8000` |
| **调试模式** | 双击 `dev.bat` | 前端 `:5173`，后端 `:8000`，热重载 |
| **仅启动 Bot** | `cd qq-ghost-bot && python main.py` | 纯命令行，不含 WebUI |
| **仅启动 NapCat** | 双击 `NapCat.Shell/launcher-win10.bat`（需管理员） | 单独启动 QQ 框架 |

> 🚀 `start.bat` / `dev.bat` 已移到项目根目录，任意路径双击即用。首次启动若无前端构建产物，会自动执行 `npm run build`。

### 📱 扫码登录

1. NapCat 启动后会弹出控制台，显示 **二维码** 或 **登录链接**
2. 使用手机 QQ **扫码授权登录**
3. 控制台显示"登录成功"后，Bot 自动连接 WebSocket
4. 在 WebUI 中可查看实时日志确认连接状态

> ⚠️ **注意**：第一次扫码可能提示失败，这是 NapCat 在创建配置文件；关闭窗口**重新扫描第二次**即可成功登录。

---

## 📖 命令大全

### 👑 主人命令（无需 @，仅在主人所在群生效）

| 命令 | 效果 |
|:---|:---|
| `不许吵了` / `闭嘴` | 当前群静音 |
| `猫猫可以说话了哦` / `在哪鬼混呢` | 当前群恢复响应 |
| `全局静音` | **所有群**静音 |
| `全局活跃` | **所有群**恢复响应 |
| `博学猫猫启动` / `乖乖回答一些问题` | 开启博学模式（8192 token 长回复） |
| `傻傻猫娘` / `变笨` | 关闭博学模式 |

### 🐱 @机器人 命令

| 命令 | 效果 |
|:---|:---|
| `@机器人 乖` | 切换为乖猫娘人格 |
| `@机器人 坏` | 切换为毒舌傲娇人格 |
| `@机器人 攻击 @某人` | 设置毒舌目标（只怼指定人） |
| `@机器人 停止攻击` | 取消毒舌目标 |
| `@机器人 清记忆` | 清除当前群聊天记录 |

### 🔑 关键词触发（无需 @）

| 关键词 | 回复 |
|:---|:---|
| `谁玩` | 我玩我玩 |
| `甲烷` | 表哥我不是甲烷... |
| `有没有玩的` | 我我我，来来来... |
| `吸血` | 吸谁的血，大大方方来吸我的血... |
| `八角笼` | 谁是好人谁是坏人 |
| `啵啵` | TD |
| `哦对了` | 是我点的举报 |
| `零号大坝` | 零号大坝是对的 |
| `小团体` | 小团体来了，你们聊 |
| `标志` / `彪子` | 标志 / 彪子 |
| `糖拌番茄` | 糖拌番茄骨汤面... |

> 💡 可在 `qq-ghost-bot/handlers.py` 的 `TRIGGERS` 字典中自定义添加关键词回复。

---

## ⚙️ 配置说明

### 主配置文件 (`launcher/data/config.json`)

| 配置项 | 类型 | 说明 |
|:---|:---|:---|
| `llm.api_key` | string | DeepSeek API 密钥 |
| `llm.api_base` | string | API 地址（默认 `https://api.deepseek.com`） |
| `llm.model` | string | 模型名（默认 `deepseek-chat`） |
| `llm.temperature` | float | 生成温度 0~1（默认 `0.7`） |
| `llm.max_tokens` | int | 最大 token 数（默认 `100`） |
| `bot.owner` | string | 主人 QQ 号（用于权限判断） |
| `bot.qq` | string | Bot 登录的 QQ 号（保存后自动生成 NapCat 配置） |
| `bot.bot_name` | string | 机器人昵称 |
| `bot.owner_title` | string | 主人称呼 |
| `bot.ws_url` | string | OneBot WebSocket 地址 |
| `bot.whitelist` | string[] | 群号白名单（空数组 = 允许所有群） |
| `background.url` | string | WebUI 背景图 URL（可选） |
| `background.theme` | string | WebUI 主题 `light` / `dark` |

> 🔍 **NapCat 路径已自动检测**：项目会自动定位 `NapCat.Shell/` 目录，不再需要手动填写 `napcat.path`。如果你使用自己安装的 NapCat，仍可在 `config.json` 中手动指定。

### 备用配置文件 (`qq-ghost-bot/.env`)

```ini
ONEBOT_WS_URL=ws://127.0.0.1:6700
LLM_API_KEY=
LLM_API_BASE=
LLM_MODEL=
BOT_NAME=
OWNER_ID=
OWNER_TITLE=
GROUP_WHITELIST=
PROB_MIMIC=0.25
PROB_REPLAY=0.1
COOLDOWN_SECONDS=8
MAX_HISTORY_PER_GROUP=500
```

> 📌 **优先级**：WebUI 配置 (`config.json`) > `.env` 文件 > 代码默认值

### 群状态文件 (`qq-ghost-bot/data/state_overrides.json`)

每个群的独立状态——人格、静音、博学模式、毒舌目标等，由系统自动管理，无需手动编辑。

---

## 📁 目录结构

```
堇言webAI/
├── start.bat                  # 🟢 生产模式一键启动
├── dev.bat                    # 🔧 调试模式一键启动
├── run.py                     # 🐍 统一启动器（Python）
├── SETUP.md                   # 📖 依赖安装说明书
├── README.md                  # 📖 本文件
├── LICENSE
│
├── NapCat.Shell/              # 🔌 QQ 连接框架 (Node.js)
│   ├── NapCatWinBootMain.exe  #   QQ 启动引导（DLL 注入）
│   ├── napcat.mjs             #   NapCat 核心
│   ├── launcher-win10.bat     #   NapCat 启动脚本（需管理员）
│   └── config/                #   OneBot 配置（WebSocket 端口等）
│
├── qq-ghost-bot/              # 🤖 Bot 核心 (Python)
│   ├── main.py                #   入口：WebSocket 连接 → 消息分发 → LLM
│   ├── handlers.py            #   消息处理：命令 / 触发词 / 流式分段
│   ├── llm.py                 #   DeepSeek 流式异步调用
│   ├── prompts.py             #   系统提示词（猫娘 / 傲娇 / 博学模式）
│   ├── state_manager.py       #   群状态：人格 / 静音 / 记忆
│   ├── config.py              #   统一配置读取（WebUI 优先）
│   ├── napcat_config_fixer.py #   NapCat OneBot 配置自动修复
│   ├── .env                   #   备用环境变量
│   ├── requirements.txt       #   Python 依赖
│   └── data/
│       └── state_overrides.json  # 群状态持久化（自动创建）
│
├── launcher/                  # 🖥️ WebUI 管理面板
│   ├── app.py                 #   FastAPI 后端（REST + WebSocket）
│   ├── manager.py             #   进程管理（启停 NapCat / Bot）
│   ├── config_manager.py      #   JSON 配置读写
│   ├── requirements.txt       #   Python 依赖
│   ├── data/
│   │   └── config.json        #   主配置文件
│   ├── static/                #   前端构建产物（npm run build）
│   └── frontend/              #   Vue 3 前端源码
│       ├── package.json
│       └── src/
│           ├── views/         #   页面：Dashboard / Groups / Logs / Setup
│           ├── components/    #   组件
│           └── api/           #   API 请求封装
```

---

## 🖥️ WebUI 管理面板

启动后在浏览器访问 `http://127.0.0.1:8000`。

| 页面 | 功能 |
|:---|:---|
| 🏠 **仪表盘** | 运行状态概览，进程启动/停止/重启 |
| 👥 **群组管理** | 查看所有群状态，按群修改人格/静音/博学模式 |
| 📋 **实时日志** | WebSocket 推送的实时运行日志 |
| ⚙️ **系统设置** | API Key、主人 QQ、白名单等全局配置 |
| 📱 **扫码登录** | 查看 NapCat 登录二维码 |

### 前端开发

```powershell
cd launcher/frontend
npm install        # 安装依赖
npm run dev        # 启动 Vite 开发服务器 (localhost:5173)
npm run build      # 构建生产版本 → launcher/static/
```

---

## 🔧 常见问题

### Q1：机器人没反应？

1. 确认 NapCat 已登录（黑窗口显示"登录成功"）
2. 确认 OneBot WebSocket 已启动（日志中有 `WebSocket 服务已启动: ws://127.0.0.1:6700`）
3. 确认 Bot 已连接（日志中有"已连接成功"）
4. 检查 DeepSeek API Key 是否有效、余额是否充足

### Q2：主人命令不生效？

- 确认 `config.json` 或 `.env` 中 `owner` / `OWNER_ID` 填写正确
- 确认当前 QQ 号与主人 QQ 号一致
- 修改配置后需**重启 Bot**

### Q3：WebUI 修改配置不生效？

Bot 检测到 `config.json` 文件变更会自动重载配置，少数情况需在 WebUI 中手动点击"重启 Bot"。

### Q4：长文本回复被截断或超时？

已内置流式分段发送（每段 200~400 字），通常无需额外配置。若仍有问题，请检查：
- NapCat WebSocket 心跳是否正常
- DeepSeek API 是否限流

### Q5：换个 QQ 号登录后连不上？

每个 QQ 号对应独立的 OneBot 配置文件。在 WebUI 设置中修改 **Bot QQ** 并保存，系统会自动生成新配置。如果需要清除旧配置，删除 `NapCat.Shell/config/` 下的 `onebot11_*.json`、`napcat_*.json`、`napcat_protocol_*.json`。

### Q6：NapCat 启动提示需要管理员权限？

NapCat 通过 DLL 注入与 QQ 通信，需要**管理员权限**。右键 `launcher-win10.bat` → "以管理员身份运行"。

### Q7：启动报 "文件名、目录名或卷标语法不正确"？

这是旧版 bat 文件在含空格路径下的兼容问题。**v2.1** 已修复，确保使用最新的 `start.bat` / `dev.bat`（纯 ASCII、无嵌套引号）。如果仍有问题，可直接用 `python run.py` 或 `python run.py --dev` 启动。

### Q8：复制到另一台电脑能用吗？

可以。项目全部使用相对路径（`__file__` / `%~dp0`），不依赖绝对路径或用户名。复制整个文件夹到任意位置、任意电脑均可直接运行，只需确保那台电脑已安装 Python 3.10+ 和 Node.js 18+。

---

## 📝 更新日志

### v2.1
- 🚀 **统一起动器**：新增 `run.py`，`start.bat` / `dev.bat` 精简为一行调用，彻底解决 cmd 路径空格/引号兼容问题
- 🔍 **NapCat 路径自动检测**：无需手动填写，自动定位项目自带的 `NapCat.Shell/`
- 📦 **Bot QQ 自动配置**：WebUI 填入 Bot QQ 保存后，自动生成 `napcat_*.json` / `onebot11_*.json` / `napcat_protocol_*.json`
- 🛡️ **全相对路径硬化**：所有文件路径基于 `__file__` / `%~dp0`，复制到任意目录/电脑直接运行
- 🔧 **`python -m uvicorn`**：替代裸 `uvicorn`，兼容未添加 PATH 的 Python 安装
- 📖 **新增 SETUP.md**：依赖安装说明书
- 🧹 **bat 文件纯 ASCII**：消除编码乱码

### v2.0
- 🖥️ WebUI 管理面板（Vue 3 + Element Plus）
- 🐱 双人格系统 + 博学模式
- 🌊 流式分段输出
- 👥 群组独立状态管理

---

## 🙏 致谢

本项目离不开以下开源项目：

| 项目 | 用途 |
|:---|:---|
| [NapCat](https://github.com/NapNeko/NapCatQQ) | QQ 机器人框架（OneBot v11 协议） |
| [DeepSeek](https://deepseek.com) | 大语言模型 API |
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
