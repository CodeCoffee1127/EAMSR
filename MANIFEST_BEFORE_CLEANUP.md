# EAMSR 项目清单（清理前）

**生成时间**: 2026-06-16  
**项目根目录**: d:\EAMSR  
**总文件数**: 100  
**总大小**: ~5.56 MB

---

## 目录结构概览

```
EAMSR/
├── __pycache__/                          (2 files, 93 KB)
├── paper_data/                           (13 files, 46 KB)
├── paper_figures/                        (6 files, 1.5 MB)
├── paper_text/                           (9 files, 40 KB)
├── project/                              (14 files, 622 KB)
│   ├── __pycache__/                      (4 files, 179 KB)
│   └── results/                          (13 files, 1.2 MB)
│       ├── p0_validation/                (3 files)
│       ├── test_ablation/                (3 files)
│       ├── test_all/                     (1 file)
│       ├── test_baseline/                (3 files)
│       ├── test_budget/                  (1 file)
│       └── test_save/                    (1 file)
└── [根目录文件]                          (43 files, 3.1 MB)
```

---

## 核心资产（必须保留）

### P2 核心数据
- `dataset_p2.jsonl` (583 KB) - P2 数据集
- `annotations_p2.json` (162 KB) - P2 标注
- `full_eamsr_p2.json` (188 KB) - P2 Full EAMSR 结果
- `baseline_p2.json` (754 KB) - P2 Baseline 结果
- `ablation_p2.json` (1.1 MB) - P2 消融结果
- `audit_p2.json` (49 KB) - P2 审计追踪
- `l2_validation_p2.json` (6 KB) - P2 L2 验证

### 统计与校验材料
- `bootstrap_ci.json` (11 KB) - Bootstrap 95% CI
- `ablation_confusion_matrices.json` (4 KB) - 消融混淆矩阵
- `runtime_breakdown.json` (1 KB) - 运行时分项
- `cross_ref_check.json` (12 KB) - 交叉引用检查
- `consistency_check.json` (8 KB) - 一致性检查
- `p2_manifest.json` (7 KB) - P2 manifest
- `p2_final_manifest.json` (1 KB) - P2 最终 manifest

### 论文底层数据与资产
- `paper_data/` (13 files) - 论文表格和图表数据
- `paper_figures/` (6 files) - 论文图表 PNG
- `paper_text/` (9 files) - 论文正文 Markdown
- `figure_captions.md` - 图注说明

### 核心脚本
- `eamsr_schemas.py` (29 KB)
- `eamsr_schemas.json` (32 KB)
- `annotation_protocol_v1.md` (36 KB)
- `l1_simulator.py` (55 KB)
- `greedy_relaxation.py` (56 KB)
- `experiment_runner.py` (62 KB)
- `p0_validation.py` (56 KB)

---

## 归档文件（移动到 _archive/）

### P1 遗留数据 → `_archive/p1_legacy/`
- `dataset_p1.jsonl`
- `annotations_p1.json`
- `ablation_results.json`
- `baseline_results.json`
- `full_eamsr_results.json`
- `l1_simulator_p1.py`
- `p1_manifest.json`
- `p1_plan.md`
- `p1_summary_report.md`

### P0 验证 → `_archive/p0_validation/`
- `P0_MANIFEST.md`
- `p0_validation_report.json`
- `project/results/p0_validation/` (3 files)

### 过程日志 → `_archive/process_logs/`
- `l1_calibration_report.json`
- `l2_validation_report.json`
- `uar_tuning_log.json`
- `p2_plan.md`
- `plan.md`
- `project/results/test_*/` (10 files)

### 重复副本 → `_archive/duplicate_project_copy/`
- `project/` 目录（除 results/ 外）

### 缓存 → 删除
- `__pycache__/`
- `*.pyc`
- `project/__pycache__/`

---

## 文件分类统计

| 类别 | 文件数 | 总大小 |
|------|--------|--------|
| core_data | 2 | 615 KB |
| annotation | 3 | 215 KB |
| raw_result | 3 | 2.1 MB |
| derived_result | 5 | 42 KB |
| paper_table | 9 | 2.4 KB |
| paper_figure | 11 | 1.6 MB |
| paper_text | 9 | 40 KB |
| source_code | 8 | 347 KB |
| validation | 4 | 26 KB |
| audit | 1 | 49 KB |
| manifest | 4 | 13 KB |
| process_log | 10 | 21 KB |
| p1_legacy | 9 | 160 KB |
| p0_validation | 4 | 48 KB |
| cache | 5 | 272 KB |
| duplicate | 10 | 357 KB |
| **总计** | **100** | **~5.56 MB** |

---

## 待确认缺失文件

以下文件在任务描述中提到，但当前目录中未发现：

- `3.method.docx` - 缺失
- `4.experiment.docx` - 缺失
- `README.md` - 缺失
- `requirements.txt` - 缺失
- `.gitignore` - 缺失
- `paper/tables/table7*.csv` - 缺失（Table 7 Panel B 尚未创建）
- `paper/tables/table7*.json` - 缺失

---

*本清单由本地 Qwen 自动生成，作为项目清理前的快照。*
