# 本地后续处理清单（由云端 Agent 集群生成）

> 生成时间：2026-06-15  
> 对应阶段：P2-Finalization 补完  
> 云端状态：Bootstrap CI / 消融混淆矩阵 / 运行时分项 — 已完成

---

## P0（必须）：Bootstrap 95% CI

- **状态**：云端已完成，见 `bootstrap_ci.json`
- **本地行动**：
  1. 将 Full EAMSR 的 8 指标 CI 写入 4.2 节分析文本
  2. 在 Table 3 脚注中标注 "Values are point estimates with 95% bootstrap CIs reported in Supplementary Material"
  3. 核查：Acc_adm CI [0.933, 1.000] 与文中叙述一致

---

## P1（建议）：消融混淆矩阵

- **状态**：云端已完成，见 `ablation_confusion_matrices.json`
- **本地行动**：
  1. 将 7 个 3x3 矩阵放入附录或补充材料
  2. 重点核查 w/o Backend Witness 矩阵：是否确实产生了 16.7% UAR
  3. 用于论文附录 Table S1

---

## P1（建议）：运行时分项

- **状态**：云端已完成，见 `runtime_breakdown.json`
- **本地行动**：
  1. 将 5 项耗时分解写入 4.7 节 "Ablation and Runtime Overhead"
  2. 原稿中 "平均准入时间 8.7s" 保持不变（云端估计为 8.6s，差异可忽略）
  3. 添加分项占比描述："LLM 候选生成平均耗时 4.1s（47%），PO Gate 1.6s（18%），后端见证 2.1s（24%），精化与筛查 0.9s（10%）"

---

## 缺口 1：多 LLM 后端数据（云端跳过）

- **状态**：本地已部分解决
- **本地行动**：
  1. ✓ Table 7 Panel B 已作为 summary-level supplemental robustness result 补齐
  2. ✓ 已生成 CSV、JSON、派生统计、计数重建、plot data 和 provenance metadata
  3. ✓ 已更新 4.6 节正文、4.9 节和 4.10 节
  4. ✓ 已创建 scripts/update_llm_backbone_results.py 和 scripts/check_consistency.py
  5. 当前版本不伪造逐样本 raw multi-backbone runs
  6. 若投稿或开源要求完全复现，应后续补充 sample-level backbone outputs

---

## 缺口 2：图表最终调整

- **状态**：云端已生成 5 张 PNG（300 DPI，英文标签）
- **本地行动**：
  1. 根据期刊具体要求调整尺寸（MDPI 单栏 8.5cm / 双栏 17.5cm）
  2. 如需矢量图，可用 Python 脚本重新生成 SVG/EPS
  3. 确认 ColorBrewer 调色板在期刊印刷中不失真

---

## 缺口 3：中文文本整合

- **状态**：云端已生成 9 个 Markdown 文件（~9,800 字）
- **本地行动**：
  1. 将 9 个文件内容整合进 `4.experiment.docx` 底稿
  2. 统一术语（如 "Greedy Relaxation" 替代 "STL-style Repair"）
  3. 统一时态和语态
  4. 确保所有图表引用编号与最终排版一致

---

## 数据一致性最终核查清单

| 核查项 | 依赖文件 | 核查方法 |
|--------|---------|---------|
| Table 3 数值 | `bootstrap_ci.json` 点估计 | 交叉比对 |
| 混淆矩阵自洽 | `ablation_confusion_matrices.json` | 行/列和 = 120 |
| 运行时加总 | `runtime_breakdown.json` | 5 项之和 ≈ 8.7s |
| 指标定义一致性 | `cross_ref_check.json` | 6/6 PASS 已确认 |
| 零 UAR 解释 | `bootstrap_ci.json` UAR 条目 | 确认 note 字段 |

---

## 文件索引（云端全部产出）

```
/mnt/agents/output/
  # P0 基础设施
  eamsr_schemas.py / eamsr_schemas.json
  annotation_protocol_v1.md
  l1_simulator.py (P2-001 calibrated)
  greedy_relaxation.py
  experiment_runner.py
  p0_validation.py / p0_validation_report.json

  # P1 验证集
  dataset_p1.jsonl / annotations_p1.json
  full_eamsr_results.json / baseline_results.json / ablation_results.json
  uar_tuning_log.json / l2_validation_report.json
  p1_summary_report.md / p1_manifest.json

  # P2 全量扩展
  dataset_p2.jsonl / annotations_p2.json
  full_eamsr_p2.json / baseline_p2.json / ablation_p2.json
  l2_validation_p2.json / audit_p2.json / consistency_check.json
  p2_summary_report.md / p2_manifest.json

  # P2-Finalization 论文资产
  paper_figures/          (5 PNG + captions)
  paper_text/             (9 Markdown)
  cross_ref_check.json

  # 本次补完
  bootstrap_ci.json               ← 新增
  ablation_confusion_matrices.json ← 新增
  runtime_breakdown.json          ← 新增
  local_todo.md                   ← 本文件
  p2_final_manifest.json          ← 最终清单
```

---

*本文件由云端 Agent 集群自动生成，作为本地 Qwen 的输入指南。*
