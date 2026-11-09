# Round 1: Baseline, data audit and first improved models

This folder groups the files for this round. `code`, `results` and `models` are relative links to the original implementation/evidence, not duplicate copies.

## Notebooks

- [README.ipynb](notebooks/README.ipynb)
- [tutorial.ipynb](notebooks/tutorial.ipynb)
- [preprocessing.ipynb](notebooks/preprocessing.ipynb)
- [01_competition_data_audit.ipynb](notebooks/01_competition_data_audit.ipynb)
- [02_improved_models_and_submission.ipynb](notebooks/02_improved_models_and_submission.ipynb)

## Reports

- [First-pass results](reports/README.md)

## Code and evidence

- [Code](code/)
- [Saved results and experiment evidence](results/)
- [Saved models](models/)

Original supplied notebooks and reference documents are included here. The combined first/second-pass journal is in [Round 2](../round2/reports/EXPERIMENT_LOG.md).
- [Column descriptions](reference/HomeCredit_columns_description.xlsx)
- [Supplied tutorial slides](reference/competition_tutorial.pptx)

## Running existing notebooks

Notebook bytes are unchanged. Their original working-directory assumption still applies: execute with `Competition` as the kernel working directory and select `Competition/.venv`. For prediction replay use `project.py` from the project root; see [the reproduction guide](../../REPRODUCTION_README.md). Historical outputs can be restored from Git as described in [the output archive guide](../../docs/OUTPUTS.md).
