#!/usr/bin/env python3
"""
改进版YOLOv8自动标注工具
针对西瓜等COCO未包含的类别添加专门处理
"""

from ultralytics import YOLO
import os
import cv2
import numpy as np

def detect_watermelon_by_color(image):
    """通过颜色特征检测西瓜（绿色外表+红色条纹）"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    lower_green = np.array([25, 40, 40])
    upper_green = np.array([85, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    
    lower_red1 = np.array([0, 43, 46])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([156, 43, 46])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask1, mask2)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)
    
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detections = []
    all_contours = contours_green + contours_red
    
    for contour in all_contours:
        area = cv2.contourArea(contour)
        if area > 2000:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h if h > 0 else 0
            if 0.5 < aspect_ratio < 2.0:
                detections.append((x, y, x+w, y+h))
    
    return detections


def main():
    DATASET_DIR = "./yolo_dataset"
    MODEL_PATH = "./yolov8m.pt"
    
    # 你的10个类别
    your_class_names = [
        "airplane", "apple", "car", "cat", "cup",
        "dog", "human", "motorcycle", "umbrella", "watermelon"
    ]
    
    # COCO数据集80类中，前9个类别对应的固定ID
    COCO_CLASS_MAP = {
        "airplane": 4,
        "apple": 47,
        "car": 2,
        "cat": 15,
        "cup": 41,
        "dog": 16,
        "human": 0,
        "motorcycle": 3,
        "umbrella": 25
    }
    
    coco_id_to_your_id = {
        COCO_CLASS_MAP[name]: idx
        for idx, name in enumerate(your_class_names)
        if name in COCO_CLASS_MAP
    }
    
    # 获取西瓜的类别ID
    watermelon_class_id = your_class_names.index("watermelon")
    
    print("正在加载YOLOv8模型...")
    model = YOLO(MODEL_PATH)
    
    split_names = ["train", "val", "test"]
    for split in split_names:
        img_dir = os.path.join(DATASET_DIR, "images", split)
        label_dir = os.path.join(DATASET_DIR, "labels", split)
        os.makedirs(label_dir, exist_ok=True)
        
        print(f"\n正在标注 {split} 集图片...")
        img_count = 0
        
        for img_name in os.listdir(img_dir):
            if not img_name.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                continue
            
            img_path = os.path.join(img_dir, img_name)
            label_name = os.path.splitext(img_name)[0] + ".txt"
            label_path = os.path.join(label_dir, label_name)
            
            img = cv2.imread(img_path)
            if img is None:
                continue
            
            img_h, img_w = img.shape[:2]
            
            # 清空或创建标注文件
            open(label_path, 'w').close()
            
            # 使用YOLO模型预测前9个类别（降低置信度阈值到0.15）
            results = model(img_path, conf=0.15, verbose=False)
            
            with open(label_path, "a", encoding="utf-8") as f:
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        coco_cls_id = int(box.cls)
                        if coco_cls_id in coco_id_to_your_id:
                            your_cls_id = coco_id_to_your_id[coco_cls_id]
                            x1, y1, x2, y2 = box.xyxy[0]
                            x_center = (x1 + x2) / 2 / img_w
                            y_center = (y1 + y2) / 2 / img_h
                            width = (x2 - x1) / img_w
                            height = (y2 - y1) / img_h
                            
                            f.write(f"{your_cls_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            
            # 专门检测西瓜（COCO不包含）
            if "watermelon" in your_class_names:
                watermelon_boxes = detect_watermelon_by_color(img)
                
                with open(label_path, "a", encoding="utf-8") as f:
                    for (x1, y1, x2, y2) in watermelon_boxes:
                        x_center = (x1 + x2) / 2 / img_w
                        y_center = (y1 + y2) / 2 / img_h
                        width = (x2 - x1) / img_w
                        height = (y2 - y1) / img_h
                        
                        f.write(f"{watermelon_class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            
            img_count += 1
            if img_count % 50 == 0:
                print(f"  已标注 {img_count} 张...")
        
        print(f" {split} 集标注完成！共标注 {img_count} 张图片")
    
    print("\n" + "=" * 60)
    print("所有图片自动标注完成！")


if __name__ == "__main__":
    main()
