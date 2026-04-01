#!/bin/bash
# 从任意目录调用 web-search-skill 的统一入口
# 自动 cd 到 skill 目录、检查/安装环境、激活 venv，然后执行命令
#
# 用法：
#   bash /path/to/web-search-skill/run.sh search "Claude AI" "LLM"
#   bash /path/to/web-search-skill/run.sh fetch https://example.com "核心观点"

set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SKILL_DIR/.venv"

# 1. 检查/安装环境
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "📦 首次运行，安装依赖..."
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --quiet --upgrade pip
    "$VENV_DIR/bin/pip" install --quiet -r "$SKILL_DIR/requirements.txt"
    echo "✅ 安装完成"
fi

# 2. 激活 venv
source "$VENV_DIR/bin/activate"

# 3. 执行子命令
SUBCMD="$1"
shift

case "$SUBCMD" in
    search)
        python "$SKILL_DIR/scripts/search.py" "$@"
        ;;
    fetch)
        python "$SKILL_DIR/scripts/fetch.py" "$@"
        ;;
    *)
        echo "用法: bash run.sh <search|fetch> [args...]" >&2
        exit 1
        ;;
esac