#!/bin/bash

# 线上工单分析 Skill - 依赖安装脚本
# 本脚本用于安装运行本技能所需的依赖

set -e

echo "=========================================="
echo "线上工单分析 Skill - 依赖安装"
echo "=========================================="
echo ""

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3，请先安装 Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ 检测到 Python 版本: $PYTHON_VERSION"

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误: 未找到 pip3，请先安装 pip"
    exit 1
fi

echo "✓ 检测到 pip3"
echo ""

# 说明
echo "本技能主要通过AI助手和SigNoz MCP工具完成分析任务。"
echo "如果需要额外的Python依赖，可以在这里添加。"
echo ""

echo "=========================================="
echo "依赖安装完成"
echo "=========================================="
echo ""
echo "提示: 本技能主要通过AI助手和SigNoz MCP工具完成分析任务，"
echo "      通常不需要额外的Python依赖。"
echo ""
