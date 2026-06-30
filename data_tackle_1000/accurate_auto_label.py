#!/usr/bin/env python3
"""
高精度自动标注工具 - Grounding DINO + SAM
完整流程：数据集拆分 + 高精度标注 + YOLO格式输出
支持的10个类别：airplane, apple, car, cat, cup, dog, human, motorcycle, umbrella, watermelon
"""

import os
import cv2
import torch
import numpy as np
import random
import shutil

from tqdm import tqdm


def split_dataset(raw_dir, yolo_dir, split_ratio=[0.7, 0.2, 0.1], seed=42):
    """按比例拆分数据集为train/val/test"""
    class_names = sorted([d for d in os.listdir(raw_dir) if os.path.isdir(os.path.join(raw_dir, d))])
    
    for split in ['train', 'val', 'test']:
        os.makedirs(os.path.join(yolo_dir, 'images', split), exist_ok=True)
        os.makedirs(os.path.join(yolo_dir, 'labels', split), exist_ok=True)
    
    with open(os.path.join(yolo_dir, 'classes.txt'), 'w', encoding='utf-8') as f:
        for name in class_names:
            f.write(f"{name}\n")
    
    yaml_content = f"""path: {os.path.abspath(yolo_dir)}
train: images/train
val: images/val
test: images/test

nc: {len(class_names)}
names: {class_names}
"""
    with open(os.path.join(yolo_dir, 'dataset.yaml'), 'w', encoding='utf-8') as f:
        f.write(yaml_content.strip())
    
    random.seed(seed)
    
    for class_name in class_names:
        class_dir = os.path.join(raw_dir, class_name)
        img_files = [f for f in os.listdir(class_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        random.shuffle(img_files)
        
        total = len(img_files)
        train_num = int(total * split_ratio[0])
        val_num = int(total * split_ratio[1])
        
        train_imgs = img_files[:train_num]
        val_imgs = img_files[train_num:train_num+val_num]
        test_imgs = img_files[train_num+val_num:]
        
        split_map = {'train': train_imgs, 'val': val_imgs, 'test': test_imgs}
        
        for split_name, imgs in split_map.items():
            for img_name in imgs:
                new_name = f"{class_name}_{img_name}"
                src = os.path.join(class_dir, img_name)
                dst = os.path.join(yolo_dir, 'images', split_name, new_name)
                shutil.copy(src, dst)
    
    print(f"✅ 数据集拆分完成！共识别 {len(class_names)} 个类别")
    return class_names


def load_grounding_dino(model_path, config_path, device):
    """加载Grounding DINO模型"""
    try:
        from groundingdino.models import build_model
        from groundingdino.util.slconfig import SLConfig
        from groundingdino.util.utils import clean_state_dict
    except ImportError:
        raise ImportError("请先安装Grounding DINO: pip install git+https://github.com/IDEA-Research/GroundingDINO.git")
    
    args = SLConfig.fromfile(config_path)
    args.device = device
    model = build_model(args)
    checkpoint = torch.load(model_path, map_location="cpu")
    model.load_state_dict(clean_state_dict(checkpoint["model"]), strict=False)
    model.eval()
    model.to(device)
    return model


def load_sam(sam_type="vit_h", checkpoint_path=None, device="cuda"):
    """加载SAM模型"""
    try:
        from segment_anything import sam_model_registry, SamPredictor
    except ImportError:
        raise ImportError("请先安装segment-anything: pip install segment-anything")
    
    if checkpoint_path is None:
        checkpoint_path = "sam_vit_h_4b8939.pth"
    sam = sam_model_registry[sam_type](checkpoint=checkpoint_path)
    sam.to(device=device)
    sam.eval()
    return SamPredictor(sam)


def detect_objects(model, image, text_prompt, box_threshold=0.35, text_threshold=0.025, device="cuda"):
    """使用Grounding DINO检测目标"""
    h, w = image.shape[:2]
    
    caption = text_prompt.lower().strip()
    if not caption.endswith('.'):
        caption = caption + '.'
    
    image_tensor = torch.from_numpy(image).permute(2, 0, 1).float().div(255.).unsqueeze(0).to(device)
    
    with torch.no_grad():
        outputs = model(image_tensor, caption=caption, box_threshold=box_threshold, text_threshold=text_threshold)
    
    boxes = outputs["boxes"].cpu().numpy()
    scores = outputs["scores"].cpu().numpy()
    
    boxes = boxes / np.array([w, h, w, h])
    
    return boxes, scores


def segment_objects(sam_predictor, image, boxes):
    """使用SAM进行精确分割"""
    sam_predictor.set_image(image)
    
    boxes_xyxy = boxes.copy()
    boxes_xyxy[:, [0, 2]] *= image.shape[1]
    boxes_xyxy[:, [1, 3]] *= image.shape[0]
    
    masks = []
    for box in boxes_xyxy:
        box_tensor = torch.as_tensor(box[None, :], dtype=torch.float32, device=sam_predictor.device)
        mask, _, _ = sam_predictor.predict(box=box_tensor, multimask_output=False)
        masks.append(mask[0])
    
    return masks


def save_yolo_label(label_path, class_id, x_center, y_center, width, height):
    """保存YOLO格式标注"""
    with open(label_path, 'a', encoding='utf-8') as f:
        f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")


def process_images(yolo_dir, class_names, dino_model, sam_predictor, device, box_threshold=0.35):
    """处理所有图片并生成标注"""
    splits = ['train', 'val', 'test']
    
    for split in splits:
        img_dir = os.path.join(yolo_dir, 'images', split)
        label_dir = os.path.join(yolo_dir, 'labels', split)
        
        img_files = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        print(f"\n处理 {split} 集 ({len(img_files)} 张图片)...")
        
        for img_file in tqdm(img_files):
            img_path = os.path.join(img_dir, img_file)
            label_path = os.path.join(label_dir, os.path.splitext(img_file)[0] + '.txt')
            
            if os.path.exists(label_path):
                os.remove(label_path)
            
            image = cv2.imread(img_path)
            if image is None:
                continue
            
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w = image.shape[:2]
            
            for class_idx, class_name in enumerate(class_names):
                boxes, scores = detect_objects(dino_model, image_rgb, class_name, box_threshold, device=device)
                
                if len(boxes) == 0:
                    continue
                
                masks = segment_objects(sam_predictor, image_rgb, boxes)
                
                for box, mask, score in zip(boxes, masks, scores):
                    y_indices, x_indices = np.where(mask)
                    if len(y_indices) == 0:
                        continue
                    
                    x_min, x_max = x_indices.min(), x_indices.max()
                    y_min, y_max = y_indices.min(), y_indices.max()
                    
                    x_center = (x_min + x_max) / 2 / w
                    y_center = (y_min + y_max) / 2 / h
                    width = (x_max - x_min) / w
                    height = (y_max - y_min) / h
                    
                    save_yolo_label(label_path, class_idx, x_center, y_center, width, height)


def main():
    # 配置参数
    RAW_DATA_DIR = "./raw_dataset"
    YOLO_DATA_DIR = "./yolo_dataset"
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    
    # 你的10个类别
    CLASS_NAMES = [
        "airplane", "apple", "car", "cat", "cup",
        "dog", "human", "motorcycle", "umbrella", "watermelon"
    ]
    
    print("="*60)
    print("🎯 高精度YOLO数据集标注工具")
    print("="*60)
    print(f"设备: {DEVICE}")
    print(f"类别: {CLASS_NAMES}")
    print("="*60)
    
    # 步骤1: 拆分数据集
    print("\n📁 步骤1: 拆分数据集...")
    split_dataset(RAW_DATA_DIR, YOLO_DATA_DIR)
    
    # 步骤2: 加载模型
    print("\n🤖 步骤2: 加载模型...")
    print("  加载Grounding DINO...")
    try:
        dino_model = load_grounding_dino("groundingdino_swint_ogc.pth", 
                                         "groundingdino/config/GroundingDINO_SwinT_OGC.py", 
                                         DEVICE)
    except Exception as e:
        print(f"  ⚠️  Grounding DINO加载失败: {e}")
        print("  请确保已下载模型文件并放置在正确路径")
        return
    
    print("  加载SAM...")
    try:
        sam_predictor = load_sam("vit_h", "sam_vit_h_4b8939.pth", DEVICE)
    except Exception as e:
        print(f"  ⚠️  SAM加载失败: {e}")
        print("  请确保已下载模型文件并放置在正确路径")
        return
    
    # 步骤3: 标注图片
    print("\n✏️  步骤3: 开始标注...")
    process_images(YOLO_DATA_DIR, CLASS_NAMES, dino_model, sam_predictor, DEVICE)
    
    # 完成
    print("\n🎉 标注完成！")
    print(f"输出目录: {os.path.abspath(YOLO_DATA_DIR)}")
    print("\n目录结构:")
    print("yolo_dataset/")
    print("├── images/")
    print("│   ├── train/")
    print("│   ├── val/")
    print("│   └── test/")
    print("├── labels/")
    print("│   ├── train/")
    print("│   ├── val/")
    print("│   └── test/")
    print("├── classes.txt")
    print("└── dataset.yaml")


if __name__ == "__main__":
    main()
