import os
import random
import shutil

# ===================== 配置已适配你的目录，无需修改 =====================
RAW_DATA_DIR = "./raw_dataset"  # 原始图片根目录
TARGET_DATA_DIR = "./yolo_dataset"  # 生成的YOLO标准数据集路径
SPLIT_RATIO = [0.7, 0.2, 0.1]  # train:val:test 7:2:1拆分比例
# ======================================================================

# 1. 自动读取所有类别，生成固定的类别ID映射
class_names = sorted([d for d in os.listdir(RAW_DATA_DIR) if os.path.isdir(os.path.join(RAW_DATA_DIR, d))])
class_to_id = {name: idx for idx, name in enumerate(class_names)}
print(f"✅ 识别到{len(class_names)}个类别：{class_names}")
print(f"✅ 类别ID映射：{class_to_id}")

# 2. 自动创建YOLO标准目录结构
split_names = ["train", "val", "test"]
for split in split_names:
    os.makedirs(os.path.join(TARGET_DATA_DIR, "images", split), exist_ok=True)
    os.makedirs(os.path.join(TARGET_DATA_DIR, "labels", split), exist_ok=True)

# 3. 生成类别列表文件classes.txt（标注、训练通用）
with open(os.path.join(TARGET_DATA_DIR, "classes.txt"), "w", encoding="utf-8") as f:
    for name in class_names:
        f.write(f"{name}\n")

# 4. 自动生成YOLO训练专用的dataset.yaml配置文件
yaml_content = f"""
# 数据集根目录
path: {os.path.abspath(TARGET_DATA_DIR)}
# 训练/验证/测试集路径
train: images/train
val: images/val
test: images/test

# 类别数量和名称
nc: {len(class_names)}
names: {class_names}
"""
with open(os.path.join(TARGET_DATA_DIR, "dataset.yaml"), "w", encoding="utf-8") as f:
    f.write(yaml_content.strip())

# 5. 按比例拆分每个类别的图片，复制到对应文件夹
random.seed(42)  # 固定随机种子，保证拆分结果可复现
for class_name in class_names:
    class_dir = os.path.join(RAW_DATA_DIR, class_name)
    # 读取该类别下所有有效图片
    img_files = [
        f for f in os.listdir(class_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))
    ]
    random.shuffle(img_files)  # 随机打乱
    total_num = len(img_files)
    print(f"📸 类别{class_name}：共{total_num}张图片")

    # 计算每个数据集的图片数量
    train_num = int(total_num * SPLIT_RATIO[0])
    val_num = int(total_num * SPLIT_RATIO[1])

    # 划分图片列表
    train_imgs = img_files[:train_num]
    val_imgs = img_files[train_num:train_num+val_num]
    test_imgs = img_files[train_num+val_num:]

    # 复制图片到对应文件夹（重命名避免不同类别同名图片覆盖）
    split_img_map = {"train": train_imgs, "val": val_imgs, "test": test_imgs}
    for split_name, imgs in split_img_map.items():
        for img_name in imgs:
            new_img_name = f"{class_name}_{img_name}"
            src_img_path = os.path.join(class_dir, img_name)
            target_img_path = os.path.join(TARGET_DATA_DIR, "images", split_name, new_img_name)
            shutil.copy(src_img_path, target_img_path)

# 运行完成提示
print("="*60)
print(f" 数据集拆分完成！生成路径：{os.path.abspath(TARGET_DATA_DIR)}")
print(f"📁 最终生成的目录结构：")
print(f"{TARGET_DATA_DIR}/")
print(f"├── images/  (train/val/test 拆分后的图片)")
print(f"├── labels/  (后续标注文件存放位置)")
print(f"├── classes.txt  (类别列表)")
print(f"└── dataset.yaml (YOLO训练专用配置文件)")