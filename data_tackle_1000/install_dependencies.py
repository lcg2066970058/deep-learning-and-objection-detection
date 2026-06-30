#!/usr/bin/env python3
"""
安装高精度标注所需的额外依赖
（假设你的conda环境已安装：torch, torchvision, opencv-python, numpy, pillow）
"""

import subprocess
import sys

def install_package(package):
    print(f"安装: {package}")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])

def main():
    print("="*60)
    print("安装高精度标注所需额外依赖...")
    print("="*60)

    install_package("tqdm")

    install_package("git+https://github.com/IDEA-Research/GroundingDINO.git")

    install_package("segment-anything")

    print("\n" + "="*60)
    print("依赖安装完成!")
    print("="*60)
    print("\n请手动下载以下模型文件:")
    print("1. Grounding DINO: groundingdino_swint_ogc.pth")
    print("   下载地址: https://github.com/IDEA-Research/GroundingDINO/releases")
    print("2. SAM ViT-H: sam_vit_h_4b8939.pth")
    print("   下载地址: https://github.com/facebookresearch/segment-anything#model-checkpoints")
    print("\n下载后将模型文件放在项目根目录")

if __name__ == "__main__":
    main()
