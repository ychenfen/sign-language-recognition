#!/bin/zsh
set -u

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
START_SH="$PROJECT_DIR/start.sh"

pause() {
  echo ""
  read -r "?Press Enter to close this window..."
}

trap 'echo ""; echo "Exit status: $?"; pause' EXIT

cd "$PROJECT_DIR" || { echo "ERROR: cannot cd to: $PROJECT_DIR"; exit 1; }

if [ ! -f "$START_SH" ]; then
  echo "ERROR: start.sh not found: $START_SH"
  exit 1
fi

chmod +x "$START_SH" 2>/dev/null || true
"$START_SH"
