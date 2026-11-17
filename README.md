# Home Credit default risk (GCI Global 2026)

Predicts the probability that a loan applicant has payment difficulties (`TARGET = 1`), scored by ROC AUC.
Only the supplied `train.csv` and `test.csv` are used: no outside data and no hand labelling. All seeds are fixed.

**Result:** a blend of LightGBM, CatBoost and a TabM neural network, all using *same-person history* (see below).
Nested out-of-fold AUC **0.7707** (5-fold cross-validation).

## Contents

| Path | Content |
| --- | --- |
| `notebooks/01_data_exploration.ipynb` | Missing values, placeholder values, signal per column, loan-term structure, train/test similarity, repeat applicants |
| `notebooks/02_feature_engineering.ipynb` | All label-free features and the same-person pairs → `work/` |
| `notebooks/03_base_models.ipynb` | LightGBM, CatBoost, CatBoost with reconstructed scores, TabM (reference models) |
| `notebooks/04_new_ideas.ipynb` | Ideas screened with a fixed decision rule; final runs of the submitted models |
| `notebooks/05_ensemble_and_submission.ipynb` | Compares blending methods with nested CV and writes `outputs/submission.csv` |
| `src/` | Shared helpers: data paths and caching (`utils.py`), the CV runner (`cv.py`), model wrappers (`models.py`) |

The notebooks are saved with their outputs, so every result can be read without re-running.

## How to run

1. Put the supplied files in a `data/` folder next to `notebooks/`:

   ```
   data/train.csv
   data/test.csv
   data/sample_submission.csv
   ```

