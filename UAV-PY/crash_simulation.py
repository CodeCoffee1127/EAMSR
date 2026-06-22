import airsim
import time
import math

print("="*55)
print("UAV Crash Simulation — Uncontrolled Descent & Motor Stall")
print("="*55)

client = airsim.MultirotorClient()
client.confirmConnection()
client.reset()
time.sleep(1.5)
client.enableApiControl(True)
client.armDisarm(True)

print("[EAMSR] Mission received: Long-range inspection")
print("[EAMSR] POE check: FAIL — insufficient energy for safe return")
print("[EAMSR] Operator override: MISSION FORCED")
print()

# 起飞并爬升到20米
client.takeoffAsync().join()
time.sleep(1)
client.moveToPositionAsync(0, 0, -20, 5, timeout_sec=20).join()
time.sleep(0.5)

# 飞向远距离航点
print("[EAMSR] Executing waypoint 1/3: (60m, 0m, 20m alt)")
client.moveToPositionAsync(60, 0, -20, 8, timeout_sec=30).join()
time.sleep(0.5)

print("[EAMSR] Executing waypoint 2/3: (120m, 0m, 20m alt)")
client.moveToPositionAsync(120, 0, -20, 8, timeout_sec=30).join()
time.sleep(0.5)

# 模拟POE拦截失败后的坠机场景
print()
print("╔═══════════════════════════════════════════════════════╗")
print("║  ⚠ CRITICAL: Battery at 3.2% — Emergency Landing     ║")
print("║  GPS: (120.0, 0.0, 20.0m) | Wind: 12 km/h NW        ║")
print("║  Motor #3: STALL DETECTED                             ║")
print("╚═══════════════════════════════════════════════════════╝")
print()
print("[CRASH] Simulating motor #3 stall — asymmetric thrust initiated")

# 施加极端横滚角，模拟电机失速导致的失控翻转
client.moveByRollPitchYawZAsync(
    roll=math.pi / 2.5,   # 72度横滚，机体严重倾斜
    pitch=0.3,
    yaw=0,
    z=-15,
    duration=1.5
).join()

time.sleep(0.5)

# 再叠加偏航旋转，形成螺旋下坠感
print("[CRASH] Initiating spiral dive with asymmetric velocity...")
client.moveByVelocityAsync(
    vx=3, vy=3, vz=8,   # vz正值=向下，产生俯冲感
    duration=1.5
).join()

print("[CRASH] Releasing API control — uncontrolled descent")
client.enableApiControl(False)
client.armDisarm(False)

# 等待坠落画面稳定，立即截图
print("\n[!] 请在 AirSim 窗口中截图 (Win+Shift+S)...")
print("    无人机正在失控下坠，画面将保持 10 秒...")
for i in range(10, 0, -1):
    print(f"    倒计时: {i} 秒", end='\r')
    time.sleep(1)
print("\n[DONE] 截图完成！")
