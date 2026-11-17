# Home Credit default risk (GCI Global 2026)

Predict the probability that a loan applicant defaults (`TARGET = 1`), scored by ROC AUC.
Only the supplied `train.csv` / `test.csv` are used: no outside data, no hand labelling.

**Start with [APPROACH.md](APPROACH.md)**: what was done to the data and the models, what worked and what did not.
The notebooks show every step with its results.

**Result:** a weighted blend of LightGBM, CatBoost and a TabM neural network, all using same-person history:
applications by the same probable person, found through date differences that stay constant between applications.
Nested out-of-fold AUC is **0.7707** (5-fold CV; 3, 6 and 9 seeds), against 0.7682 for the previous submission's recipe
and 0.7666 for the rebuilt original recipe.
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
| [04_new_ideas](notebooks/04_new_ideas.ipynb) | Population statistics, repeat-applicant history, neighbour default rate, same-person history (round 2): screened, then confirmed |
| [05_ensemble_and_submission](notebooks/05_ensemble_and_submission.ipynb) | Compares blending methods with nested CV, writes the submission |

## Reproduce

```sh
conda create -p ./.venv python=3.12
.venv/bin/pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
cd notebooks
export HC_DEVICE=mps   # optional, Apple silicon only
for nb in 0*.ipynb; do ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 "$nb"; done
```

Everything runs on CPU (8 threads by default; set `HC_THREADS` to change). On Apple silicon, `HC_DEVICE=mps`
trains TabM on the GPU (one epoch: 5.6 s vs 10.7 s on the M1 CPU). The 3-seed run took **4 h 40 min on an M1
MacBook with `HC_DEVICE=mps`** (notebook 03: 1.5 h, 04: 3.2 h, 05: 1 min); the 3 extra CatBoost and 6 extra TabM
seeds of the final version add about 4.5 h. TabM takes about 30 minutes per seed there. On an 8-core x86 desktop without a GPU, the same pipeline should take roughly 9 hours (estimate from the earlier 6–7 h run without round 2).

* **Apple silicon + conda:** the pip wheel of PyTorch ships its own `libomp.dylib`, which clashes with conda's
  (`OMP: Error #15` on `import torch`). Fix: replace `site-packages/torch/lib/libomp.dylib` with a symlink to the
  environment's `lib/libomp.dylib`.

* **Caching.** Each model run is cached in `work/preds/` per seed and keyed by its settings and columns, so
  re-running a notebook only computes what is missing. If you change the feature code, delete `work/` first.
* **Repeatability.** All seeds are fixed. Two sources of tiny floating-point differences remain:
  - multi-threaded LightGBM in the score reconstruction (about 1e-13);
  - PyTorch on different devices (CPU vs MPS) and thread counts.

  The submission was produced on an M1 with `HC_DEVICE=mps`. The extra v2 seeds (CatBoost 3–5, TabM 3–8) were
  trained by separate processes with the same code and settings as notebook 04 (TabM with `HC_THREADS=2`, CatBoost
  with `HC_THREADS=6`) and picked up from the cache. CatBoost and TabM results differ from an x86 run in the 4th decimal, so a re-run elsewhere reproduces
  the submission up to such small differences rather than byte for byte.
