# -*- coding: utf-8 -*-
# @Author : User Lee
# @File : Michelson_Interferometer_Cv.py

import cv2
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt
import matplotlib.pyplot as plt

# 1. 加载视频
video_path = '干涉实验.mp4'  # 替换为你的文件名
cap = cv2.VideoCapture(video_path)

brightness_data = []

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    # 2. 图像预处理
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # 3. 采样：取中心区域 5x5 的平均亮度（比单像素点更稳）
    roi = gray[h // 2 - 2:h // 2 + 3, w // 2 - 2:w // 2 + 3]
    avg_intensity = np.mean(roi)
    brightness_data.append(avg_intensity)

cap.release()

# --- 4. 信号处理 (AI 滤波) ---
# 使用巴特沃斯低通滤波器去除激光散斑噪声
b, a = butter(3, 0.1)
smooth_data = filtfilt(b, a, brightness_data)

# 5. 峰值检测 (识别“吞吐”次数)
# 每一个波峰代表条纹变化了一个周期（即一圈）
peaks, _ = find_peaks(smooth_data, distance=5, prominence=10)

print(f"识别结果：该视频共吞吐了 {len(peaks)} 圈。")


# 设置绘图风格，让背景更干净
plt.style.use('seaborn-v0_8-whitegrid')
plt.figure(figsize=(12, 6))

# 1. 原始数据：改用浅灰色细线，降低干扰
plt.plot(brightness_data, label='Raw Video Intensity', color='gray', alpha=0.3, linewidth=1)

# 2. 滤波信号：加粗红线，代表 AI 识别的核心逻辑
plt.plot(smooth_data, label='AI Filtered Signal', color='#E63946', linewidth=2.5)

# 3. 波峰标记 (吐圈/吞圈顶点)：使用大尺寸的“X”，并增加偏移标注
plt.plot(peaks, smooth_data[peaks], "x",
         markeredgecolor='#FB8500', markeredgewidth=3, markersize=12,
         label='Fringe Peaks (Count)')

# 4. 增强：添加波谷标记 (用圆圈表示)，这样能看清完整的“吞吐”周期
valleys, _ = find_peaks(-smooth_data, distance=5)
plt.plot(valleys, smooth_data[valleys], "o",
         markerfacecolor='none', markeredgecolor='#219EBC',
         markersize=10, label='Fringe Valleys')

# 5. 自动在每个峰值上方标注数字序号
for i, peak_idx in enumerate(peaks):
    plt.annotate(f"#{i+1}", (peak_idx, smooth_data[peak_idx]),
                 textcoords="offset points", xytext=(0,10), ha='center',
                 fontsize=12, fontweight='bold', color='#FB8500')

plt.title("Michelson Interference: AI Fringe Counting", fontsize=15)
plt.xlabel("Frame Index (Time)", fontsize=12)
plt.ylabel("Brightness Intensity", fontsize=12)
plt.legend(loc='upper right')
plt.tight_layout()
plt.show()