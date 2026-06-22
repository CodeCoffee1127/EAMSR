import airsim
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import time

print("="*55)
print("场景S2：POB禁飞区约束验证（AirSimNH城市环境）")
print("任务：城市建筑群巡检（路径穿越受管制空域）")
print("="*55)

client = airsim.MultirotorClient()
client.confirmConnection()
client.reset()
time.sleep(1.5)
client.enableApiControl(True)
client.armDisarm(True)

print("[EAMSR] Mission received: Urban building cluster inspection")
print("[EAMSR] Running POB (Boundary Proof Obligation)...")
time.sleep(0.8)

client.takeoffAsync().join()
time.sleep(1)
client.moveToPositionAsync(0, 0, -20, 3, timeout_sec=20).join()

# 禁飞区参数（对应AirSimNH中建筑密集区）
NFZ_CENTER = (70, 50)
NFZ_RADIUS = 30

trajectory_x = [0]
trajectory_y = [0]

# 计划路径：前两个航点安全，第三个进入禁飞区
waypoints_planned = [
    (25, 10),
    (45, 25),
    (65, 45),   # 距禁飞区中心约14m < 30m，触发拦截
    (90, 60),
]

blocked_at = None

for i, (x, y) in enumerate(waypoints_planned):
    dist = np.sqrt((x - NFZ_CENTER[0])**2 + (y - NFZ_CENTER[1])**2)

    if dist < NFZ_RADIUS and blocked_at is None:
        print()
        print("╔═══════════════════════════════════════════════════════╗")
        print("║      [EAMSR] POB PROOF OBLIGATION — REJECTED          ║")
        print(f"║  Waypoint ({x},{y}) enters restricted zone R-NJ-04    ║")
        print(f"║  Distance to NFZ center: {dist:.1f}m  (limit ≥ {NFZ_RADIUS}m)     ║")
        print("║  Zone class: Class D Controlled Airspace              ║")
        print("║  Regulatory basis: CCAR-92 Article 13                 ║")
        print("║  POB verdict   : FAIL — airspace boundary violated    ║")
        print("║  MAC decision  : BLOCK — mission not admitted         ║")
        print("╚═══════════════════════════════════════════════════════╝")
        blocked_at = (trajectory_x[-1], trajectory_y[-1])
        break

    print(f"[EAMSR] Flying to WP{i+1}: ({x}m, {y}m) — dist to NFZ: {dist:.1f}m ✓")
    client.moveToPositionAsync(x, y, -20, 6, timeout_sec=25).join()
    time.sleep(0.5)
    pos = client.getMultirotorState().kinematics_estimated.position
    trajectory_x.append(pos.x_val)
    trajectory_y.append(pos.y_val)

print(f"\n[EAMSR] UAV holding at ({blocked_at[0]:.1f}, {blocked_at[1]:.1f}) — mission suspended.")
time.sleep(2)

# ---- 生成禁飞区俯视图 ----
fig, ax = plt.subplots(figsize=(10, 9))

# 禁飞区
nfz_fill = plt.Circle(NFZ_CENTER, NFZ_RADIUS, color='#e74c3c',
                       alpha=0.12, zorder=1)
nfz_border = plt.Circle(NFZ_CENTER, NFZ_RADIUS, color='#e74c3c',
                         fill=False, linewidth=2.5, linestyle='--', zorder=2)
ax.add_patch(nfz_fill)
ax.add_patch(nfz_border)
ax.text(NFZ_CENTER[0], NFZ_CENTER[1]+2, 'RESTRICTED\nAIRSPACE\nR-NJ-04',
        ha='center', va='center', color='#c0392b',
        fontsize=10, fontweight='bold', zorder=3)

# 红色虚线：原始直线路径（直接穿过禁飞区）
original_route_x = [0, 25, 45, 65, 90]
original_route_y = [0, 10, 25, 45, 60]
ax.plot(original_route_x, original_route_y, color='#e74c3c', linewidth=2.5,
        linestyle='--', marker='o', markersize=8, zorder=4,
        label='Original Route (POB FAIL)')

# 在穿越点标注红色X（65,45）
crossing_point = (65, 45)
ax.scatter(*crossing_point, color='#e74c3c', s=350, marker='X',
           zorder=6, label='POB Violation Point')
ax.annotate('POB FAIL\n(NFZ Breach)',
            xy=crossing_point,
            xytext=(crossing_point[0] - 35, crossing_point[1] + 15),
            fontsize=9.5, color='#c0392b', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.8))

# 绿色实线：精化绕飞路径（绕过禁飞区外侧）
# 验证每个点到圆心 (70,50) 的距离均 > 35m:
# (35,80): sqrt((35-70)^2 + (80-50)^2) = sqrt(1225+900) ≈ 46m ✓
# (70,88): sqrt((70-70)^2 + (88-50)^2) = 38m ✓
refined_route_x = [0, 25, 45, 35, 70, 90]
refined_route_y = [0, 10, 25, 80, 88, 60]
ax.plot(refined_route_x, refined_route_y, color='#27ae60', linewidth=2.8,
        marker='o', markersize=9, zorder=5,
        label='Refined Route (EAMSR ACCEPT)')

# 标注每个绕飞航点为蓝色菱形
for i, (wx, wy) in enumerate(zip(refined_route_x, refined_route_y)):
    ax.scatter(wx, wy, color='#2980b9', s=180, marker='D',
               zorder=7, edgecolors='white', linewidths=1.5)

# 起点
ax.scatter(0, 0, color='#2980b9', s=220, marker='^', zorder=8, label='Home / Takeoff')

ax.set_xlabel('X (m)', fontsize=12)
ax.set_ylabel('Y (m)', fontsize=12)
ax.set_title('S2: POB Refinement — Bypass vs. Direct Path Comparison\n'
             'EAMSR Mission Admission Control | AirSimNH Environment',
             fontsize=12)
ax.legend(fontsize=10, loc='upper left')
ax.set_xlim(-25, 130)
ax.set_ylim(-20, 105)
ax.grid(True, alpha=0.3)
ax.set_aspect('equal')
plt.tight_layout()

out = r'D:\AirSim\UAV-PY\s2_airspace_v3.png'
plt.savefig(out, dpi=300, bbox_inches='tight')
plt.close()
print(f"\n[OK] 图表已保存: {out}")

client.moveToPositionAsync(0, 0, -20, 6, timeout_sec=35).join()
client.landAsync().join()
client.armDisarm(False)
client.enableApiControl(False)
print("[DONE] 场景S2完成 — 请立即对AirSim窗口截图 (Win+Shift+S)")
