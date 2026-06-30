from ultralytics import YOLO
import os
import cv2

# ===================== 已适配你的目录，无需修改 =====================
DATASET_DIR = "./yolo_dataset"  # 拆分好的YOLO数据集路径
MODEL_PATH = "./yolov8m.pt"  # 刚下载的模型路径
# ==================================================================

# 1. 读取你的类别列表，和COCO预训练模型做精准映射
with open(os.path.join(DATASET_DIR, "classes.txt"), "r", encoding="utf-8") as f:
    your_class_names = [line.strip() for line in f.readlines()]

# COCO数据集80类中，你的10个类别对应的固定ID（无需修改）
COCO_CLASS_MAP = {
    "airplane": 4,
    "apple": 47,
    "car": 2,
    "cat": 15,
    "cup": 41,
    "dog": 16,
    "human": 0,
    "motorcycle": 3,
    "umbrella": 25,
    "watermelon": 49
}
# 生成COCO ID → 你的类别ID的映射
coco_id_to_your_id = {
    COCO_CLASS_MAP[name]: idx
    for idx, name in enumerate(your_class_names)
    if name in COCO_CLASS_MAP
}

# 2. 加载YOLOv8预训练模型
print("正在加载YOLOv8模型...")
model = YOLO(MODEL_PATH)

# 3. 遍历train/val/test三个文件夹，批量生成YOLO格式标注
split_names = ["train", "val", "test"]
for split in split_names:
    img_dir = os.path.join(DATASET_DIR, "images", split)
    label_dir = os.path.join(DATASET_DIR, "labels", split)
    os.makedirs(label_dir, exist_ok=True)

    print(f"\n正在标注 {split} 集图片...")
    # 遍历所有图片
    img_count = 0
    for img_name in os.listdir(img_dir):
        if not img_name.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
            continue

        img_path = os.path.join(img_dir, img_name)
        # 标注文件路径：和图片同名，后缀为.txt
        label_name = os.path.splitext(img_name)[0] + ".txt"
        label_path = os.path.join(label_dir, label_name)

        # 用YOLO模型预测目标
        results = model(img_path, verbose=False)

        # 解析预测结果，生成YOLO格式标注
        img = cv2.imread(img_path)
        img_h, img_w = img.shape[:2]

        with open(label_path, "w", encoding="utf-8") as f:
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    coco_cls_id = int(box.cls)
                    # 只保留你的10个类别，过滤其他无关目标
                    if coco_cls_id not in coco_id_to_your_id:
                        continue

                    # 转换为你的类别ID
                    your_cls_id = coco_id_to_your_id[coco_cls_id]
                    # 转换为YOLO标准格式：class_id x_center y_center width height（归一化）
                    x1, y1, x2, y2 = box.xyxy[0]
                    x_center = (x1 + x2) / 2 / img_w
                    y_center = (y1 + y2) / 2 / img_h
                    width = (x2 - x1) / img_w
                    height = (y2 - y1) / img_h

                    # 写入标注文件
                    f.write(f"{your_cls_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        img_count += 1
        if img_count % 50 == 0:
            print(f"  已标注 {img_count} 张...")

    print(f" {split} 集标注完成！共标注 {img_count} 张图片，标注文件保存在：{label_dir}")

print("\n" + "=" * 60)
print("所有图片自动标注完成！")
print("你的完整YOLO数据集已经准备好，可直接用于模型训练")