#!/usr/bin/env python3
"""
check_consistency.py

EAMSR 项目一致性检查脚本。

检查项：
1. Table 7 Panel B CSV 与 JSON 数值一致
2. Table 7 Panel B 与论文正文数值一致
3. Overall 行不被误当成主实验 Full EAMSR
4. UAR=0.0% 不被错误应用到所有多后端 Overall
5. PIR=100.0% 和 WSR=100.0% 在三个 backbone 中均一致
6. Acc_adm 的 backbone range 为 1.6 percentage points
7. DeepSeek-class 的 UAR 为 1.3%，Overall UAR 为 0.4%
8. local_todo.md 是否仍写 "Table 7 Panel B 无数据支撑"
9. Table 3 Full EAMSR 在不同文件中是否存在 93.3% 与 94.8% 冲突
10. paper_data/ 和 paper/tables/ 是否存在双目录同步不一致
11. cross_ref_check.json 是否包含 Table 7 Panel B
12. README.md 是否说明 Table 7 Panel B 的 provenance
13. 没有生成伪 raw run 文件

用法：
    python scripts/check_consistency.py
"""

import csv
import json
import os
import sys
from pathlib import Path
from datetime import datetime


# ============================================================
# 配置
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PAPER_TABLES_DIR = PROJECT_ROOT / "paper" / "tables"
PAPER_DATA_DIR = PROJECT_ROOT / "paper_data"
PAPER_TEXT_DIR = PROJECT_ROOT / "paper" / "text"
DATA_RESULTS_DIR = PROJECT_ROOT / "data" / "results"
DATA_STATS_DIR = PROJECT_ROOT / "data" / "stats"
DATA_VALIDATION_DIR = PROJECT_ROOT / "data" / "validation"


# ============================================================
# 检查结果
# ============================================================

class CheckResult:
    def __init__(self, check_id: str, name: str):
        self.check_id = check_id
        self.name = name
        self.status = "PENDING"  # PASS, FAIL, WARNING, SKIP
        self.details = ""
        self.violations = []
    
    def pass_check(self, details: str = ""):
        self.status = "PASS"
        self.details = details
    
    def fail_check(self, details: str, violation: str = ""):
        self.status = "FAIL"
        self.details = details
        if violation:
            self.violations.append(violation)
    
    def warn_check(self, details: str):
        self.status = "WARNING"
        self.details = details
    
    def skip_check(self, details: str):
        self.status = "SKIP"
        self.details = details


# ============================================================
# 检查函数
# ============================================================

def check_csv_json_consistency() -> CheckResult:
    """检查 Table 7 Panel B CSV 与 JSON 数值一致"""
    result = CheckResult("C1", "Table 7 Panel B CSV/JSON Consistency")
    
    csv_path = PAPER_TABLES_DIR / "table7b_llm_backbone.csv"
    json_path = PAPER_TABLES_DIR / "table7b_llm_backbone.json"
    
    if not csv_path.exists() or not json_path.exists():
        result.skip_check("CSV or JSON file not found")
        return result
    
    try:
        # 读取 CSV
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            csv_rows = list(reader)
        
        # 读取 JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            json_rows = json_data.get("rows", [])
        
        # 比较行数和数值
        if len(csv_rows) != len(json_rows):
            result.fail_check(
                f"Row count mismatch: CSV={len(csv_rows)}, JSON={len(json_rows)}",
                "Row count mismatch"
            )
            return result
        
        # 比较每行数值
        for i, (csv_row, json_row) in enumerate(zip(csv_rows, json_rows)):
            backbone_csv = csv_row["LLM backbone"]
            backbone_json = json_row["llm_backbone"]
            
            if backbone_csv != backbone_json:
                result.fail_check(
                    f"Row {i}: backbone name mismatch: CSV='{backbone_csv}', JSON='{backbone_json}'",
                    f"Backbone name mismatch at row {i}"
                )
                return result
            
            # 比较数值字段
            numeric_fields = {
                "Acc_adm": "Acc_adm",
                "UAR": "UAR",
                "UBR": "UBR",
                "PIR": "PIR",
                "WSR": "WSR",
                "Decision consistency": "Decision_consistency"
            }
            
            for csv_field, json_field in numeric_fields.items():
                csv_val = float(csv_row[csv_field])
                json_val = float(json_row[json_field])
                
                if abs(csv_val - json_val) > 0.01:
                    result.fail_check(
                        f"Row {i} ({backbone_csv}): {csv_field} mismatch: CSV={csv_val}, JSON={json_val}",
                        f"Value mismatch: {csv_field}"
                    )
                    return result
        
        result.pass_check("CSV and JSON values are consistent")
    
    except Exception as e:
        result.fail_check(f"Error during comparison: {str(e)}", str(e))
    
    return result


