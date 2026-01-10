#!/usr/bin/env python3
"""
Mac M4 LoRA自动化训练脚本
只需提供基本参数即可一键开始训练

使用方法:
python auto_lora_train_mps.py --lora_name "my_character" --comfyui_dir "/path/to/ComfyUI" --train_dir "/path/to/images"
"""

import argparse
import subprocess
import shutil
import os
import sys
import json
import time
from pathlib import Path
import torch
from transformers import CLIPProcessor, CLIPModel

# ========================== 核心配置 ==========================

# M4专属基础参数配置
BASE_PARAMS = {
    "network_dim": 32,
    "network_alpha": 32,
    "learning_rate": 2e-4,
    "train_batch_size": 2,  # M4推荐批次
    "max_train_epochs": 50,
    "clip_skip": 2,
    "lowram": True,
    "save_every_n_epochs": 10,
    "save_precision": "fp16",
    "resolution": "512,512",
    "device": "mps",
    "gradient_checkpointing": True,
    "mixed_precision": "fp16"
}

# 反馈-参数映射表
FEEDBACK_PARAM_MAP = {
    "特征不明显": {
        "network_dim": lambda x: min(x+16, 64),
        "max_train_epochs": lambda x: x+20,
        "learning_rate": lambda x: x*1.1
    },
    "风格偏差大": {
        "learning_rate": lambda x: x*0.5,
        "clip_skip": 1,
        "max_train_epochs": lambda x: max(x-10, 30)
    },
    "显存不足": {
        "train_batch_size": lambda x: max(1, x-1),
        "network_dim": lambda x: max(x-16, 16),
        "gradient_checkpointing": True
    },
    "过拟合": {
        "learning_rate": lambda x: x*0.6,
        "max_train_epochs": lambda x: max(x-15, 20),
        "train_batch_size": lambda x: min(x+1, 3)
    }
}

# ========================== 工具函数 ==========================

