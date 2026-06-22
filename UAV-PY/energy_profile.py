import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 5))

# 通过任务（S3）的能量曲线
d_ok = np.array([0, 40, 57, 40, 0])  # 各段距离累计
d_ok_cum = np.cumsum([0, 56.6, 40, 40, 56.6])
e_ok = np.array([100, 82.1, 74.3, 66.5, 48.7])  # 剩余电量%

# 被拒任务（S1强制执行）的能量曲线  
d_rej_cum = np.cumsum([0, 60, 60, 60, 120])
e_rej = np.array([100, 75.2, 50.4, 25.6, -23.1])  # 会耗尽

ax.plot(d_ok_cum, e_ok, color='#27ae60', linewidth=2.5,
        marker='o', markersize=7, label='Approved Mission AirSim-E3 (BW-Energy ✓)')
ax.plot(d_rej_cum, e_rej, color='#e74c3c', linewidth=2.5,
        marker='s', markersize=7, linestyle='--', label='Rejected Mission AirSim-E1 (BW-Energy ✗, forced execution)')

# BW-Energy安全阈值线
ax.axhline(y=20, color='#e67e22', linewidth=2, linestyle=':',
           label='BW-Energy Safety Threshold (20% reserve)')

# 标注坠机区域
ax.axhspan(-30, 0, alpha=0.08, color='red')
ax.text(230, -15, 'Battery Depleted\n(UAV crash risk)', 
        color='#c0392b', fontsize=9, ha='center')

# 标注拦截点
ax.annotate('EAMSR BW-Energy\nBLOCKED HERE\n(91.7 Wh > 80 Wh)',
            xy=(120, 50.4), xytext=(90, 30),
            fontsize=9, color='#c0392b', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.8))

ax.set_xlabel('Cumulative Flight Distance (m)', fontsize=12)
ax.set_ylabel('Battery Remaining (%)', fontsize=12)
ax.set_title('Energy Profile Analysis: EAMSR BW-Energy Validation\n'
             'Approved vs. Rejected Mission Comparison', fontsize=12)
ax.legend(fontsize=10, loc='upper right')
ax.set_xlim(-5, 310)
ax.set_ylim(-30, 110)
ax.grid(True, alpha=0.3)
ax.axhline(y=0, color='black', linewidth=0.8, alpha=0.5)

plt.tight_layout()
plt.savefig(r'D:\AirSim\UAV-PY\energy_profile_v2.png', dpi=300, bbox_inches='tight')
plt.close()
print('[OK] Energy Profile图已保存: D:\\AirSim\\UAV-PY\\energy_profile_v2.png')