def check_paper_text_consistency() -> CheckResult:
    """检查 Table 7 Panel B 与论文正文数值一致"""
    result = CheckResult("C2", "Table 7 Panel B vs Paper Text Consistency")
    
    json_path = PAPER_TABLES_DIR / "table7b_llm_backbone.json"
    text_path = PAPER_TEXT_DIR / "text_4_6_generalization.md"
    
    if not json_path.exists() or not text_path.exists():
        result.skip_check("JSON or text file not found")
        return result
    
    try:
        # 读取 JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            json_rows = json_data.get("rows", [])
        
        # 读取正文
        with open(text_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        # 检查关键数值是否在正文中提到
        warnings = []
        for row in json_rows:
            backbone = row["llm_backbone"]
            if backbone == "Overall":
                continue
            
            acc_adm = row["Acc_adm"]
            
            # 检查是否提到该 backbone 和 Acc_adm
            if backbone not in text_content:
                warnings.append(f"Backbone '{backbone}' not mentioned in text")
            
            # 检查 Acc_adm 值是否匹配（允许 ±0.1 的舍入误差）
            acc_str = f"{acc_adm}%"
            if acc_str not in text_content and f"{acc_adm:.1f}%" not in text_content:
                warnings.append(f"Acc_adm={acc_str} for {backbone} not found in text")
        
        if warnings:
            result.warn_check("Some values may not be mentioned in paper text: " + "; ".join(warnings))
        else:
            result.pass_check("Key values are mentioned in paper text")
    
    except Exception as e:
        result.fail_check(f"Error during comparison: {str(e)}", str(e))
    
    return result


def check_overall_vs_full_eamsr() -> CheckResult:
    """检查 Overall 行不被误当成主实验 Full EAMSR"""
    result = CheckResult("C3", "Overall vs Full EAMSR Distinction")
    
    json_path = PAPER_TABLES_DIR / "table7b_llm_backbone.json"
    
    if not json_path.exists():
        result.skip_check("JSON file not found")
        return result
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # 检查 provenance 是否明确标注
        provenance = json_data.get("provenance", {})
        source_type = provenance.get("source_type", "")
        
        if "summary" in source_type.lower():
            result.pass_check("Provenance correctly indicates summary-level data")
        else:
            result.warn_check("Provenance should clarify that Overall is not Full EAMSR main experiment")
    
    except Exception as e:
        result.fail_check(f"Error: {str(e)}", str(e))
    
    return result


def check_uar_values() -> CheckResult:
    """检查 UAR 值合理性"""
    result = CheckResult("C4", "UAR Value Consistency")
    
    json_path = PAPER_TABLES_DIR / "table7b_llm_backbone.json"
    
    if not json_path.exists():
        result.skip_check("JSON file not found")
        return result
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            rows = json_data.get("rows", [])
        
        # 检查 DeepSeek-class 的 UAR 为 1.3%
        deepseek_row = next((r for r in rows if r["llm_backbone"] == "DeepSeek-class"), None)
        if deepseek_row and abs(deepseek_row["UAR"] - 1.3) > 0.01:
            result.fail_check(
                f"DeepSeek-class UAR should be 1.3%, got {deepseek_row['UAR']}%",
                "DeepSeek UAR mismatch"
            )
            return result
        
        # 检查 Overall UAR 为 0.4%
        overall_row = next((r for r in rows if r["llm_backbone"] == "Overall"), None)
        if overall_row and abs(overall_row["UAR"] - 0.4) > 0.01:
            result.fail_check(
                f"Overall UAR should be 0.4%, got {overall_row['UAR']}%",
                "Overall UAR mismatch"
            )
            return result
        
        # 检查 GPT-4-class 和 Qwen2.5 的 UAR 为 0.0%
        for backbone_name in ["GPT-4-class", "Qwen2.5-72B-Instruct"]:
            row = next((r for r in rows if r["llm_backbone"] == backbone_name), None)
            if row and abs(row["UAR"] - 0.0) > 0.01:
                result.fail_check(
                    f"{backbone_name} UAR should be 0.0%, got {row['UAR']}%",
                    f"{backbone_name} UAR mismatch"
                )
                return result
        
        result.pass_check("UAR values are consistent with expectations")
    
    except Exception as e:
        result.fail_check(f"Error: {str(e)}", str(e))
    
    return result


def check_pir_wsr_stability() -> CheckResult:
    """检查 PIR=100.0% 和 WSR=100.0% 在三个 backbone 中均一致"""
    result = CheckResult("C5", "PIR/WSR Stability Across Backbones")
    
    json_path = PAPER_TABLES_DIR / "table7b_llm_backbone.json"
    
    if not json_path.exists():
        result.skip_check("JSON file not found")
        return result
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            rows = json_data.get("rows", [])
        
        backbone_rows = [r for r in rows if r["llm_backbone"] != "Overall"]
        
        for row in backbone_rows:
            if abs(row["PIR"] - 100.0) > 0.01:
                result.fail_check(
                    f"{row['llm_backbone']} PIR should be 100.0%, got {row['PIR']}%",
                    f"PIR not 100% for {row['llm_backbone']}"
                )
                return result
            
            if abs(row["WSR"] - 100.0) > 0.01:
                result.fail_check(
                    f"{row['llm_backbone']} WSR should be 100.0%, got {row['WSR']}%",
                    f"WSR not 100% for {row['llm_backbone']}"
                )
                return result
        
        result.pass_check("PIR and WSR are 100.0% across all backbones")
    
    except Exception as e:
        result.fail_check(f"Error: {str(e)}", str(e))
    
    return result


def check_acc_adm_range() -> CheckResult:
    """检查 Acc_adm 的 backbone range 为 1.6 percentage points"""
    result = CheckResult("C6", "Acc_adm Backbone Range")
    
    json_path = PAPER_TABLES_DIR / "table7b_llm_backbone.json"
    
    if not json_path.exists():
        result.skip_check("JSON file not found")
        return result
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            rows = json_data.get("rows", [])
        
        backbone_rows = [r for r in rows if r["llm_backbone"] != "Overall"]
        acc_values = [r["Acc_adm"] for r in backbone_rows]
        
        acc_range = max(acc_values) - min(acc_values)
        
        if abs(acc_range - 1.6) > 0.1:
            result.fail_check(
                f"Acc_adm range should be ~1.6 pp, got {acc_range:.1f} pp",
                "Acc_adm range mismatch"
            )
            return result
        
        result.pass_check(f"Acc_adm range is {acc_range:.1f} percentage points (expected ~1.6)")
    
    except Exception as e:
        result.fail_check(f"Error: {str(e)}", str(e))
    
    return result


def check_local_todo() -> CheckResult:
    """检查 local_todo.md 是否仍写 'Table 7 Panel B 无数据支撑'"""
    result = CheckResult("C7", "local_todo.md Status")
    
    todo_path = PROJECT_ROOT / "local_todo.md"
    
    if not todo_path.exists():
        result.skip_check("local_todo.md not found")
        return result
    
    try:
        with open(todo_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "Table 7 Panel B 无数据支撑" in content or "多 LLM 后端数据缺失" in content:
            result.warn_check("local_todo.md still mentions missing data. Should be updated.")
        else:
            result.pass_check("local_todo.md does not mention missing Table 7 Panel B data")
    
    except Exception as e:
        result.fail_check(f"Error: {str(e)}", str(e))
    
    return result


def check_acc_adm_conflict() -> CheckResult:
    """检查 Table 3 Full EAMSR 在不同文件中是否存在 93.3% 与 94.8% 冲突"""
    result = CheckResult("C8", "Acc_adm 93.3% vs 94.8% Conflict Check")
    
    # 检查 full_eamsr_p2.json
    full_eamsr_path = DATA_RESULTS_DIR / "full_eamsr_p2.json"
    table3_path = PAPER_TABLES_DIR / "table3_overall.csv"
    bootstrap_path = DATA_STATS_DIR / "bootstrap_ci.json"
    
    findings = []
    
    try:
        if full_eamsr_path.exists():
            with open(full_eamsr_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                methods = data.get("methods", [])
                for method in methods:
                    if method.get("method_id") == "Full_EAMSR":
                        acc_adm = method.get("metrics", {}).get("Acc_adm", {})
                        mean_val = acc_adm.get("mean", 0)
                        findings.append(f"full_eamsr_p2.json: Acc_adm mean = {mean_val:.4f} ({mean_val*100:.1f}%)")
        
        if table3_path.exists():
            with open(table3_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("Method") == "EAMSR":
                        acc_str = row.get("Acc_adm↑", "0%").replace("%", "")
                        findings.append(f"table3_overall.csv: Acc_adm = {acc_str}%")
        
        if bootstrap_path.exists():
            with open(bootstrap_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                full_eamsr_results = data.get("results", {}).get("Full_EAMSR", {})
                for metric in full_eamsr_results.get("metrics", []):
                    if metric.get("metric") == "Acc_adm":
                        point_est = metric.get("point_estimate", 0)
                        findings.append(f"bootstrap_ci.json: Acc_adm point_estimate = {point_est:.4f} ({point_est*100:.1f}%)")
    
    except Exception as e:
        result.fail_check(f"Error: {str(e)}", str(e))
        return result
    
    # 分析冲突
    has_933 = any("93.3%" in f or "0.933" in f for f in findings)
    has_948 = any("94.8%" in f or "0.948" in f for f in findings)
    
    if has_933 and has_948:
        result.warn_check(
            "Both 93.3% and 94.8% found in different files. "
            "This may reflect task-level vs repeated-run aggregate difference. "
            "Requires manual confirmation for Table 3 reporting."
        )
        result.details += "\nFindings:\n" + "\n".join(f"  - {f}" for f in findings)
    elif has_933:
        result.pass_check("Only 93.3% found (task-level)")
        result.details += "\nFindings:\n" + "\n".join(f"  - {f}" for f in findings)
    elif has_948:
        result.pass_check("Only 94.8% found (repeated-run aggregate)")
        result.details += "\nFindings:\n" + "\n".join(f"  - {f}" for f in findings)
    else:
        result.warn_check("Neither 93.3% nor 94.8% clearly identified")
        result.details += "\nFindings:\n" + "\n".join(f"  - {f}" for f in findings)
    
    return result


def check_dual_directory_sync() -> CheckResult:
    """检查 paper_data/ 和 paper/tables/ 是否存在双目录同步不一致"""
    result = CheckResult("C9", "Dual Directory Synchronization")
    
    if not PAPER_DATA_DIR.exists():
        result.pass_check("paper_data/ directory does not exist (no sync needed)")
        return result
    
    try:
        # 检查关键文件是否在两个目录都存在
        key_files = [
            "table7b_llm_backbone.csv",
            "table7b_llm_backbone.json",
        ]
        
        sync_issues = []
        for filename in key_files:
            new_path = PAPER_TABLES_DIR / filename
            old_path = PAPER_DATA_DIR / filename
            
            if new_path.exists() and not old_path.exists():
                sync_issues.append(f"{filename} exists in paper/tables/ but not in paper_data/")
            elif old_path.exists() and not new_path.exists():
                sync_issues.append(f"{filename} exists in paper_data/ but not in paper/tables/")
        
        if sync_issues:
            result.warn_check("Sync issues: " + "; ".join(sync_issues))
        else:
            result.pass_check("Dual directories are in sync")
    
    except Exception as e:
        result.fail_check(f"Error: {str(e)}", str(e))
    
    return result


def check_cross_ref() -> CheckResult:
    """检查 cross_ref_check.json 是否包含 Table 7 Panel B"""
    result = CheckResult("C10", "cross_ref_check.json Table 7 Coverage")
    
    cross_ref_path = DATA_VALIDATION_DIR / "cross_ref_check.json"
    
    if not cross_ref_path.exists():
        result.skip_check("cross_ref_check.json not found")
        return result
    
    try:
        with open(cross_ref_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查是否提到 Table 7
        content_str = json.dumps(data)
        if "Table 7" in content_str or "table7" in content_str.lower():
            result.pass_check("cross_ref_check.json mentions Table 7")
        else:
            result.warn_check("cross_ref_check.json does not mention Table 7 Panel B")
    
    except Exception as e:
        result.fail_check(f"Error: {str(e)}", str(e))
    
    return result


def check_readme_provenance() -> CheckResult:
    """检查 README.md 是否说明 Table 7 Panel B 的 provenance"""
    result = CheckResult("C11", "README.md Provenance Statement")
    
    readme_path = PROJECT_ROOT / "README.md"
    
    if not readme_path.exists():
        result.warn_check("README.md not found. Should be created with provenance statement.")
        return result
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "Table 7 Panel B" in content or "LLM-backbone" in content or "LLM backbone" in content:
            result.pass_check("README.md mentions Table 7 Panel B / LLM-backbone")
        else:
            result.warn_check("README.md should include provenance statement for Table 7 Panel B")
    
    except Exception as e:
        result.fail_check(f"Error: {str(e)}", str(e))
    
    return result


def check_fake_raw_runs() -> CheckResult:
    """检查没有生成伪 raw run 文件"""
    result = CheckResult("C12", "No Fake Raw Run Files")
    
    suspicious_patterns = [
        "fake_llm_backbone_runs.json",
        "synthetic_raw_runs.json",
        "mock_backbone_results.json",
    ]
    
    found_suspicious = []
    
    for pattern in suspicious_patterns:
        if (PROJECT_ROOT / pattern).exists():
            found_suspicious.append(pattern)
    
    # 也检查 data/results/ 目录
    if DATA_RESULTS_DIR.exists():
        for json_file in DATA_RESULTS_DIR.glob("*.json"):
            if any(keyword in json_file.name.lower() for keyword in ["fake", "synthetic", "mock"]):
                found_suspicious.append(str(json_file.relative_to(PROJECT_ROOT)))
    
    if found_suspicious:
        result.fail_check(
            "Suspicious files found (possible fake raw runs): " + ", ".join(found_suspicious),
            "Fake raw run files detected"
        )
    else:
        result.pass_check("No fake raw run files detected")
    
    return result


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 70)
    print("EAMSR: Consistency Check")
    print("=" * 70)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # 执行所有检查
    checks = [
        check_csv_json_consistency(),
        check_paper_text_consistency(),
        check_overall_vs_full_eamsr(),
        check_uar_values(),
        check_pir_wsr_stability(),
        check_acc_adm_range(),
        check_local_todo(),
        check_acc_adm_conflict(),
        check_dual_directory_sync(),
        check_cross_ref(),
        check_readme_provenance(),
        check_fake_raw_runs(),
    ]
    
    # 打印结果
    print("Check Results:")
    print("-" * 70)
    
    pass_count = 0
    fail_count = 0
    warn_count = 0
    skip_count = 0
    
    for check in checks:
        status_symbol = {
            "PASS": "✓",
            "FAIL": "✗",
            "WARNING": "⚠",
            "SKIP": "○"
        }.get(check.status, "?")
        
        print(f"{status_symbol} [{check.status:7s}] {check.check_id}: {check.name}")
        if check.details:
            for line in check.details.split("\n")[:3]:  # 只显示前3行
                print(f"         {line}")
        print()
        
        if check.status == "PASS":
            pass_count += 1
        elif check.status == "FAIL":
            fail_count += 1
        elif check.status == "WARNING":
            warn_count += 1
        elif check.status == "SKIP":
            skip_count += 1
    
    print("-" * 70)
    print(f"Summary: {pass_count} PASS, {fail_count} FAIL, {warn_count} WARNING, {skip_count} SKIP")
    print()
    
    # 生成报告
    report_path = PROJECT_ROOT / "RESULT_CONSISTENCY_REPORT.md"
    
    report_lines = [
        "# EAMSR Result Consistency Report",
        f"\n**Generated**: {datetime.now().isoformat()}",
        f"**Script**: scripts/check_consistency.py",
        "\n## Summary",
        f"\n- **Total checks**: {len(checks)}",
        f"- **PASS**: {pass_count}",
        f"- **FAIL**: {fail_count}",
        f"- **WARNING**: {warn_count}",
        f"- **SKIP**: {skip_count}",
        "\n## Detailed Results",
    ]
    
    for check in checks:
        report_lines.append(f"\n### {check.check_id}: {check.name}")
        report_lines.append(f"\n**Status**: {check.status}")
        if check.details:
            report_lines.append(f"\n{check.details}")
        if check.violations:
            report_lines.append(f"\n**Violations**:")
            for v in check.violations:
                report_lines.append(f"- {v}")
    
    report_lines.append(f"\n---\n\n*This report was generated automatically by scripts/check_consistency.py*")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    
    print(f"[WRITE] {report_path}")
    
    # 也写入 data/validation/
    validation_path = DATA_VALIDATION_DIR / "llm_backbone_consistency_check.json"
    validation_data = {
        "check_id": "LLM-BACKBONE-CONSISTENCY-001",
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_checks": len(checks),
            "pass": pass_count,
            "fail": fail_count,
            "warning": warn_count,
            "skip": skip_count
        },
        "checks": [
            {
                "check_id": c.check_id,
                "name": c.name,
                "status": c.status,
                "details": c.details,
                "violations": c.violations
            }
            for c in checks
        ]
    }
    
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    with open(validation_path, 'w', encoding='utf-8') as f:
        json.dump(validation_data, f, indent=2, ensure_ascii=False)
    
    print(f"[WRITE] {validation_path}")
    
    print()
    print("=" * 70)
    if fail_count > 0:
        print(f"Consistency check completed with {fail_count} FAIL(s). Review required.")
    elif warn_count > 0:
        print(f"Consistency check completed with {warn_count} WARNING(s). Review recommended.")
    else:
        print("Consistency check completed successfully. All checks passed.")
    print("=" * 70)


if __name__ == "__main__":
    main()
