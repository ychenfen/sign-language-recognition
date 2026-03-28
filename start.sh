#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
BACKEND_REQUIREMENTS="$SCRIPT_DIR/backend/requirements.txt"
PORT="${PORT:-}"
SERVER_URL=""
SERVER_PID=""

find_available_port() {
  local candidate
  for candidate in 5001 5002 5003 5004 5005 5010; do
    if ! python3 - "$candidate" <<'PY'
import socket
import sys

port = int(sys.argv[1])
sock = socket.socket()
sock.settimeout(0.5)
code = sock.connect_ex(("127.0.0.1", port))
sock.close()
raise SystemExit(0 if code == 0 else 1)
PY
    then
      echo "$candidate"
      return 0
    fi
  done

  return 1
}

open_browser() {
  if command -v open >/dev/null 2>&1; then
    open "$SERVER_URL" >/dev/null 2>&1 || true
  fi
}

cleanup() {
  if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

cd "$SCRIPT_DIR"

if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/.env"
  set +a
fi

if [ -z "$PORT" ]; then
  PORT="$(find_available_port || true)"
fi

if [ -z "$PORT" ]; then
  echo "ERROR: 未找到可用端口，请手动设置 PORT 环境变量后重试。"
  exit 1
fi

SERVER_URL="http://127.0.0.1:$PORT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: 未找到 python3，请先安装 Python 3。"
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "[1/6] 创建 Python 虚拟环境"
  python3 -m venv "$VENV_DIR"
fi

echo "[2/6] 激活虚拟环境"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "[3/6] 安装后端依赖"
python -m pip install --upgrade pip
pip install -r "$BACKEND_REQUIREMENTS"

if [ ! -f "$SCRIPT_DIR/dist/index.html" ]; then
  if ! command -v npm >/dev/null 2>&1; then
    echo "ERROR: 未找到 npm，且当前目录没有 dist 构建产物。请先在开发机执行 npm install && npm run build。"
    exit 1
  fi
  echo "[4/6] 安装前端依赖"
  npm install
  echo "[5/6] 构建前端"
  npm run build
else
  echo "[4/6] 检测到 dist 构建产物，跳过前端构建"
  echo "[5/6] 如需重新构建，请在开发机执行 npm install && npm run build"
fi

if curl -fsS "$SERVER_URL/api/health" >/dev/null 2>&1; then
  echo "检测到服务已在运行：$SERVER_URL"
  open_browser
  exit 0
fi

echo "[6/6] 启动服务"
FLASK_DEBUG=0 PORT="$PORT" python "$SCRIPT_DIR/backend/sign_recognition_api.py" &
SERVER_PID=$!

for _ in $(seq 1 20); do
  if curl -fsS "$SERVER_URL/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if curl -fsS "$SERVER_URL/api/health" >/dev/null 2>&1; then
  echo "服务已启动：$SERVER_URL"
  open_browser
else
  echo "WARNING: 服务启动超时，请查看上方日志。"
fi

wait "$SERVER_PID"
