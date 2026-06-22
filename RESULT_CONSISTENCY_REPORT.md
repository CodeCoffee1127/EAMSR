# EAMSR Result Consistency Report

**Generated**: 2026-06-22T12:17:59.211536
**Script**: scripts/check_consistency.py

## Summary

- **Total checks**: 12
- **PASS**: 10
- **FAIL**: 0
- **WARNING**: 2
- **SKIP**: 0

## Detailed Results

### C1: Table 7 Panel B CSV/JSON Consistency

**Status**: PASS

CSV and JSON values are consistent

### C2: Table 7 Panel B vs Paper Text Consistency

**Status**: PASS

Key values are mentioned in paper text

### C3: Overall vs Full EAMSR Distinction

**Status**: PASS

Provenance correctly indicates summary-level data

### C4: UAR Value Consistency

**Status**: PASS

UAR values are consistent with expectations

### C5: PIR/WSR Stability Across Backbones

**Status**: PASS

PIR and WSR are 100.0% across all backbones

### C6: Acc_adm Backbone Range

**Status**: PASS

Acc_adm range is 1.6 percentage points (expected ~1.6)

### C7: local_todo.md Status

**Status**: PASS

local_todo.md does not mention missing Table 7 Panel B data

### C8: Acc_adm 93.3% vs 94.8% Conflict Check

**Status**: WARNING

Both 93.3% and 94.8% found in different files. This may reflect task-level vs repeated-run aggregate difference. Requires manual confirmation for Table 3 reporting.
Findings:
  - full_eamsr_p2.json: Acc_adm mean = 0.9483 (94.8%)
  - table3_overall.csv: Acc_adm = 93.3%
  - bootstrap_ci.json: Acc_adm point_estimate = 0.9667 (96.7%)

### C9: Dual Directory Synchronization

**Status**: PASS

paper_data/ directory does not exist (no sync needed)

### C10: cross_ref_check.json Table 7 Coverage

**Status**: WARNING

cross_ref_check.json does not mention Table 7 Panel B

### C11: README.md Provenance Statement

**Status**: PASS

README.md mentions Table 7 Panel B / LLM-backbone

### C12: No Fake Raw Run Files

**Status**: PASS

No fake raw run files detected

---

*This report was generated automatically by scripts/check_consistency.py*