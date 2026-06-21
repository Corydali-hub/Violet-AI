# Violet-AI — 安装说明书

## 1. 最低环境

| 环境 | 最低版本 | 说明 |
|------|----------|------|
| 操作系统 | Windows 10 | NapCat 仅支持 Windows |
| Python | 3.10+ | Bot 核心 + WebUI 后端 |
| QQ | 最新正式版 | NapCat 需要 Hook QQ 进程 |

> Node.js / npm 仅在**二次开发前端**时需要。本项目已预构建前端产物，普通使用不需要安装。

## 2. 外部服务

| 服务 | 用途 | 获取 |
|------|------|------|
| DeepSeek API Key | LLM 对话 | https://platform.deepseek.com 免费注册 |
| Tavily API Key（可选） | 联网搜索 | https://tavily.com 免费注册 |

## 3. 安装

### 安装 Python 依赖（必须）

```powershell
pip install -r qq-ghost-bot/requirements.txt -r launcher/requirements.txt
```

> 下载慢可加清华镜像：`-i https://pypi.tuna.tsinghua.edu.cn/simple`

### 启动

双击 `start.bat` 即可。首次运行会自动修复 NapCat WebSocket 配置。

## 4. 二次开发前端（可选）

如需修改 WebUI，才需要安装 Node.js 并构建：

```powershell
cd launcher/frontend
npm install
npm run build
cd ../..
```

> npm 下载慢可换淘宝源：`npm config set registry https://registry.npmmirror.com`

## 5. 常见问题

### python 不是内部命令

Python 未安装或未加 PATH。从 https://python.org 下载，安装时勾选 "Add Python to PATH"。

### DeepSeek API 报错

- 确认 API Key 已在 WebUI 设置页填入
- 检查余额：https://platform.deepseek.com
- 确认能访问 `https://api.deepseek.com`

### NapCat 需要管理员权限

NapCat 通过 DLL 注入与 QQ 通信，启动时必须允许。
