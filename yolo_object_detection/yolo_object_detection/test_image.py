from ultralytics import YOLO
import cv2

# 加载你训练好的模型
model = YOLO("outputs/train/weights/best.pt")

# 替换成你要测试的图片路径
test_img_path = "datasets/yolo_dataset/images/test/apple_apple_028.jpg"

# 执行检测
results = model(test_img_path, conf=0.5)

# 可视化结果
annotated_img = results[0].plot()
cv2.imshow("检测结果", annotated_img)
print("按任意键关闭窗口")
cv2.waitKey(0)
cv2.destroyAllWindows()

# 打印检测到的物体信息
print("\n检测结果：")
for box in results[0].boxes:
    cls_id = int(box.cls[0])
    cls_name = model.names[cls_id]
    conf = float(box.conf[0])
    bbox = box.xyxy[0].cpu().numpy().astype(int)
    print(f"物体：{cls_name}，置信度：{conf:.2f}，坐标：{bbox}")