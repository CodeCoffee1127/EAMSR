import airsim
import time

print("正在连接AirSim...")
client = airsim.MultirotorClient()
client.confirmConnection()
print("连接成功！")

client.enableApiControl(True)
client.armDisarm(True)
print("API控制已开启")

# 获取当前无人机状态
state = client.getMultirotorState()
print(f"当前位置: {state.kinematics_estimated.position}")
print("测试完成，AirSim连接正常！")
