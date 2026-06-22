# EAMSR 项目清单（清理后）

**生成时间**: 2026-06-16  
**项目根目录**: d:\EAMSR  
**清理操作**: 归档冗余文件、整理目录结构、补全 Table 7 Panel B 数据

---

## 新目录结构

```
EAMSR/
├── README.md                                    # 项目说明
├── requirements.txt                             # Python 依赖
├── .gitignore                                   # Git 忽略规则
├── local_todo.md                                # 本地待办清单（已更新）
│
├── data/                                        # 数据文件
│   ├── raw/
│   │   └── dataset_p2.jsonl                     # P2 数据集 (583 KB)
│   ├── annotations/
│   │   └── annotations_p2.json                  # P2 标注 (162 KB)
│   ├── results/
│   │   ├── full_eamsr_p2.json                   # Full EAMSR 结果 (188 KB)
│   │   ├── baseline_p2.json                     # Baseline 结果 (754 KB)
│   │   └── ablation_p2.json                     # 消融结果 (1.1 MB)
│   ├── stats/
│   │   ├── bootstrap_ci.json                    # Bootstrap 95% CI (11 KB)
│   │   ├── ablation_confusion_matrices.json     # 消融混淆矩阵 (4 KB)
│   │   └── runtime_breakdown.json               # 运行时分项 (1 KB)
│   └── validation/
│       ├── l2_validation_p2.json                # L2 验证 (6 KB)
│       ├── consistency_check.json               # 一致性检查 (8 KB)
│       ├── cross_ref_check.json                 # 交叉引用检查 (12 KB)
│       └── llm_backbone_consistency_check.json  # LLM-backbone 一致性检查（新增）
│
├── src/                                         # 源代码
│   └── eamsr/
│       ├── __init__.py                          # 包初始化
│       ├── eamsr_schemas.py                     # Schema 定义 (29 KB)
│       ├── eamsr_schemas.json                   # Schema JSON (32 KB)
│       ├── l1_simulator.py                      # L1 模拟器 (55 KB)
│       ├── greedy_relaxation.py                 # 贪婪松弛 (56 KB)
│       ├── experiment_runner.py                 # 实验运行器 (62 KB)
│       └── annotation_protocol_v1.md            # 标注协议 (36 KB)
│
├── scripts/                                     # 工具脚本
│   ├── update_llm_backbone_results.py           # 更新 LLM-backbone 结果（新增）
│   ├── check_consistency.py                     # 一致性检查（新增）
│   └── p0_validation.py                         # P0 验证 (56 KB)
│
├── paper/                                       # 论文资产
│   ├── tables/                                  # 论文表格
│   │   ├── table2_dataset.csv
│   │   ├── table3_overall.csv
│   │   ├── table4a_grounding.csv
│   │   ├── table4b_risk_handling.csv
│   │   ├── table5_witness.csv
│   │   ├── table6a_refinement.csv
│   │   ├── table6b_repair.csv
│   │   ├── table8_ablation.csv
│   │   ├── table7a_generalization.csv           # Panel A（新增）
│   │   ├── table7a_generalization.json          # Panel A JSON（新增）
│   │   ├── table7b_llm_backbone.csv             # Panel B（新增）
│   │   ├── table7b_llm_backbone.json            # Panel B JSON（新增）
│   │   ├── table7b_llm_backbone_derived_stats.json    # 派生统计（新增）
│   │   ├── table7b_llm_backbone_count_reconstruction.json  # 计数重建（新增）
│   │   ├── table7b_llm_backbone_plot_data.json  # 制图数据（新增）
│   │   ├── table7_generalization_and_backbone.json  # Table 7 完整（新增）
│   │   └── table7_generalization_and_backbone.md    # Table 7 Markdown（新增）
│   ├── figures/                                 # 论文图表
│   │   ├── fig4_mac_flow.png
│   │   ├── fig5_witness.png
│   │   ├── fig6_uar_ablation.png
│   │   ├── fig7_cases.png
│   │   ├── fig8_confusion.png
│   │   ├── figure_captions.md
│   │   ├── fig_confusion.json
│   │   ├── fig4_mac_flow.json
│   │   ├── fig5_witness.json
│   │   ├── fig6_uar_ablation.json
│   │   └── fig7_cases.json
│   ├── text/                                    # 论文正文
│   │   ├── text_4_2_overall.md
│   │   ├── text_4_3_contract.md
│   │   ├── text_4_4_witness.md
│   │   ├── text_4_5_refinement.md
│   │   ├── text_4_6_generalization.md           # 已更新
│   │   ├── text_4_7_ablation.md
│   │   ├── text_4_8_cases.md
│   │   ├── text_4_9_threats.md                  # 已更新
│   │   └── text_4_10_summary.md                 # 已更新
│   └── doc/                                     # 论文文档
│       └── (待添加: 3.method.docx, 4.experiment.docx)
│
├── audit/
│   └── audit_p2.json                            # P2 审计追踪 (49 KB)
│
├── manifests/                                   # 项目清单
│   ├── p2_manifest.json
│   ├── p2_final_manifest.json
│   ├── p2_final_summary.md
│   ├── p2_summary_report.md
│   ├── file_inventory_before.json               # 清理前清单
│   ├── file_inventory_after.json                # 清理后清单
│   └── table7b_data_manifest.json               # Table 7B 数据清单
│
├── _archive/                                    # 归档文件
│   ├── p0_validation/                           # P0 验证（已归档）
│   ├── p1_legacy/                               # P1 遗留数据（已归档）
│   ├── process_logs/                            # 过程日志（已归档）
│   ├── process_redundant/                       # 过程冗余（待使用）
│   └── duplicate_project_copy/                  # 重复副本（已归档）
│
├── MANIFEST_BEFORE_CLEANUP.md                   # 清理前清单（Markdown）
├── MANIFEST_AFTER_CLEANUP.md                    # 本文件
├── PROJECT_CLEANUP_REPORT.md                    # 项目清理报告
├── RESULT_CONSISTENCY_REPORT.md                 # 结果一致性报告
└── LLM_BACKBONE_COMPLETION_REPORT.md            # LLM-backbone 补全报告
```

---

## 清理操作汇总

### 已归档
- **P1 遗留数据** (9 files) → `_archive/p1_legacy/`
- **P0 验证数据** (4 files) → `_archive/p0_validation/`
- **过程日志** (15 files) → `_archive/process_logs/`
- **重复副本** (9 files) → `_archive/duplicate_project_copy/`

### 已删除
- `__pycache__/` 目录及所有 `.pyc` 文件
- `project/__pycache__/` 目录及所有 `.pyc` 文件

### 新增
- Table 7 Panel B 完整数据生态 (7 files)
- 一致性检查脚本和 LLM-backbone 更新脚本
- README.md、.gitignore、requirements.txt
- 项目清单和报告文件

---

## 已知问题

1. **Acc_adm 93.3% vs 94.8% 冲突**
   - `full_eamsr_p2.json`: 94.8% (repeated-run aggregate)
   - `table3_overall.csv`: 93.3% (task-level)
   - 状态：需要人工确认 Table 3 报告口径

2. **缺失文件**
   - `3.method.docx` - 未找到
   - `4.experiment.docx` - 未找到
   - 状态：可能需要从其他位置恢复或重新生成

3. **Table 7 Panel B 数据来源**
   - 当前为 summary-level supplemental result
   - 无逐样本 multi-backbone raw runs
   - 状态：已在 provenance 中明确标注

---

*本清单由本地 Qwen 自动生成，作为项目清理后的最终快照。*
