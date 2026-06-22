# PUBLICATION_INVENTORY.md

**生成日期:** 2026-06-22  
**项目:** D:\EAMSR  
**用途:** EAMSR 论文公开发布前文件清点与合规分类

---

## 一、总体统计

| 指标 | 数值 |
|------|------|
| **总文件数** | 219 个（不含 .git 目录） |
| **总大小** | 约 17.43 MB |
| **目录数** | 33 个（不含 .git 目录） |
| **最大文件** | 无 >50MB 文件 |

---

## 二、应公开上传的文件（合规文件）

| 目录 | 文件数 | 说明 |
|------|--------|------|
| `src/eamsr/` | 7 | 核心源代码 + 协议文档 |
| `data/` | 12 | 数据集、结果、验证数据 |
| `scripts/` | 4 | 实验脚本 |
| `paper/tables/` | 22 | 论文表格数据（不含 .bak） |
| `paper/text/` | 9 | 论文正文片段 |
| `paper/figures/` | 12 | 最终版图表（不含 archive/abandoned） |
| `manifests/` | 6 | 清单和摘要 |
| `audit/` | 1 | 审计数据 |
| `UAV-PY/` | 14 | 无人机仿真代码（不含 backup 和 __pycache__） |
| `UAV-PY/airsim/` | 4 | AirSim 客户端封装 |
| 根目录文档 | 12 | README, requirements.txt, 报告等 |

**小计：约 91 个合规文件**

### 详细清单

#### src/eamsr/
- `__init__.py`
- `annotation_protocol_v1.md`
- `eamsr_schemas.json`
- `eamsr_schemas.py`
- `experiment_runner.py`
- `greedy_relaxation.py`
- `l1_simulator.py`

#### data/
- `annotations/annotations_p2.json`
- `raw/dataset_p2.jsonl`
- `results/ablation_p2.json`
- `results/baseline_p2.json`
- `results/full_eamsr_p2.json`
- `stats/ablation_confusion_matrices.json`
- `stats/bootstrap_ci.json`
- `stats/runtime_breakdown.json`
- `validation/consistency_check.json`
- `validation/cross_ref_check.json`
- `validation/l2_validation_p2.json`
- `validation/llm_backbone_consistency_check.json`

#### scripts/
- `check_consistency.py`
- `draw_experiment_figures.py`
- `p0_validation.py`
- `update_llm_backbone_results.py`

#### paper/figures/ (最终版)
- `fig3_overall_performance_tradeoff.pdf`
- `fig3_overall_performance_tradeoff.png`
- `fig3_overall_performance_tradeoff.svg`
- `fig3_overall_performance_tradeoff_rev.pdf`
- `fig3_overall_performance_tradeoff_rev.png`
- `fig4_backend_witness_margins.pdf`
- `fig4_backend_witness_margins.png`
- `fig4_backend_witness_margins.svg`
- `fig4_backend_witness_margins_rev.pdf`
- `fig4_backend_witness_margins_rev.png`
- `fig5_ablation_runtime_overhead.pdf`
- `fig5_ablation_runtime_overhead.png`
- `fig5_ablation_runtime_overhead.svg`
- `fig5_ablation_runtime_overhead_rev.pdf`
- `fig5_ablation_runtime_overhead_rev.png`
- `figure_data_used.json`
- `figure_generation_report.md`
- `figure_style_config.json`

#### paper/tables/ (不含 .bak)
- `fig4_mac_flow.json`
- `fig5_witness.json`
- `fig6_uar_ablation.json`
- `fig7_cases.json`
- `fig_confusion.json`
- `table2_dataset.csv`
- `table3_overall.csv`
- `table4a_grounding.csv`
- `table4b_risk_handling.csv`
- `table5_witness.csv`
- `table6a_refinement.csv`
- `table6b_repair.csv`
- `table7a_generalization.csv`
- `table7a_generalization.json`
- `table7b_llm_backbone.csv`
- `table7b_llm_backbone.json`
- `table7b_llm_backbone_count_reconstruction.json`
- `table7b_llm_backbone_derived_stats.json`
- `table7b_llm_backbone_plot_data.json`
- `table7_generalization_and_backbone.json`
- `table7_generalization_and_backbone.md`
- `table8_ablation.csv`

