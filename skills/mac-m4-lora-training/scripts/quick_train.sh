#!/bin/bash

# Mac M4 LoRA 一键训练脚本
# 使用方法: ./quick_train.sh

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                Mac M4 LoRA 一键训练工具                      ║"
echo "║                                                              ║"
echo "║  🚀 只需提供3个参数即可开始训练                               ║"
echo "║  📁 LoRA名称 + ComfyUI路径 + 训练图片目录                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python"
    exit 1
fi

# 获取用户输入
read -p "🏷️  请输入LoRA名称 (例如: my_character): " LORA_NAME
if [ -z "$LORA_NAME" ]; then
    echo "❌ LoRA名称不能为空"
    exit 1
fi

read -p "📁 请输入ComfyUI安装目录 (例如: /Users/username/ComfyUI): " COMFYUI_DIR
if [ -z "$COMFYUI_DIR" ]; then
    echo "❌ ComfyUI目录不能为空"
    exit 1
fi

read -p "🖼️  请输入训练图片目录 (例如: ./my_images): " TRAIN_DIR
if [ -z "$TRAIN_DIR" ]; then
    echo "❌ 训练图片目录不能为空"
    exit 1
fi

# 可选参数
read -p "🎯 请输入触发词 (可选，回车使用LoRA名称): " TRIGGER_WORD
if [ -z "$TRIGGER_WORD" ]; then
    TRIGGER_WORD="$LORA_NAME"
fi

read -p "💬 训练反馈 (可选，如'特征不明显'): " FEEDBACK

echo
echo "📋 训练配置确认:"
echo "   LoRA名称: $LORA_NAME"
echo "   ComfyUI目录: $COMFYUI_DIR"
echo "   训练图片目录: $TRAIN_DIR"
echo "   触发词: $TRIGGER_WORD"
if [ ! -z "$FEEDBACK" ]; then
    echo "   训练反馈: $FEEDBACK"
fi
echo

read -p "确认开始训练? (y/N): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "❌ 训练已取消"
    exit 0
fi

# 构建Python命令
PYTHON_CMD="python3 auto_lora_train_mps.py --lora_name \"$LORA_NAME\" --comfyui_dir \"$COMFYUI_DIR\" --train_dir \"$TRAIN_DIR\" --trigger_word \"$TRIGGER_WORD\""

if [ ! -z "$FEEDBACK" ]; then
    PYTHON_CMD="$PYTHON_CMD --feedback \"$FEEDBACK\""
fi

echo
echo "🚀 开始执行训练..."
echo "命令: $PYTHON_CMD"
echo

# 执行训练
eval $PYTHON_CMD

# 检查执行结果
if [ $? -eq 0 ]; then
    echo
    echo "🎉 训练完成！"
    echo "LoRA模型已自动部署到ComfyUI"
else
    echo
    echo "❌ 训练失败，请检查错误信息"
    exit 1
fi