def print_banner():
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                Mac M4 LoRA 自动化训练工具                    ║
║                                                              ║
║  🚀 专为Mac M4芯片优化                                        ║
║  🧠 智能参数调优                                              ║
║  📊 完整自动化流程                                            ║
║  💾 显存优化管理                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_system_requirements():
    """检查系统要求"""
    print("🔍 检查系统要求...")
    
    # 检查macOS版本
    try:
        result = subprocess.run(['sw_vers', '-productVersion'], capture_output=True, text=True)
        macos_version = result.stdout.strip()
        print(f"   macOS版本: {macos_version}")
        
        major_version = int(macos_version.split('.')[0])
        if major_version < 13:
            print("❌ 需要macOS 13.0或更高版本以支持MPS")
            return False
    except:
        print("⚠️  无法检测macOS版本")
    
    # 检查MPS支持
    try:
        import torch
        mps_available = torch.backends.mps.is_available()
        print(f"   MPS加速: {'✅ 可用' if mps_available else '❌ 不可用'}")
        if not mps_available:
            print("❌ MPS加速不可用，请检查系统配置")
            return False
    except ImportError:
        print("❌ PyTorch未安装")
        return False
    
    # 检查内存
    try:
        result = subprocess.run(['system_profiler', 'SPHardwareDataType'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'Memory:' in line:
                memory = line.split(':')[1].strip()
                print(f"   系统内存: {memory}")
                break
    except:
        print("⚠️  无法检测系统内存")
    
    print("✅ 系统检查完成")
    return True

def setup_environment():
    """设置训练环境"""
    print("🛠️  设置训练环境...")
    
    # 检查sd-scripts目录
    if not os.path.exists('sd-scripts'):
        print("📥 克隆sd-scripts仓库...")
        try:
            subprocess.run(['git', 'clone', 'https://github.com/kohya-ss/sd-scripts.git'], check=True)
        except subprocess.CalledProcessError:
            print("❌ 克隆sd-scripts失败")
            return False
    
    # 检查必要的Python包
    required_packages = ['torch', 'transformers', 'accelerate', 'pillow']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少必要的Python包: {', '.join(missing_packages)}")
        print("请先安装依赖: pip install torch torchvision transformers accelerate pillow")
        return False
    
    print("✅ 环境设置完成")
    return True

def get_user_inputs():
    """获取用户输入参数"""
    parser = argparse.ArgumentParser(description="Mac M4 LoRA 自动训练工具")
    parser.add_argument("--lora_name", type=str, required=True, 
                       help="LoRA模型名称（不含后缀）")
    parser.add_argument("--comfyui_dir", type=str, required=True, 
                       help="ComfyUI安装目录路径")
    parser.add_argument("--train_dir", type=str, required=True, 
                       help="训练图片目录路径")
    parser.add_argument("--trigger_word", type=str, default="", 
                       help="LoRA触发词（可选，默认使用lora_name）")
    parser.add_argument("--feedback", type=str, default="", 
                       help="训练反馈（如'特征不明显'）")
    parser.add_argument("--base_model", type=str, default="", 
                       help="基础模型路径（可选）")
    
    args = parser.parse_args()
    
    # 设置默认触发词
    if not args.trigger_word:
        args.trigger_word = args.lora_name
    
    return args

def validate_paths(args):
    """验证路径有效性"""
    print("📁 验证路径...")
    
    # 检查训练目录
    if not os.path.exists(args.train_dir):
        print(f"❌ 训练目录不存在: {args.train_dir}")
        return False
    
    # 检查训练图片
    img_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')
    image_files = [f for f in os.listdir(args.train_dir) 
                   if f.lower().endswith(img_extensions)]
    
    if len(image_files) == 0:
        print(f"❌ 训练目录中没有找到图片文件: {args.train_dir}")
        return False
    
    print(f"   找到 {len(image_files)} 张训练图片")
    
    # 检查ComfyUI目录
    comfyui_lora_dir = os.path.join(args.comfyui_dir, "models", "loras")
    if not os.path.exists(comfyui_lora_dir):
        print(f"❌ ComfyUI LoRA目录不存在: {comfyui_lora_dir}")
        print("请确认ComfyUI安装路径正确")
        return False
    
    print(f"   ComfyUI LoRA目录: {comfyui_lora_dir}")
    
    print("✅ 路径验证完成")
    return True

def parse_feedback(feedback_text):
    """解析用户反馈并调整参数"""
    adjusted_params = {}
    if not feedback_text:
        return adjusted_params
    
    print(f"🧠 解析训练反馈: {feedback_text}")
    
    for keyword, param_rules in FEEDBACK_PARAM_MAP.items():
        if keyword in feedback_text:
            print(f"   检测到关键词: {keyword}")
            for param, rule in param_rules.items():
                if callable(rule):
                    adjusted_params[param] = rule(BASE_PARAMS.get(param, 0))
                else:
                    adjusted_params[param] = rule
    
    if adjusted_params:
        print(f"   调整参数: {adjusted_params}")
    
    return adjusted_params

def generate_train_csv(train_dir, trigger_word):
    """生成训练CSV文件"""
    print("📝 生成训练标注文件...")
    
    csv_path = os.path.join(train_dir, "train.csv")
    img_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')
    
    image_count = 0
    with open(csv_path, "w", encoding="utf-8") as f:
        for img_name in os.listdir(train_dir):
            if img_name.lower().endswith(img_extensions):
                img_path = os.path.join(train_dir, img_name)
                f.write(f"{img_path},{trigger_word}\n")
                image_count += 1
    
    print(f"   生成标注文件: {csv_path}")
    print(f"   标注图片数量: {image_count}")
    
    return csv_path

def create_config_file(train_dir):
    """创建模型配置文件"""
    config_dir = os.path.join("sd-scripts", "configs")
    os.makedirs(config_dir, exist_ok=True)
    
    config_path = os.path.join(config_dir, "training_config.yaml")
    
    config_content = """
model:
  model_type: "sd2"
  
training:
  resolution: 512
  clip_skip: 2
  gradient_checkpointing: true
  mixed_precision: "fp16"
  device: "mps"
"""
    
    with open(config_path, "w") as f:
        f.write(config_content)
    
    return config_path

def build_training_command(args, final_params, csv_path, config_path):
    """构建训练命令"""
    print("🔧 构建训练命令...")
    
    # 创建输出目录
    output_dir = os.path.join(args.train_dir, "lora_output")
    os.makedirs(output_dir, exist_ok=True)
    
    # 基础命令
    cmd = [
        "python", "train_network.py",
        "--train_data_dir", args.train_dir,
        "--output_dir", output_dir,
        "--network_module", "networks.lora",
        "--network_dim", str(final_params["network_dim"]),
        "--network_alpha", str(final_params["network_alpha"]),
        "--learning_rate", str(final_params["learning_rate"]),
        "--train_batch_size", str(final_params["train_batch_size"]),
        "--max_train_epochs", str(final_params["max_train_epochs"]),
        "--save_every_n_epochs", str(final_params["save_every_n_epochs"]),
        "--save_precision", final_params["save_precision"],
        "--resolution", final_params["resolution"],
        "--clip_skip", str(final_params["clip_skip"]),
        "--mixed_precision", final_params["mixed_precision"],
        "--output_name", args.lora_name
    ]
    
    # 添加可选参数
    if final_params.get("lowram"):
        cmd.append("--lowram")
    
    if final_params.get("gradient_checkpointing"):
        cmd.append("--gradient_checkpointing")
    
    # 如果有基础模型
    if args.base_model and os.path.exists(args.base_model):
        cmd.extend(["--pretrained_model_name_or_path", args.base_model])
    
    print(f"   输出目录: {output_dir}")
    
    return cmd, output_dir

def run_training(cmd):
    """执行训练"""
    print("🚀 开始LoRA训练...")
    print(f"   训练命令: {' '.join(cmd)}")
    
    # 切换到sd-scripts目录
    original_dir = os.getcwd()
    os.chdir("sd-scripts")
    
    try:
        # 执行训练
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # 实时输出训练日志
        for line in process.stdout:
            print(f"   {line.rstrip()}")
        
        process.wait()
        
        if process.returncode != 0:
            raise Exception(f"训练失败，返回码: {process.returncode}")
        
        print("✅ 训练完成")
        
    finally:
        os.chdir(original_dir)

def copy_lora_to_comfyui(output_dir, lora_name, comfyui_dir):
    """拷贝LoRA模型到ComfyUI"""
    print("📦 部署LoRA模型到ComfyUI...")
    
    # 查找生成的LoRA文件
    lora_files = []
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".safetensors") and lora_name in file:
                lora_files.append(os.path.join(root, file))
    
    if not lora_files:
        print("❌ 未找到生成的LoRA模型文件")
        return False
    
    # 选择最新的文件
    latest_lora = max(lora_files, key=os.path.getmtime)
    print(f"   找到LoRA文件: {os.path.basename(latest_lora)}")
    
    # 拷贝到ComfyUI
    comfyui_lora_dir = os.path.join(comfyui_dir, "models", "loras")
    target_path = os.path.join(comfyui_lora_dir, f"{lora_name}.safetensors")
    
    try:
        shutil.copy2(latest_lora, target_path)
        print(f"✅ LoRA模型已部署到: {target_path}")
        return True
    except Exception as e:
        print(f"❌ 拷贝失败: {e}")
        return False

def save_training_log(args, final_params, success=True):
    """保存训练日志"""
    log_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "lora_name": args.lora_name,
        "train_dir": args.train_dir,
        "trigger_word": args.trigger_word,
        "feedback": args.feedback,
        "parameters": final_params,
        "success": success
    }
    
    log_file = os.path.join(args.train_dir, f"{args.lora_name}_training_log.json")
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    print(f"📋 训练日志已保存: {log_file}")

