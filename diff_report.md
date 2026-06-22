# EAMSR 实验数据与图像资产全局同步修正 — 差异报告

**生成时间**: 2026-06-17  
**扫描范围**: `d:\EAMSR\` 全目录  
**冻结数据源**: 任务描述 Section 2

---

## 执行摘要

| 类别 | 待修改文件数 | 待修改位置数 |
|------|------------|------------|
| CSV 表格 | 4 | 8 |
| JSON 数据 | 6 | 12 |
| Markdown 文本 | 9 | 33 |
| Python 脚本 | 1 | 15 |
| 图像文件 | 0 | 0（由脚本自动生成，无需手动修改） |
| **总计** | **20** | **68** |

---

## 1. CSV 表格数值修正

### 1.1 `paper/tables/table3_overall.csv`

| 行 | 列 | 当前值 | 目标值 | 规则来源 |
|----|----|--------|--------|---------|
| LLM+Backend | UAR | `22.4%` | `21.8%` | Section 2.3 — LLM+Backend 行 UAR 必须从 22.4% 修正为 21.8%（17/78） |
| EAMSR | Acc_adm | `93.3%` | `93.3%` | ✓ 已正确，无需修改 |
| EAMSR | UAR | `0.0%` | `0.0%` | ✓ 已正确 |
| EAMSR | CNR | `88.9%` | `88.9%` | ✓ 已正确 |

**注意**: `STL Repair` 名称在 CSV 中为 `STL Repair`（无 `-style`），根据规则应替换为 `Greedy Relaxation`。

### 1.2 `paper/tables/table5_witness.csv`

| 行 | 列 | 当前值 | 目标值 | 规则来源 |
|----|----|--------|--------|---------|
| Overall | Time_margin | `36.5s` | `37.0s` | Section 2.3 — Table 5 Overall time-window margin 从 36.5 s 改为 37.0 s |
| S1-S6 | 各场景时间 | 保持不变 | 保持不变 | 仅修改 Overall 行，场景级数据不变 |

### 1.3 `paper/tables/table8_ablation.csv`

| 行 | 列 | 当前值 | 目标值 | 规则来源 |
|----|----|--------|--------|---------|
| w/o Evidence | UAR | `8.9%` | `9.0%` | Section 2.3 — Table 8 w/o Evidence PO 的 UAR 从 8.9% 改为 9.0%（7/78） |
| Full EAMSR | Acc_adm | `93.3%` | `93.3%` | ✓ 已正确 |

### 1.4 `paper/tables/table4a_grounding.csv` 和 `table4b_risk_handling.csv`

**Section 2.3 要求**: Table 4 Panel A Overall 行必须重算为 `93.4% / 90.5% / 88.7% / 94.9% / 91.6%`。

当前 `table4a_grounding.csv` 的 Overall 行为：
```
Overall,93.5%,90.9%,88.7%,95.2%,91.2%
```

需要修改为：
```
Overall,93.4%,90.5%,88.7%,94.9%,91.6%
```

**差异**:
| 列 | 当前值 | 目标值 |
|----|--------|--------|
| Anchor_cov | `93.5%` | `93.4%` |
| Clause_prec | `90.9%` | `90.5%` |
| Clause_rec | `88.7%` | `88.7%` ✓ |
| Evidence_cov | `95.2%` | `94.9%` |
| Pending_det | `91.2%` | `91.6%` |

---

## 2. JSON 数据文件修正

### 2.1 `paper/tables/table7b_llm_backbone.json` 及相关文件

| 文件 | 字段 | 当前值 | 目标值 |
|------|------|--------|--------|
| `table7b_llm_backbone.json` | `LLM+Backend.Acc_adm` | `93.3` | 需确认是否为 UAR 值（任务要求 UAR=21.8%） |
| `table7b_llm_backbone_plot_data.json` | `LLM+Backend.Acc_adm` | `93.3` | 同上 |
| `table7b_llm_backbone_derived_stats.json` | `max` | `93.3` | 同上 |
| `table7b_llm_backbone_count_reconstruction.json` | `Acc_adm_percent` | `93.3` | 同上 |

**注意**: 这些 JSON 文件中的 `93.3` 是 EAMSR 的 Acc_adm，无需修改。需要确认是否有 LLM+Backend 的 UAR 字段需要修正。

### 2.2 `paper/tables/fig5_witness.json`

| 字段 | 当前值 | 目标值 |
|------|--------|--------|
| `time_margin_s_mean` | `36.5` | `37.0` |
| `description` 中的 `S1` | `"S1 powerline inspection"` | `"AirSim-E1 powerline inspection"`（仅限 4.8 节语境） |

### 2.3 `paper/tables/fig6_uar_ablation.json`

| 字段 | 当前值 | 目标值 |
|------|--------|--------|
| 数组元素 | `8.9` | `9.0`（w/o Evidence UAR） |

### 2.4 `paper/tables/fig_confusion.json`

| 字段 | 当前值 | 目标值 |
|------|--------|--------|
| `baseline.uar` | `21.8` | ✓ 已正确（21.8%） |
| `eamsr.accuracy` | `93.3` | ✓ 已正确 |

### 2.5 `paper/tables/fig7_cases.json`

| 字段 | 当前值 | 目标值 |
|------|--------|--------|
| `scenario` | `"S2_Disaster_area"` | 需确认是否在 4.8 节语境中（当前 4.8 节文本未使用 S1/S2/S3 编号） |
| `scenario` | `"S1_Powerline"` | 同上 |

**注意**: 当前 `text_4_8_cases.md` 使用的是 `MS-S2-T2-semi_structured-05` 等样本 ID，而非 `S1/S2/S3` 场景编号。需确认是否需要在 JSON 中修改。

---

## 3. Markdown 文本文件修正

### 3.1 全局字符串替换（所有 .md 文件）

| 旧字符串 | 新字符串 | 涉及文件 | 出现次数 |
|---------|---------|---------|---------|
| `STL Repair` | `Greedy Relaxation` | `text_4_2_overall.md`, `text_4_5_refinement.md`, `text_4_10_summary.md`, `text_4_9_threats.md` | 12 |
| `STL-style Repair` | `Greedy Relaxation` | 无（仅在 Python 脚本中出现） | 0 |
| `22.4%`（LLM+Backend 上下文） | `21.8%` | `text_4_2_overall.md`, `text_4_7_ablation.md`, `text_4_10_summary.md` | 3 |
| `36.5\,\text{s}` | `37.0\,\text{s}` | `text_4_4_witness.md`, `text_4_10_summary.md` | 2 |
| `36.5s` | `37.0s` | `text_4_4_witness.md` | 1 |
| `8.9%`（w/o Evidence 上下文） | `9.0%` | `text_4_7_ablation.md` | 2 |

### 3.2 4.8 节术语隔离（`text_4_8_cases.md`）

**当前状态**: 该文件未使用 `POE/POB/POA/POM/POU` 缩写，也未使用 `S1/S2/S3` 场景编号。案例使用样本 ID（如 `MS-S2-T2-semi_structured-05`）。

**结论**: 4.8 节文本无需术语替换。但需确认：
- 任务描述要求将 `场景 S1/S2/S3` 改为 `AirSim-E1/E2/E3`，但当前 4.8 节未使用这些编号。
- 任务描述中的 AirSim-E1/E2/E3 能量/空域/标准通过案例**未在当前 4.8 节文本中体现**。

**待用户确认**: 
1. 是否需要将当前 4.8 节的 4 个案例（a/b/c/d）重命名为 AirSim-E1/E2/E3？
2. 还是 AirSim-E1/E2/E3 是额外的仿真案例，需新增到 4.8 节？

### 3.3 `text_4_5_refinement.md` — Greedy Relaxation 基线名称

当前文本已正确使用 `Greedy Relaxation`（原称 STL Repair），无需修改。

---

## 4. Python 绘图脚本修正

### 4.1 `scripts/draw_experiment_figures.py`

| 位置 | 当前值 | 目标值 | 修改类型 |
|------|--------|--------|---------|
| Line 25 | `"STL-style Repair"` | `"Greedy Relaxation"` | 字符串替换 |
| Line 28 | `"UAR": 22.4`（LLM+Backend） | `"UAR": 21.8` | 数值修正 |
| Line 30 | `"STL-style Repair": {...}` | `"Greedy Relaxation": {...}` | 字典键替换 |
| Line 36 | `["S1", "S2", "S3", "S4", "S5", "S6"]` | 保持不变 | ✓ 场景编号非 4.8 节语境 |
| Line 40 | `"overall_time": 36.5` | `"overall_time": 37.0` | 数值修正 |
| Line 45 | `8.9`（display_uar 索引 2） | `9.0` | 数值修正 |
| Line 61 | `"STL-style Repair": "#009E73"` | `"Greedy Relaxation": "#009E73"` | 字典键替换 |
| Line 148-149 | `annotation_offsets` 和 `marker_sizes` 中的 `"STL-style Repair"` | `"Greedy Relaxation"` | 字典键替换 |
| Line 359 | `if eamsr["Acc_adm"] != 93.3` | 保持不变 | ✓ 已正确 |
| Line 362 | `if TABLE5_DATA["overall_time"] != 36.5` | `if TABLE5_DATA["overall_time"] != 37.0` | 验证逻辑修正 |
| Line 413 | `UAR=22.4%`（注释） | `UAR=21.8%` | 注释修正 |
| Line 419 | `time=36.5s`（注释） | `time=37.0s` | 注释修正 |

---

## 5. 图像文件处理

### 5.1 文件名检查

扫描结果：所有图像文件名不包含 `STL-style`、`POE`、`POB`、`S1_scene`、`S2_scene`、`S3_scene`、`36.5` 等需要替换的字符串。

**结论**: 无需重命名图像文件。

### 5.2 图像内文字标签

所有图像由 `scripts/draw_experiment_figures.py` 自动生成。修改脚本后重新运行即可更新图像内的文字标签（如图例、标题、数值标注）。

**操作**: 在修正 Python 脚本后，重新运行 `python scripts/draw_experiment_figures.py` 生成新图像。

---

## 6. 禁止修改清单（已确认不触碰）

- [x] `3.method.docx`：未在项目目录中找到，跳过
- [x] Method 章 3.3 的 `PO_E`, `PO_A`, `PO_M`, `PO_U`, `PO_B`：未在当前扫描范围内找到，跳过
- [x] 总样本数 `120`、标签分布 `42/47/31`、风险类别 `T1=30, T2-T6=18`：未在本次修改范围内
- [x] 已关闭事项（C1-C4）：不改动

---

## 7. 待用户确认事项

### 7.1 4.8 节 AirSim 案例命名

**问题**: 任务描述要求将 `场景 S1/S2/S3` 改为 `AirSim-E1/E2/E3`，但当前 `text_4_8_cases.md` 使用的是样本 ID（如 `MS-S2-T2-semi_structured-05`），而非场景编号。

**选项**:
1. 当前 4.8 节不涉及 AirSim 仿真，无需修改场景编号
2. AirSim-E1/E2/E3 是新增的仿真案例，需添加到 4.8 节
3. 需要将现有案例 (a)/(b)/(c)/(d) 重命名为 AirSim-E1/E2/E3

**建议**: 选项 1（当前 4.8 节是案例分析，非 AirSim 仿真）

### 7.2 Table 4 Panel A Overall 行重算

**问题**: 任务描述要求 Table 4 Panel A Overall 行为 `93.4% / 90.5% / 88.7% / 94.9% / 91.6%`，但当前 `table4a_grounding.csv` 的 Overall 行为 `93.5% / 90.9% / 88.7% / 95.2% / 91.2%`。

**操作**: 按任务描述修正为 `93.4% / 90.5% / 88.7% / 94.9% / 91.6%`

### 7.3 跳过文件标记

若用户希望跳过某些文件的修改，请在下方列出：

```
[SKIP] <文件路径> — 原因
```

---

## 8. 执行计划

### Step 1: 用户确认 ✓（等待中）

请用户回复 **"确认执行"** 或提出修改意见。

### Step 2: 备份

创建 `backup_20260617_HHMMSS/` 文件夹，复制所有待修改文件。

### Step 3: 数据文件修正

按以下顺序执行：
1. CSV 表格数值修正（4 个文件）
2. JSON 数据文件修正（6 个文件）
3. Markdown 文本全局替换（9 个文件）
4. Python 脚本修正（1 个文件）

### Step 4: 图像重新生成

运行 `python scripts/draw_experiment_figures.py` 生成新图像。

### Step 5: 验证

生成 `verification_report.md`，检查所有修正是否到位。

---

## 附录：完整文件清单

### 待修改文件（20 个）

**CSV（4 个）**:
1. `paper/tables/table3_overall.csv`
2. `paper/tables/table4a_grounding.csv`
3. `paper/tables/table5_witness.csv`
4. `paper/tables/table8_ablation.csv`

**JSON（6 个）**:
5. `paper/tables/fig5_witness.json`
6. `paper/tables/fig6_uar_ablation.json`
7. `paper/tables/table7b_llm_backbone.json`
8. `paper/tables/table7b_llm_backbone_plot_data.json`
9. `paper/tables/table7b_llm_backbone_derived_stats.json`
10. `paper/tables/table7b_llm_backbone_count_reconstruction.json`

**Markdown（9 个）**:
11. `paper/text/text_4_2_overall.md`
12. `paper/text/text_4_4_witness.md`
13. `paper/text/text_4_5_refinement.md`
14. `paper/text/text_4_7_ablation.md`
15. `paper/text/text_4_10_summary.md`
16. `paper/text/text_4_6_generalization.md`
17. `paper/text/text_4_9_threats.md`
18. `paper/text/text_4_3_contract.md`

**Python（1 个）**:
19. `scripts/draw_experiment_figures.py`

**图像（0 个）**: 由脚本自动生成，无需手动修改

---

**报告完成**。等待用户确认后执行修正。
