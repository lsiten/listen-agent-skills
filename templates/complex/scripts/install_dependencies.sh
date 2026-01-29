#!/bin/bash

# {{skill-name}} 依赖安装脚本
# 用于安装skill所需的系统和Python依赖

set -e

echo "=========================================="
echo "  {{skill-name}} 依赖安装"
echo "=========================================="

# 检查Python版本
echo ""
echo "[1/3] 检查Python环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "✅ Python已安装: $PYTHON_VERSION"
else
    echo "❌ Python3未安装，请先安装Python 3.8+"
    exit 1
fi

# 安装Python依赖
echo ""
echo "[2/3] 安装Python依赖..."

# 基础依赖（根据实际需求修改）
DEPENDENCIES=(
    "requests"      # HTTP请求
    "pyyaml"        # YAML解析
    "python-dotenv" # 环境变量
)

for dep in "${DEPENDENCIES[@]}"; do
    echo "  安装 $dep..."
    pip install "$dep" --quiet 2>/dev/null || {
        echo "  ⚠️ 无法通过pip安装 $dep，尝试pip3..."
        pip3 install "$dep" --quiet 2>/dev/null || {
            echo "  ❌ 安装 $dep 失败"
            exit 1
        }
    }
done

echo "✅ Python依赖安装完成"

# 检查配置目录
echo ""
echo "[3/3] 准备配置目录..."

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$SKILL_DIR/config"
OUTPUT_DIR="$SKILL_DIR/output"

mkdir -p "$CONFIG_DIR"
mkdir -p "$OUTPUT_DIR"

echo "✅ 配置目录已准备: $CONFIG_DIR"
echo "✅ 输出目录已准备: $OUTPUT_DIR"

echo ""
echo "=========================================="
echo "  安装完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "  1. 编辑配置文件（如需要）"
echo "  2. 运行 skill 主程序"
echo ""