def print_summary(args, success=True):
    """打印训练总结"""
    print("\n" + "="*60)
    if success:
        print("🎉 LoRA训练完成！")
        print(f"   模型名称: {args.lora_name}")
        print(f"   触发词: {args.trigger_word}")
        print(f"   ComfyUI路径: {os.path.join(args.comfyui_dir, 'models', 'loras', f'{args.lora_name}.safetensors')}")
        print("\n💡 使用提示:")
        print(f"   在ComfyUI中加载LoRA: {args.lora_name}.safetensors")
        print(f"   在提示词中使用: {args.trigger_word}")
    else:
        print("❌ 训练失败")
        print("请检查错误信息并重试")
    print("="*60)

# ========================== 主函数 ==========================

def main():
    """主函数"""
    try:
        # 打印启动横幅
        print_banner()
        
        # 获取用户输入
        args = get_user_inputs()
        
        # 检查系统要求
        if not check_system_requirements():
            sys.exit(1)
        
        # 设置环境
        if not setup_environment():
            sys.exit(1)
        
        # 验证路径
        if not validate_paths(args):
            sys.exit(1)
        
        # 解析反馈并调整参数
        adjusted_params = parse_feedback(args.feedback)
        final_params = {**BASE_PARAMS, **adjusted_params}
        
        print(f"🎯 最终训练参数:")
        for key, value in final_params.items():
            print(f"   {key}: {value}")
        
        # 生成训练文件
        csv_path = generate_train_csv(args.train_dir, args.trigger_word)
        config_path = create_config_file(args.train_dir)
        
        # 构建训练命令
        cmd, output_dir = build_training_command(args, final_params, csv_path, config_path)
        
        # 执行训练
        run_training(cmd)
        
        # 部署到ComfyUI
        copy_success = copy_lora_to_comfyui(output_dir, args.lora_name, args.comfyui_dir)
        
        # 保存训练日志
        save_training_log(args, final_params, copy_success)
        
        # 打印总结
        print_summary(args, copy_success)
        
    except KeyboardInterrupt:
        print("\n⚠️  训练被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 训练过程出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()