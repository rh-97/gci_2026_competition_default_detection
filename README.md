# Home Credit default risk (GCI Global 2026)

Predict the probability that a loan applicant defaults (`TARGET = 1`), scored by ROC AUC.
Only the supplied `train.csv` / `test.csv` are used: no outside data, no hand labelling.

**Start with [APPROACH.md](APPROACH.md)**: what was done to the data and the models, what worked and what did not.
The notebooks show every step with its results.

**Result:** a stacked blend of LightGBM, CatBoost and a TabM neural network, all using a new repeat-applicant
history feature. Out-of-fold AUC is **0.7682** (5-fold CV, 3 seeds), against 0.7667 for the rebuilt previous recipe.
The submission is [outputs/submission.csv](outputs/submission.csv).

## Layout

| Path | Content |
| --- | --- |
| [APPROACH.md](APPROACH.md) | Method write-up: data, features, models, validation, results |
| [notebooks/](notebooks/) | The analysis, run in order (outputs are saved in the notebooks) |
| [src/](src/) | Small generic helpers: paths and caching, CV runner, model wrappers |
| [data/](data/) | Supplied data: train, test, sample submission, column descriptions |
| [outputs/](outputs/) | `submission.csv` and `cv_results.json` (blend weights and scores) |
| [docs/competition_rules.ipynb](docs/competition_rules.ipynb) | Supplied competition description and rules |
| `work/` | Regenerated caches (features, per-model predictions); git-ignored |

| Notebook | What it does |
| --- | --- |
| [01_data_exploration](notebooks/01_data_exploration.ipynb) | Missingness, placeholder values, signal per column, loan-term structure, train/test similarity, repeat applicants |
| [02_feature_engineering](notebooks/02_feature_engineering.ipynb) | Builds all label-free features for train and test → `work/features.parquet` |
| [03_base_models](notebooks/03_base_models.ipynb) | LightGBM, CatBoost, CatBoost with reconstructed scores, TabM neural net (5-fold CV, 3 seeds) |
| [04_new_ideas](notebooks/04_new_ideas.ipynb) | Population statistics, repeat-applicant history, neighbour default rate: screened, then confirmed |
| [05_ensemble_and_submission](notebooks/05_ensemble_and_submission.ipynb) | Compares blending methods with nested CV, writes the submission |

## Reproduce

```sh
conda create -p ./.venv python=3.12
.venv/bin/pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
cd notebooks
for nb in 0*.ipynb; do ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 "$nb"; done
```

Everything runs on CPU (8 threads by default; set `HC_THREADS` to change). A full run takes about 6–7 hours on an
8-core desktop. TabM accounts for about 4 hours (about an hour per seed) and CatBoost for about 2.

* **Caching.** Each model run is cached in `work/preds/` per seed and keyed by its settings and columns, so
  re-running a notebook only computes what is missing. If you change the feature code, delete `work/` first.
* **Repeatability.** All seeds are fixed. Two sources of tiny floating-point differences remain:
  - multi-threaded LightGBM in the score reconstruction (about 1e-13);
  - PyTorch on different thread counts.

  The three TabM-new seeds used for the submission were trained as three parallel processes with
  `HC_THREADS=3`, using the same code and settings as notebook 04. A re-run therefore reproduces the submission
  up to such small differences rather than byte for byte.
