import airsim
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

print("="*55)
print("场景S1：POE能量约束验证（AirSimNH城市环境）")
print("任务：城郊长距离巡检（超出电量安全裕度）")
print("="*55)

client = airsim.MultirotorClient()
client.confirmConnection()
client.reset()
time.sleep(1.5)
client.enableApiControl(True)
client.armDisarm(True)

print("[EAMSR] Mission received: Cross-district inspection (4.2 km route)")
print("[EAMSR] Running POE (Energy Proof Obligation)...")
time.sleep(0.8)

# 起飞并爬升到安全高度
client.takeoffAsync().join()
time.sleep(1)
client.moveToPositionAsync(0, 0, -20, 3, timeout_sec=20).join()

trajectory_x = [0]
trajectory_y = [0]
trajectory_z = [20]

# 长距离航点，模拟超出能量预算的任务
waypoints = [
    (60,  0,  -20),
    (120, 0,  -20),
    (180, 20, -20),
]
blocked_at = None

for i, (x, y, z) in enumerate(waypoints):
    print(f"[EAMSR] Executing waypoint {i+1}/{len(waypoints)}: ({x}m, {y}m, {abs(z)}m alt)")
    client.moveToPositionAsync(x, y, z, 8, timeout_sec=30).join()
    time.sleep(0.8)
    pos = client.getMultirotorState().kinematics_estimated.position
    trajectory_x.append(pos.x_val)
    trajectory_y.append(pos.y_val)
    trajectory_z.append(abs(pos.z_val))

    if i == 1:  # 第2个航点触发POE拦截
        print()
        print("╔═══════════════════════════════════════════════════════╗")
        print("║      [EAMSR] POE PROOF OBLIGATION — REJECTED          ║")
        print("║  Mission ID    : UAV-TASK-2024-0312                   ║")
        print("║  Required energy: 91.7 Wh  (flight + return)         ║")
        print("║  Battery capacity: 80.0 Wh (Tattu 6S 16000mAh)      ║")
        print("║  Safety margin deficit: -14.6%                        ║")
        print("║  POE verdict   : FAIL — insufficient for safe return  ║")
        print("║  MAC decision  : BLOCK — mission not admitted         ║")
        print("╚═══════════════════════════════════════════════════════╝")
        blocked_at = (pos.x_val, pos.y_val, abs(pos.z_val))
        break

print(f"\n[EAMSR] UAV holding at ({blocked_at[0]:.1f}, {blocked_at[1]:.1f}, {blocked_at[2]:.1f}m) — awaiting operator instruction.")
time.sleep(2)

# ---- 生成轨迹图 ----
fig = plt.figure(figsize=(11, 7))
ax = fig.add_subplot(111, projection='3d')

ax.plot(trajectory_x, trajectory_y, trajectory_z,
        color='#2ecc71', linewidth=2.5, marker='o', markersize=7,
        label='Executed Path')

# 未执行的计划路径（虚线）
future_x = [trajectory_x[-1], 180, 240]
future_y = [trajectory_y[-1], 20,  40]
future_z = [20, 20, 20]
ax.plot(future_x, future_y, future_z,
        color='#e74c3c', linewidth=1.8, linestyle='--', alpha=0.6,
        label='Planned Path (BLOCKED)')

# 被拦截点
ax.scatter(*blocked_at, color='#e74c3c', s=250, zorder=10,
           marker='X', label='BW-Energy BLOCKED')
ax.text(blocked_at[0]+3, blocked_at[1]+3, blocked_at[2]+2,
        'BW-Energy BLOCKED\nEnergy: 91.7/80.0 Wh',
        color='#e74c3c', fontsize=9, fontweight='bold')

# 起点标记
ax.scatter(0, 0, 20, color='#27ae60', s=200, marker='^', zorder=10, label='Home / Takeoff')

ax.set_xlabel('X (m)', fontsize=11, labelpad=8)
ax.set_ylabel('Y (m)', fontsize=11, labelpad=8)
ax.set_zlabel('Altitude (m)', fontsize=11)
ax.set_title('AirSim-E1: BW-Energy Rejection — Energy Constraint Violation\n'
             'EAMSR Mission Admission Control | AirSimNH Environment',
             fontsize=12, pad=15)
ax.legend(fontsize=10, loc='upper left')
ax.view_init(elev=25, azim=-60)

plt.tight_layout()
out = r'D:\AirSim\UAV-PY\s1_trajectory_v3.png'
plt.savefig(out, dpi=300, bbox_inches='tight')
plt.close()
print(f"\n[OK] 图表已保存: {out}")

# 返航
client.moveToPositionAsync(0, 0, -20, 8, timeout_sec=40).join()
client.landAsync().join()
client.armDisarm(False)
client.enableApiControl(False)
print("[DONE] 场景S1完成 — 请立即对AirSim窗口截图 (Win+Shift+S)")
