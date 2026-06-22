# EAMSR: Evidence-Carrying Mission Admission Contracts for Natural-Language UAV Task Submission

This repository contains the public replication materials for the paper **"Evidence-Carrying Mission Admission Contracts for Natural-Language UAV Task Submission"**, submitted to *Drones* (MDPI).

The repository includes the EAMSR-Bench dataset, experimental code, result tables, paper figures, validation and audit records, and UAV/AirSim scenario scripts supporting the findings of the study.

---

## Repository Structure

```
EAMSR/
├── src/eamsr/                   # Core EAMSR source code
│   ├── __init__.py
│   ├── eamsr_schemas.py         # Data schema definitions
│   ├── eamsr_schemas.json       # JSON schema for validation
│   ├── experiment_runner.py     # Main experiment orchestration
│   ├── greedy_relaxation.py     # Greedy relaxation algorithm
│   ├── l1_simulator.py          # L1-level contract simulator
│   └── annotation_protocol_v1.md # Annotation protocol documentation
│
├── data/                        # Dataset and experimental results
│   ├── raw/                     # Raw dataset
│   │   └── dataset_p2.jsonl     # EAMSR-Bench P2 dataset (120 UAV task instructions)
│   ├── annotations/             # Human annotations
│   │   └── annotations_p2.json  # P2 annotation records
│   ├── results/                 # Experimental results
│   │   ├── full_eamsr_p2.json   # Full EAMSR pipeline results
│   │   ├── baseline_p2.json     # Baseline comparison results
│   │   └── ablation_p2.json     # Ablation study results
│   ├── stats/                   # Statistical analyses
│   │   ├── bootstrap_ci.json    # Bootstrap 95% confidence intervals
│   │   ├── ablation_confusion_matrices.json
│   │   └── runtime_breakdown.json
│   └── validation/              # Validation and consistency checks
│       ├── consistency_check.json
│       ├── cross_ref_check.json
│       ├── l2_validation_p2.json
│       └── llm_backbone_consistency_check.json
│
├── scripts/                     # Reproduction and analysis scripts
│   ├── check_consistency.py     # Result consistency verification
│   ├── draw_experiment_figures.py # Figure generation
│   ├── p0_validation.py         # P0-level validation
│   └── update_llm_backbone_results.py
│
├── paper/                       # Paper artifacts
│   ├── figures/                 # Paper figures (PDF, PNG, SVG)
│   │   ├── fig3_overall_performance_tradeoff.*
│   │   ├── fig4_backend_witness_margins.*
│   │   ├── fig5_ablation_runtime_overhead.*
│   │   └── figure_*.json        # Figure generation metadata
│   ├── tables/                  # Paper table data (CSV, JSON)
│   │   ├── table2_dataset.csv
│   │   ├── table3_overall.csv
│   │   ├── table4a_grounding.csv
│   │   ├── table4b_risk_handling.csv
│   │   ├── table5_witness.csv
│   │   ├── table6a_refinement.csv
│   │   ├── table6b_repair.csv
│   │   ├── table7a_generalization.*
│   │   ├── table7b_llm_backbone.*
│   │   └── table8_ablation.csv
│   └── text/                    # Paper text sections (markdown)
│
├── manifests/                   # Project manifests and inventories
├── audit/                       # Audit trail records
├── UAV-PY/                      # UAV/AirSim simulation scripts
│   ├── airsim/                  # AirSim client wrapper
│   ├── scenario_s1_energy.py    # Energy consumption scenario
│   ├── scenario_s2_airspace.py  # Airspace compliance scenario
│   ├── scenario_s3_success.py   # Mission success scenario
│   └── *.png                    # Generated simulation figures
│
├── verification_report.md       # Verification report
├── diff_report.md               # Difference analysis report
├── RESULT_CONSISTENCY_REPORT.md # Result consistency report
├── LLM_BACKBONE_COMPLETION_REPORT.md
├── PROJECT_CLEANUP_REPORT.md
├── MANIFEST_BEFORE_CLEANUP.md
├── MANIFEST_AFTER_CLEANUP.md
├── PUBLICATION_INVENTORY.md     # Publication inventory
└── SECURITY_AND_SIZE_CHECK.md   # Security and size check report
```

---

## Installation

### Prerequisites

- **Python**: 3.9 or higher recommended
- **pip**: Latest version

### Setup

```bash
# Clone the repository
git clone https://github.com/CodeCoffee1127/EAMSR.git
cd EAMSR

# Install dependencies
pip install -r requirements.txt
```

### AirSim Simulation (Optional)

The `UAV-PY/` directory contains simulation scripts that can interface with Microsoft AirSim for UAV scenario validation. AirSim is **not required** for reproducing the main experimental results reported in the paper. The published figures and tables are generated from the dataset and code in `src/` and `data/`.

