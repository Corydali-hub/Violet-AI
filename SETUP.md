# 堇言AI — 依赖与安装说明书

## 1. 最低环境要求

| 环境 | 最低版本 | 说明 |
|------|----------|------|
| 操作系统 | Windows 10 | NapCat 仅支持 Windows |
| Python | 3.10+ | Bot 核心 + WebUI 后端 |
| Node.js | 18 LTS | NapCat 运行时 + 前端构建 |
| npm | 9.x+ | 随 Node.js 自带 |
| QQ | 最新正式版 | NapCat 需要 Hook QQ 进程 |

## 2. 外部服务

| 服务 | 用途 | 获取方式 |
|------|------|----------|
| DeepSeek API Key | LLM 对话 | https://platform.deepseek.com 免费注册 |

## 3. 安装步骤

### 3.1 安装 Python 依赖

```powershell
pip install -r qq-ghost-bot/requirements.txt -r launcher/requirements.txt
```

### 3.2 构建前端（仅一次）

```powershell
cd launcher/frontend
npm install
npm run build
cd ../..
```

> 也可以直接双击 `start.bat`，首次运行会自动构建。

### 3.3 启动

| 模式 | 操作 |
|------|------|
| 生产模式 | 双击 `start.bat` |
| 开发模式 | 双击 `dev.bat` |

## 4. 常见问题

### pip 安装慢

```powershell
pip install -r launcher/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### npm 安装慢

```powershell
npm config set registry https://registry.npmmirror.com
npm install
```

### python 不是内部命令

Python 未安装或未添加到 PATH。从 https://python.org 下载安装，勾选 "Add Python to PATH"。

### npm 不是内部命令

Node.js 未安装。从 https://nodejs.org 下载 LTS 版本安装。

### NapCat 需要管理员权限

NapCat 通过 DLL 注入与 QQ 通信，启动时必须允许管理员权限。

### DeepSeek API 调用失败

- 确认 API Key 正确填入（WebUI 设置页）
- 检查账户余额：https://platform.deepseek.com
- 确认网络能访问 `https://api.deepseek.com`
