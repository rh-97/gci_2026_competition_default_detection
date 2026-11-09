# Competition rounds

Read the focused reports in this order:

1. [Data audit and EDA](round1/reports/EDA_REPORT.md): what the data contain and what we observed.
2. [Dataset enhancement](round2/reports/DATASET_ENHANCEMENT_REPORT.md): what inputs changed, why, how and the results.
3. [Model selection](round5/reports/MODEL_SELECTION_REPORT.md): what was tested, how choices were made and why the final blend won.

Start with a round folder; its README links the notebooks, reports, implementation, models and raw results.

| Round | Scope |
| --- | --- |
| [Round 1](round1/README.md) | Baseline, data audit and first improved models |
| [Round 2](round2/README.md) | Feature engineering and two-seed ensemble |
| [Round 3](round3/README.md) | Signed term features and three-seed bagging |
| [Round 4](round4/README.md) | Stopped incremental search |
| [Round 5](round5/README.md) | Structural models, neural ensemble and score reconstruction |

The consolidated [project report](../PROJECT_REPORT.md) covers the full progression. The shared implementation remains in `improvements/` to preserve existing checkpoint imports and frozen source signatures. No Python package refactor was introduced.
