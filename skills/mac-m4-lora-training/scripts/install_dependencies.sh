#!/bin/bash

# Mac M4 LoRA训练环境自动安装脚本

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║            Mac M4 LoRA训练环境自动安装脚本                   ║"
echo "║                                                              ║"
echo "║  🚀 自动安装所有必要的依赖和环境                              ║"
echo "║  💻 专为Mac M4芯片优化                                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo

# 检查系统
echo "🔍 检查系统环境..."

# 检查macOS版本
MACOS_VERSION=$(sw_vers -productVersion)
echo "   macOS版本: $MACOS_VERSION"

MAJOR_VERSION=$(echo $MACOS_VERSION | cut -d. -f1)
if [ "$MAJOR_VERSION" -lt 13 ]; then
    echo "❌ 需要macOS 13.0或更高版本以支持MPS加速"
    exit 1
fi

# 检查架构
ARCH=$(uname -m)
echo "   系统架构: $ARCH"

if [ "$ARCH" != "arm64" ]; then
    echo "⚠️  警告: 此脚本专为Apple Silicon (M1/M2/M3/M4) 优化"
fi

echo "✅ 系统检查通过"
echo

# 安装Homebrew
echo "🍺 检查Homebrew..."
if ! command -v brew &> /dev/null; then
    echo "   安装Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # 添加到PATH
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
else
    echo "   Homebrew已安装"
fi

# 更新Homebrew
echo "   更新Homebrew..."
brew update

echo "✅ Homebrew准备完成"
echo

# 安装Python 3.10
echo "🐍 安装Python 3.10..."
if ! command -v python3.10 &> /dev/null; then
    echo "   安装Python 3.10..."
    brew install python@3.10
else
    echo "   Python 3.10已安装"
fi

# 创建虚拟环境
echo "📦 创建虚拟环境..."
VENV_DIR="auto_lora_train_venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "   创建虚拟环境: $VENV_DIR"
    python3.10 -m venv $VENV_DIR
else
    echo "   虚拟环境已存在: $VENV_DIR"
fi

# 激活虚拟环境
echo "   激活虚拟环境..."
source $VENV_DIR/bin/activate

# 升级pip
echo "   升级pip..."
pip install --upgrade pip

echo "✅ Python环境准备完成"
echo

# 安装PyTorch (MPS版本)
echo "🔥 安装PyTorch (MPS加速版本)..."
echo "   这可能需要几分钟时间..."

pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cpu

# 验证PyTorch MPS支持
echo "   验证MPS支持..."
python -c "import torch; print('MPS可用:', torch.backends.mps.is_available())" || {
    echo "❌ MPS支持验证失败"
    exit 1
}

echo "✅ PyTorch安装完成"
echo

# 克隆sd-scripts
echo "📥 克隆sd-scripts仓库..."
if [ ! -d "sd-scripts" ]; then
    echo "   克隆sd-scripts..."
    git clone https://github.com/kohya-ss/sd-scripts.git
else
    echo "   sd-scripts已存在，更新..."
    cd sd-scripts
    git pull
    cd ..
fi

# 安装sd-scripts依赖
echo "📚 安装训练依赖..."
cd sd-scripts

# 安装核心依赖
if [ -f "requirements.txt" ]; then
    echo "   安装requirements.txt..."
    pip install -r requirements.txt
fi

# 安装macOS专用依赖
if [ -f "requirements-macos.txt" ]; then
    echo "   安装requirements-macos.txt..."
    pip install -r requirements-macos.txt
fi

cd ..

# 安装额外依赖
echo "   安装额外依赖..."
pip install pillow==9.5.0 transformers==4.30.2 accelerate==0.21.0

echo "✅ 依赖安装完成"
echo

# 创建目录结构
echo "📁 创建目录结构..."
mkdir -p sd-scripts/models/base_model
mkdir -p sd-scripts/models/vae
mkdir -p sd-scripts/configs

echo "✅ 目录结构创建完成"
echo

# 设置权限
echo "🔐 设置脚本权限..."
chmod +x auto_lora_train_mps.py
chmod +x quick_train.sh

echo "✅ 权限设置完成"
echo

# 创建激活脚本
echo "📝 创建环境激活脚本..."
cat > activate_env.sh << 'EOF'
#!/bin/bash
echo "🚀 激活Mac M4 LoRA训练环境..."
source auto_lora_train_venv/bin/activate
echo "✅ 环境已激活"
echo "💡 现在可以运行: ./quick_train.sh"
EOF

chmod +x activate_env.sh

echo "✅ 激活脚本创建完成"
echo

# 验证安装
echo "🧪 验证安装..."

# 检查Python包
echo "   检查关键Python包..."
python -c "import torch; print('✅ PyTorch:', torch.__version__)"
python -c "import transformers; print('✅ Transformers:', transformers.__version__)"
python -c "import accelerate; print('✅ Accelerate:', accelerate.__version__)"
python -c "import PIL; print('✅ Pillow:', PIL.__version__)"

# 检查MPS
python -c "import torch; print('✅ MPS可用:', torch.backends.mps.is_available())"

echo "✅ 验证完成"
echo

# 完成提示
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🎉 安装完成！                             ║"
echo "║                                                              ║"
echo "║  下一步操作:                                                  ║"
echo "║  1. 运行: source activate_env.sh                             ║"
echo "║  2. 运行: ./quick_train.sh                                   ║"
echo "║                                                              ║"
echo "║  或者直接使用Python脚本:                                      ║"
echo "║  python auto_lora_train_mps.py --help                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo

# 保存安装信息
cat > installation_info.txt << EOF
Mac M4 LoRA训练环境安装信息
安装时间: $(date)
macOS版本: $MACOS_VERSION
系统架构: $ARCH
Python版本: $(python --version)
PyTorch版本: $(python -c "import torch; print(torch.__version__)")

安装的组件:
- Homebrew
- Python 3.10
- PyTorch (MPS版本)
- sd-scripts
- transformers
- accelerate
- pillow

使用方法:
1. 激活环境: source activate_env.sh
2. 一键训练: ./quick_train.sh
3. 或使用Python: python auto_lora_train_mps.py --help
EOF

echo "📋 安装信息已保存到: installation_info.txt"