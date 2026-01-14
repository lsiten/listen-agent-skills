#!/bin/bash

# 问卷数据分析技能 - 依赖安装脚本

echo "📦 安装问卷数据分析技能依赖包..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

# 检查pip是否安装
if ! command -v pip3 &> /dev/null; then
    echo "❌ 未找到 pip3，请先安装 pip"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"
echo "✅ pip 版本: $(pip3 --version)"

# 安装依赖包
echo ""
echo "📥 开始安装依赖包..."

pip3 install pandas numpy matplotlib seaborn scipy scikit-learn jinja2 openpyxl python-docx python-pptx pdfplumber pytesseract Pillow

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 依赖包安装完成！"
    echo ""
    echo "已安装的包："
    echo "  - pandas (数据处理)"
    echo "  - numpy (数值计算)"
    echo "  - matplotlib (基础绘图)"
    echo "  - seaborn (高级可视化)"
    echo "  - scipy (统计分析)"
    echo "  - scikit-learn (机器学习分析)"
    echo "  - jinja2 (HTML模板渲染)"
    echo "  - openpyxl (Excel文件处理)"
    echo "  - python-docx (Word文件处理)"
    echo "  - python-pptx (PowerPoint文件处理)"
    echo "  - pdfplumber (PDF文件处理)"
    echo "  - pytesseract (OCR文字识别)"
    echo "  - Pillow (图片处理)"
    echo ""
    echo "⚠️  注意：如果使用图片OCR功能，还需要安装Tesseract OCR引擎："
    echo "   macOS: brew install tesseract"
    echo "   Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "   Windows: 下载安装 https://github.com/UB-Mannheim/tesseract/wiki"
else
    echo ""
    echo "❌ 依赖包安装失败，请检查错误信息"
    exit 1
fi
