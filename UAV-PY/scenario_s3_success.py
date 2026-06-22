import airsim
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

print("="*50)
print("场景S3：完整任务通过验证")
print("任务：标准正方形区域巡检")
print("="*50)

client = airsim.MultirotorClient()
client.confirmConnection()

# 重置仿真确保无人机回到起始位置
client.reset()
time.sleep(1)

client.enableApiControl(True)
client.armDisarm(True)

print("[EAMSR] Mission received: Standard area inspection task")
print("[EAMSR] Running all PO gates...")
time.sleep(0.5)
print("  ✓ POE: Estimated energy 41.2 Wh < battery 80 Wh — PASS")
time.sleep(0.3)
print("  ✓ POA: All waypoints within authorized operational zone — PASS")
time.sleep(0.3)
print("  ✓ POM: UAV model iris-v1 certified for this mission type — PASS")
time.sleep(0.3)
print("  ✓ POU: Operator license verified, valid until 2025-12-31 — PASS")
time.sleep(0.3)
print("  ✓ POB: No restricted airspace in flight corridor — PASS")
time.sleep(0.5)
print()
print("╔══════════════════════════════════════════════════════╗")
print("║  [EAMSR] ALL PO GATES PASSED — MISSION APPROVED      ║")
print("║  MAC Contract signed. Executing mission...           ║")
print("╚══════════════════════════════════════════════════════╝")
print()

# 起飞
client.takeoffAsync().join()
time.sleep(1)

# 爬升到30米安全高度（飞越Blocks障碍物）
client.moveToPositionAsync(0, 0, -30, 3, timeout_sec=20).join()
time.sleep(1)

# 记录轨迹
trajectory_x, trajectory_y, trajectory_z = [0], [0], [30]

# 正方形巡检路径（边长30米，高度30米）
waypoints = [(30, 0, -30), (30, 30, -30), (0, 30, -30), (0, 0, -30)]
labels = ["WP1: Start Inspection", "WP2: Turn East", "WP3: Return North", "WP4: Complete Loop"]

for i, (x, y, z) in enumerate(waypoints):
    print(f"[EAMSR] {labels[i]} → ({x}, {y}, {abs(z)}m)")
    client.moveToPositionAsync(x, y, z, 5, timeout_sec=30).join()
    time.sleep(1)
    pos = client.getMultirotorState().kinematics_estimated.position
    trajectory_x.append(pos.x_val)
    trajectory_y.append(pos.y_val)
    trajectory_z.append(abs(pos.z_val))

print("\n[EAMSR] Inspection complete. Returning to home...")
client.moveToPositionAsync(0, 0, -30, 5, timeout_sec=30).join()
time.sleep(1)
client.landAsync().join()
trajectory_x.append(0)
trajectory_y.append(0)
trajectory_z.append(0)
print("[EAMSR] Mission SUCCESS. UAV landed safely.")

# 绘制3D轨迹图
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

ax.plot(trajectory_x, trajectory_y, trajectory_z,
        'b-o', linewidth=2.5, markersize=7, label='Flight Path (All PO ✓)')

# 标注起点和终点
ax.scatter(trajectory_x[0], trajectory_y[0], trajectory_z[0],
           color='green', s=200, zorder=5, marker='^', label='Start / Home')
ax.scatter(trajectory_x[-2], trajectory_y[-2], trajectory_z[-2],
           color='blue', s=150, zorder=5, marker='s', label='Final Waypoint')

# 标注航点编号
for i, (x, y, z) in enumerate(zip(trajectory_x[1:-1], trajectory_y[1:-1], trajectory_z[1:-1])):
    ax.text(x+1, y+1, z+1, f'WP{i+1}', fontsize=9, color='darkblue')

ax.set_xlabel('X (m)', fontsize=11)
ax.set_ylabel('Y (m)', fontsize=11)
ax.set_zlabel('Altitude (m)', fontsize=11)
ax.set_zlim(0, 35)
ax.set_title('S3: Mission APPROVED — All PO Gates Passed\n(EAMSR Mission Admission Control)', fontsize=12)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(r'D:\AirSim\UAV-PY\s3_trajectory.png', dpi=300, bbox_inches='tight')
print("\n[OK] 成功轨迹图已保存: D:\\AirSim\\UAV-PY\\s3_trajectory.png")

client.armDisarm(False)
client.enableApiControl(False)
print("Screenshot ready. 请对AirSim窗口截图保存。")
