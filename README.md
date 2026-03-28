# 手语学习平台

基于 Vue 3 + Flask + MediaPipe 的手语学习与识别项目，包含手语词典、学习练习、实时识别、AI 助手和后台管理。

## 适用场景

- 开发调试：前端用 Vite，后端单独运行。
- 客户交付：使用预构建前端，由 Flask 统一托管页面和 API。

## 功能概览

- 手语词典、学习、测试、社区、个人中心
- 实时静态手势识别
- 动态动作识别入口
- AI 学习建议与练习反馈
- 本地管理员演示账号

## 环境要求

- Node.js 16+
- Python 3.9+
- 现代浏览器

## 客户交付模式

适合发给客户现场安装。

### macOS

1. 保持整个项目目录完整。
2. 如需 AI 助手，在项目根目录创建 `.env`，填写：
   - `DASHSCOPE_API_KEY`
3. 双击 [Start.command](/Users/yuchenxu/Desktop/手语识别/Start.command)，或在终端执行：

```bash
chmod +x start.sh Start.command
./start.sh
```

启动后脚本会自动打开浏览器，并打印实际访问地址；默认优先使用 `http://127.0.0.1:5001`。

说明：

- 首次启动会自动创建 `.venv` 并安装 Python 依赖。
- 如果目录中已有 `dist`，客户机器不需要单独安装 Node.js。
- 若 `5001` 端口被占用，脚本会自动尝试 `5002/5003...` 等空闲端口。
- 启动地址以终端输出为准。

### Windows

适合放在 `C:\Users\Lenovo\Desktop\手语识别学习平台` 这类中文路径下直接双击运行。

1. 保持整个项目目录完整。
2. 如需 AI 助手，在项目根目录创建 `.env`，填写：
   - `DASHSCOPE_API_KEY`
3. 双击 [Start-Windows.bat](/Users/yuchenxu/Desktop/手语识别/Start-Windows.bat)。

说明：

- Windows 启动脚本会先关闭之前从当前项目启动的旧服务，再启动新服务。
- 默认优先尝试 `5001`，若端口被其他程序占用，会自动切换到 `5002/5003...`。
- 运行日志会写到 `.runtime/server.out.log` 和 `.runtime/server.err.log`。
- 首次启动会自动创建 `.venv` 并安装 Python 依赖。

详细交付说明见 [客户安装说明.md](/Users/yuchenxu/Desktop/手语识别/客户安装说明.md)。

## 开发模式

### 1. 安装前端依赖

```bash
npm install
```

### 2. 启动前端开发服务器

```bash
npm run dev
```

默认地址为 `http://127.0.0.1:3001`，并通过 Vite 代理转发 `/api` 到后端 `5001` 端口。

### 3. 安装后端依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 4. 启动后端

```bash
python3 backend/sign_recognition_api.py
```

## 环境变量

根目录 `.env.example`：

- `VITE_BAIDU_API_KEY`
- `VITE_BAIDU_SECRET_KEY`
- `DASHSCOPE_API_KEY`

后端目录 `backend/.env.example`：

- `DASHSCOPE_API_KEY`

## 默认管理员账号

- 用户名：`admin`
- 密码：`admin123`

## 项目结构

```text
.
├── backend/
│   ├── ai_integration.py
│   ├── gesture_api.py
│   ├── requirements.txt
│   └── sign_recognition_api.py
├── src/
├── public/
├── dist/
├── start.sh
├── Start.command
└── 客户安装说明.md
```

## 当前交付边界

- 静态手势识别可直接运行。
- AI 助手在未配置 `DASHSCOPE_API_KEY` 时会退化为离线回复。
- 动态 LSTM 识别依赖 TensorFlow，默认未随基础交付一起安装。
