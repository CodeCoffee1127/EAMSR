import airsim
import numpy as np
import cv2

client = airsim.MultirotorClient()
client.confirmConnection()

# 设置相机姿态：高空俯视
# NED坐标：z为负表示向上
# 尝试150米高度，如果看不到完整城市范围，可调整到200-300米
camera_pose = airsim.Pose(
    airsim.Vector3r(0, 0, -150),  # 位置：原点上方150米
    airsim.to_quaternion(-np.pi/2, 0, 0)  # pitch=-90度，朝向正下方
)
client.simSetCameraPose("0", camera_pose)

# 获取截图（使用uncompressed格式避免UE4崩溃）
# 第三个参数False表示返回未压缩的RGB数据
responses = client.simGetImages([
    airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)
])

if responses[0].height > 0:
    img1d = np.frombuffer(responses[0].image_data_uint8, dtype=np.uint8)
    img_rgb = img1d.reshape(responses[0].height, responses[0].width, 3)
    
    # 将BGR转换为RGB（OpenCV默认BGR格式）
    img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB)
    
    output_path = r'D:\AirSim\UAV-PY\top_down_view.png'
    cv2.imwrite(output_path, img_rgb, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    print(f"[OK] 俯视截图已保存: {output_path}")
    print(f"图片尺寸: {responses[0].width} x {responses[0].height}")
else:
    print("[ERROR] 获取图像失败，请检查AirSim是否正在运行")