To run AirSim simulations (optional):
1. Install [Microsoft AirSim](https://github.com/microsoft/airsim) following the official instructions
2. Configure the AirSim environment according to the scenario scripts in `UAV-PY/`
3. Run individual scenario scripts (e.g., `python UAV-PY/scenario_s1_energy.py`)

**Note**: The AirSim client wrapper in `UAV-PY/airsim/` is a lightweight wrapper for the AirSim Python API. It does not include the full AirSim binary or simulation environment.

---

## Reproducing the Main Results

### 1. Run Consistency Checks

Verify the consistency of experimental results:

```bash
python scripts/check_consistency.py
```

This script checks:
- Data integrity across result files
- Cross-reference consistency between tables and figures
- LLM backbone consistency validation

### 2. Generate Paper Figures

Reproduce the figures used in the paper:

```bash
python scripts/draw_experiment_figures.py
```

Generated figures will be saved to `paper/figures/`.

### 3. Run Experiments (Optional)

The core experiments have already been executed and results are provided in `data/results/`. To re-run the full pipeline:

```bash
python src/eamsr/experiment_runner.py
```

**Note**: Some experiment scripts may require access to LLM APIs (e.g., OpenAI, Qwen, DeepSeek). The repository **does not include any API keys or credentials**. Users must configure their own API keys via environment variables if they wish to re-run LLM-dependent experiments.

### 4. LLM Backbone Robustness Analysis

Update and verify LLM backbone results:

```bash
python scripts/update_llm_backbone_results.py
```

---

## Data Description

### EAMSR-Bench Dataset

- **`data/raw/dataset_p2.jsonl`**: The core EAMSR-Bench P2 dataset containing 120 natural-language UAV task instructions across 6 application scenarios: S1 Powerline inspection, S2 Disaster-area search, S3 Campus delivery, S4 River monitoring, S5 Bridge inspection, and S6 Communication-limited task.

- **`data/annotations/annotations_p2.json`**: Human annotations for the P2 dataset, including contract labels, witness requirements, and risk assessments.

### Experimental Results

**Main Results (Table 3):** EAMSR achieves **93.3% admission accuracy** (112/120 tasks correct) and **0.0% unwarranted admission rate** across 120 tasks. Human labels: 42 ADMIT / 47 CLARIFY / 31 REJECT. Correct final decisions: 42 ADMIT, 43 CLARIFY, 28 REJECT. The remaining 8 errors occur only between CLARIFY and REJECT; no non-admissible sample is incorrectly output as ADMIT.

**Note on 94.8%:** The value `0.9483` (94.8%) appearing in `full_eamsr_p2.json` under `repeated_run_summary` is a supplementary statistic representing the mean accuracy over 5 random seeds. It is **not** the Table 3 task-level final decision accuracy. The public repository explicitly separates `main_task_level_metrics` (93.3%) from `repeated_run_summary` (94.8%) to avoid ambiguity.

- **`data/results/full_eamsr_p2.json`**: Results from the full EAMSR pipeline with all contract layers enabled.
- **`data/results/baseline_p2.json`**: Baseline comparison results (without EAMSR contracts).
- **`data/results/ablation_p2.json`**: Ablation study results showing the contribution of each contract layer.

### Statistical Analyses

- **`data/stats/bootstrap_ci.json`**: Bootstrap 95% confidence intervals for key metrics.
- **`data/stats/ablation_confusion_matrices.json`**: Confusion matrices for ablation studies.
- **`data/stats/runtime_breakdown.json`**: Runtime breakdown by contract layer and operation type.

### Validation Records

- **`data/validation/consistency_check.json`**: Internal consistency validation results.
- **`data/validation/cross_ref_check.json`**: Cross-reference validation between tables and figures.
- **`data/validation/l2_validation_p2.json`**: L2-level contract validation results.
- **`data/validation/llm_backbone_consistency_check.json`**: LLM backbone robustness validation.

---

## Paper Artifacts

### Tables

All tables referenced in the paper are available in `paper/tables/` in both CSV and JSON formats where applicable. Key tables include:

- **Table 2**: Dataset statistics and scenario distribution
- **Table 3**: Overall performance comparison (EAMSR vs. Baseline)
- **Table 4**: Grounding accuracy and risk handling
- **Table 5**: Witness generation and verification
- **Table 6**: Contract refinement and repair
- **Table 7**: Generalization and LLM backbone robustness
- **Table 8**: Ablation study results

### Figures

Paper figures are provided in PDF (for LaTeX), PNG (for preview), and SVG (for editing) formats:

- **Figure 3**: Overall performance tradeoff
- **Figure 4**: Backend witness margins
- **Figure 5**: Ablation runtime overhead

Figure generation metadata and style configurations are included in `paper/figures/`.

---

## License

This repository contains materials for the paper submitted to *Drones* (MDPI).

- **Source code**: Licensed under the [MIT License](LICENSE) (see `LICENSE` file).
- **Dataset, tables, and figures**: Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) unless otherwise specified.
- **Third-party components**: The `UAV-PY/airsim/` directory contains a wrapper for Microsoft AirSim API. AirSim is licensed under the Apache 2.0 License by Microsoft Corporation. See the [AirSim repository](https://github.com/microsoft/airsim) for details.

---

## Citation

If you use this repository or the EAMSR-Bench dataset in your research, please cite:

```bibtex
@article{huang2026eamsr,
  title = {Evidence-Carrying Mission Admission Contracts for Natural-Language UAV Task Submission},
  author = {Huang, Zhiwei and Wei, Gang and Wang, Gang and Liu, Xuan and Sun, Haolun and Han, Xiaoyang and Yuan, Hui},
  journal = {Drones},
  year = {2026},
  note = {Manuscript submitted}
}
```

---

## Data Availability

The EAMSR-Bench dataset, AirSim scenario configurations, source code, validation records, and paper artifacts supporting the findings of this study are openly available in the public GitHub repository at:

**https://github.com/CodeCoffee1127/EAMSR**

---

## Reproducibility Checklist

- [x] Dataset publicly available
- [x] Source code publicly available
- [x] Experimental results provided
- [x] Statistical analyses provided
- [x] Validation records provided
- [x] Paper figures and tables provided
- [x] Reproduction scripts provided
- [x] `.gitignore` configured
- [x] `requirements.txt` provided
- [x] No sensitive information (API keys, credentials) included
- [x] No model weights or large binary files included

---

## Contact

For questions about this repository or the EAMSR project, please contact the corresponding author of the paper.

---

## Disclaimer

This repository is provided "as is" for academic replication purposes. The authors make no warranties regarding the completeness or accuracy of the data, code, or results. Users are responsible for ensuring compliance with local regulations when using UAV simulation environments.
