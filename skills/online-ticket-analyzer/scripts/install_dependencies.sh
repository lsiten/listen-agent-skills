#!/bin/bash

# 线上工单分析技能依赖安装脚本

echo "🚀 安装线上工单分析技能依赖..."

# 检查Python版本
echo "🔍 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [ -z "$python_version" ]; then
    echo "❌ 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

echo "✅ Python版本: $python_version"

# 检查pip
echo "🔍 检查pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ 未找到pip3，请先安装pip"
    exit 1
fi

echo "✅ pip已安装"

# 安装Python依赖包
echo "📦 安装Python依赖包..."
pip3 install requests Pillow markdown jinja2 python-dateutil

# 检查是否安装pytesseract（可选）
echo "🔍 检查OCR依赖..."
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract OCR已安装"
    pip3 install pytesseract
else
    echo "⚠️  Tesseract OCR未安装，图片OCR功能将不可用"
    echo "   安装方法："
    echo "   - macOS: brew install tesseract"
    echo "   - Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "   - Windows: 下载安装 https://github.com/UB-Mannheim/tesseract/wiki"
fi

echo ""
echo "✅ 依赖安装完成！"
echo ""
echo "📝 下一步："
echo "   1. 确保SigNoz MCP Server已配置"
echo "   2. 运行分析脚本：python scripts/analyze_ticket.py --help"
