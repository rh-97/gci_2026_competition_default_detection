# Round 5: Structural models, neural ensemble and score reconstruction

This folder groups the files for this round. `code`, `results` and `models` are relative links to the original implementation/evidence, not duplicate copies.

## Notebooks

- [07_signal_opportunity_audit.ipynb](notebooks/07_signal_opportunity_audit.ipynb)
- [08_high_upside_modeling_plan.ipynb](notebooks/08_high_upside_modeling_plan.ipynb)
- [08b_local_gpu_amendment.ipynb](notebooks/08b_local_gpu_amendment.ipynb)
- [08c_compute_budget_policy.ipynb](notebooks/08c_compute_budget_policy.ipynb)
- [09_high_upside_results_reproduction.ipynb](notebooks/09_high_upside_results_reproduction.ipynb)

## Reports

- [IMPROVEMENT_REPORT.md](reports/IMPROVEMENT_REPORT.md)
- [HIGH_UPSIDE_EXPERIMENT_LOG.md](reports/HIGH_UPSIDE_EXPERIMENT_LOG.md)
- [Standalone EDA report, including the later error audit](../round1/reports/EDA_REPORT.md)
- [ROC curve](reports/roc_curve.png): saved development validation predictions, AUC **0.76626**.

## Plans

- [HIGH_UPSIDE_PLAN.md](plans/HIGH_UPSIDE_PLAN.md)

## Code and evidence

- [Code](code/)
- [Saved results and experiment evidence](results/)
- [Saved models](models/)

## Running existing notebooks

Notebook bytes are unchanged. Their original working-directory assumption still applies: execute with `Competition` as the kernel working directory and select `Competition/.venv`. For prediction replay use `project.py` from the project root; see [the reproduction guide](../../REPRODUCTION_README.md). Historical outputs can be restored from Git as described in [the output archive guide](../../docs/OUTPUTS.md).
