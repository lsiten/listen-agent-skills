#!/bin/bash

# {{name}} 任务执行脚本

echo "🚀 执行 {{name}} 任务..."

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --input)
            INPUT="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --config)
            CONFIG="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 验证参数
if [ -z "$INPUT" ]; then
    echo "❌ 缺少 --input 参数"
    exit 1
fi

if [ -z "$OUTPUT" ]; then
    echo "❌ 缺少 --output 参数"
    exit 1
fi

echo "📁 输入: $INPUT"
echo "📁 输出: $OUTPUT"
echo "⚙️ 配置: ${CONFIG:-默认配置}"

# 执行任务
echo "⚡ 开始处理..."
# 在这里添加具体的任务逻辑

echo "✅ 任务完成！"