#### paper/text/
- `text_4_2.md`
- `text_4_3.md`
- `text_4_4.md`
- `text_4_5.md`
- `text_4_6.md`
- `text_4_7.md`
- `text_4_8.md`
- `text_4_9.md`
- `text_4_10.md`

#### manifests/
- `file_inventory_after.json`
- `p2_final_manifest.json`
- `p2_final_summary.md`
- `p2_manifest.json`
- `p2_summary_report.md`
- `table7b_data_manifest.json`

#### audit/
- `audit_p2.json`

#### UAV-PY/ (核心文件)
- `airsim/__init__.py`
- `airsim/client.py`
- `airsim/types.py`
- `airsim/utils.py`
- `crash_simulation.py`
- `energy_profile.py`
- `energy_profile.png`
- `figure_update_report.md`
- `s1_energy_v2.py`
- `s1_trajectory.png`
- `s1_trajectory.v2.png`
- `s2_airspace.py`
- `s2_airspace.png`
- `s2_airspace.v2.png`
- `s2_airspace.v3.png`
- `s2_airspace.v3_1.png`
- `s3_success_v2.py`
- `s3_trajectory.png`
- `s3_trajectory.v2.png`
- `scenario_s1_energy.py`
- `scenario_s2_airspace.py`
- `scenario_s3_success.py`
- `test_connection.py`
- `top_down_capture.py`
- `top_down_capture.png`

#### 根目录文档
- `README.md`
- `requirements.txt`
- `.gitignore`
- `verification_report.md`
- `diff_report.md`
- `RESULT_CONSISTENCY_REPORT.md`
- `LLM_BACKBONE_COMPLETION_REPORT.md`
- `PROJECT_CLEANUP_REPORT.md`
- `MANIFEST_BEFORE_CLEANUP.md`
- `MANIFEST_AFTER_CLEANUP.md`
- `file_inventory_before.json`
- `local_todo.md`

---

## 三、原则上不上传的文件

| 目录/文件 | 文件数 | 原因 |
|-----------|--------|------|
| `_archive/` | 36 | 归档/历史数据 |
| `backup_20260617/` | 19 | 备份副本 |
| `UAV-PY/backup_figures_20260617/` | 8 | 旧版图表备份 |
| `paper/figures/archive_round1/` | 9 | 第一轮迭代旧版图表 |
| `paper/figures/archive_round2/` | 9 | 第二轮迭代旧版图表 |
| `paper/figures/archive_round3/` | 3 | 第三轮迭代旧版图表 |
| `paper/figures/archive_round4/` | 3 | 第四轮迭代旧版图表 |
| `paper/figures/abandoned/` | 6 | 废弃图表 |
| `paper/tables/*.bak` | 5 | 备份文件 |
| `-p/` | 0 | 空目录 |
| `paper/doc/` | 0 | 空目录 |
| `_archive/process_redundant/` | 0 | 空目录 |
| `backup_20260617/paper/figures/` | 0 | 空目录 |

**小计：约 98 个不建议上传的文件**

### 详细说明

#### _archive/
- `duplicate_project_copy/` — src/eamsr/ 的完整冗余副本（9 文件）
- `p0_validation/` — P0 阶段遗留验证数据（5 文件）
- `p1_legacy/` — P1 阶段遗留数据（9 文件）
- `process_logs/` — 实验过程日志（13 文件）
- `process_redundant/` — 空目录

#### backup_20260617/
- `paper/tables/` — 表格备份（10 文件）
- `paper/text/` — 文本备份（8 文件）
- `scripts/draw_experiment_figures.py` — 脚本备份（1 文件）

#### paper/figures/archive_round*/
- 多轮迭代的历史版本图表，保留最终版即可

#### paper/figures/abandoned/
- 已废弃的图表版本（fig4~fig8 旧版）

#### UAV-PY/backup_figures_20260617/
- 旧版 energy/s1/s2/s3 图表备份（8 文件）

