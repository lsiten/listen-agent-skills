# Mac M4 LoRA自动化训练 Skill

## 描述

专为Mac M4芯片优化的LoRA（Low-Rank Adaptation）自动化训练工具，支持无GUI操作、参数自动调优、MPS加速和自然语言反馈优化。

## 核心特性

- 🚀 **M4芯片专属优化** - 完全适配ARM架构和MPS加速
- 🧠 **智能参数调优** - 基于自然语言反馈自动调整训练参数
- 📊 **自动化流程** - 从数据准备到模型部署的完整自动化
- 💾 **显存优化** - 针对M4共享内存架构的显存管理策略
- 🔄 **ComfyUI集成** - 训练完成自动拷贝到ComfyUI目录
- 📝 **CSV自动打标** - 自动生成训练数据标注文件

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

## 安装指南

### 1. 环境准备

```bash
# 安装Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装Python 3.10
brew install python@3.10

# 创建虚拟环境
python3.10 -m venv auto_lora_train_venv
source auto_lora_train_venv/bin/activate
```

### 2. 依赖安装

```bash
# 安装PyTorch MPS版本
pip3 install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cpu

# 克隆sd-scripts
git clone https://github.com/kohya-ss/sd-scripts.git
cd sd-scripts

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-macos.txt
pip install pillow==9.5.0 transformers==4.30.2 accelerate==0.21.0 argparse==1.4.0
```

### 3. 目录结构

```
sd-scripts/
├─ models/
│  ├─ base_model/          # 基础模型文件
│  └─ vae/                 # VAE模型文件
├─ configs/
│  └─ Qwen-Image-2512-mps.yaml  # 模型配置
├─ auto_lora_train_mps.py  # 主训练脚本
└─ my_train_images/        # 训练图片目录
```

## 使用方法

### 基础训练命令

```bash
python auto_lora_train_mps.py \
  --train_dir "./my_train_images" \
  --lora_name "my_character_lora" \
  --comfyui_lora_dir "/Users/用户名/ComfyUI/models/Loras" \
  --trigger_word "ai_character"
```

### 带反馈调参训练

```bash
python auto_lora_train_mps.py \
  --train_dir "./my_train_images" \
  --lora_name "my_character_lora_v2" \
  --comfyui_lora_dir "/Users/用户名/ComfyUI/models/Loras" \
  --trigger_word "ai_character" \
  --feedback "角色特征不明显"
```

### 参数说明

- `--train_dir`: 训练图片目录路径
- `--lora_name`: LoRA模型名称（不含后缀）
- `--comfyui_lora_dir`: ComfyUI的LoRA模型目录
- `--trigger_word`: LoRA触发词
- `--feedback`: 自然语言反馈（可选）
- `--ref_img`: 参考图片路径（可选）

## 反馈关键词与参数调整

| 反馈关键词 | 参数调整策略 |
|------------|--------------|
| "特征不明显" | 增加network_dim、延长训练轮数、提高学习率 |
| "风格偏差大" | 降低学习率、减少训练轮数、调整clip_skip |
| "显存不足" | 减少批次大小、降低network_dim、启用梯度检查点 |
| "过拟合" | 降低学习率、减少训练轮数、增加批次大小 |

## M4专属优化

### 显存优化策略
- `network_dim` 最大不超过64
- `train_batch_size` 建议1-2（M4 Max可尝试3）
- 必须启用 `--gradient_checkpointing` 和 `--lowram`
- 训练时关闭其他大型软件

### 性能调优
- 使用混合精度训练（fp16）
- 启用梯度检查点节省显存
- 优化批次大小平衡速度与稳定性

## 常见问题解决

| 问题 | 解决方案 |
|------|----------|
| MPS设备未找到 | 确认macOS≥13.0，验证PyTorch MPS支持 |
| 训练速度慢 | 降低network_dim/批次，启用混合精度 |
| 模型拷贝失败 | 检查ComfyUI目录权限 |
| CLIP评估报错 | 降级transformers到4.30.2 |

## 扩展功能

- **多轮迭代训练**: 支持循环反馈和持续调参
- **训练监控**: 输出详细日志和loss曲线
- **批量处理**: 支持多数据集并行训练
- **提示词优化**: 自动生成高质量触发词

## 技术架构

- **核心框架**: sd-scripts + PyTorch MPS
- **模型支持**: Stable Diffusion 2.x系列
- **加速技术**: MPS (Metal Performance Shaders)
- **评估工具**: CLIP相似度评估
- **自动化**: 端到端训练部署流程
