# # -*- coding: utf-8 -*-
# # @Author : User Lee
# # @File : Michelson_Interferometer_Cv.py
# 
# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# 
# 
# def process_video_with_markers(video_path):
#     cap = cv2.VideoCapture(video_path)
# 
#     # 算法参数
#     brightness_history = []
#     counts = 0
#     state = "INIT"  # 状态机：INIT, LOOKING_FOR_PEAK, LOOKING_FOR_VALLEY
# 
#     # 阈值设置（建议根据你的视频亮度动态调整）
#     # 也可以使用：threshold_high = np.mean(history) + np.std(history)
#     high_thresh = 180
#     low_thresh = 100
# 
#     # 为了让标记明显，我们准备一个实时画布
#     plt.ion()  # 开启交互模式
#     fig, ax = plt.subplots(figsize=(10, 4))
#     line_raw, = ax.plot([], [], color='gray', alpha=0.3, label='Raw')
#     line_smooth, = ax.plot([], [], color='red', linewidth=2, label='AI Filtered')
#     ax.set_ylim(0, 255)
#     ax.legend()
# 
#     frame_idx = 0
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret: break
# 
#         # 1. 区域采样 (ROI)
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         h, w = gray.shape
#         # 取中心点及其周围的小方块平均值，抗噪性更好
#         roi = gray[h // 2 - 5:h // 2 + 5, w // 2 - 5:w // 2 + 5]
#         curr_brightness = np.mean(roi)
#         brightness_history.append(curr_brightness)
# 
#         # 2. 实时滤波 (简单移动平均，适合视频流)
#         window_size = 5
#         if len(brightness_history) > window_size:
#             smooth_val = np.mean(brightness_history[-window_size:])
#         else:
#             smooth_val = curr_brightness
# 
#         # 3. 状态机计数逻辑 (识别 Fringe Peaks 和 Valleys)
#         # 相比简单的阈值，这种逻辑能防止在临界点反复跳变
#         marker_color = (0, 255, 0)  # 默认绿色
#         if state == "INIT":
#             state = "LOOKING_FOR_PEAK"
# 
#         if state == "LOOKING_FOR_PEAK" and smooth_val > high_thresh:
#             counts += 1
#             state = "LOOKING_FOR_VALLEY"
#             marker_color = (0, 255, 255)  # 发现波峰时变黄
# 
#         elif state == "LOOKING_FOR_VALLEY" and smooth_val < low_thresh:
#             state = "LOOKING_FOR_PEAK"
#             marker_color = (255, 0, 0)  # 发现波谷时变蓝
# 
#         # 4. 视频画面上的“明显标记”
#         # 在中心画一个圆圈，颜色随状态改变
#         cv2.circle(frame, (int(w // 2.3), int(h // 2.05)), 20, marker_color, 2)
#         # 绘制巨大的计数文字
#         cv2.putText(frame, f"Fringe Count: {counts}", (50, 80),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
#         # 状态文字
#         cv2.putText(frame, f"State: {state}", (50, 130),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, marker_color, 2)
# 
#         # 5. 更新实时曲线图
#         if frame_idx % 2 == 0:  # 每2帧更新一次图表，节省性能
#             line_raw.set_data(range(len(brightness_history)), brightness_history)
#             line_smooth.set_data(range(len(brightness_history)),
#                                  [np.mean(brightness_history[max(0, i - 5):i + 1]) for i in
#                                   range(len(brightness_history))])
#             ax.set_xlim(max(0, frame_idx - 100), frame_idx + 10)  # 窗口随时间滑动
#             fig.canvas.draw()
#             fig.canvas.flush_events()
# 
#         cv2.imshow('AI Fringe Detector', frame)
#         frame_idx += 1
# 
#         if cv2.waitKey(1) & 0xFF == ord('q'): break
# 
#     cap.release()
#     cv2.destroyAllWindows()
#     plt.ioff()
#     plt.show()
# 
# 
# # 调用
# process_video_with_markers('干涉实验.mp4')


import cv2
import numpy as np


def process_video_with_markers(video_path):
    cap = cv2.VideoCapture(video_path)

    counts = 0
    state = "LOOKING_FOR_PEAK"
    brightness_history = []

    # --- 调整参数 ---
    offset_x = -20  # 负数向左挪，正数向右挪。请根据实际画面调整这个值
    offset_y = 0  # 如果上下也歪了，可以调这个
    window_size = 30

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 1. 自动寻找光圈中心
        _, thresh_img = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        M = cv2.moments(thresh_img)
        if M["m00"] != 0:
            # 计算基础圆心并叠加手动偏移
            center_x = int(M["m10"] / M["m00"]) + offset_x
            center_y = int(M["m01"] / M["m00"]) + offset_y
        else:
            h, w = gray.shape
            center_x = int(w // 2) + offset_x
            center_y = int(h // 2) + offset_y

        # 2. 采样并记录亮度 (确保采样坐标不越界)
        h_img, w_img = gray.shape
        cx = max(5, min(w_img - 5, center_x))
        cy = max(5, min(h_img - 5, center_y))

        roi = gray[cy - 5:cy + 5, cx - 5:cx + 5]
        curr_brightness = np.mean(roi)
        brightness_history.append(curr_brightness)

        # 3. 自适应阈值计算
        if len(brightness_history) > window_size:
            recent_data = brightness_history[-window_size:]
            b_max, b_min = np.max(recent_data), np.min(recent_data)
            dynamic_high = b_min + (b_max - b_min) * 0.7
            dynamic_low = b_min + (b_max - b_min) * 0.3
            smooth_val = np.mean(brightness_history[-5:])

            # 4. 计数逻辑
            marker_color = (0, 255, 0)
            if state == "LOOKING_FOR_PEAK" and smooth_val > dynamic_high:
                counts += 1
                state = "LOOKING_FOR_VALLEY"
                marker_color = (0, 255, 255)
            elif state == "LOOKING_FOR_VALLEY" and smooth_val < dynamic_low:
                state = "LOOKING_FOR_PEAK"
                marker_color = (255, 0, 0)
        else:
            marker_color = (128, 128, 128)

        # 5. 绘制
        cv2.circle(frame, (center_x, center_y), 30, marker_color, 3)
        cv2.putText(frame, f"Fringe Count: {counts}", (50, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)

        cv2.imshow('Manual Offset Adjustment', frame)
        if cv2.waitKey(20) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()


process_video_with_markers('干涉实验.mp4')