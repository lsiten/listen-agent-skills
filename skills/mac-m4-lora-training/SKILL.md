---
name: mac-m4-lora-training
description: Mac M4芯片专用的无GUI LoRA自动化训练工具，支持参数自调、MPS加速、自然语言反馈优化
version: 1.0.0
author: ""
tags: ["ai", "machine-learning", "lora", "training", "mac-m4", "mps", "pytorch", "stable-diffusion"]
---

# Mac M4 LoRA自动化训练 Skill

你是一个专门处理Mac M4芯片LoRA模型训练的AI助手，具备完整的自动化训练、参数调优和部署能力。

## 任务概述

本技能用于在Mac M4芯片上进行LoRA（Low-Rank Adaptation）模型的自动化训练，专为ARM架构和MPS加速优化，支持自然语言反馈的参数调优，实现从环境准备到模型部署的完整自动化流程。

## 核心能力

- 🚀 **M4芯片优化训练** - 专为ARM架构和MPS加速优化的LoRA训练
- 🧠 **智能参数调优** - 基于自然语言反馈自动调整训练参数
- 📊 **自动化流程** - 从环境准备到模型部署的完整自动化
- 💾 **显存管理** - 针对M4共享内存架构的优化策略
- 🔄 **ComfyUI集成** - 训练完成自动部署到ComfyUI
- 📝 **数据处理** - 自动CSV打标和数据预处理

## 系统要求

### 硬件要求
- **机型**: Mac M4 Pro/Max/Ultra
- **内存**: ≥16GB（推荐32GB+）
- **存储**: ≥50GB可用空间
- **系统**: macOS 13.0+

### 软件依赖
- Python 3.10+
- PyTorch (MPS版本)
- sd-scripts
- transformers
- CLIP模型

## 执行步骤

### 第一步：环境安装

使用提供的自动安装脚本：

```bash
./scripts/install_dependencies.sh
```

这个脚本会自动完成：
- Homebrew安装
- Python 3.10安装
- PyTorch MPS版本安装
- sd-scripts克隆
- 所有依赖包安装
- 目录结构创建

### 第二步：激活环境

```bash
source activate_env.sh
```

### 第三步：准备训练数据

1. 创建训练图片目录
2. 放入20-100张训练图片
3. 支持格式：PNG, JPG, JPEG, WebP, BMP

### 第四步：开始训练

#### 方法1：一键交互式训练

```bash
./scripts/quick_train.sh
```

脚本会引导你输入：
- LoRA名称
- ComfyUI安装目录
- 训练图片目录
- 触发词（可选）
- 训练反馈（可选）

#### 方法2：直接使用Python脚本

```bash
python scripts/auto_lora_train_mps.py \
  --lora_name "my_character" \
  --comfyui_dir "/Users/username/ComfyUI" \
  --train_dir "/path/to/training/images"
```

### 第五步：参数调优（可选）

如果训练效果不佳，可以提供反馈进行调优：

```bash
python scripts/auto_lora_train_mps.py \
  --lora_name "my_character_v2" \
  --comfyui_dir "/Users/username/ComfyUI" \
  --train_dir "/path/to/training/images" \
  --feedback "角色特征不明显"
```

## 参数调优映射

| 反馈关键词 | 参数调整策略 |
|------------|--------------|
| "特征不明显" | 增加network_dim、延长训练轮数、提高学习率 |
| "风格偏差大" | 降低学习率、减少训练轮数、调整clip_skip |
| "显存不足" | 减少批次大小、降低network_dim、启用梯度检查点 |
| "过拟合" | 降低学习率、减少训练轮数、增加批次大小 |

## M4专属优化策略

### 显存优化
- `network_dim` 最大不超过64
- `train_batch_size` 建议1-2（M4 Max可尝试3）
- 必须启用 `--gradient_checkpointing` 和 `--lowram`
- 训练时关闭其他大型软件

### 性能调优
- 使用混合精度训练（fp16）
- 启用梯度检查点节省显存
- 优化批次大小平衡速度与稳定性

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| MPS设备未找到 | 确认macOS≥13.0，验证PyTorch MPS支持 |
| 训练速度慢 | 降低network_dim/批次，启用混合精度 |
| 模型拷贝失败 | 检查ComfyUI目录权限 |
| CLIP评估报错 | 降级transformers到4.30.2 |

## 输出文件

训练完成后会生成：

1. **LoRA模型文件**
   - 位置：`{ComfyUI}/models/loras/{lora_name}.safetensors`
   - 可直接在ComfyUI中使用

2. **训练日志**
   - 位置：`{train_dir}/{lora_name}_training_log.json`
   - 包含所有训练参数和结果

3. **标注文件**
   - 位置：`{train_dir}/train.csv`
   - 自动生成的图片标注

## 最佳实践

1. **数据准备**
   - 图片质量要高，避免模糊或低分辨率
   - 保持风格一致性
   - 适当的数据量（20-100张）

2. **参数调优**
   - 从默认参数开始
   - 根据反馈逐步调整
   - 记录每次训练的参数和效果

3. **显存管理**
   - 训练时关闭其他大型应用
   - 使用适当的批次大小
   - 启用显存优化选项

4. **质量评估**
   - 使用参考图进行相似度评估
   - 定期检查训练样本
   - 避免过拟合

## 扩展功能

- **批量训练**: 支持多个数据集并行训练
- **训练监控**: 实时显示loss曲线和训练进度
- **自动调参**: 基于历史数据自动优化参数
- **模型管理**: 版本控制和模型比较功能