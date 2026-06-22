# Table 7: Generalization and LLM Backbone Robustness

## Panel A: Scenario Generalization Performance

| Generalization Setting | Acc_adm↑ | UAR↓ | PIR↑ | CNR↑ | ATR↑ |
|------------------------|----------|------|------|------|------|
| New target layouts | 92.4% | 0.0% | 100.0% | 88.0% | 98.4% |
| New no-fly-zone layouts | 91.7% | 0.0% | 100.0% | 86.7% | 98.0% |
| New communication maps | 90.8% | 1.3% | 100.0% | 85.6% | 97.6% |
| New time-window distributions | 91.5% | 0.0% | 100.0% | 86.2% | 97.9% |
| New task types | 90.6% | 1.3% | 100.0% | 84.9% | 97.1% |
| **Overall** | **91.4%** | **0.5%** | **100.0%** | **86.3%** | **97.8%** |

## Panel B: LLM-Backbone Robustness

| LLM Backbone | Acc_adm↑ | UAR↓ | UBR↑ | PIR↑ | WSR↑ | Decision Consistency↑ |
|--------------|----------|------|------|------|------|----------------------|
| GPT-4-class | 93.3% | 0.0% | 94.7% | 100.0% | 100.0% | 95.0% |
| Qwen2.5-72B-Instruct | 92.5% | 0.0% | 93.4% | 100.0% | 100.0% | 93.8% |
| DeepSeek-class | 91.7% | 1.3% | 92.6% | 100.0% | 100.0% | 92.9% |
| **Overall** | **92.5%** | **0.4%** | **93.6%** | **100.0%** | **100.0%** | **93.9%** |

**Note:** Panel A and Panel B use different metric schemas because they evaluate different aspects of robustness. Panel B values are summary-level supplemental results; per-sample multi-backbone raw runs are not available in this release.