#### paper/tables/*.bak
- table7b_llm_backbone 系列文件的备份（5 文件）

---

## 四、必须排除的文件

| 类型 | 文件数 | 路径/模式 |
|------|--------|-----------|
| Python 缓存 | 4 | `UAV-PY/airsim/__pycache__/*.pyc` |
| 权重/模型文件 | 0 | 未发现 .pt/.pth/.ckpt/.safetensors/.bin |
| 虚拟环境 | 0 | 未发现 venv/env 目录 |
| .env 文件 | 0 | 未发现 |
| 密钥/令牌文件 | 0 | 未发现含 key/token/secret/password 的文件名 |
| 日志文件 | 0 | 未发现 .log 文件 |

**小计：4 个必须排除的缓存文件**

---

## 五、潜在问题清单

### 5.1 大文件检查
**结果：未发现 >50MB 的文件。** 项目总大小仅约 17.43MB，无大文件风险。

### 5.2 敏感信息检查
**结果：文件名层面未发现敏感文件。**
- 无 `.env` 文件
- 无包含 `key`/`token`/`secret`/`password`/`credential` 的文件名
- 无虚拟环境目录
- 无权重模型文件

**注意：** 仍需进行内容级敏感信息扫描（见阶段 2）。

### 5.3 重复文件

共发现 **22 个文件名** 在多处出现（共 47 个实例）：

| 文件名 | 出现次数 | 位置 |
|--------|----------|------|
| `fig5_ablation_runtime_overhead.{pdf,png,svg}` | 5 处 | figures/ + archive_round1~4 |
| `fig3_overall_performance_tradeoff.{pdf,png,svg}` | 3 处 | figures/ + archive_round1~2 |
| `fig4_backend_witness_margins.{pdf,png,svg}` | 3 处 | figures/ + archive_round1~2 |
| `annotation_protocol_v1.md` | 2 处 | src/eamsr/ + _archive/duplicate_project_copy/ |
| `eamsr_schemas.{json,py}` | 2 处 | src/eamsr/ + _archive/duplicate_project_copy/ |
| `experiment_runner.py` | 2 处 | src/eamsr/ + _archive/duplicate_project_copy/ |
| `greedy_relaxation.py` | 2 处 | src/eamsr/ + _archive/duplicate_project_copy/ |
| `draw_experiment_figures.py` | 2 处 | scripts/ + backup_20260617/scripts/ |
| `p0_validation.py` | 2 处 | scripts/ + _archive/duplicate_project_copy/ |
| `table7b_llm_backbone.*` 系列 | 多个 | paper/tables/ + backup_20260617/ |
| `text_4_*` 系列 | 多个 | paper/text/ + backup_20260617/paper/text/ |
| UAV-PY 图表文件 | 多个 | UAV-PY/ + backup_figures_20260617/ |

**建议：** `_archive/duplicate_project_copy/` 是 `src/eamsr/` 的完整副本，应排除。

### 5.4 .gitignore 问题
当前 `.gitignore` 中包含 `requirements.txt` 作为排除项，这会导致 `requirements.txt` 不会被 git 跟踪。**建议从 .gitignore 中移除该规则**，因为公开项目需要此文件用于复现。

### 5.5 缺失文件
- **LICENSE** — 根目录无许可证文件（需确认）
- **REPRODUCIBILITY.md** — 无专门的复现说明文档（建议创建）

---

## 六、总结

### 6.1 发布建议
- **推荐上传：** 约 91 个合规文件
- **不应上传：** 约 98 个归档/备份/冗余文件
- **必须排除：** 4 个 Python 缓存文件

### 6.2 需修复的问题
1. 修改 `.gitignore`：移除 `requirements.txt` 排除规则
2. 排除 `_archive/duplicate_project_copy/` 冗余副本
3. 排除 `.bak` 备份文件
4. 排除空目录
5. 添加 LICENSE（待确认）
6. 创建复现说明文档

---

**报告生成完毕。** 项目整体结构清晰，数据完整，主要问题集中在归档/备份文件的冗余上。
