"""
YOLO格式自动标注工具（适配YOLOv8）
功能：基于YOLOv8预训练模型，批量为图片生成YOLO格式的标注文件
适配：你的10类数据集（human/car/motorcycle/airplane/umbrella/cat/dog/cup/apple/watermelon）
"""
from ultralytics import YOLO
import os
import sys
from pathlib import Path

# ===================== 核心配置项（根据你的实际情况修改） =====================
# 1. 数据集根目录（拆分后的YOLO数据集路径）
DATASET_ROOT = "./yolo_dataset"
# 2. YOLOv8预训练模型路径（本地文件或自动下载）
MODEL_PATH = "./yolov8m.pt"  # 本地有文件则用本地，无则自动下载
# 3. 置信度阈值（过滤低置信度的错误标注，建议0.5-0.7）
CONF_THRESHOLD = 0.5
# 4. 需要标注的图片格式
SUPPORTED_IMG_FORMATS = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")
# =============================================================================

# -------------------- 固定配置（无需修改） --------------------
# COCO数据集80类 → 你的10类 映射表（COCO ID: 类别名）
COCO_ID_TO_NAME = {
    0: "human",
    2: "car",
    3: "motorcycle",
    4: "airplane",
    25: "umbrella",
    15: "cat",
    16: "dog",
    41: "cup",
    47: "apple",
    49: "watermelon"
}
# 反向映射：类别名 → COCO ID
NAME_TO_COCO_ID = {v: k for k, v in COCO_ID_TO_NAME.items()}


def check_environment():
    """检查运行环境和前置条件"""
    print("===== 环境检查 =====")
    # 1. 检查数据集目录是否存在
    dataset_path = Path(DATASET_ROOT)
    if not dataset_path.exists():
        print(f"❌ 数据集目录不存在：{DATASET_ROOT}")
        print("请确认已运行split_dataset.py生成拆分后的数据集")
        sys.exit(1)

    # 2. 检查classes.txt是否存在
    classes_file = dataset_path / "classes.txt"
    if not classes_file.exists():
        print(f"❌ 类别文件不存在：{classes_file}")
        sys.exit(1)

    # 3. 读取并验证类别列表
    with open(classes_file, "r", encoding="utf-8") as f:
        global YOUR_CLASS_NAMES, NAME_TO_YOUR_ID
        YOUR_CLASS_NAMES = [line.strip() for line in f.readlines() if line.strip()]
        NAME_TO_YOUR_ID = {name: idx for idx, name in enumerate(YOUR_CLASS_NAMES)}

    # 验证类别是否匹配
    unmatched_classes = [name for name in YOUR_CLASS_NAMES if name not in NAME_TO_COCO_ID]
    if unmatched_classes:
        print(f"❌ 以下类别不在COCO映射表中：{unmatched_classes}")
        print("请检查classes.txt中的类别名是否正确")
        sys.exit(1)

    # 4. 检查图片文件夹是否存在
    for split in ["train", "val", "test"]:
        img_dir = dataset_path / "images" / split
        if not img_dir.exists():
            print(f"❌ 图片文件夹不存在：{img_dir}")
            sys.exit(1)
        if len(list(img_dir.glob("*"))) == 0:
            print(f"⚠️  图片文件夹为空：{img_dir}")

    print("✅ 环境检查通过")
    return True


def generate_yolo_annotation(model, img_path, label_path):
    """
    为单张图片生成YOLO格式标注
    :param model: 加载好的YOLO模型
    :param img_path: 图片路径
    :param label_path: 标注文件保存路径
    """
    try:
        # 1. 模型预测（关闭冗余日志）
        results = model(
            img_path,
            verbose=False,
            conf=CONF_THRESHOLD,  # 过滤低置信度框
            imgsz=640  # 统一输入尺寸，提升预测稳定性
        )
        result = results[0]  # 取第一张图片的预测结果

        # 2. 获取原图尺寸（从预测结果中获取，无需额外读取图片）
        img_h, img_w = result.orig_shape

        # 3. 解析预测框，生成YOLO标注
        with open(label_path, "w", encoding="utf-8") as f:
            if result.boxes is None:
                return True  # 无目标，生成空文件

            for box in result.boxes:
                # 获取COCO类别ID和置信度
                coco_cls_id = int(box.cls)
                conf = float(box.conf)

                # 过滤非目标类别
                if coco_cls_id not in COCO_ID_TO_NAME:
                    continue

                # 转换为你的类别ID
                cls_name = COCO_ID_TO_NAME[coco_cls_id]
                your_cls_id = NAME_TO_YOUR_ID[cls_name]

                # 转换为YOLO格式（归一化中心坐标、宽高）
                x1, y1, x2, y2 = box.xyxy[0]  # 左上角、右下角坐标
                x_center = (x1 + x2) / 2 / img_w
                y_center = (y1 + y2) / 2 / img_h
                width = (x2 - x1) / img_w
                height = (y2 - y1) / img_h

                # 写入标注文件（保留6位小数，符合YOLO标准）
                f.write(
                    f"{your_cls_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
                )

        return True

    except Exception as e:
        print(f"❌ 处理图片失败 {img_path}：{str(e)}")
        return False


def batch_annotate():
    """批量标注train/val/test数据集"""
    # 1. 加载YOLO模型
    print("\n===== 加载模型 =====")
    try:
        model = YOLO(MODEL_PATH)
        print(f"✅ 模型加载成功：{MODEL_PATH}")
    except Exception as e:
        print(f"❌ 模型加载失败：{str(e)}")
        sys.exit(1)

    # 2. 遍历所有数据集拆分（train/val/test）
    dataset_path = Path(DATASET_ROOT)
    total_success = 0
    total_failed = 0

    for split in ["train", "val", "test"]:
        print(f"\n===== 开始标注 {split} 集 =====")
        # 定义路径
        img_dir = dataset_path / "images" / split
        label_dir = dataset_path / "labels" / split
        label_dir.mkdir(exist_ok=True)  # 创建标注文件夹（不存在则创建）

        # 遍历图片文件
        img_files = [f for f in img_dir.glob("*") if f.suffix.lower() in SUPPORTED_IMG_FORMATS]
        if not img_files:
            print(f"⚠️  无图片需要标注：{img_dir}")
            continue

        # 批量处理
        success = 0
        failed = 0
        for idx, img_file in enumerate(img_files, 1):
            # 标注文件路径（和图片同名，后缀改为.txt）
            label_file = label_dir / f"{img_file.stem}.txt"

            # 生成标注
            if generate_yolo_annotation(model, str(img_file), str(label_file)):
                success += 1
            else:
                failed += 1

            # 每50张输出一次进度
            if idx % 50 == 0:
                print(f"  进度：{idx}/{len(img_files)} 张，成功：{success}，失败：{failed}")

        # 输出拆分集统计
        print(f"✅ {split} 集标注完成：")
        print(f"  总数：{len(img_files)} 张")
        print(f"  成功：{success} 张")
        print(f"  失败：{failed} 张")
        print(f"  标注文件保存至：{label_dir}")

        total_success += success
        total_failed += failed

    # 输出总统计
    print("\n===== 标注完成 ======")
    print(f"📊 总统计：")
    print(f"  成功标注：{total_success} 张")
    print(f"  标注失败：{total_failed} 张")
    print(f"  所有标注文件已保存至 {DATASET_ROOT}/labels 目录")


if __name__ == "__main__":
    # 1. 检查环境
    if not check_environment():
        sys.exit(1)

    # 2. 批量标注
    batch_annotate()