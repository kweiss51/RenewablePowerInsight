#!/usr/bin/env python3
"""
Setup script for Energy LLM dependencies
Installs all required packages for custom Language Model training
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip()}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("   Please use Python 3.8 or higher")
        return False

def check_pip():
    """Check if pip is available and update it"""
    print("🔧 Checking pip...")
    try:
        import pip
        print(f"✅ pip is available")
        # Update pip
        return run_command(f"{sys.executable} -m pip install --upgrade pip", "Updating pip")
    except ImportError:
        print("❌ pip is not available")
        return False

def install_pytorch():
    """Install PyTorch with appropriate CUDA support"""
    print("🔥 Installing PyTorch...")
    
    # Check for CUDA
    try:
        result = subprocess.run("nvidia-smi", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("🎮 NVIDIA GPU detected, installing PyTorch with CUDA support")
            torch_command = f"{sys.executable} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
        else:
            print("💻 No NVIDIA GPU detected, installing CPU-only PyTorch")
            torch_command = f"{sys.executable} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
    except:
        print("💻 Installing CPU-only PyTorch")
        torch_command = f"{sys.executable} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
    
    return run_command(torch_command, "Installing PyTorch")

def install_ml_packages():
    """Install machine learning packages"""
    packages = [
        "transformers>=4.21.0",
        "datasets>=2.0.0",
        "accelerate>=0.20.0",
        "tokenizers>=0.13.0",
        "scikit-learn>=1.0.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "tqdm>=4.64.0",
        "wandb>=0.13.0",  # Optional for experiment tracking
        "tensorboard>=2.9.0",  # Optional for logging
    ]
    
    print("🤖 Installing ML packages...")
    package_string = " ".join(packages)
    return run_command(f"{sys.executable} -m pip install {package_string}", "Installing ML packages")

def install_additional_packages():
    """Install additional utility packages"""
    packages = [
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "newspaper3k>=0.2.8",
        "feedparser>=6.0.0",
        "python-dotenv>=0.19.0",
        "flask>=2.2.0"
    ]
    
    print("🛠️ Installing additional packages...")
    package_string = " ".join(packages)
    return run_command(f"{sys.executable} -m pip install {package_string}", "Installing additional packages")

def verify_installation():
    """Verify that key packages are installed correctly"""
    print("🔍 Verifying installation...")
    
    test_imports = [
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("datasets", "Datasets"),
        ("numpy", "NumPy"),
        ("sklearn", "Scikit-learn"),
        ("pandas", "Pandas"),
        ("tqdm", "TQDM")
    ]
    
    all_good = True
    for package, name in test_imports:
        try:
            __import__(package)
            print(f"✅ {name} imported successfully")
        except ImportError as e:
            print(f"❌ {name} import failed: {e}")
            all_good = False
    
    return all_good

def create_config_files():
    """Create configuration files for the ML pipeline"""
    print("📝 Creating configuration files...")
    
    # Create .env template if it doesn't exist
    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        env_content = """# Energy LLM Configuration
# OpenAI API Key (optional, for fallback)
OPENAI_API_KEY=your_openai_api_key_here

# Weights & Biases (optional, for experiment tracking)
WANDB_API_KEY=your_wandb_api_key_here

# Training configuration
ENERGY_LLM_DATA_DIR=training_data/raw
ENERGY_LLM_PROCESSED_DIR=training_data/processed
ENERGY_LLM_MODEL_DIR=model_checkpoints
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Created {env_path}")
    
    # Create directories
    base_dir = Path(__file__).parent.parent
    directories = [
        base_dir / 'training_data' / 'raw',
        base_dir / 'training_data' / 'processed',
        base_dir / 'model_checkpoints',
        base_dir / 'logs'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Energy LLM Setup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check and update pip
    if not check_pip():
        sys.exit(1)
    
    # Install PyTorch
    if not install_pytorch():
        print("❌ PyTorch installation failed. Please install manually:")
        print("   Visit: https://pytorch.org/get-started/locally/")
        sys.exit(1)
    
    # Install ML packages
    if not install_ml_packages():
        print("❌ ML packages installation failed")
        sys.exit(1)
    
    # Install additional packages
    if not install_additional_packages():
        print("❌ Additional packages installation failed")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        sys.exit(1)
    
    # Create config files
    if not create_config_files():
        print("❌ Configuration file creation failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your API keys (optional)")
    print("2. Run data collection: python ml_models/train_pipeline.py --stage collect")
    print("3. Train your custom model: python ml_models/train_pipeline.py --stage all")
    print("4. Your custom Energy LLM will be ready for blog generation!")
    
    print("\n💡 Quick start command:")
    print("python ml_models/train_pipeline.py --model-size base --num-epochs 3")

if __name__ == "__main__":
    main()
