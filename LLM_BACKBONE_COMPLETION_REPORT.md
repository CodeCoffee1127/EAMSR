# LLM-Backbone Robustness Data Completion Report

**Generated**: 2026-06-16T09:20:20.221582
**Script**: scripts/update_llm_backbone_results.py

## Summary

- **Raw multi-backbone runs detected**: False
- **Source files**: N/A (summary-level data used)
- **Provenance type**: user_provided_supplemental_summary

## Files Generated

### Table 7 Panel B Core Files
- `paper/tables/table7b_llm_backbone.csv` - CSV table
- `paper/tables/table7b_llm_backbone.json` - JSON table with metadata

### Derived Statistics
- `paper/tables/table7b_llm_backbone_derived_stats.json` - Metric ranges and deltas

### Count Reconstruction
- `paper/tables/table7b_llm_backbone_count_reconstruction.json` - Approximate counts from percentages

### Plot Data
- `paper/tables/table7b_llm_backbone_plot_data.json` - Figure-ready JSON

### Old Directory Compatibility
- `paper_data/` directory does not exist, no sync performed

## Provenance

```json
{
  "source_type": "user_provided_supplemental_summary",
  "raw_trial_data_available": false,
  "source_files": [
    "user-provided local instruction for LLM-backbone robustness integration"
  ],
  "aggregation": "summary-level values only",
  "generated_by": "scripts/update_llm_backbone_results.py",
  "note": "This file records summary-level LLM-backbone robustness values for local paper integration. It must not be treated as reconstructed 120×5 raw trial data."
}
```

## Warnings

No per-sample multi-backbone raw run file was found unless raw_trial_data_available is true.
These values should not be used to regenerate per-sample confusion matrices unless raw trial data are provided.

## Next Steps

1. Review the generated files for correctness.
2. Update paper text (Section 4.6) if not already done.
3. Run `scripts/check_consistency.py` to validate consistency.
4. If raw multi-backbone runs become available, re-run this script to recompute from raw data.

---

*This report was generated automatically by scripts/update_llm_backbone_results.py*
