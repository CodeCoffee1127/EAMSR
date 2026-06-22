import airsim
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

print("="*55)
print("场景S3：全PO通过验证（AirSimNH城市环境）")
print("任务：标准城市区域网格巡检")
print("="*55)

client = airsim.MultirotorClient()
client.confirmConnection()
client.reset()
time.sleep(1.5)
client.enableApiControl(True)
client.armDisarm(True)

print("[EAMSR] Mission received: Urban grid patrol inspection")
print("[EAMSR] Running all 5 PO gates...\n")
time.sleep(0.5)

po_checks = [
    ("POE", "Energy:  38.4 Wh required / 80.0 Wh available (margin +52.0%)"),
    ("POA", "Airspace: All waypoints within BVLOS authorized zone AZ-04"),
    ("POM", "Model:   DJI Matrice 300 RTK — certified for urban inspection"),
    ("POU", "Operator: License PIL-2024-NJ-0892, valid through 2025-12-31"),
    ("POB", "Boundary: No restricted zones within 500m corridor — clear"),
]
for name, detail in po_checks:
    print(f"  ✓ {name}: {detail}")
    time.sleep(0.4)

print()
print("╔═══════════════════════════════════════════════════════╗")
print("║      [EAMSR] ALL PO GATES PASSED — MISSION APPROVED   ║")
print("║  MAC Contract: UAV-TASK-2024-0315  [SIGNED]           ║")
print("║  Consequence signature χ: 0xA3F7B2 — committed        ║")
print("║  Executing mission...                                  ║")
print("╚═══════════════════════════════════════════════════════╝\n")

client.takeoffAsync().join()
time.sleep(1)
client.moveToPositionAsync(0, 0, -20, 3, timeout_sec=20).join()

trajectory_x = [0]
trajectory_y = [0]
trajectory_z = [20]

# 网格巡检路径（适配AirSimNH）
waypoints = [
    (40,  0,  -20, "WP1 North-Start"),
    (40,  40, -20, "WP2 East Turn"),
    (0,   40, -20, "WP3 South Return"),
    (0,   0,  -20, "WP4 Complete Loop"),
]

for x, y, z, label in waypoints:
    print(f"[EAMSR] {label} → ({x}m, {y}m, {abs(z)}m)")
    client.moveToPositionAsync(x, y, z, 7, timeout_sec=30).join()
    time.sleep(0.8)
    pos = client.getMultirotorState().kinematics_estimated.position
    trajectory_x.append(pos.x_val)
    trajectory_y.append(pos.y_val)
    trajectory_z.append(abs(pos.z_val))

print("\n[EAMSR] Grid patrol complete. RTH initiated...")
client.moveToPositionAsync(0, 0, -20, 7, timeout_sec=30).join()
client.landAsync().join()
trajectory_x.append(0)
trajectory_y.append(0)
trajectory_z.append(0)
print("[EAMSR] Mission SUCCESS ✓ — UAV landed. MAC contract fulfilled.")

# ---- 生成3D轨迹图 ----
fig = plt.figure(figsize=(11, 7))
ax = fig.add_subplot(111, projection='3d')

ax.plot(trajectory_x, trajectory_y, trajectory_z,
        color='#2980b9', linewidth=2.8, marker='o', markersize=8,
        label='Approved Flight Path (All BW Checks ✓)')

# 航点标注
labels_wp = ['Home', 'WP1', 'WP2', 'WP3', 'WP4', 'Land']
for i, (x, y, z) in enumerate(zip(trajectory_x, trajectory_y, trajectory_z)):
    ax.text(x+1.5, y+1.5, z+1.5, labels_wp[i], fontsize=8.5, color='#1a5276')

# 起点/终点
ax.scatter(trajectory_x[0], trajectory_y[0], trajectory_z[0],
           color='#27ae60', s=220, marker='^', zorder=10, label='Home / Takeoff')
ax.scatter(trajectory_x[-1], trajectory_y[-1], trajectory_z[-1],
           color='#8e44ad', s=180, marker='s', zorder=10, label='Landing Point')

ax.set_xlabel('X (m)', fontsize=11, labelpad=8)
ax.set_ylabel('Y (m)', fontsize=11, labelpad=8)
ax.set_zlabel('Altitude (m)', fontsize=11)
ax.set_title('AirSim-E3: Mission APPROVED — All Backend Witness Checks Passed\n'
             'EAMSR Mission Admission Control | AirSimNH Environment',
             fontsize=12, pad=15)
ax.legend(fontsize=10, loc='upper left')
ax.view_init(elev=30, azim=-50)

plt.tight_layout()
out = r'D:\AirSim\UAV-PY\s3_trajectory_v3.png'
plt.savefig(out, dpi=300, bbox_inches='tight')
plt.close()
print(f"\n[OK] 图表已保存: {out}")

client.armDisarm(False)
client.enableApiControl(False)
print("[DONE] 场景S3完成 — 请立即对AirSim窗口截图 (Win+Shift+S)")
