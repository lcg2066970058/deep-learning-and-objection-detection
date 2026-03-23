import numpy as np

# 生成一个 256x256 的随机二维数组（模拟灰度图）
random_data = np.random.rand(256, 256)  # 数值范围 0~1

# 保存为 .npy 文件
np.save("yournpyfile.npy", random_data)

print("✅ 成功创建：yournpyfile.npy")
print("数据形状：", random_data.shape)
print("数据类型：", random_data.dtype)