2. Create the environment (Python 3.12) and run the notebooks in order:

   ```sh
   conda create -p ./.venv python=3.12
   .venv/bin/pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
   cd notebooks
   export HC_DEVICE=mps   # optional: Apple-silicon GPU for TabM; leave unset for CPU
   for nb in 0*.ipynb; do
     ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 "$nb"
   done
   ```

   The submission is written to `outputs/submission.csv`. Intermediate files go to `work/` (features, and every
   model's predictions per seed). A re-run only computes what is not cached yet; delete `work/` to start from scratch.

* **Run time.** About 9 hours on an M1 MacBook with `HC_DEVICE=mps`. Most of it is TabM (9 seeds, about 30 minutes
  each) and CatBoost (about 25 minutes per seed). Without a GPU, TabM takes roughly twice as long.
* **Threads.** 8 CPU threads by default; set `HC_THREADS` to change.
* **Apple silicon with conda:** the pip build of PyTorch ships its own `libomp.dylib`, which clashes with conda's
  (`OMP: Error #15` on `import torch`). Fix: replace `.venv/lib/python3.12/site-packages/torch/lib/libomp.dylib`
  with a symlink to `.venv/lib/libomp.dylib`.
* **Repeatability.** All seeds are fixed. CatBoost and TabM results can differ in the 4th decimal between machines
  (x86 vs ARM, CPU vs GPU). For the submitted file, the extra CatBoost seeds (3–5) and TabM seeds (3–8) were trained
  in separate processes with exactly the same code and settings as notebook 04 and picked up from its cache. A
  re-run therefore reproduces the submission up to such small floating-point differences.

## Method

**Validation.** 5-fold stratified cross-validation; each seed uses its own fold split. Every training row gets an
out-of-fold prediction; test predictions average the fold models. Train and test are hard to tell apart (a
classifier separating them reaches AUC 0.513 only), so cross-validation is a fair stand-in for the test set.
Decisions are made on cross-validation, not on the public leaderboard.

**Features (notebook 02).**
* *Cleaning:* `DAYS_EMPLOYED = 365243` (a placeholder, mostly pensioners) becomes missing plus a flag.
* *Base set (55 columns):* affordability ratios (income, credit, annuity, goods price), employment length relative
  to age, summaries of the three external scores, loan term (credit / annuity) and its distance to multiples of
  6 and 12 months, an implied interest rate under assumed terms, and missing-value counts.
* *Reconstructed external scores (6 columns):* a LightGBM regressor predicts each external score from the other
  columns, fitted out-of-fold on train + test (no labels involved). It gives an estimate where the score is
  missing and the residual where it is present.
* *Same-person pairs (5 columns):* `DAYS_*` columns count back from the application date, so for one person
  applying twice, birth − ID publication, birth − registration, birth − employment start and birth − last phone
  change stay constant. Two applications with the same gender count as the same person when at least 3 of the
  4 differences match, or 2 match and region population and education are equal too. That gives 3,455 pairs;
  2.9% of applicants have one. The columns describe the pair structure: number of matched applications, how many
  are earlier or later, the smallest gap in days and the strongest match.

**Label-based features (notebook 04).** Computed inside each fold from that fold's training labels only. Pairs
never link a row to itself, so a training row never sees its own label.
* *Repeat history:* defaults among other applications with the same (gender, birth − ID publication,
  birth − registration).
* *Same-person history:* defaults among the matched applications, split into later, earlier, exact duplicates
  and all-4-match pairs, and the gap to the nearest default. When one application of a pair defaulted, the other
  did 38–47% of the time (base rate 8%).

The features are model inputs, never rules: the models decide how much to trust them.

**Models.**
* *LightGBM:* 21 leaves, row and column subsampling, L1/L2 regularisation.
* *CatBoost:* depth 5, L2 = 8, native categorical handling, with the reconstructed scores.
* *TabM* (Gorishniy et al., 2024): 16 weight-sharing MLPs averaged, piecewise-linear number embeddings.

The neural network makes different errors from the trees, which helps the blend. Each final model trains for a
fixed length found in a development run, so no fold influences its own model.

**Idea screening (notebook 04).** Each idea was tested with LightGBM on two seeds against a control with the same
folds and kept only if it gained at least 0.0002 AUC (rule fixed before running).

| Idea | AUC | Decision |
| --- | --- | --- |
| Control (base features) | 0.76288 | |
| Population statistics over train + test | 0.76272 | dropped |
| Repeat history | 0.76423 | kept |
| Neighbour default rate (most similar applicants) | 0.76294 | dropped |
| Repeat history + same-person history | **0.76620** | kept |

**Blend (notebook 05).** Equal weights, optimised weights and logistic stacking are compared with nested
cross-validation (fitted on 4/5 of the out-of-fold rows, scored on the rest). Among blends within 0.0001 of the
best, the one with the fewest models is chosen.

| Model (out-of-fold AUC) | Seeds | AUC |
| --- | --- | --- |
| LightGBM | 3 | 0.76634 |
| CatBoost-recon | 6 | 0.76889 |
| TabM | 9 | 0.76833 |
| **Blend** (logistic stacking: 0.076 / 0.475 / 0.448) | | **0.77073** (nested) |

For comparison: the same recipe without any repeat-applicant features scores 0.7666, and with the first repeat
history only 0.7683. The version with 3 seeds per model scored 0.77375 on the public leaderboard.

**Tried without gain:** CatBoost tuning on the final features (depth 6–7, stronger L2, 254 borders, bagging);
features describing how an application changed between a person's applications; external scores borrowed from
the other application; population statistics; neighbour default rate. In earlier project rounds: random forest,
logistic regression, XGBoost, small MLPs, broader feature sets, class weighting, target encodings of category
interactions.

## References

* Y. Gorishniy, A. Kotelnikov, A. Babenko. *TabM: Advancing Tabular Deep Learning with Parameter-Efficient
  Ensembling.* 2024. Packages `tabm` and `rtdl_num_embeddings` (piecewise-linear embeddings: Gorishniy, Rubachev,
  Babenko, *On Embeddings for Numerical Features in Tabular Deep Learning*, NeurIPS 2022).
* LightGBM, CatBoost, scikit-learn and PyTorch, used through their standard APIs.

All other code was written for this project.
