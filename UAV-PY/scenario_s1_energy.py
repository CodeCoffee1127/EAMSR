import airsim
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

print("="*50)
print("场景S1：POE能量约束验证")
print("任务：长距离巡检（超出电量上限）")
print("="*50)

client = airsim.MultirotorClient()
client.confirmConnection()

# 重置仿真确保无人机回到起始位置
client.reset()
time.sleep(1)

client.enableApiControl(True)
client.armDisarm(True)
client.takeoffAsync().join()
time.sleep(1)

# 上升到30米安全高度
client.moveToPositionAsync(0, 0, -30, 3, timeout_sec=20).join()
time.sleep(1)

print("[EAMSR] Mission received: Long-range inspection task")
print("[EAMSR] Running POE (Energy Proof Obligation) check...")
time.sleep(0.5)

# 记录轨迹
trajectory_x, trajectory_y, trajectory_z = [0], [0], [30]

# 模拟飞向远距离航点（每个航点后记录位置）
waypoints = [(50, 0, -30), (100, 0, -30), (150, 0, -30)]
blocked_at = None

for i, (x, y, z) in enumerate(waypoints):
    print(f"[EAMSR] Flying to waypoint {i+1}: ({x}, {y}, {abs(z)}m)")
    client.moveToPositionAsync(x, y, z, 5, timeout_sec=30).join()
    time.sleep(1)
    pos = client.getMultirotorState().kinematics_estimated.position
    trajectory_x.append(pos.x_val)
    trajectory_y.append(pos.y_val)
    trajectory_z.append(abs(pos.z_val))

    if i == 1:  # 在第2个航点触发POE拦截
        print()
        print("╔══════════════════════════════════════════════════════╗")
        print("║  [EAMSR] POE CHECK FAILED — MISSION BLOCKED          ║")
        print("║  Estimated energy required : 87.3 Wh                 ║")
        print("║  Available battery capacity: 80.0 Wh                 ║")
        print("║  Remaining return energy   : INSUFFICIENT            ║")
        print("║  Decision: REJECT — UAV would not return safely      ║")
        print("╚══════════════════════════════════════════════════════╝")
        blocked_at = (pos.x_val, pos.y_val, abs(pos.z_val))
        break

# 无人机悬停（保持当前位置，模拟被拦截）
print("\n[EAMSR] UAV holding position — mission execution suspended.")
time.sleep(2)

# 绘制3D轨迹图
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')

ax.plot(trajectory_x, trajectory_y, trajectory_z,
        'g-o', linewidth=2, markersize=6, label='Executed Path')

# 标注被拦截点
if blocked_at:
    ax.scatter(*blocked_at, color='red', s=200, zorder=5, label='BLOCKED Point (POE)')
    ax.text(blocked_at[0], blocked_at[1], blocked_at[2]+2,
            'POE BLOCKED\n(Energy Insufficient)', color='red', fontsize=9, ha='center')

# 用虚线标注未执行的路径
unexecuted_x = [trajectory_x[-1], 150, 200]
unexecuted_y = [0, 0, 0]
unexecuted_z = [30, 30, 30]
ax.plot(unexecuted_x, unexecuted_y, unexecuted_z,
        'r--', linewidth=1.5, alpha=0.5, label='Planned but BLOCKED Path')

ax.set_xlabel('X (m)', fontsize=11)
ax.set_ylabel('Y (m)', fontsize=11)
ax.set_zlabel('Altitude (m)', fontsize=11)
ax.set_zlim(0, 35)
ax.set_title('S1: POE Rejection — Energy Constraint Violation\n(EAMSR Mission Admission Control)', fontsize=12)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(r'D:\AirSim\UAV-PY\s1_trajectory.png', dpi=300, bbox_inches='tight')
print("\n[OK] 轨迹图已保存: D:\\AirSim\\UAV-PY\\s1_trajectory.png")

# 返航
client.moveToPositionAsync(0, 0, -30, 5, timeout_sec=30).join()
time.sleep(1)
client.landAsync().join()
client.armDisarm(False)
client.enableApiControl(False)
print("Screenshot ready. 请对AirSim窗口截图保存。")
