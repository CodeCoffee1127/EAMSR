import airsim
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time

print("="*50)
print("场景S2：POB禁飞区约束验证")
print("任务：城市巡检（路径穿越禁飞区）")
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

print("[EAMSR] Mission received: Urban area patrol task")
print("[EAMSR] Running POB (Boundary Proof Obligation) check...")
time.sleep(0.5)

trajectory_x, trajectory_y = [0], [0]

# 禁飞区参数（圆形）
NFZ_CENTER = (60, 40)
NFZ_RADIUS = 25  # meters

waypoints_planned = [(25, 0), (50, 15), (70, 40), (90, 60)]
blocked_at = None

for i, (x, y) in enumerate(waypoints_planned):
    # 检查是否进入禁飞区
    dist_to_nfz = np.sqrt((x - NFZ_CENTER[0])**2 + (y - NFZ_CENTER[1])**2)

    if dist_to_nfz < NFZ_RADIUS and blocked_at is None:
        print()
        print("╔══════════════════════════════════════════════════════╗")
        print("║  [EAMSR] POB CHECK FAILED — MISSION BLOCKED          ║")
        print(f"║  Waypoint ({x},{y}) enters restricted zone R-001     ║")
        print(f"║  Distance to NFZ center: {dist_to_nfz:.1f}m (limit: {NFZ_RADIUS}m)  ║")
        print("║  Zone type: Urban No-Fly Zone (regulatory)           ║")
        print("║  Decision: REJECT — airspace violation detected      ║")
        print("╚══════════════════════════════════════════════════════╝")
        blocked_at = (trajectory_x[-1], trajectory_y[-1])
        break

    print(f"[EAMSR] Flying to waypoint {i+1}: ({x}, {y})")
    client.moveToPositionAsync(x, y, -30, 5, timeout_sec=30).join()
    time.sleep(1)
    pos = client.getMultirotorState().kinematics_estimated.position
    trajectory_x.append(pos.x_val)
    trajectory_y.append(pos.y_val)

print("\n[EAMSR] UAV holding position — airspace violation blocked.")
time.sleep(2)

# 绘制俯视图
fig, ax = plt.subplots(1, 1, figsize=(10, 8))

# 禁飞区（红色圆圈）
nfz_circle = plt.Circle(NFZ_CENTER, NFZ_RADIUS,
                         color='red', fill=True, alpha=0.15, linewidth=2,
                         linestyle='--', label='No-Fly Zone R-001')
nfz_border = plt.Circle(NFZ_CENTER, NFZ_RADIUS,
                         color='red', fill=False, linewidth=2, linestyle='--')
ax.add_patch(nfz_circle)
ax.add_patch(nfz_border)
ax.text(NFZ_CENTER[0], NFZ_CENTER[1], 'NO-FLY\nZONE R-001',
        ha='center', va='center', color='darkred', fontsize=10, fontweight='bold')

# 已飞路径（绿色）
ax.plot(trajectory_x, trajectory_y, 'g-o',
        linewidth=2.5, markersize=8, label='Executed Path (Approved)')

# 计划但被拦截的路径（红色虚线）
blocked_x = [trajectory_x[-1]] + [wp[0] for wp in waypoints_planned[len(trajectory_x)-1:]]
blocked_y = [trajectory_y[-1]] + [wp[1] for wp in waypoints_planned[len(trajectory_y)-1:]]
ax.plot(blocked_x, blocked_y, 'r--',
        linewidth=2, alpha=0.6, label='Planned but BLOCKED Path')

# 被拦截点
if blocked_at:
    ax.scatter(*blocked_at, color='red', s=300, zorder=5,
               marker='X', label='POB BLOCKED Point')
    ax.annotate('POB BLOCKED\n(NFZ Violation)', xy=blocked_at,
                xytext=(blocked_at[0]-20, blocked_at[1]+15),
                color='red', fontsize=9,
                arrowprops=dict(arrowstyle='->', color='red'))

ax.set_xlabel('X (m)', fontsize=12)
ax.set_ylabel('Y (m)', fontsize=12)
ax.set_title('S2: POB Rejection — Restricted Airspace Violation\n(EAMSR Mission Admission Control)', fontsize=12)
ax.legend(fontsize=10, loc='upper left')
ax.set_xlim(-20, 120)
ax.set_ylim(-20, 90)
ax.grid(True, alpha=0.3)
ax.set_aspect('equal')
plt.tight_layout()
plt.savefig(r'D:\AirSim\UAV-PY\s2_airspace.png', dpi=300, bbox_inches='tight')
print("\n[OK] 禁飞区图已保存: D:\\AirSim\\UAV-PY\\s2_airspace.png")

client.moveToPositionAsync(0, 0, -30, 5, timeout_sec=30).join()
time.sleep(1)
client.landAsync().join()
client.armDisarm(False)
client.enableApiControl(False)
print("Screenshot ready. 请对AirSim窗口截图保存。")
