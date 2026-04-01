#!/bin/bash
# 在 skill 目录下创建 .venv 并安装依赖
# 用法：cd web-search-skill && bash setup.sh

set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SKILL_DIR/.venv"

if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "✅ 环境已存在，跳过安装"
else
    echo "📦 创建虚拟环境：$VENV_DIR"
    python3 -m venv "$VENV_DIR"

    echo "⬆️  安装依赖..."
    "$VENV_DIR/bin/pip" install --quiet --upgrade pip
    "$VENV_DIR/bin/pip" install --quiet -r "$SKILL_DIR/requirements.txt"

    echo "✅ 环境准备完成"
fi
echo ""
echo "激活方式："
echo "  source $VENV_DIR/bin/activate"