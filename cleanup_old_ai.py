#!/usr/bin/env python3
"""
清理脚本：移除旧的AI模型相关依赖
"""

import subprocess
import sys
import os

def run_command(command):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ 成功执行: {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 执行失败: {command}")
        print(f"错误信息: {e.stderr}")
        return False

def main():
    """主清理函数"""
    print("🧹 开始清理旧的AI模型依赖...")
    
    # 要卸载的包列表
    packages_to_remove = [
        'torch',
        'torchvision', 
        'torchaudio',
        'numpy',  # torch 相关的numpy可能有冲突
        'matplotlib',
        'sympy',
        'networkx',
        'fsspec',
        'filelock',
        'contourpy',
        'cycler',
        'fonttools',
        'kiwisolver',
        'mpmath',
        'packaging',
        'pillow',
        'pyparsing'
    ]
    
    print(f"📦 准备卸载 {len(packages_to_remove)} 个包...")
    
    # 卸载包
    for package in packages_to_remove:
        print(f"卸载 {package}...")
        command = f"pip uninstall {package} -y"
        run_command(command)
    
    print("\n🔄 重新安装项目依赖...")
    
    # 重新安装新的依赖
    if run_command("pip install -r requirements.txt"):
        print("✅ 依赖安装完成!")
    else:
        print("❌ 依赖安装失败，请手动安装")
        
    print("\n🎉 清理完成！项目现在使用轻量化的依赖。")
    print("📝 请确保已在 .env 文件中配置 DEEPSEEK_API_KEY")
    
    # 检查关键依赖是否安装成功
    print("\n🔍 检查关键依赖...")
    critical_packages = ['flask', 'requests', 'python-dotenv', 'gevent']
    
    for package in critical_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装，请手动安装: pip install {package}")

if __name__ == "__main__":
    main() 