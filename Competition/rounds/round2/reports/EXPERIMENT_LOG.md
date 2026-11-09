# Complete competition experiment log

Updated automatically from retained artifacts: 2026-11-08T15:00:30.428876+00:00.

This is the living record of hypotheses, implementations, results, decisions and limitations.
The JSON/CSV ledger contains every trial's complete configuration; this document provides the reasons and interpretation.
First-pass rationales are reconstructed from retained source and clearly marked as retrospective. Second-pass hypotheses are recorded before their runs.

## Confirmed competition result

The user confirmed that `output/submission_improved.csv` achieved **public ROC-AUC 0.7654**, with displayed rank **1,094** (`hasanRocky`).
This is a screenshot snapshot, not a permanent rank. The submitted file's SHA-256 is `71cd8588031deef62dadd8eeddb8e33965cbe42b6e0fc25c41e673271b08c616`.
The private/full-test score is unknown. No second-pass public score is assumed or invented.

## Data, rules and reproducibility

- Only supplied `input/train.csv` and `input/test.csv` supply model rows; the supplied Excel file is a data dictionary.
- No external training data, pretrained model weights, recovered test labels, manual predictions or downloaded reference notebooks.
- Software dependencies are installed in `Competition/.venv`; software downloads do not add dataset rows.
- Preserve all existing notebooks, the first-pass CSV, original models and first-pass reproduction ZIP. New work lives under `improvements/round2` and new notebooks.
- Fixed seeds and fold indices, fold-fitted encoders and saved models make each result reviewable and reproducible.

## Validation chronology and limitations

The original partition is 60% inner fit, 20% inner validation and 20% historical audit.
The 80% development portion has five fixed stratified folds. All second-pass screening and selection remain inside that development portion.
The first-pass baseline and candidate AUCs therefore have comparable folds and row identities.

The first-pass audit was evaluated once after its selection, scoring **0.755506** versus **0.666573** for the tutorial-style RF.
Its paired bootstrap gain interval was **0.079682–0.097858**. This is a historical check. It must not be called a fresh untouched test for second-pass models.
Public feedback is one observed score for a frozen CSV, not a per-experiment tuning signal.
New development OOF gains are selection-biased estimates, so promising candidates need fold consistency and a second split-seed comparison.
Any historical-audit comparison in this pass must be labeled descriptive and performed after new selection, not used to retune.

## First-pass findings: what worked and what did not

1. All original features plus boosting substantially improved on the five-feature tutorial RF.
2. Same-settings LightGBM raw/engineered CV improved **0.749947 → 0.756102**. This is the strongest controlled evidence for the financial/score feature family.
3. Compact depth-5 CatBoost scored **0.760790** in development CV, above the larger-feature version (**0.759728**) and deeper compact version (**0.760148**).
4. Tuned LightGBM added complementary errors: the final two-thirds CatBoost / one-third LightGBM blend scored **0.761772** development OOF AUC.
5. Broad categorical crosses, feature pruning and class weighting failed to beat the best screened configurations. These were not proof that such methods never help.
6. Histogram boosting (**0.753292 CV**) and spline logistic regression (**0.748304 CV**) were weaker. The additive spline representation may miss useful interactions, but that mechanism was not isolated.
7. The best three-model blend improved development AUC by only **0.000072** over the selected pair. It was rejected by a pre-audit complexity threshold of 0.00015. That threshold is a heuristic, not a statistical significance test.
8. Gain/feature-importance pruning removed columns that may still contribute jointly; the tested top-25/40/55/70 variants did not outperform the tuned reference.

## Second-pass design

Current screen status: **34 complete, 0 failed, 0 pending**.

The first trial must reproduce the old compact CatBoost predictions within 1e-10 before other comparisons are trusted.
New trials test XGBoost, CatBoost regularization/quantization/categorical handling, native missing bins,
targeted feature families and two alternative LightGBM variants. The search does not assume every added feature should help.

### New feature families: how and why

- **Risk**: clipped score logits, geometric/harmonic summaries, a predefined 1:2:3 score-weighted mean, conservative mean-minus-dispersion, age×score and term×score interactions. These can simplify nonlinear relationships for shallow trees. They add representations, not new information or externally estimated risk scores.
- **Finance**: income minus 12 annuity payments, per-person margins, per-adult amounts, goods/income, credit-cost amount and distances to multiples of 6/12 in the credit/annuity ratio. The factor 12 is an explicit hypothetical payment-frequency transform; the dictionary does not establish a customer's actual payment schedule.
- **Hypothetical rates**: for assumed 24/36/60 payment periods, solve `annuity/credit = r / (1 - (1+r)^(-n))` by 28 bisection steps. Impossible positive-rate cases become missing. These are redundant nonlinear transforms of the payment ratio, not claims to have recovered actual interest rates or loan terms.
- **Missingness/structure**: individual absence indicators, an eight-state external-score absence pattern, coarse organization labels before `:` and deterministic five-year age bands. These can expose collection segments, but extra categorical states can also overfit.
- **Combined**: concatenate all targeted additions to test complementarity versus added noise.

### Comparisons and stopping rules

Screen on the original inner split, then advance promising models and diverse algorithms to common five-fold development CV.
Evaluate AUC gain, fold consistency, runtime, iteration saturation and complementary errors, not just the best single score.
Use paired OOF comparisons for descriptive uncertainty. Recheck finalists with fixed iterations on another development fold seed.
The new-recipe gate is at least +0.0002 primary OOF AUC, positive pooled second-seed gain and positive gain in at least three of five second-seed folds.
Second-seed weights are frozen. A two-seed averaging diagnostic is also planned: it must improve over the better individual seed by more than 0.00015 for both baseline and candidate before doubling the final model bank.
Freeze candidate/weights before any historical-audit description or new test prediction. Preserve the old public-scored CSV as the fallback.

## Per-trial index

| Pass | Experiment | Status | Inner AUC | Delta to stated reference | Development CV AUC |
| --- | --- | --- | --- | --- | --- |
| pass1 | tutorial_rf | complete | 0.659983 | 0.000000 | — |
| pass1 | lgb_raw | complete | 0.736784 | 0.076801 | 0.749947 |
| pass1 | lgb_engineered | complete | 0.744063 | 0.007279 | 0.756102 |
| pass1 | lgb_extended | complete | 0.737550 | -0.006513 | — |
| pass1 | lgb_grouped | complete | 0.737398 | -0.006665 | — |
| pass1 | lgb_tune_00 | complete | 0.743643 | -0.000420 | — |
| pass1 | lgb_tune_01 | complete | 0.738712 | -0.005352 | — |
| pass1 | lgb_tune_02 | complete | 0.743030 | -0.001033 | — |
| pass1 | lgb_tune_03 | complete | 0.735715 | -0.008348 | — |
| pass1 | lgb_tune_04 | complete | 0.738801 | -0.005262 | — |
| pass1 | lgb_tune_05 | complete | 0.742856 | -0.001207 | — |
| pass1 | lgb_tune_06 | complete | 0.743358 | -0.000705 | — |
| pass1 | lgb_tune_07 | complete | 0.739569 | -0.004494 | — |
| pass1 | lgb_tune_08 | complete | 0.743508 | -0.000555 | — |
| pass1 | lgb_tune_09 | complete | 0.744441 | 0.000378 | — |
| pass1 | lgb_tune_10 | complete | 0.744747 | 0.000683 | — |
| pass1 | lgb_tune_11 | complete | 0.745002 | 0.000939 | — |
| pass1 | lgb_tune_12 | complete | 0.746578 | 0.002515 | 0.757388 |
| pass1 | lgb_tune_13 | complete | 0.745606 | 0.001543 | — |
| pass1 | lgb_tune_14 | complete | 0.745436 | 0.001373 | — |
| pass1 | lgb_tune_15 | complete | 0.747151 | 0.003088 | 0.757328 |
| pass1 | lgb_tune_16 | complete | 0.745213 | 0.001150 | — |
| pass1 | lgb_tune_17 | complete | 0.745560 | 0.001497 | — |
| pass1 | lgb_tune_18 | complete | 0.740470 | -0.003593 | — |
| pass1 | lgb_tune_19 | complete | 0.743381 | -0.000682 | — |
| pass1 | lgb_tune_20 | complete | 0.745865 | 0.001802 | — |
| pass1 | lgb_tune_21 | complete | 0.745921 | 0.001858 | — |
| pass1 | lgb_tune_22 | complete | 0.746107 | 0.002044 | — |
| pass1 | lgb_tune_23 | complete | 0.743351 | -0.000712 | — |
| pass1 | cat_depth4 | complete | 0.748959 | 0.001299 | 0.759728 |
| pass1 | cat_depth5 | complete | 0.747660 | 0.000000 | — |
| pass1 | cat_depth6 | complete | 0.747212 | -0.000448 | — |
| pass1 | cat_depth7 | complete | 0.747337 | -0.000322 | — |
| pass1 | logistic_0.01 | complete | 0.732960 | 0.000648 | — |
| pass1 | logistic_0.1 | complete | 0.732312 | 0.000000 | — |
| pass1 | logistic_1.0 | complete | 0.731796 | -0.000516 | — |
| pass1 | hgb_10 | complete | 0.741282 | -0.000327 | — |
| pass1 | hgb_20 | complete | 0.741609 | 0.000000 | 0.753292 |
| pass1 | hgb_31 | complete | 0.741303 | -0.000306 | — |
| pass1 | spline_0.01 | complete | 0.736017 | -0.000520 | — |
| pass1 | spline_0.1 | complete | 0.736537 | 0.000000 | 0.748304 |
| pass1 | spline_1.0 | complete | 0.735930 | -0.000607 | — |
| pass1 | lgb_engineered_groups | complete | 0.745036 | 0.000973 | — |
| pass1 | lgb_lean | complete | 0.743296 | -0.000767 | — |
| pass1 | lgb_scores | complete | 0.738912 | -0.005151 | — |
| pass1 | lgb_small_8 | complete | 0.745126 | 0.001063 | — |
| pass1 | lgb_small_12 | complete | 0.745416 | 0.001352 | — |
| pass1 | lgb_weight_2.0 | complete | 0.744176 | 0.000112 | — |
| pass1 | lgb_weight_5.0 | complete | 0.744965 | 0.000902 | — |
| pass1 | cat_raw | complete | 0.741656 | -0.006004 | — |
| pass1 | cat_lean | complete | 0.748493 | 0.000833 | 0.760790 |
| pass1 | lgb_top_25 | complete | 0.738165 | -0.008986 | — |
| pass1 | lgb_top_40 | complete | 0.742890 | -0.004262 | — |
| pass1 | lgb_top_55 | complete | 0.745922 | -0.001229 | — |
| pass1 | lgb_top_70 | complete | 0.746336 | -0.000815 | 0.756960 |
| pass1 | cat_lean_depth4 | complete | 0.747615 | -0.000878 | — |
| pass1 | cat_lean_depth6 | complete | 0.748028 | -0.000464 | 0.760148 |
| pass2 | r2_cat_baseline | complete | 0.748493 | 0.000000 | — |
| pass2 | r2_cat_risk | complete | 0.746813 | -0.001680 | — |
| pass2 | r2_cat_finance | complete | 0.749082 | 0.000590 | — |
| pass2 | r2_cat_missing | complete | 0.747589 | -0.000903 | — |
| pass2 | r2_cat_combined | complete | 0.748670 | 0.000177 | — |
| pass2 | r2_cat_slow | complete | 0.748572 | 0.000079 | — |
| pass2 | r2_cat_strong_l2 | complete | 0.747663 | -0.000829 | — |
| pass2 | r2_cat_weak_l2 | complete | 0.747569 | -0.000924 | — |
| pass2 | r2_cat_onehot10 | complete | 0.748004 | -0.000489 | — |
| pass2 | r2_cat_onehot64 | complete | 0.748193 | -0.000300 | — |
| pass2 | r2_cat_borders512 | complete | 0.747731 | -0.000762 | — |
| pass2 | r2_cat_rsm075 | complete | 0.748607 | 0.000115 | — |
| pass2 | r2_cat_ordered | complete | 0.747732 | -0.000761 | — |
| pass2 | r2_cat_native_missing | complete | 0.748981 | 0.000489 | 0.760561 |
| pass2 | r2_xgb_d3 | complete | 0.745542 | -0.002951 | — |
| pass2 | r2_xgb_d4 | complete | 0.745160 | -0.003332 | — |
| pass2 | r2_xgb_d5 | complete | 0.744544 | -0.003948 | — |
| pass2 | r2_xgb_lean | complete | 0.745215 | -0.003278 | — |
| pass2 | r2_lgb_smooth_cats | complete | 0.747658 | -0.000835 | 0.758417 |
| pass2 | r2_lgb_linear | complete | 0.743766 | -0.004727 | — |
| pass2 | r2_cat_burden | complete | 0.747691 | -0.000801 | — |
| pass2 | r2_cat_term_proxies | complete | 0.749952 | 0.001460 | 0.762254 |
| pass2 | r2_cat_finance_native | complete | 0.749235 | 0.000743 | — |
| pass2 | r2_cat_finance_tuned | complete | 0.749273 | 0.000781 | — |
| pass2 | r2_cat_ctr1 | complete | 0.747827 | -0.000665 | — |
| pass2 | r2_cat_ctr2 | complete | 0.748095 | -0.000397 | — |
| pass2 | r2_cat_bayesian_rsm075 | complete | 0.747148 | -0.001345 | — |
| pass2 | r2_xgb_finance | complete | 0.747225 | -0.001268 | 0.758883 |
| pass2 | r2_lgb_finance | complete | 0.746487 | -0.002005 | — |
| pass2 | r2_cat_budget_control | complete | 0.748493 | 0.000000 | — |
| pass2 | r2_cat_proxies_native | complete | 0.749647 | 0.001155 | 0.761574 |
| pass2 | r2_cat_rates_only | complete | 0.748473 | -0.000019 | — |
| pass2 | r2_cat_distances_only | complete | 0.748766 | 0.000273 | — |
| pass2 | r2_cat_proxies_rsm075 | complete | 0.749288 | 0.000795 | — |

## Detailed experiment notes

Each comparison below states its reference. Cross-algorithm deltas combine representation and learner effects.
An observed difference is evidence about this configuration on this split, not proof of the suggested mechanism.
All first-pass notes are retrospective reconstructions; every second-pass candidate has a contemporaneous hypothesis in its plan/event record.

### pass1 / tutorial_rf

**Hypothesis:** Establish a fair, split-safe version of the supplied five-feature tutorial baseline.

**How:** `rf` on `tutorial_five` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{}`

**Runner settings:** `{"max_depth": 10, "n_estimators": 100, "n_jobs": 4, "random_state": 0}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.659983; reference `tutorial_rf` (0.659983); delta 0.000000; best trees None; runtime seconds —.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `tutorial_rf` AUC 0.659983; delta 0.000000. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.149742; log loss 0.268023; Brier 0.072150. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. A reference point, not a serious attempt to use all available information.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_raw

**Hypothesis:** Using all original predictors and histogram boosting should improve on the five-feature RF.

**How:** `lgb` on `raw` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "raw", "kind": "lgb", "name": "lgb_raw", "params": {"colsample_bytree": 0.9, "max_bin": 127, "max_depth": -1, "min_child_samples": 100, "num_leaves": 24, "reg_alpha": 0.1, "reg_lambda": 10, "subsample": 0.85, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.9, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 127, "max_depth": -1, "min_child_samples": 100, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 24, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.1, "reg_lambda": 10, "subsample": 0.85, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.736784; reference `tutorial_rf` (0.659983); delta 0.076801; best trees 483; runtime seconds 5.14.

**CV:** pooled AUC 0.749947; fold AUCs `[0.7457303157688067, 0.7538936687258065, 0.7478034336694058, 0.7476336991821007, 0.7547624733025291]`; fold tree counts `[333, 511, 351, 356, 437]`.

**Parent comparison:** `tutorial_rf` AUC 0.659983; delta 0.076801. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.222588; log loss 0.251980; Brier 0.068964. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Advanced to five-fold development CV. Algorithm and feature count change jointly; the next raw/engineered comparison is the controlled feature ablation.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_engineered

**Hypothesis:** Loan/income ratios, age/employment ratios and external-score summaries may simplify useful interactions.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "kind": "lgb", "name": "lgb_engineered", "params": {"colsample_bytree": 0.9, "max_bin": 127, "max_depth": -1, "min_child_samples": 100, "num_leaves": 24, "reg_alpha": 0.1, "reg_lambda": 10, "subsample": 0.85, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.9, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 127, "max_depth": -1, "min_child_samples": 100, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 24, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.1, "reg_lambda": 10, "subsample": 0.85, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.744063; reference `lgb_raw` (0.736784); delta 0.007279; best trees 662; runtime seconds 9.01.

**CV:** pooled AUC 0.756102; fold AUCs `[0.7506505522081611, 0.7589658381234831, 0.757087012058926, 0.7542114224628345, 0.7598237715572652]`; fold tree counts `[412, 375, 354, 401, 277]`.

**Parent comparison:** `lgb_raw` AUC 0.736784; delta 0.007279. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.232630; log loss 0.250031; Brier 0.068486. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Advanced to five-fold development CV. Same-settings five-fold CV confirms a gain from 0.749947 to 0.756102, supporting this feature family.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_extended

**Hypothesis:** Additional categorical crosses, log features, age bands and optional group summaries may expose further structure.

**How:** `lgb` on `extended` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "extended", "kind": "lgb", "name": "lgb_extended", "params": {"colsample_bytree": 0.9, "max_bin": 127, "max_depth": -1, "min_child_samples": 100, "num_leaves": 24, "reg_alpha": 0.1, "reg_lambda": 10, "subsample": 0.85, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.9, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 127, "max_depth": -1, "min_child_samples": 100, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 24, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.1, "reg_lambda": 10, "subsample": 0.85, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.737550; reference `lgb_engineered` (0.744063); delta -0.006513; best trees 486; runtime seconds 9.67.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.006513. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.223979; log loss 0.252040; Brier 0.068927. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. The broader representation screened worse; added split opportunities or sparse category combinations may introduce noise.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_grouped

**Hypothesis:** Additional categorical crosses, log features, age bands and optional group summaries may expose further structure.

**How:** `lgb` on `extended` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "extended", "groups": true, "kind": "lgb", "name": "lgb_grouped", "params": {"colsample_bytree": 0.9, "max_bin": 127, "max_depth": -1, "min_child_samples": 100, "num_leaves": 24, "reg_alpha": 0.1, "reg_lambda": 10, "subsample": 0.85, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.9, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 127, "max_depth": -1, "min_child_samples": 100, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 24, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.1, "reg_lambda": 10, "subsample": 0.85, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.737398; reference `lgb_engineered` (0.744063); delta -0.006665; best trees 459; runtime seconds 11.64.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.006665. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.224468; log loss 0.251970; Brier 0.068895. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. The broader representation screened worse; added split opportunities or sparse category combinations may introduce noise.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_00

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_00", "params": {"colsample_bytree": 0.7652330811644328, "max_bin": 255, "max_depth": -1, "min_child_samples": 148, "num_leaves": 45, "reg_alpha": 0.018170180928652968, "reg_lambda": 0.652583271652393, "subsample": 0.8271190783202719, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.7652330811644328, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 148, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 45, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.018170180928652968, "reg_lambda": 0.652583271652393, "subsample": 0.8271190783202719, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.743643; reference `lgb_engineered` (0.744063); delta -0.000420; best trees 435; runtime seconds 10.38.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.000420. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.232953; log loss 0.250211; Brier 0.068528. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_01

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `extended` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "extended", "groups": true, "kind": "lgb", "name": "lgb_tune_01", "params": {"colsample_bytree": 0.8967196619343512, "max_bin": 127, "max_depth": -1, "min_child_samples": 349, "num_leaves": 20, "reg_alpha": 0.6732698427206649, "reg_lambda": 8.310860102624094, "subsample": 0.9890245833565928, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.8967196619343512, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 127, "max_depth": -1, "min_child_samples": 349, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 20, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.6732698427206649, "reg_lambda": 8.310860102624094, "subsample": 0.9890245833565928, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.738712; reference `lgb_engineered` (0.744063); delta -0.005352; best trees 339; runtime seconds 7.69.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.005352. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.226772; log loss 0.251448; Brier 0.068801. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_02

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": false, "kind": "lgb", "name": "lgb_tune_02", "params": {"colsample_bytree": 0.725046618438576, "max_bin": 63, "max_depth": -1, "min_child_samples": 204, "num_leaves": 47, "reg_alpha": 6.045311521986175, "reg_lambda": 13.320793623704482, "subsample": 0.8572834631300237, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.725046618438576, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 63, "max_depth": -1, "min_child_samples": 204, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 47, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 6.045311521986175, "reg_lambda": 13.320793623704482, "subsample": 0.8572834631300237, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.743030; reference `lgb_engineered` (0.744063); delta -0.001033; best trees 259; runtime seconds 6.45.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.001033. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.231201; log loss 0.250006; Brier 0.068485. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_03

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `extended` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "extended", "groups": true, "kind": "lgb", "name": "lgb_tune_03", "params": {"colsample_bytree": 0.8877509010778653, "max_bin": 127, "max_depth": -1, "min_child_samples": 52, "num_leaves": 42, "reg_alpha": 0.002578254216781311, "reg_lambda": 0.6853497491826263, "subsample": 0.7129799526301828, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.8877509010778653, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 127, "max_depth": -1, "min_child_samples": 52, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 42, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.002578254216781311, "reg_lambda": 0.6853497491826263, "subsample": 0.7129799526301828, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.735715; reference `lgb_engineered` (0.744063); delta -0.008348; best trees 335; runtime seconds 8.38.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.008348. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.222840; log loss 0.252420; Brier 0.068975. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_04

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `extended` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "extended", "groups": true, "kind": "lgb", "name": "lgb_tune_04", "params": {"colsample_bytree": 0.6824704554254913, "max_bin": 63, "max_depth": -1, "min_child_samples": 160, "num_leaves": 30, "reg_alpha": 0.008450124590987818, "reg_lambda": 4.0749466913192975, "subsample": 0.8238561240836021, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.6824704554254913, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 63, "max_depth": -1, "min_child_samples": 160, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 30, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.008450124590987818, "reg_lambda": 4.0749466913192975, "subsample": 0.8238561240836021, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.738801; reference `lgb_engineered` (0.744063); delta -0.005262; best trees 317; runtime seconds 8.54.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.005262. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.225531; log loss 0.251336; Brier 0.068770. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_05

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_05", "params": {"colsample_bytree": 0.9624419798590104, "max_bin": 63, "max_depth": -1, "min_child_samples": 234, "num_leaves": 37, "reg_alpha": 0.04330527884780594, "reg_lambda": 3.386424244493785, "subsample": 0.8168366720016197, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.9624419798590104, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 63, "max_depth": -1, "min_child_samples": 234, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 37, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.04330527884780594, "reg_lambda": 3.386424244493785, "subsample": 0.8168366720016197, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.742856; reference `lgb_engineered` (0.744063); delta -0.001207; best trees 350; runtime seconds 11.20.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.001207. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.230475; log loss 0.250438; Brier 0.068599. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_06

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": false, "kind": "lgb", "name": "lgb_tune_06", "params": {"colsample_bytree": 0.8198210636755052, "max_bin": 63, "max_depth": -1, "min_child_samples": 294, "num_leaves": 20, "reg_alpha": 0.00190476335724297, "reg_lambda": 0.3808158557191752, "subsample": 0.9148380294892694, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.8198210636755052, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 63, "max_depth": -1, "min_child_samples": 294, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 20, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.00190476335724297, "reg_lambda": 0.3808158557191752, "subsample": 0.9148380294892694, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.743358; reference `lgb_engineered` (0.744063); delta -0.000705; best trees 564; runtime seconds 10.53.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.000705. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.232533; log loss 0.250058; Brier 0.068465. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_07

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `extended` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "extended", "groups": false, "kind": "lgb", "name": "lgb_tune_07", "params": {"colsample_bytree": 0.7313531708890701, "max_bin": 127, "max_depth": -1, "min_child_samples": 176, "num_leaves": 45, "reg_alpha": 7.043741573368013, "reg_lambda": 14.16537350976517, "subsample": 0.9899086313887235, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.7313531708890701, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 127, "max_depth": -1, "min_child_samples": 176, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 45, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 7.043741573368013, "reg_lambda": 14.16537350976517, "subsample": 0.9899086313887235, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.739569; reference `lgb_engineered` (0.744063); delta -0.004494; best trees 297; runtime seconds 11.96.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.004494. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.226939; log loss 0.251272; Brier 0.068768. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_08

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_08", "params": {"colsample_bytree": 0.9200665023873321, "max_bin": 255, "max_depth": -1, "min_child_samples": 97, "num_leaves": 13, "reg_alpha": 5.17238600396412, "reg_lambda": 0.45177078769529433, "subsample": 0.6784069253819305, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.9200665023873321, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 97, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 13, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 5.17238600396412, "reg_lambda": 0.45177078769529433, "subsample": 0.6784069253819305, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.743508; reference `lgb_engineered` (0.744063); delta -0.000555; best trees 782; runtime seconds 14.33.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.000555. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.231546; log loss 0.250083; Brier 0.068505. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_09

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_09", "params": {"colsample_bytree": 0.7634614881240677, "max_bin": 255, "max_depth": -1, "min_child_samples": 162, "num_leaves": 38, "reg_alpha": 0.17481947281502147, "reg_lambda": 0.23470730903827638, "subsample": 0.9631927502349246, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.7634614881240677, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 162, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 38, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.17481947281502147, "reg_lambda": 0.23470730903827638, "subsample": 0.9631927502349246, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.744441; reference `lgb_engineered` (0.744063); delta 0.000378; best trees 456; runtime seconds 13.73.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.000378. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.232441; log loss 0.249991; Brier 0.068503. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_10

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_10", "params": {"colsample_bytree": 0.8530873294402385, "max_bin": 255, "max_depth": -1, "min_child_samples": 131, "num_leaves": 14, "reg_alpha": 0.21547047510160577, "reg_lambda": 0.6587863894843841, "subsample": 0.9555468612325263, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.8530873294402385, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 131, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 14, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.21547047510160577, "reg_lambda": 0.6587863894843841, "subsample": 0.9555468612325263, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.744747; reference `lgb_engineered` (0.744063); delta 0.000683; best trees 793; runtime seconds 15.14.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.000683. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.232292; log loss 0.249798; Brier 0.068472. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_11

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_11", "params": {"colsample_bytree": 0.8000881291780853, "max_bin": 255, "max_depth": -1, "min_child_samples": 100, "num_leaves": 17, "reg_alpha": 0.22552926805304213, "reg_lambda": 0.36604656775974564, "subsample": 0.933325997310737, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.8000881291780853, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 100, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 17, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.22552926805304213, "reg_lambda": 0.36604656775974564, "subsample": 0.933325997310737, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.745002; reference `lgb_engineered` (0.744063); delta 0.000939; best trees 728; runtime seconds 16.74.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.000939. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.234146; log loss 0.249676; Brier 0.068404. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_12

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_12", "params": {"colsample_bytree": 0.7016450200644813, "max_bin": 255, "max_depth": -1, "min_child_samples": 76, "num_leaves": 16, "reg_alpha": 1.6865703875308493, "reg_lambda": 0.5703637874410369, "subsample": 0.960384200459015, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.7016450200644813, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 76, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 16, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 1.6865703875308493, "reg_lambda": 0.5703637874410369, "subsample": 0.960384200459015, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.746578; reference `lgb_engineered` (0.744063); delta 0.002515; best trees 849; runtime seconds 18.42.

**CV:** pooled AUC 0.757388; fold AUCs `[0.7515190383288642, 0.7605168700723451, 0.7579962680325605, 0.755287054156671, 0.7617547868726724]`; fold tree counts `[516, 605, 813, 405, 601]`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.002515. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.235055; log loss 0.249264; Brier 0.068339. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Advanced to five-fold development CV. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_13

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_13", "params": {"colsample_bytree": 0.7191764739632918, "max_bin": 255, "max_depth": -1, "min_child_samples": 73, "num_leaves": 13, "reg_alpha": 0.3383552094629685, "reg_lambda": 1.1129906076406433, "subsample": 0.9783878685095276, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.7191764739632918, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 73, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 13, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.3383552094629685, "reg_lambda": 1.1129906076406433, "subsample": 0.9783878685095276, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.745606; reference `lgb_engineered` (0.744063); delta 0.001543; best trees 939; runtime seconds 16.95.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.001543. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.231726; log loss 0.249630; Brier 0.068449. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_14

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_14", "params": {"colsample_bytree": 0.6489502246662009, "max_bin": 255, "max_depth": -1, "min_child_samples": 61, "num_leaves": 15, "reg_alpha": 1.6993246668017472, "reg_lambda": 0.2174410134760038, "subsample": 0.9877070624071099, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.6489502246662009, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 61, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 15, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 1.6993246668017472, "reg_lambda": 0.2174410134760038, "subsample": 0.9877070624071099, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.745436; reference `lgb_engineered` (0.744063); delta 0.001373; best trees 746; runtime seconds 14.96.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.001373. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.232833; log loss 0.249515; Brier 0.068413. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_15

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_15", "params": {"colsample_bytree": 0.6846068413999578, "max_bin": 255, "max_depth": -1, "min_child_samples": 89, "num_leaves": 21, "reg_alpha": 3.687185564401245, "reg_lambda": 2.1323824335960286, "subsample": 0.961965333135664, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.6846068413999578, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 89, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 21, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 3.687185564401245, "reg_lambda": 2.1323824335960286, "subsample": 0.961965333135664, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.747151; reference `lgb_engineered` (0.744063); delta 0.003088; best trees 844; runtime seconds 19.16.

**CV:** pooled AUC 0.757328; fold AUCs `[0.7514156817480501, 0.7600112588747114, 0.7574728751267328, 0.7562619228374088, 0.7616778723031425]`; fold tree counts `[590, 639, 523, 768, 456]`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.003088. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.237033; log loss 0.249067; Brier 0.068260. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Retained in the first-pass public-scored ensemble (confirmed public AUC 0.7654). This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_16

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_16", "params": {"colsample_bytree": 0.6148105309759075, "max_bin": 255, "max_depth": -1, "min_child_samples": 161, "num_leaves": 19, "reg_alpha": 5.253642888313459, "reg_lambda": 0.751447868942907, "subsample": 0.999529777296887, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.6148105309759075, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 161, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 19, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 5.253642888313459, "reg_lambda": 0.751447868942907, "subsample": 0.999529777296887, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.745213; reference `lgb_engineered` (0.744063); delta 0.001150; best trees 544; runtime seconds 14.01.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.001150. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.234888; log loss 0.249421; Brier 0.068370. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_17

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_17", "params": {"colsample_bytree": 0.6887299521210465, "max_bin": 255, "max_depth": -1, "min_child_samples": 126, "num_leaves": 32, "reg_alpha": 1.9062509287974798, "reg_lambda": 1.2958348142896836, "subsample": 0.931150306878146, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.6887299521210465, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 126, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 32, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 1.9062509287974798, "reg_lambda": 1.2958348142896836, "subsample": 0.931150306878146, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.745560; reference `lgb_engineered` (0.744063); delta 0.001497; best trees 561; runtime seconds 20.28.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.001497. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.236120; log loss 0.249467; Brier 0.068345. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_18

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `extended` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "extended", "groups": true, "kind": "lgb", "name": "lgb_tune_18", "params": {"colsample_bytree": 0.6380710940932686, "max_bin": 255, "max_depth": -1, "min_child_samples": 73, "num_leaves": 21, "reg_alpha": 0.8430223434949234, "reg_lambda": 7.012900547344847, "subsample": 0.9932795302337665, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.6380710940932686, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 73, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 21, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.8430223434949234, "reg_lambda": 7.012900547344847, "subsample": 0.9932795302337665, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.740470; reference `lgb_engineered` (0.744063); delta -0.003593; best trees 373; runtime seconds 14.77.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.003593. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.229514; log loss 0.250884; Brier 0.068677. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_19

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_19", "params": {"colsample_bytree": 0.7485195977745238, "max_bin": 63, "max_depth": -1, "min_child_samples": 87, "num_leaves": 16, "reg_alpha": 8.836681679932243, "reg_lambda": 1.4293683811585762, "subsample": 0.8392543286099333, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.7485195977745238, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 63, "max_depth": -1, "min_child_samples": 87, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 16, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 8.836681679932243, "reg_lambda": 1.4293683811585762, "subsample": 0.8392543286099333, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.743381; reference `lgb_engineered` (0.744063); delta -0.000682; best trees 567; runtime seconds 15.27.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.000682. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.233739; log loss 0.249854; Brier 0.068416. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_20

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_20", "params": {"colsample_bytree": 0.6966732598524357, "max_bin": 255, "max_depth": -1, "min_child_samples": 51, "num_leaves": 25, "reg_alpha": 0.1442947960154403, "reg_lambda": 0.31190183790323456, "subsample": 0.9213050927267354, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.6966732598524357, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 51, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 25, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 0.1442947960154403, "reg_lambda": 0.31190183790323456, "subsample": 0.9213050927267354, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.745865; reference `lgb_engineered` (0.744063); delta 0.001802; best trees 561; runtime seconds 18.13.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.001802. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.233172; log loss 0.249520; Brier 0.068406. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_21

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_21", "params": {"colsample_bytree": 0.742825268226029, "max_bin": 255, "max_depth": -1, "min_child_samples": 92, "num_leaves": 17, "reg_alpha": 2.7972741874288203, "reg_lambda": 7.9483221299740014, "subsample": 0.9793438469230858, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.742825268226029, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 92, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 17, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 2.7972741874288203, "reg_lambda": 7.9483221299740014, "subsample": 0.9793438469230858, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.745921; reference `lgb_engineered` (0.744063); delta 0.001858; best trees 821; runtime seconds 22.79.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.001858. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.234650; log loss 0.249369; Brier 0.068353. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_22

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_22", "params": {"colsample_bytree": 0.7485499123045329, "max_bin": 255, "max_depth": -1, "min_child_samples": 105, "num_leaves": 21, "reg_alpha": 2.16467625438755, "reg_lambda": 4.911744732892914, "subsample": 0.9704195474219368, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.7485499123045329, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 105, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 21, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 2.16467625438755, "reg_lambda": 4.911744732892914, "subsample": 0.9704195474219368, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.746107; reference `lgb_engineered` (0.744063); delta 0.002044; best trees 695; runtime seconds 20.76.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.002044. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.234021; log loss 0.249400; Brier 0.068388. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / lgb_tune_23

**Hypothesis:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**How:** `lgb` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_tune_23", "params": {"colsample_bytree": 0.7861038803344867, "max_bin": 63, "max_depth": -1, "min_child_samples": 123, "num_leaves": 27, "reg_alpha": 3.88832071957301, "reg_lambda": 7.902003345019391, "subsample": 0.992629081235298, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.7861038803344867, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 63, "max_depth": -1, "min_child_samples": 123, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 27, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 3.88832071957301, "reg_lambda": 7.902003345019391, "subsample": 0.992629081235298, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.743351; reference `lgb_engineered` (0.744063); delta -0.000712; best trees 428; runtime seconds 16.05.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.000712. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.233156; log loss 0.249948; Brier 0.068450. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / cat_depth4

**Hypothesis:** Native categorical learning and a different boosting implementation may outperform the LightGBM family. Compare depths 4–7 and leaf regularization to control capacity.

**How:** `cat` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "kind": "cat", "name": "cat_depth4", "params": {"depth": 4, "l2_leaf_reg": 5, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 4, "eval_metric": "AUC", "iterations": 3000, "l2_leaf_reg": 5, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 150, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.748959; reference `cat_depth5` (0.747660); delta 0.001299; best trees 1828; runtime seconds 163.20.

**CV:** pooled AUC 0.759728; fold AUCs `[0.7548125890433909, 0.7617443827000072, 0.7597617401977121, 0.7584493962490403, 0.763915217306999]`; fold tree counts `[1404, 1142, 1441, 1723, 1395]`.

**Parent comparison:** `cat_depth5` AUC 0.747660; delta 0.001299. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.236405; log loss 0.248420; Brier 0.068200. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Advanced to five-fold development CV. Depth and regularization were changed jointly, so the depth effect is not perfectly isolated.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / cat_depth5

**Hypothesis:** Native categorical learning and a different boosting implementation may outperform the LightGBM family. Compare depths 4–7 and leaf regularization to control capacity.

**How:** `cat` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "kind": "cat", "name": "cat_depth5", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 3000, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 150, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.747660; reference `cat_depth5` (0.747660); delta 0.000000; best trees 1464; runtime seconds 128.31.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `cat_depth5` AUC 0.747660; delta 0.000000. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.233610; log loss 0.248824; Brier 0.068289. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Depth and regularization were changed jointly, so the depth effect is not perfectly isolated.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / cat_depth6

**Hypothesis:** Native categorical learning and a different boosting implementation may outperform the LightGBM family. Compare depths 4–7 and leaf regularization to control capacity.

**How:** `cat` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "kind": "cat", "name": "cat_depth6", "params": {"depth": 6, "l2_leaf_reg": 8, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 6, "eval_metric": "AUC", "iterations": 3000, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 150, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.747212; reference `cat_depth5` (0.747660); delta -0.000448; best trees 1016; runtime seconds 155.90.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `cat_depth5` AUC 0.747660; delta -0.000448. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.235235; log loss 0.248843; Brier 0.068264. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Depth and regularization were changed jointly, so the depth effect is not perfectly isolated.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / cat_depth7

**Hypothesis:** Native categorical learning and a different boosting implementation may outperform the LightGBM family. Compare depths 4–7 and leaf regularization to control capacity.

**How:** `cat` on `engineered` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "kind": "cat", "name": "cat_depth7", "params": {"depth": 7, "l2_leaf_reg": 12, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 7, "eval_metric": "AUC", "iterations": 3000, "l2_leaf_reg": 12, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 150, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.747337; reference `cat_depth5` (0.747660); delta -0.000322; best trees 932; runtime seconds 162.36.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `cat_depth5` AUC 0.747660; delta -0.000322. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.232882; log loss 0.248873; Brier 0.068317. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Depth and regularization were changed jointly, so the depth effect is not perfectly isolated.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / logistic_0.01

**Hypothesis:** A regularized linear classifier may generalize well or diversify boosted models.

**How:** `logistic` on `extended` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"C": 0.01}`

**Runner settings:** `{"C": 0.01, "categorical": "OneHotEncoder(ignore unknown)", "imputer": "training median + missing indicators", "max_iter": 1000, "scaler": "StandardScaler", "solver": "lbfgs"}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.732960; reference `logistic_0.1` (0.732312); delta 0.000648; best trees None; runtime seconds —.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `logistic_0.1` AUC 0.732312; delta 0.000648. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.216272; log loss 0.252981; Brier 0.069145. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Linear effects may be insufficient for nonlinear score and payment interactions; this is an explanation, not a proven mechanism.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / logistic_0.1

**Hypothesis:** A regularized linear classifier may generalize well or diversify boosted models.

**How:** `logistic` on `extended` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"C": 0.1}`

**Runner settings:** `{"C": 0.1, "categorical": "OneHotEncoder(ignore unknown)", "imputer": "training median + missing indicators", "max_iter": 1000, "scaler": "StandardScaler", "solver": "lbfgs"}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.732312; reference `logistic_0.1` (0.732312); delta 0.000000; best trees None; runtime seconds —.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `logistic_0.1` AUC 0.732312; delta 0.000000. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.217072; log loss 0.253231; Brier 0.069189. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Linear effects may be insufficient for nonlinear score and payment interactions; this is an explanation, not a proven mechanism.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / logistic_1.0

**Hypothesis:** A regularized linear classifier may generalize well or diversify boosted models.

**How:** `logistic` on `extended` features. Source: `improvements/experiment.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"C": 1.0}`

**Runner settings:** `{"C": 1.0, "categorical": "OneHotEncoder(ignore unknown)", "imputer": "training median + missing indicators", "max_iter": 1000, "scaler": "StandardScaler", "solver": "lbfgs"}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.731796; reference `logistic_0.1` (0.732312); delta -0.000516; best trees None; runtime seconds —.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `logistic_0.1` AUC 0.732312; delta -0.000516. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.216324; log loss 0.253448; Brier 0.069237. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Linear effects may be insufficient for nonlinear score and payment interactions; this is an explanation, not a proven mechanism.

**Evidence:** `improvements/artifacts/screen_results.json`.

### pass1 / hgb_10

**Hypothesis:** Native-categorical histogram gradient boosting offers a separate implementation and leaf-complexity tradeoff.

**How:** `hgb` on `engineered` features. Source: `improvements/supplement.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "kind": "hgb", "name": "hgb_10", "params": {"l2_regularization": 15.0, "max_leaf_nodes": 10, "min_samples_leaf": 100}}`

**Runner settings:** `{"l2_regularization": 15.0, "learning_rate": 0.05, "max_iter": 1800, "max_leaf_nodes": 10, "min_samples_leaf": 100, "n_iter_no_change": 50, "random_state": 20261108, "scoring": "roc_auc", "validation_fraction": 0.15}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.741282; reference `hgb_20` (0.741609); delta -0.000327; best trees 383; runtime seconds 10.31.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `hgb_20` AUC 0.741609; delta -0.000327. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.226542; log loss 0.250748; Brier 0.068682. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This family was competitive enough to validate, but did not match CatBoost or tuned LightGBM.

**Evidence:** `improvements/artifacts/supplement_results.json`.

### pass1 / hgb_20

**Hypothesis:** Native-categorical histogram gradient boosting offers a separate implementation and leaf-complexity tradeoff.

**How:** `hgb` on `engineered` features. Source: `improvements/supplement.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "kind": "hgb", "name": "hgb_20", "params": {"l2_regularization": 15.0, "max_leaf_nodes": 20, "min_samples_leaf": 100}}`

**Runner settings:** `{"l2_regularization": 15.0, "learning_rate": 0.05, "max_iter": 1800, "max_leaf_nodes": 20, "min_samples_leaf": 100, "n_iter_no_change": 50, "random_state": 20261108, "scoring": "roc_auc", "validation_fraction": 0.15}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.741609; reference `hgb_20` (0.741609); delta 0.000000; best trees 422; runtime seconds 15.58.

**CV:** pooled AUC 0.753292; fold AUCs `[0.7487858608915573, 0.7555360160327065, 0.7517760648544519, 0.7525390977105045, 0.7576819234244003]`; fold tree counts `[230, 313, 250, 241, 324]`.

**Parent comparison:** `hgb_20` AUC 0.741609; delta 0.000000. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.230458; log loss 0.250708; Brier 0.068615. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Advanced to five-fold development CV. This family was competitive enough to validate, but did not match CatBoost or tuned LightGBM.

**Evidence:** `improvements/artifacts/supplement_results.json`.

### pass1 / hgb_31

**Hypothesis:** Native-categorical histogram gradient boosting offers a separate implementation and leaf-complexity tradeoff.

**How:** `hgb` on `engineered` features. Source: `improvements/supplement.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "kind": "hgb", "name": "hgb_31", "params": {"l2_regularization": 15.0, "max_leaf_nodes": 31, "min_samples_leaf": 100}}`

**Runner settings:** `{"l2_regularization": 15.0, "learning_rate": 0.05, "max_iter": 1800, "max_leaf_nodes": 31, "min_samples_leaf": 100, "n_iter_no_change": 50, "random_state": 20261108, "scoring": "roc_auc", "validation_fraction": 0.15}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.741303; reference `hgb_20` (0.741609); delta -0.000306; best trees 186; runtime seconds 10.45.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `hgb_20` AUC 0.741609; delta -0.000306. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.228703; log loss 0.250619; Brier 0.068617. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. This family was competitive enough to validate, but did not match CatBoost or tuned LightGBM.

**Evidence:** `improvements/artifacts/supplement_results.json`.

### pass1 / spline_0.01

**Hypothesis:** Quantile transforms and smooth univariate splines may recover nonlinear signal with less tree variance.

**How:** `spline` on `engineered` features. Source: `improvements/supplement.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "kind": "spline", "name": "spline_0.01", "params": {"C": 0.01}}`

**Runner settings:** `{"C": 0.01, "imputer": "training median + missing indicators", "include_bias": false, "max_iter": 700, "quantile_distribution": "uniform", "quantiles": 100, "solver": "lbfgs", "spline_degree": 3, "spline_knot_positions": "uniform", "spline_knots": 5}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.736017; reference `spline_0.1` (0.736537); delta -0.000520; best trees 1; runtime seconds 11.01.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `spline_0.1` AUC 0.736537; delta -0.000520. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.220378; log loss 0.251970; Brier 0.068962. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Smooth additive effects remain weaker than the tree models; cross-feature interactions are one plausible missing component.

**Evidence:** `improvements/artifacts/supplement_results.json`.

### pass1 / spline_0.1

**Hypothesis:** Quantile transforms and smooth univariate splines may recover nonlinear signal with less tree variance.

**How:** `spline` on `engineered` features. Source: `improvements/supplement.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "kind": "spline", "name": "spline_0.1", "params": {"C": 0.1}}`

**Runner settings:** `{"C": 0.1, "imputer": "training median + missing indicators", "include_bias": false, "max_iter": 700, "quantile_distribution": "uniform", "quantiles": 100, "solver": "lbfgs", "spline_degree": 3, "spline_knot_positions": "uniform", "spline_knots": 5}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.736537; reference `spline_0.1` (0.736537); delta 0.000000; best trees 1; runtime seconds 12.76.

**CV:** pooled AUC 0.748304; fold AUCs `[0.7448702137931862, 0.7521273883011915, 0.748449861626878, 0.7462556527197185, 0.7498400485761109]`; fold tree counts `[1, 1, 1, 1, 1]`.

**Parent comparison:** `spline_0.1` AUC 0.736537; delta 0.000000. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.223733; log loss 0.251849; Brier 0.068877. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Advanced to five-fold development CV. Smooth additive effects remain weaker than the tree models; cross-feature interactions are one plausible missing component.

**Evidence:** `improvements/artifacts/supplement_results.json`.

### pass1 / spline_1.0

**Hypothesis:** Quantile transforms and smooth univariate splines may recover nonlinear signal with less tree variance.

**How:** `spline` on `engineered` features. Source: `improvements/supplement.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "kind": "spline", "name": "spline_1.0", "params": {"C": 1.0}}`

**Runner settings:** `{"C": 1.0, "imputer": "training median + missing indicators", "include_bias": false, "max_iter": 700, "quantile_distribution": "uniform", "quantiles": 100, "solver": "lbfgs", "spline_degree": 3, "spline_knot_positions": "uniform", "spline_knots": 5}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.735930; reference `spline_0.1` (0.736537); delta -0.000607; best trees 1; runtime seconds 16.58.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `spline_0.1` AUC 0.736537; delta -0.000607. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.224158; log loss 0.252068; Brier 0.068902. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Smooth additive effects remain weaker than the tree models; cross-feature interactions are one plausible missing component.

**Evidence:** `improvements/artifacts/supplement_results.json`.

### pass1 / lgb_engineered_groups

**Hypothesis:** Fold-fitted category frequencies and group-relative financial/score values may normalize peer groups.

**How:** `lgb` on `engineered` features. Source: `improvements/supplement.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_engineered_groups", "params": {"colsample_bytree": 1.0, "max_bin": 127, "max_depth": -1, "min_child_samples": 200, "num_leaves": 16, "reg_alpha": 1.0, "reg_lambda": 20, "subsample": 0.9, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 1.0, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 127, "max_depth": -1, "min_child_samples": 200, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 16, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 1.0, "reg_lambda": 20, "subsample": 0.9, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.745036; reference `lgb_engineered` (0.744063); delta 0.000973; best trees 681; runtime seconds 20.72.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.000973. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.233595; log loss 0.249615; Brier 0.068404. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Several settings change together; the result does not isolate a single causal mechanism.

**Evidence:** `improvements/artifacts/supplement_results.json`.

### pass1 / lgb_lean

**Hypothesis:** A compact feature subset may remove redundant interactions and reduce variance.

**How:** `lgb` on `lean` features. Source: `improvements/refine.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "lean", "kind": "lgb", "name": "lgb_lean", "params": {"colsample_bytree": 1.0, "max_bin": 127, "max_depth": -1, "min_child_samples": 200, "num_leaves": 16, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.9, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 1.0, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 127, "max_depth": -1, "min_child_samples": 200, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 16, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.9, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.743296; reference `lgb_engineered` (0.744063); delta -0.000767; best trees 560; runtime seconds 13.21.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.000767. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.231250; log loss 0.250085; Brier 0.068523. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. These LightGBM variants did not beat its engineered feature set; feature selection is model dependent.

**Evidence:** `improvements/artifacts/refine_results.json`.

### pass1 / lgb_scores

**Hypothesis:** A compact feature subset may remove redundant interactions and reduce variance.

**How:** `lgb` on `scores` features. Source: `improvements/refine.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "scores", "kind": "lgb", "name": "lgb_scores", "params": {"colsample_bytree": 1.0, "max_bin": 127, "max_depth": -1, "min_child_samples": 200, "num_leaves": 16, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.9, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 1.0, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 127, "max_depth": -1, "min_child_samples": 200, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 16, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.9, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.738912; reference `lgb_engineered` (0.744063); delta -0.005151; best trees 670; runtime seconds 11.93.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta -0.005151. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.225592; log loss 0.251426; Brier 0.068801. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. These LightGBM variants did not beat its engineered feature set; feature selection is model dependent.

**Evidence:** `improvements/artifacts/refine_results.json`.

### pass1 / lgb_small_8

**Hypothesis:** Shallower trees with strong regularization may improve generalization.

**How:** `lgb` on `engineered` features. Source: `improvements/refine.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "kind": "lgb", "name": "lgb_small_8", "params": {"colsample_bytree": 1.0, "max_bin": 255, "max_depth": -1, "min_child_samples": 200, "num_leaves": 8, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.9, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 1.0, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 200, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 8, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.9, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.745126; reference `lgb_engineered` (0.744063); delta 0.001063; best trees 1371; runtime seconds 18.94.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.001063. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.231659; log loss 0.249828; Brier 0.068487. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Several settings change together; the result does not isolate a single causal mechanism.

**Evidence:** `improvements/artifacts/refine_results.json`.

### pass1 / lgb_small_12

**Hypothesis:** Shallower trees with strong regularization may improve generalization.

**How:** `lgb` on `engineered` features. Source: `improvements/refine.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "kind": "lgb", "name": "lgb_small_12", "params": {"colsample_bytree": 1.0, "max_bin": 255, "max_depth": -1, "min_child_samples": 200, "num_leaves": 12, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.9, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 1.0, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 200, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 12, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.9, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.745416; reference `lgb_engineered` (0.744063); delta 0.001352; best trees 839; runtime seconds 14.93.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.001352. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.233410; log loss 0.249592; Brier 0.068410. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Several settings change together; the result does not isolate a single causal mechanism.

**Evidence:** `improvements/artifacts/refine_results.json`.

### pass1 / lgb_weight_2.0

**Hypothesis:** Increasing positive-class weight may prioritize minority-class ranking.

**How:** `lgb` on `engineered` features. Source: `improvements/refine.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "kind": "lgb", "name": "lgb_weight_2.0", "params": {"colsample_bytree": 1.0, "max_bin": 127, "max_depth": -1, "min_child_samples": 200, "num_leaves": 16, "reg_alpha": 1.0, "reg_lambda": 20.0, "scale_pos_weight": 2.0, "subsample": 0.9, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 1.0, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 127, "max_depth": -1, "min_child_samples": 200, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 16, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 1.0, "reg_lambda": 20.0, "scale_pos_weight": 2.0, "subsample": 0.9, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.744176; reference `lgb_engineered` (0.744063); delta 0.000112; best trees 672; runtime seconds 13.32.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.000112. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.230808; log loss 0.267019; Brier 0.073826. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Class weighting did not beat the best unweighted candidates; it can also shift probability calibration. Imbalance alone is not evidence weighting will help AUC.

**Evidence:** `improvements/artifacts/refine_results.json`.

### pass1 / lgb_weight_5.0

**Hypothesis:** Increasing positive-class weight may prioritize minority-class ranking.

**How:** `lgb` on `engineered` features. Source: `improvements/refine.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "engineered", "kind": "lgb", "name": "lgb_weight_5.0", "params": {"colsample_bytree": 1.0, "max_bin": 127, "max_depth": -1, "min_child_samples": 200, "num_leaves": 16, "reg_alpha": 1.0, "reg_lambda": 20.0, "scale_pos_weight": 5.0, "subsample": 0.9, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 1.0, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 127, "max_depth": -1, "min_child_samples": 200, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 16, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 1.0, "reg_lambda": 20.0, "scale_pos_weight": 5.0, "subsample": 0.9, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.744965; reference `lgb_engineered` (0.744063); delta 0.000902; best trees 673; runtime seconds 13.27.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_engineered` AUC 0.744063; delta 0.000902. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.228511; log loss 0.359024; Brier 0.107748. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Class weighting did not beat the best unweighted candidates; it can also shift probability calibration. Imbalance alone is not evidence weighting will help AUC.

**Evidence:** `improvements/artifacts/refine_results.json`.

### pass1 / cat_raw

**Hypothesis:** Test whether CatBoost can learn sufficient relationships from the original columns without derived ratios.

**How:** `cat` on `raw` features. Source: `improvements/refine.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "raw", "kind": "cat", "name": "cat_raw", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 3000, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 150, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.741656; reference `cat_depth5` (0.747660); delta -0.006004; best trees 1285; runtime seconds 96.96.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `cat_depth5` AUC 0.747660; delta -0.006004. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.226727; log loss 0.250422; Brier 0.068661. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Lower AUC supports retaining derived financial and score features for this model.

**Evidence:** `improvements/artifacts/refine_results.json`.

### pass1 / cat_lean

**Hypothesis:** A compact set of strong financial/score features may reduce distracting split opportunities.

**How:** `cat` on `lean` features. Source: `improvements/refine.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "lean", "kind": "cat", "name": "cat_lean", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 3000, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 150, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.748493; reference `cat_depth5` (0.747660); delta 0.000833; best trees 1670; runtime seconds 170.87.

**CV:** pooled AUC 0.760790; fold AUCs `[0.7561397974146384, 0.7624387853469601, 0.7601855734989755, 0.7608974525116583, 0.7643846403543672]`; fold tree counts `[1396, 1075, 1529, 2017, 1666]`.

**Parent comparison:** `cat_depth5` AUC 0.747660; delta 0.000833. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.233994; log loss 0.248728; Brier 0.068302. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Retained in the first-pass public-scored ensemble (confirmed public AUC 0.7654). The compact depth-5 representation won development CV; deeper trees did not help overall. The feature explanation is plausible, not causal proof.

**Evidence:** `improvements/artifacts/refine_results.json`.

### pass1 / lgb_top_25

**Hypothesis:** Remove weaker original/derived columns using development-only gain rankings.

**How:** `lgb` on `engineered` features. Source: `improvements/select_features.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"columns": ["EXT_MEAN", "ORGANIZATION_TYPE", "AMT_CREDIT_OVER_AMT_ANNUITY", "OCCUPATION_TYPE", "EXT_SUM", "EXT_MIN", "EXT_SOURCE_3", "AMT_CREDIT_OVER_AMT_GOODS_PRICE", "EXT_2_3_PRODUCT", "DAYS_EMPLOYED", "AMT_ANNUITY_OVER_AMT_GOODS_PRICE", "DAYS_ID_PUBLISH", "AGE_AT_EMPLOYMENT", "CAR_OVER_AGE", "CREDIT_TERM", "EXT_STD", "CREDIT_GOODS_DIFF", "EMPLOYED_YEARS", "DAYS_LAST_PHONE_CHANGE", "EXT_MEAN_TIMES_TERM", "DAYS_EMPLOYED_OVER_BIRTH", "EXT_MAX", "DAYS_REGISTRATION", "DAYS_REGISTRATION_OVER_BIRTH", "REGION_POPULATION_RELATIVE"], "features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_top_25", "params": {"colsample_bytree": 0.6846068413999578, "max_bin": 255, "max_depth": -1, "min_child_samples": 89, "num_leaves": 21, "reg_alpha": 3.687185564401245, "reg_lambda": 2.1323824335960286, "subsample": 0.961965333135664, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.6846068413999578, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 89, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 21, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 3.687185564401245, "reg_lambda": 2.1323824335960286, "subsample": 0.961965333135664, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.738165; reference `lgb_tune_15` (0.747151); delta -0.008986; best trees 430; runtime seconds 13.52.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_tune_15` AUC 0.747151; delta -0.008986. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.231408; log loss 0.251091; Brier 0.068599. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Pruning failed to improve the tuned reference; correlated weak features can still help an ensemble of trees.

**Evidence:** `improvements/artifacts/feature_selection_results.json`.

### pass1 / lgb_top_40

**Hypothesis:** Remove weaker original/derived columns using development-only gain rankings.

**How:** `lgb` on `engineered` features. Source: `improvements/select_features.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"columns": ["EXT_MEAN", "ORGANIZATION_TYPE", "AMT_CREDIT_OVER_AMT_ANNUITY", "OCCUPATION_TYPE", "EXT_SUM", "EXT_MIN", "EXT_SOURCE_3", "AMT_CREDIT_OVER_AMT_GOODS_PRICE", "EXT_2_3_PRODUCT", "DAYS_EMPLOYED", "AMT_ANNUITY_OVER_AMT_GOODS_PRICE", "DAYS_ID_PUBLISH", "AGE_AT_EMPLOYMENT", "CAR_OVER_AGE", "CREDIT_TERM", "EXT_STD", "CREDIT_GOODS_DIFF", "EMPLOYED_YEARS", "DAYS_LAST_PHONE_CHANGE", "EXT_MEAN_TIMES_TERM", "DAYS_EMPLOYED_OVER_BIRTH", "EXT_MAX", "DAYS_REGISTRATION", "DAYS_REGISTRATION_OVER_BIRTH", "REGION_POPULATION_RELATIVE", "DAYS_BIRTH", "CREDIT_GOODS_DIFF_RATIO", "EXT_2_3_DIFF", "AGE_YEARS", "EXT_SOURCE_2", "EXT_MEAN_OVER_AGE", "PHONE_OVER_EMPLOYED", "CODE_GENDER", "DAYS_ID_PUBLISH_OVER_BIRTH", "ANNUITY_PER_PERSON", "DAYS_LAST_PHONE_CHANGE_OVER_BIRTH", "AMT_GOODS_PRICE", "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY", "EDUCATION_RANK", "CREDIT_PER_PERSON"], "features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_top_40", "params": {"colsample_bytree": 0.6846068413999578, "max_bin": 255, "max_depth": -1, "min_child_samples": 89, "num_leaves": 21, "reg_alpha": 3.687185564401245, "reg_lambda": 2.1323824335960286, "subsample": 0.961965333135664, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.6846068413999578, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 89, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 21, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 3.687185564401245, "reg_lambda": 2.1323824335960286, "subsample": 0.961965333135664, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.742890; reference `lgb_tune_15` (0.747151); delta -0.004262; best trees 470; runtime seconds 18.06.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_tune_15` AUC 0.747151; delta -0.004262. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.232498; log loss 0.250046; Brier 0.068470. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Pruning failed to improve the tuned reference; correlated weak features can still help an ensemble of trees.

**Evidence:** `improvements/artifacts/feature_selection_results.json`.

### pass1 / lgb_top_55

**Hypothesis:** Remove weaker original/derived columns using development-only gain rankings.

**How:** `lgb` on `engineered` features. Source: `improvements/select_features.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"columns": ["EXT_MEAN", "ORGANIZATION_TYPE", "AMT_CREDIT_OVER_AMT_ANNUITY", "OCCUPATION_TYPE", "EXT_SUM", "EXT_MIN", "EXT_SOURCE_3", "AMT_CREDIT_OVER_AMT_GOODS_PRICE", "EXT_2_3_PRODUCT", "DAYS_EMPLOYED", "AMT_ANNUITY_OVER_AMT_GOODS_PRICE", "DAYS_ID_PUBLISH", "AGE_AT_EMPLOYMENT", "CAR_OVER_AGE", "CREDIT_TERM", "EXT_STD", "CREDIT_GOODS_DIFF", "EMPLOYED_YEARS", "DAYS_LAST_PHONE_CHANGE", "EXT_MEAN_TIMES_TERM", "DAYS_EMPLOYED_OVER_BIRTH", "EXT_MAX", "DAYS_REGISTRATION", "DAYS_REGISTRATION_OVER_BIRTH", "REGION_POPULATION_RELATIVE", "DAYS_BIRTH", "CREDIT_GOODS_DIFF_RATIO", "EXT_2_3_DIFF", "AGE_YEARS", "EXT_SOURCE_2", "EXT_MEAN_OVER_AGE", "PHONE_OVER_EMPLOYED", "CODE_GENDER", "DAYS_ID_PUBLISH_OVER_BIRTH", "ANNUITY_PER_PERSON", "DAYS_LAST_PHONE_CHANGE_OVER_BIRTH", "AMT_GOODS_PRICE", "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY", "EDUCATION_RANK", "CREDIT_PER_PERSON", "OWN_CAR_AGE", "EXT_SOURCE_1", "INCOME_AFTER_ANNUITY", "INCOME_PER_PERSON", "EXT_1_2_PRODUCT", "AMT_ANNUITY", "AMT_INCOME_TOTAL_OVER_AMT_GOODS_PRICE", "AMT_INCOME_TOTAL_OVER_AMT_CREDIT", "EXT_1_2_DIFF", "AMT_REQ_CREDIT_BUREAU_YEAR", "BUREAU_SUM", "NAME_FAMILY_STATUS", "NAME_EDUCATION_TYPE", "REGION_RATING_CLIENT", "AMT_CREDIT"], "features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_top_55", "params": {"colsample_bytree": 0.6846068413999578, "max_bin": 255, "max_depth": -1, "min_child_samples": 89, "num_leaves": 21, "reg_alpha": 3.687185564401245, "reg_lambda": 2.1323824335960286, "subsample": 0.961965333135664, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.6846068413999578, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 89, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 21, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 3.687185564401245, "reg_lambda": 2.1323824335960286, "subsample": 0.961965333135664, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.745922; reference `lgb_tune_15` (0.747151); delta -0.001229; best trees 727; runtime seconds 29.13.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_tune_15` AUC 0.747151; delta -0.001229. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.235832; log loss 0.249398; Brier 0.068345. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. Pruning failed to improve the tuned reference; correlated weak features can still help an ensemble of trees.

**Evidence:** `improvements/artifacts/feature_selection_results.json`.

### pass1 / lgb_top_70

**Hypothesis:** Remove weaker original/derived columns using development-only gain rankings.

**How:** `lgb` on `engineered` features. Source: `improvements/select_features.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"columns": ["EXT_MEAN", "ORGANIZATION_TYPE", "AMT_CREDIT_OVER_AMT_ANNUITY", "OCCUPATION_TYPE", "EXT_SUM", "EXT_MIN", "EXT_SOURCE_3", "AMT_CREDIT_OVER_AMT_GOODS_PRICE", "EXT_2_3_PRODUCT", "DAYS_EMPLOYED", "AMT_ANNUITY_OVER_AMT_GOODS_PRICE", "DAYS_ID_PUBLISH", "AGE_AT_EMPLOYMENT", "CAR_OVER_AGE", "CREDIT_TERM", "EXT_STD", "CREDIT_GOODS_DIFF", "EMPLOYED_YEARS", "DAYS_LAST_PHONE_CHANGE", "EXT_MEAN_TIMES_TERM", "DAYS_EMPLOYED_OVER_BIRTH", "EXT_MAX", "DAYS_REGISTRATION", "DAYS_REGISTRATION_OVER_BIRTH", "REGION_POPULATION_RELATIVE", "DAYS_BIRTH", "CREDIT_GOODS_DIFF_RATIO", "EXT_2_3_DIFF", "AGE_YEARS", "EXT_SOURCE_2", "EXT_MEAN_OVER_AGE", "PHONE_OVER_EMPLOYED", "CODE_GENDER", "DAYS_ID_PUBLISH_OVER_BIRTH", "ANNUITY_PER_PERSON", "DAYS_LAST_PHONE_CHANGE_OVER_BIRTH", "AMT_GOODS_PRICE", "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY", "EDUCATION_RANK", "CREDIT_PER_PERSON", "OWN_CAR_AGE", "EXT_SOURCE_1", "INCOME_AFTER_ANNUITY", "INCOME_PER_PERSON", "EXT_1_2_PRODUCT", "AMT_ANNUITY", "AMT_INCOME_TOTAL_OVER_AMT_GOODS_PRICE", "AMT_INCOME_TOTAL_OVER_AMT_CREDIT", "EXT_1_2_DIFF", "AMT_REQ_CREDIT_BUREAU_YEAR", "BUREAU_SUM", "NAME_FAMILY_STATUS", "NAME_EDUCATION_TYPE", "REGION_RATING_CLIENT", "AMT_CREDIT", "EXT_1_3_DIFF", "AMT_REQ_CREDIT_BUREAU_QRT", "EXT_PRODUCT", "NAME_CONTRACT_TYPE", "CONTACT_FLAGS_SUM", "EXT_1_3_PRODUCT", "AMT_INCOME_TOTAL", "FLAG_WORK_PHONE", "MISSING_COUNT", "AMT_REQ_CREDIT_BUREAU_MON", "NAME_HOUSING_TYPE", "NAME_INCOME_TYPE", "CNT_FAM_MEMBERS", "CHILDREN_FRACTION", "CNT_CHILDREN"], "features": "engineered", "groups": true, "kind": "lgb", "name": "lgb_top_70", "params": {"colsample_bytree": 0.6846068413999578, "max_bin": 255, "max_depth": -1, "min_child_samples": 89, "num_leaves": 21, "reg_alpha": 3.687185564401245, "reg_lambda": 2.1323824335960286, "subsample": 0.961965333135664, "subsample_freq": 1}}`

**Runner settings:** `{"colsample_bytree": 0.6846068413999578, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 89, "n_estimators": 3500, "n_jobs": 4, "num_leaves": 21, "objective": "binary", "patience": 150, "random_state": 20261108, "reg_alpha": 3.687185564401245, "reg_lambda": 2.1323824335960286, "subsample": 0.961965333135664, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.746336; reference `lgb_tune_15` (0.747151); delta -0.000815; best trees 709; runtime seconds 31.65.

**CV:** pooled AUC 0.756960; fold AUCs `[0.7509011609473633, 0.759740689529022, 0.7569456564594452, 0.7556996077480901, 0.7616753946629475]`; fold tree counts `[430, 562, 491, 494, 424]`.

**Parent comparison:** `lgb_tune_15` AUC 0.747151; delta -0.000815. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.235382; log loss 0.249296; Brier 0.068334. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Advanced to five-fold development CV. Pruning failed to improve the tuned reference; correlated weak features can still help an ensemble of trees.

**Evidence:** `improvements/artifacts/feature_selection_results.json`.

### pass1 / cat_lean_depth4

**Hypothesis:** A compact set of strong financial/score features may reduce distracting split opportunities.

**How:** `cat` on `lean` features. Source: `improvements/refine_cat.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "lean", "kind": "cat", "name": "cat_lean_depth4", "params": {"depth": 4, "l2_leaf_reg": 5, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 4, "eval_metric": "AUC", "iterations": 3000, "l2_leaf_reg": 5, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 150, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.747615; reference `cat_lean` (0.748493); delta -0.000878; best trees 1494; runtime seconds 158.99.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `cat_lean` AUC 0.748493; delta -0.000878. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.234843; log loss 0.248733; Brier 0.068247. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Not advanced individually; retained as a screening/ablation result. The compact depth-5 representation won development CV; deeper trees did not help overall. The feature explanation is plausible, not causal proof.

**Evidence:** `improvements/artifacts/cat_refine_results.json`.

### pass1 / cat_lean_depth6

**Hypothesis:** A compact set of strong financial/score features may reduce distracting split opportunities.

**How:** `cat` on `lean` features. Source: `improvements/refine_cat.py`. Rationale origin: Retrospective reconstruction from retained source, not a contemporaneous preregistration.

**Configuration:** `{"features": "lean", "kind": "cat", "name": "cat_lean_depth6", "params": {"depth": 6, "l2_leaf_reg": 12, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 6, "eval_metric": "AUC", "iterations": 3000, "l2_leaf_reg": 12, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 150, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.748028; reference `cat_lean` (0.748493); delta -0.000464; best trees 1395; runtime seconds 188.16.

**CV:** pooled AUC 0.760148; fold AUCs `[0.7556287236286321, 0.761300432718767, 0.7589825960363566, 0.75967152048028, 0.7652528916574625]`; fold tree counts `[1315, 1017, 1174, 1500, 1357]`.

**Parent comparison:** `cat_lean` AUC 0.748493; delta -0.000464. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.234245; log loss 0.248827; Brier 0.068319. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Advanced to five-fold development CV. The compact depth-5 representation won development CV; deeper trees did not help overall. The feature explanation is plausible, not causal proof.

**Evidence:** `improvements/artifacts/cat_refine_results.json`.

### pass2 / r2_cat_baseline

**Hypothesis:** Reproduce the first-pass compact CatBoost to verify implementation equivalence.

**How:** `cat` on `lean` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "Reproduce the first-pass compact CatBoost to verify implementation equivalence.", "kind": "cat", "max_iterations": 3000, "name": "r2_cat_baseline", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}, "patience": 150}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 3000, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 150, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.748493; reference `pass1_cat_lean_inner` (0.748493); delta 0.000000; best trees 1670; runtime seconds 85.46.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `pass1_cat_lean_inner` AUC —; delta —. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.233994; log loss 0.248728; Brier 0.068302. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Implementation/stopping-budget control; used to interpret other trials, not claimed as a new recipe. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_baseline.json`.

### pass2 / r2_cat_risk

**Hypothesis:** Smooth score summaries and score/age/term interactions may help shallow trees model risk.

**How:** `cat` on `risk` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "risk", "hypothesis": "Smooth score summaries and score/age/term interactions may help shallow trees model risk.", "kind": "cat", "name": "r2_cat_risk", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.746813; reference `pass1_cat_lean_inner` (0.748493); delta -0.001680; best trees 1493; runtime seconds 146.70.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_budget_control` AUC 0.748493; delta -0.001680. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.232027; log loss 0.249195; Brier 0.068410. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_risk.json`.

### pass2 / r2_cat_finance

**Hypothesis:** Payment burden, per-adult amounts and hypothetical payment-period rates may expose financial structure.

**How:** `cat` on `finance` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "finance", "hypothesis": "Payment burden, per-adult amounts and hypothetical payment-period rates may expose financial structure.", "kind": "cat", "name": "r2_cat_finance", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.749082; reference `pass1_cat_lean_inner` (0.748493); delta 0.000590; best trees 1841; runtime seconds 177.35.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_budget_control` AUC 0.748493; delta 0.000590. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.236951; log loss 0.248491; Brier 0.068227. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_finance.json`.

### pass2 / r2_cat_missing

**Hypothesis:** Joint missing-score patterns and coarse organization groups may expose data-collection segments.

**How:** `cat` on `missing` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "missing", "hypothesis": "Joint missing-score patterns and coarse organization groups may expose data-collection segments.", "kind": "cat", "name": "r2_cat_missing", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.747589; reference `pass1_cat_lean_inner` (0.748493); delta -0.000903; best trees 1541; runtime seconds 185.97.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_budget_control` AUC 0.748493; delta -0.000903. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.233370; log loss 0.248945; Brier 0.068347. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_missing.json`.

### pass2 / r2_cat_combined

**Hypothesis:** The three targeted feature families may be complementary; their combination may also add noise.

**How:** `cat` on `combined` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "combined", "hypothesis": "The three targeted feature families may be complementary; their combination may also add noise.", "kind": "cat", "name": "r2_cat_combined", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.748670; reference `pass1_cat_lean_inner` (0.748493); delta 0.000177; best trees 1576; runtime seconds 196.55.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_budget_control` AUC 0.748493; delta 0.000177. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.232529; log loss 0.248862; Brier 0.068393. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_combined.json`.

### pass2 / r2_cat_slow

**Hypothesis:** Smaller boosting steps may improve the bias/variance tradeoff.

**How:** `cat` on `lean` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "Smaller boosting steps may improve the bias/variance tradeoff.", "kind": "cat", "max_iterations": 5000, "name": "r2_cat_slow", "params": {"depth": 5, "l2_leaf_reg": 8, "learning_rate": 0.025, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 5000, "l2_leaf_reg": 8, "learning_rate": 0.025, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.748572; reference `pass1_cat_lean_inner` (0.748493); delta 0.000079; best trees 2392; runtime seconds 232.24.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_budget_control` AUC 0.748493; delta 0.000079. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.234310; log loss 0.248606; Brier 0.068270. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_slow.json`.

### pass2 / r2_cat_strong_l2

**Hypothesis:** Stronger leaf shrinkage may reduce overfitting in sparse categorical groups.

**How:** `cat` on `lean` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "Stronger leaf shrinkage may reduce overfitting in sparse categorical groups.", "kind": "cat", "max_iterations": 5000, "name": "r2_cat_strong_l2", "params": {"depth": 5, "l2_leaf_reg": 30, "random_strength": 1.0}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 5000, "l2_leaf_reg": 30, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 1.0, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.747663; reference `pass1_cat_lean_inner` (0.748493); delta -0.000829; best trees 1829; runtime seconds 179.30.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_budget_control` AUC 0.748493; delta -0.000829. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.232898; log loss 0.248950; Brier 0.068354. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_strong_l2.json`.

### pass2 / r2_cat_weak_l2

**Hypothesis:** Less shrinkage may recover useful signal suppressed by the first-pass settings.

**How:** `cat` on `lean` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "Less shrinkage may recover useful signal suppressed by the first-pass settings.", "kind": "cat", "max_iterations": 5000, "name": "r2_cat_weak_l2", "params": {"depth": 5, "l2_leaf_reg": 2, "random_strength": 0.1}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 5000, "l2_leaf_reg": 2, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.1, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.747569; reference `pass1_cat_lean_inner` (0.748493); delta -0.000924; best trees 1276; runtime seconds 150.60.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_budget_control` AUC 0.748493; delta -0.000924. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.233943; log loss 0.248922; Brier 0.068320. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_weak_l2.json`.

### pass2 / r2_cat_onehot10

**Hypothesis:** One-hot splits for low-cardinality categories may outperform ordered target statistics.

**How:** `cat` on `lean` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "One-hot splits for low-cardinality categories may outperform ordered target statistics.", "kind": "cat", "max_iterations": 5000, "name": "r2_cat_onehot10", "params": {"depth": 5, "l2_leaf_reg": 8, "one_hot_max_size": 10, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 5000, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "one_hot_max_size": 10, "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.748004; reference `pass1_cat_lean_inner` (0.748493); delta -0.000489; best trees 1299; runtime seconds 96.05.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_budget_control` AUC 0.748493; delta -0.000489. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.234043; log loss 0.248798; Brier 0.068305. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_onehot10.json`.

### pass2 / r2_cat_onehot64

**Hypothesis:** One-hot splits for every raw category may avoid noisy target statistics, at the cost of expressiveness.

**How:** `cat` on `lean` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "One-hot splits for every raw category may avoid noisy target statistics, at the cost of expressiveness.", "kind": "cat", "max_iterations": 5000, "name": "r2_cat_onehot64", "params": {"depth": 5, "l2_leaf_reg": 8, "one_hot_max_size": 64, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 5000, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "one_hot_max_size": 64, "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.748193; reference `pass1_cat_lean_inner` (0.748493); delta -0.000300; best trees 1783; runtime seconds 49.46.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_budget_control` AUC 0.748493; delta -0.000300. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.234218; log loss 0.248829; Brier 0.068314. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_onehot64.json`.

### pass2 / r2_cat_borders512

**Hypothesis:** Finer numeric quantization may preserve useful external-score and loan-term thresholds.

**How:** `cat` on `lean` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "Finer numeric quantization may preserve useful external-score and loan-term thresholds.", "kind": "cat", "max_iterations": 5000, "name": "r2_cat_borders512", "params": {"border_count": 512, "depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "border_count": 512, "depth": 5, "eval_metric": "AUC", "iterations": 5000, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.747731; reference `pass1_cat_lean_inner` (0.748493); delta -0.000762; best trees 1350; runtime seconds 166.86.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_budget_control` AUC 0.748493; delta -0.000762. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.232934; log loss 0.248978; Brier 0.068366. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_borders512.json`.

### pass2 / r2_cat_rsm075

**Hypothesis:** Column sampling and Bayesian bootstrap may diversify trees and improve generalization.

**How:** `cat` on `lean` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "Column sampling and Bayesian bootstrap may diversify trees and improve generalization.", "kind": "cat", "max_iterations": 5000, "name": "r2_cat_rsm075", "params": {"bagging_temperature": 1.0, "depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5, "rsm": 0.75}}`

**Runner settings:** `{"allow_writing_files": false, "bagging_temperature": 1.0, "depth": 5, "eval_metric": "AUC", "iterations": 5000, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "rsm": 0.75, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.748607; reference `pass1_cat_lean_inner` (0.748493); delta 0.000115; best trees 1540; runtime seconds 168.29.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_budget_control` AUC 0.748493; delta 0.000115. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.235640; log loss 0.248566; Brier 0.068239. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation. A parameter preflight resolved bootstrap_type=MVS despite bagging_temperature=1; this is not evidence for a Bayesian-bootstrap effect. The explicit Bayesian follow-up tests that separately.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_rsm075.json`.

### pass2 / r2_cat_ordered

**Hypothesis:** Ordered boosting may reduce prediction shift from fitting residuals on the training rows.

**How:** `cat` on `lean` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "Ordered boosting may reduce prediction shift from fitting residuals on the training rows.", "kind": "cat", "max_iterations": 3500, "name": "r2_cat_ordered", "params": {"boosting_type": "Ordered", "depth": 5, "l2_leaf_reg": 8, "learning_rate": 0.06, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "boosting_type": "Ordered", "depth": 5, "eval_metric": "AUC", "iterations": 3500, "l2_leaf_reg": 8, "learning_rate": 0.06, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.747732; reference `pass1_cat_lean_inner` (0.748493); delta -0.000761; best trees 840; runtime seconds 244.18.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_budget_control` AUC 0.748493; delta -0.000761. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.237232; log loss 0.248466; Brier 0.068142. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_ordered.json`.

### pass2 / r2_cat_native_missing

**Hypothesis:** Native numeric missing bins may handle absence differently from the -999 sentinel.

**How:** `cat` on `lean` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "Native numeric missing bins may handle absence differently from the -999 sentinel.", "kind": "cat", "missing": "native", "name": "r2_cat_native_missing", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "native", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.748981; reference `pass1_cat_lean_inner` (0.748493); delta 0.000489; best trees 1660; runtime seconds 225.43.

**CV:** pooled AUC 0.760561; fold AUCs `[0.7562517715321543, 0.76287801150067, 0.7596007708352542, 0.7598536482793566, 0.764382503838547]`; fold tree counts `[1561, 1170, 1666, 1496, 1210]`.

**Parent comparison:** `r2_cat_budget_control` AUC 0.748493; delta 0.000489. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.235197; log loss 0.248551; Brier 0.068261. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Validated on common folds; not retained in the current blend. Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_native_missing.json`.

### pass2 / r2_xgb_d3

**Hypothesis:** A separate histogram-boosting implementation may improve individual AUC or add complementary ensemble errors.

**How:** `xgb` on `engineered` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "engineered", "hypothesis": "A separate histogram-boosting implementation may improve individual AUC or add complementary ensemble errors.", "kind": "xgb", "name": "r2_xgb_d3", "params": {"colsample_bytree": 0.85, "max_bin": 256, "max_depth": 3, "min_child_weight": 30, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.85}}`

**Runner settings:** `{"colsample_bytree": 0.85, "device": "cpu", "enable_categorical": true, "eval_metric": "auc", "learning_rate": 0.035, "max_bin": 256, "max_depth": 3, "min_child_weight": 30, "n_estimators": 4500, "n_jobs": 4, "objective": "binary:logistic", "patience": 200, "random_state": 20261108, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.85, "tree_method": "hist"}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.745542; reference `pass1_cat_lean_inner` (0.748493); delta -0.002951; best trees 1117; runtime seconds 46.90.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_xgb_d4` AUC 0.745160; delta 0.000382. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.231564; log loss 0.249560; Brier 0.068417. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Evidence:** `improvements/round2/artifacts/screen/r2_xgb_d3.json`.

### pass2 / r2_xgb_d4

**Hypothesis:** A separate histogram-boosting implementation may improve individual AUC or add complementary ensemble errors.

**How:** `xgb` on `engineered` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "engineered", "hypothesis": "A separate histogram-boosting implementation may improve individual AUC or add complementary ensemble errors.", "kind": "xgb", "name": "r2_xgb_d4", "params": {"colsample_bytree": 0.85, "max_bin": 256, "max_depth": 4, "min_child_weight": 30, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.85}}`

**Runner settings:** `{"colsample_bytree": 0.85, "device": "cpu", "enable_categorical": true, "eval_metric": "auc", "learning_rate": 0.035, "max_bin": 256, "max_depth": 4, "min_child_weight": 30, "n_estimators": 4500, "n_jobs": 4, "objective": "binary:logistic", "patience": 200, "random_state": 20261108, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.85, "tree_method": "hist"}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.745160; reference `pass1_cat_lean_inner` (0.748493); delta -0.003332; best trees 707; runtime seconds 34.69.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `pass1_cat_lean_inner` AUC —; delta —. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.232923; log loss 0.249576; Brier 0.068381. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Evidence:** `improvements/round2/artifacts/screen/r2_xgb_d4.json`.

### pass2 / r2_xgb_d5

**Hypothesis:** A separate histogram-boosting implementation may improve individual AUC or add complementary ensemble errors.

**How:** `xgb` on `engineered` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "engineered", "hypothesis": "A separate histogram-boosting implementation may improve individual AUC or add complementary ensemble errors.", "kind": "xgb", "name": "r2_xgb_d5", "params": {"colsample_bytree": 0.85, "max_bin": 256, "max_depth": 5, "min_child_weight": 30, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.85}}`

**Runner settings:** `{"colsample_bytree": 0.85, "device": "cpu", "enable_categorical": true, "eval_metric": "auc", "learning_rate": 0.035, "max_bin": 256, "max_depth": 5, "min_child_weight": 30, "n_estimators": 4500, "n_jobs": 4, "objective": "binary:logistic", "patience": 200, "random_state": 20261108, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.85, "tree_method": "hist"}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.744544; reference `pass1_cat_lean_inner` (0.748493); delta -0.003948; best trees 599; runtime seconds 32.95.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_xgb_d4` AUC 0.745160; delta -0.000616. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.232507; log loss 0.249792; Brier 0.068431. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Evidence:** `improvements/round2/artifacts/screen/r2_xgb_d5.json`.

### pass2 / r2_xgb_lean

**Hypothesis:** The compact representation may also reduce noise for XGBoost.

**How:** `xgb` on `lean` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "The compact representation may also reduce noise for XGBoost.", "kind": "xgb", "name": "r2_xgb_lean", "params": {"colsample_bytree": 0.85, "max_bin": 256, "max_depth": 4, "min_child_weight": 30, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.85}}`

**Runner settings:** `{"colsample_bytree": 0.85, "device": "cpu", "enable_categorical": true, "eval_metric": "auc", "learning_rate": 0.035, "max_bin": 256, "max_depth": 4, "min_child_weight": 30, "n_estimators": 4500, "n_jobs": 4, "objective": "binary:logistic", "patience": 200, "random_state": 20261108, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.85, "tree_method": "hist"}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.745215; reference `pass1_cat_lean_inner` (0.748493); delta -0.003278; best trees 888; runtime seconds 27.43.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_xgb_d4` AUC 0.745160; delta 0.000055. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.233187; log loss 0.249632; Brier 0.068420. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Evidence:** `improvements/round2/artifacts/screen/r2_xgb_lean.json`.

### pass2 / r2_lgb_smooth_cats

**Hypothesis:** Stronger categorical smoothing may improve group-relative LightGBM generalization.

**How:** `lgb` on `engineered` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "engineered", "groups": true, "hypothesis": "Stronger categorical smoothing may improve group-relative LightGBM generalization.", "kind": "lgb", "name": "r2_lgb_smooth_cats", "params": {"cat_l2": 30.0, "cat_smooth": 100.0, "colsample_bytree": 0.8, "max_bin": 255, "min_child_samples": 150, "num_leaves": 16, "reg_alpha": 1.0, "reg_lambda": 10.0, "subsample": 0.9, "subsample_freq": 1}}`

**Runner settings:** `{"cat_l2": 30.0, "cat_smooth": 100.0, "colsample_bytree": 0.8, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "min_child_samples": 150, "n_estimators": 4500, "n_jobs": 4, "num_leaves": 16, "objective": "binary", "patience": 200, "random_state": 20261108, "reg_alpha": 1.0, "reg_lambda": 10.0, "subsample": 0.9, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.747658; reference `pass1_cat_lean_inner` (0.748493); delta -0.000835; best trees 713; runtime seconds 18.02.

**CV:** pooled AUC 0.758417; fold AUCs `[0.7534399231660427, 0.7610435139773477, 0.7563183573092727, 0.7579565196282846, 0.7633306198983952]`; fold tree counts `[477, 605, 522, 759, 673]`.

**Parent comparison:** `pass1_cat_lean_inner` AUC —; delta —. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.238556; log loss 0.248661; Brier 0.068173. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Validated on common folds; not retained in the current blend. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Evidence:** `improvements/round2/artifacts/screen/r2_lgb_smooth_cats.json`.

### pass2 / r2_lgb_linear

**Hypothesis:** Linear models inside leaves may model smooth financial relationships more efficiently than constant leaves.

**How:** `lgb` on `lean` features. Source: `improvements/round2/round2.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "Linear models inside leaves may model smooth financial relationships more efficiently than constant leaves.", "kind": "lgb", "max_iterations": 1500, "name": "r2_lgb_linear", "params": {"colsample_bytree": 0.8, "linear_lambda": 10.0, "linear_tree": true, "max_bin": 127, "min_child_samples": 150, "num_leaves": 16, "reg_alpha": 1.0, "reg_lambda": 10.0, "subsample": 0.9, "subsample_freq": 1}, "patience": 100}`

**Runner settings:** `{"colsample_bytree": 0.8, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "linear_lambda": 10.0, "linear_tree": true, "max_bin": 127, "min_child_samples": 150, "n_estimators": 1500, "n_jobs": 4, "num_leaves": 16, "objective": "binary", "patience": 100, "random_state": 20261108, "reg_alpha": 1.0, "reg_lambda": 10.0, "subsample": 0.9, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.743766; reference `pass1_cat_lean_inner` (0.748493); delta -0.004727; best trees 450; runtime seconds 9.06.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `pass1_cat_lean_inner` AUC —; delta —. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.231614; log loss 0.249928; Brier 0.068476. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Evidence:** `improvements/round2/artifacts/screen/r2_lgb_linear.json`.

### pass2 / r2_cat_burden

**Hypothesis:** Isolate the payment-burden and household-amount block from the hypothetical rate/term proxies.

**How:** `cat` on `finance` features. Source: `improvements/round2/adaptive.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"columns": ["NAME_CONTRACT_TYPE", "CODE_GENDER", "CNT_CHILDREN", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE", "NAME_FAMILY_STATUS", "NAME_HOUSING_TYPE", "REGION_POPULATION_RELATIVE", "DAYS_BIRTH", "DAYS_EMPLOYED", "DAYS_REGISTRATION", "DAYS_ID_PUBLISH", "OWN_CAR_AGE", "FLAG_MOBIL", "FLAG_EMP_PHONE", "FLAG_WORK_PHONE", "OCCUPATION_TYPE", "CNT_FAM_MEMBERS", "REGION_RATING_CLIENT", "ORGANIZATION_TYPE", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "DAYS_LAST_PHONE_CHANGE", "AMT_REQ_CREDIT_BUREAU_HOUR", "AMT_REQ_CREDIT_BUREAU_MON", "AMT_REQ_CREDIT_BUREAU_QRT", "AMT_REQ_CREDIT_BUREAU_YEAR", "EMPLOYED_SENTINEL", "MISSING_COUNT", "CREDIT_TERM", "CREDIT_GOODS_DIFF_RATIO", "INCOME_PER_PERSON", "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY", "AMT_INCOME_TOTAL_OVER_AMT_CREDIT", "DAYS_EMPLOYED_OVER_BIRTH", "EXT_MEAN", "EXT_MIN", "EXT_MAX", "EXT_STD", "EXT_COUNT", "AGE_AT_EMPLOYMENT", "INCOME_MINUS_12_ANNUITIES", "MARGIN_PER_PERSON", "INCOME_PER_ADULT", "CREDIT_PER_ADULT", "GOODS_OVER_INCOME", "CREDIT_COST_AMOUNT"], "features": "finance", "hypothesis": "Isolate the payment-burden and household-amount block from the hypothetical rate/term proxies.", "kind": "cat", "name": "r2_cat_burden", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}, "source": "improvements/round2/adaptive.py"}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.747691; reference `pass1_cat_lean_inner` (0.748493); delta -0.000801; best trees 1695; runtime seconds 223.84.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_finance` AUC 0.749082; delta -0.001391. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.232916; log loss 0.248995; Brier 0.068359. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_burden.json`.

### pass2 / r2_cat_term_proxies

**Hypothesis:** Isolate the redundant nonlinear rate/term representations; test whether quantization alone explains the finance gain.

**How:** `cat` on `finance` features. Source: `improvements/round2/adaptive.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"columns": ["NAME_CONTRACT_TYPE", "CODE_GENDER", "CNT_CHILDREN", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE", "NAME_FAMILY_STATUS", "NAME_HOUSING_TYPE", "REGION_POPULATION_RELATIVE", "DAYS_BIRTH", "DAYS_EMPLOYED", "DAYS_REGISTRATION", "DAYS_ID_PUBLISH", "OWN_CAR_AGE", "FLAG_MOBIL", "FLAG_EMP_PHONE", "FLAG_WORK_PHONE", "OCCUPATION_TYPE", "CNT_FAM_MEMBERS", "REGION_RATING_CLIENT", "ORGANIZATION_TYPE", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "DAYS_LAST_PHONE_CHANGE", "AMT_REQ_CREDIT_BUREAU_HOUR", "AMT_REQ_CREDIT_BUREAU_MON", "AMT_REQ_CREDIT_BUREAU_QRT", "AMT_REQ_CREDIT_BUREAU_YEAR", "EMPLOYED_SENTINEL", "MISSING_COUNT", "CREDIT_TERM", "CREDIT_GOODS_DIFF_RATIO", "INCOME_PER_PERSON", "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY", "AMT_INCOME_TOTAL_OVER_AMT_CREDIT", "DAYS_EMPLOYED_OVER_BIRTH", "EXT_MEAN", "EXT_MIN", "EXT_MAX", "EXT_STD", "EXT_COUNT", "AGE_AT_EMPLOYMENT", "ASSUMED_PERIOD_RATE_24", "ASSUMED_PERIOD_RATE_36", "ASSUMED_PERIOD_RATE_60", "TERM_MULTIPLE_6_DISTANCE", "TERM_MULTIPLE_12_DISTANCE"], "features": "finance", "hypothesis": "Isolate the redundant nonlinear rate/term representations; test whether quantization alone explains the finance gain.", "kind": "cat", "name": "r2_cat_term_proxies", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}, "source": "improvements/round2/adaptive.py"}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.749952; reference `pass1_cat_lean_inner` (0.748493); delta 0.001460; best trees 1480; runtime seconds 197.40.

**CV:** pooled AUC 0.762254; fold AUCs `[0.7575674180416604, 0.7646017415548696, 0.7622346190065159, 0.7613174959741045, 0.765635489574521]`; fold tree counts `[1385, 1332, 1637, 1636, 1568]`.

**Parent comparison:** `r2_cat_finance` AUC 0.749082; delta 0.000870. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.239172; log loss 0.248121; Brier 0.068117. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Retained in the final frozen ensemble at weight 0.562500. Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_term_proxies.json`.

### pass2 / r2_cat_finance_native

**Hypothesis:** Test whether native missing bins and financial features provide complementary gains.

**How:** `cat` on `finance` features. Source: `improvements/round2/adaptive.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "finance", "hypothesis": "Test whether native missing bins and financial features provide complementary gains.", "kind": "cat", "missing": "native", "name": "r2_cat_finance_native", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}, "source": "improvements/round2/adaptive.py"}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "native", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.749235; reference `pass1_cat_lean_inner` (0.748493); delta 0.000743; best trees 1467; runtime seconds 206.99.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_finance` AUC 0.749082; delta 0.000153. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.235389; log loss 0.248428; Brier 0.068239. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_finance_native.json`.

### pass2 / r2_cat_finance_tuned

**Hypothesis:** Combine the finance representation with the best screened alternative CatBoost parameter recipe (r2_cat_rsm075); this tests interaction rather than assuming additive gains.

**How:** `cat` on `finance` features. Source: `improvements/round2/adaptive.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "finance", "hypothesis": "Combine the finance representation with the best screened alternative CatBoost parameter recipe (r2_cat_rsm075); this tests interaction rather than assuming additive gains.", "kind": "cat", "max_iterations": 5000, "name": "r2_cat_finance_tuned", "params": {"bagging_temperature": 1.0, "depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5, "rsm": 0.75}, "source": "improvements/round2/adaptive.py"}`

**Runner settings:** `{"allow_writing_files": false, "bagging_temperature": 1.0, "depth": 5, "eval_metric": "AUC", "iterations": 5000, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "rsm": 0.75, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.749273; reference `pass1_cat_lean_inner` (0.748493); delta 0.000781; best trees 1694; runtime seconds 209.02.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_finance` AUC 0.749082; delta 0.000191. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.236726; log loss 0.248513; Brier 0.068242. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_finance_tuned.json`.

### pass2 / r2_cat_ctr1

**Hypothesis:** The saved baseline resolves max_ctr_complexity=4. Restricting categorical-combination complexity may reduce variance.

**How:** `cat` on `lean` features. Source: `improvements/round2/adaptive.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "The saved baseline resolves max_ctr_complexity=4. Restricting categorical-combination complexity may reduce variance.", "kind": "cat", "name": "r2_cat_ctr1", "params": {"depth": 5, "l2_leaf_reg": 8, "max_ctr_complexity": 1, "random_strength": 0.5}, "source": "improvements/round2/adaptive.py"}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "max_ctr_complexity": 1, "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.747827; reference `pass1_cat_lean_inner` (0.748493); delta -0.000665; best trees 1470; runtime seconds 122.05.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_budget_control` AUC 0.748493; delta -0.000665. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.234963; log loss 0.248828; Brier 0.068293. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_ctr1.json`.

### pass2 / r2_cat_ctr2

**Hypothesis:** The saved baseline resolves max_ctr_complexity=4. Restricting categorical-combination complexity may reduce variance.

**How:** `cat` on `lean` features. Source: `improvements/round2/adaptive.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "The saved baseline resolves max_ctr_complexity=4. Restricting categorical-combination complexity may reduce variance.", "kind": "cat", "name": "r2_cat_ctr2", "params": {"depth": 5, "l2_leaf_reg": 8, "max_ctr_complexity": 2, "random_strength": 0.5}, "source": "improvements/round2/adaptive.py"}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "max_ctr_complexity": 2, "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.748095; reference `pass1_cat_lean_inner` (0.748493); delta -0.000397; best trees 1664; runtime seconds 215.76.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_budget_control` AUC 0.748493; delta -0.000397. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.234983; log loss 0.248799; Brier 0.068288. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_ctr2.json`.

### pass2 / r2_cat_bayesian_rsm075

**Hypothesis:** Explicitly switch bootstrap from the resolved MVS default to Bayesian; compare against the column-sampling trial whose bootstrap remained MVS.

**How:** `cat` on `lean` features. Source: `improvements/round2/adaptive.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "Explicitly switch bootstrap from the resolved MVS default to Bayesian; compare against the column-sampling trial whose bootstrap remained MVS.", "kind": "cat", "name": "r2_cat_bayesian_rsm075", "params": {"bagging_temperature": 1.0, "bootstrap_type": "Bayesian", "depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5, "rsm": 0.75}, "source": "improvements/round2/adaptive.py"}`

**Runner settings:** `{"allow_writing_files": false, "bagging_temperature": 1.0, "bootstrap_type": "Bayesian", "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "rsm": 0.75, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.747148; reference `pass1_cat_lean_inner` (0.748493); delta -0.001345; best trees 1685; runtime seconds 215.49.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_rsm075` AUC 0.748607; delta -0.001459. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.235787; log loss 0.248824; Brier 0.068277. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_bayesian_rsm075.json`.

### pass2 / r2_xgb_finance

**Hypothesis:** Check whether the financial representation also helps the best screened XGBoost recipe.

**How:** `xgb` on `finance` features. Source: `improvements/round2/adaptive.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "finance", "hypothesis": "Check whether the financial representation also helps the best screened XGBoost recipe.", "kind": "xgb", "name": "r2_xgb_finance", "params": {"colsample_bytree": 0.85, "max_bin": 256, "max_depth": 3, "min_child_weight": 30, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.85}, "source": "improvements/round2/adaptive.py"}`

**Runner settings:** `{"colsample_bytree": 0.85, "device": "cpu", "enable_categorical": true, "eval_metric": "auc", "learning_rate": 0.035, "max_bin": 256, "max_depth": 3, "min_child_weight": 30, "n_estimators": 4500, "n_jobs": 4, "objective": "binary:logistic", "patience": 200, "random_state": 20261108, "reg_alpha": 1.0, "reg_lambda": 20.0, "subsample": 0.85, "tree_method": "hist"}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.747225; reference `pass1_cat_lean_inner` (0.748493); delta -0.001268; best trees 1515; runtime seconds 82.82.

**CV:** pooled AUC 0.758883; fold AUCs `[0.753633772858824, 0.7625033562974215, 0.7602666239618288, 0.7564753662003603, 0.7616299443285021]`; fold tree counts `[1012, 1119, 1212, 1132, 937]`.

**Parent comparison:** `r2_xgb_d3` AUC 0.745542; delta 0.001683. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.235441; log loss 0.249090; Brier 0.068335. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Validated on common folds; not retained in the current blend. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Evidence:** `improvements/round2/artifacts/screen/r2_xgb_finance.json`.

### pass2 / r2_lgb_finance

**Hypothesis:** Check whether the finance representation improves the known complementary LightGBM configuration.

**How:** `lgb` on `finance` features. Source: `improvements/round2/adaptive.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "finance", "groups": true, "hypothesis": "Check whether the finance representation improves the known complementary LightGBM configuration.", "kind": "lgb", "name": "r2_lgb_finance", "params": {"colsample_bytree": 0.6846068413999578, "max_bin": 255, "max_depth": -1, "min_child_samples": 89, "num_leaves": 21, "reg_alpha": 3.687185564401245, "reg_lambda": 2.1323824335960286, "subsample": 0.961965333135664, "subsample_freq": 1}, "source": "improvements/round2/adaptive.py"}`

**Runner settings:** `{"colsample_bytree": 0.6846068413999578, "deterministic": true, "force_col_wise": true, "learning_rate": 0.035, "max_bin": 255, "max_depth": -1, "min_child_samples": 89, "n_estimators": 4500, "n_jobs": 4, "num_leaves": 21, "objective": "binary", "patience": 200, "random_state": 20261108, "reg_alpha": 3.687185564401245, "reg_lambda": 2.1323824335960286, "subsample": 0.961965333135664, "subsample_freq": 1}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.746487; reference `pass1_cat_lean_inner` (0.748493); delta -0.002005; best trees 697; runtime seconds 19.00.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `lgb_tune_15` AUC 0.747151; delta -0.000664. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.237970; log loss 0.249166; Brier 0.068279. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Evidence:** `improvements/round2/artifacts/screen/r2_lgb_finance.json`.

### pass2 / r2_cat_budget_control

**Hypothesis:** Hold features and all model parameters fixed while increasing patience 150→200 and the cap 3000→4500. Test whether the changed stopping budget explains apparent gains from other trials.

**How:** `cat` on `lean` features. Source: `improvements/round2/budget_control.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"features": "lean", "hypothesis": "Hold features and all model parameters fixed while increasing patience 150\u2192200 and the cap 3000\u21924500. Test whether the changed stopping budget explains apparent gains from other trials.", "kind": "cat", "name": "r2_cat_budget_control", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}, "source": "improvements/round2/budget_control.py"}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.748493; reference `pass1_cat_lean_inner` (0.748493); delta 0.000000; best trees 1670; runtime seconds 139.76.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_baseline` AUC 0.748493; delta 0.000000. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.233994; log loss 0.248728; Brier 0.068302. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Implementation/stopping-budget control; used to interpret other trials, not claimed as a new recipe. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_budget_control.json`.

### pass2 / r2_cat_proxies_native

**Hypothesis:** The proxy-only representation improved screening by 0.00146; combine it with the independently promising native missing policy.

**How:** `cat` on `finance` features. Source: `improvements/round2/proxy_followup.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"columns": ["NAME_CONTRACT_TYPE", "CODE_GENDER", "CNT_CHILDREN", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE", "NAME_FAMILY_STATUS", "NAME_HOUSING_TYPE", "REGION_POPULATION_RELATIVE", "DAYS_BIRTH", "DAYS_EMPLOYED", "DAYS_REGISTRATION", "DAYS_ID_PUBLISH", "OWN_CAR_AGE", "FLAG_MOBIL", "FLAG_EMP_PHONE", "FLAG_WORK_PHONE", "OCCUPATION_TYPE", "CNT_FAM_MEMBERS", "REGION_RATING_CLIENT", "ORGANIZATION_TYPE", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "DAYS_LAST_PHONE_CHANGE", "AMT_REQ_CREDIT_BUREAU_HOUR", "AMT_REQ_CREDIT_BUREAU_MON", "AMT_REQ_CREDIT_BUREAU_QRT", "AMT_REQ_CREDIT_BUREAU_YEAR", "EMPLOYED_SENTINEL", "MISSING_COUNT", "CREDIT_TERM", "CREDIT_GOODS_DIFF_RATIO", "INCOME_PER_PERSON", "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY", "AMT_INCOME_TOTAL_OVER_AMT_CREDIT", "DAYS_EMPLOYED_OVER_BIRTH", "EXT_MEAN", "EXT_MIN", "EXT_MAX", "EXT_STD", "EXT_COUNT", "AGE_AT_EMPLOYMENT", "ASSUMED_PERIOD_RATE_24", "ASSUMED_PERIOD_RATE_36", "ASSUMED_PERIOD_RATE_60", "TERM_MULTIPLE_6_DISTANCE", "TERM_MULTIPLE_12_DISTANCE"], "features": "finance", "hypothesis": "The proxy-only representation improved screening by 0.00146; combine it with the independently promising native missing policy.", "kind": "cat", "missing": "native", "name": "r2_cat_proxies_native", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}, "source": "improvements/round2/proxy_followup.py"}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "native", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.749647; reference `pass1_cat_lean_inner` (0.748493); delta 0.001155; best trees 1724; runtime seconds 226.02.

**CV:** pooled AUC 0.761574; fold AUCs `[0.7574203992748918, 0.764277180477028, 0.761151443557688, 0.7597911069582141, 0.7655988097272872]`; fold tree counts `[1699, 807, 1557, 1895, 1540]`.

**Parent comparison:** `r2_cat_term_proxies` AUC 0.749952; delta -0.000305. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.236775; log loss 0.248398; Brier 0.068218. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Retained in the final frozen ensemble at weight 0.250000. Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_proxies_native.json`.

### pass2 / r2_cat_rates_only

**Hypothesis:** Separate the hypothetical positive-rate transforms from the term-rounding distances.

**How:** `cat` on `finance` features. Source: `improvements/round2/proxy_followup.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"columns": ["NAME_CONTRACT_TYPE", "CODE_GENDER", "CNT_CHILDREN", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE", "NAME_FAMILY_STATUS", "NAME_HOUSING_TYPE", "REGION_POPULATION_RELATIVE", "DAYS_BIRTH", "DAYS_EMPLOYED", "DAYS_REGISTRATION", "DAYS_ID_PUBLISH", "OWN_CAR_AGE", "FLAG_MOBIL", "FLAG_EMP_PHONE", "FLAG_WORK_PHONE", "OCCUPATION_TYPE", "CNT_FAM_MEMBERS", "REGION_RATING_CLIENT", "ORGANIZATION_TYPE", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "DAYS_LAST_PHONE_CHANGE", "AMT_REQ_CREDIT_BUREAU_HOUR", "AMT_REQ_CREDIT_BUREAU_MON", "AMT_REQ_CREDIT_BUREAU_QRT", "AMT_REQ_CREDIT_BUREAU_YEAR", "EMPLOYED_SENTINEL", "MISSING_COUNT", "CREDIT_TERM", "CREDIT_GOODS_DIFF_RATIO", "INCOME_PER_PERSON", "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY", "AMT_INCOME_TOTAL_OVER_AMT_CREDIT", "DAYS_EMPLOYED_OVER_BIRTH", "EXT_MEAN", "EXT_MIN", "EXT_MAX", "EXT_STD", "EXT_COUNT", "AGE_AT_EMPLOYMENT", "ASSUMED_PERIOD_RATE_24", "ASSUMED_PERIOD_RATE_36", "ASSUMED_PERIOD_RATE_60"], "features": "finance", "hypothesis": "Separate the hypothetical positive-rate transforms from the term-rounding distances.", "kind": "cat", "name": "r2_cat_rates_only", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}, "source": "improvements/round2/proxy_followup.py"}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.748473; reference `pass1_cat_lean_inner` (0.748493); delta -0.000019; best trees 1497; runtime seconds 199.52.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_term_proxies` AUC 0.749952; delta -0.001479. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.235579; log loss 0.248612; Brier 0.068248. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_rates_only.json`.

### pass2 / r2_cat_distances_only

**Hypothesis:** Separate the 6/12-period term-distance transforms from hypothetical rates.

**How:** `cat` on `finance` features. Source: `improvements/round2/proxy_followup.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"columns": ["NAME_CONTRACT_TYPE", "CODE_GENDER", "CNT_CHILDREN", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE", "NAME_FAMILY_STATUS", "NAME_HOUSING_TYPE", "REGION_POPULATION_RELATIVE", "DAYS_BIRTH", "DAYS_EMPLOYED", "DAYS_REGISTRATION", "DAYS_ID_PUBLISH", "OWN_CAR_AGE", "FLAG_MOBIL", "FLAG_EMP_PHONE", "FLAG_WORK_PHONE", "OCCUPATION_TYPE", "CNT_FAM_MEMBERS", "REGION_RATING_CLIENT", "ORGANIZATION_TYPE", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "DAYS_LAST_PHONE_CHANGE", "AMT_REQ_CREDIT_BUREAU_HOUR", "AMT_REQ_CREDIT_BUREAU_MON", "AMT_REQ_CREDIT_BUREAU_QRT", "AMT_REQ_CREDIT_BUREAU_YEAR", "EMPLOYED_SENTINEL", "MISSING_COUNT", "CREDIT_TERM", "CREDIT_GOODS_DIFF_RATIO", "INCOME_PER_PERSON", "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY", "AMT_INCOME_TOTAL_OVER_AMT_CREDIT", "DAYS_EMPLOYED_OVER_BIRTH", "EXT_MEAN", "EXT_MIN", "EXT_MAX", "EXT_STD", "EXT_COUNT", "AGE_AT_EMPLOYMENT", "TERM_MULTIPLE_6_DISTANCE", "TERM_MULTIPLE_12_DISTANCE"], "features": "finance", "hypothesis": "Separate the 6/12-period term-distance transforms from hypothetical rates.", "kind": "cat", "name": "r2_cat_distances_only", "params": {"depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5}, "source": "improvements/round2/proxy_followup.py"}`

**Runner settings:** `{"allow_writing_files": false, "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.748766; reference `pass1_cat_lean_inner` (0.748493); delta 0.000273; best trees 1953; runtime seconds 229.34.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_term_proxies` AUC 0.749952; delta -0.001186. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.234805; log loss 0.248750; Brier 0.068332. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_distances_only.json`.

### pass2 / r2_cat_proxies_rsm075

**Hypothesis:** Test whether the promising proxy block complements column sampling while retaining the resolved MVS bootstrap.

**How:** `cat` on `finance` features. Source: `improvements/round2/proxy_followup.py`. Rationale origin: Written in the candidate plan before this trial started.

**Configuration:** `{"columns": ["NAME_CONTRACT_TYPE", "CODE_GENDER", "CNT_CHILDREN", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE", "NAME_FAMILY_STATUS", "NAME_HOUSING_TYPE", "REGION_POPULATION_RELATIVE", "DAYS_BIRTH", "DAYS_EMPLOYED", "DAYS_REGISTRATION", "DAYS_ID_PUBLISH", "OWN_CAR_AGE", "FLAG_MOBIL", "FLAG_EMP_PHONE", "FLAG_WORK_PHONE", "OCCUPATION_TYPE", "CNT_FAM_MEMBERS", "REGION_RATING_CLIENT", "ORGANIZATION_TYPE", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3", "DAYS_LAST_PHONE_CHANGE", "AMT_REQ_CREDIT_BUREAU_HOUR", "AMT_REQ_CREDIT_BUREAU_MON", "AMT_REQ_CREDIT_BUREAU_QRT", "AMT_REQ_CREDIT_BUREAU_YEAR", "EMPLOYED_SENTINEL", "MISSING_COUNT", "CREDIT_TERM", "CREDIT_GOODS_DIFF_RATIO", "INCOME_PER_PERSON", "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY", "AMT_INCOME_TOTAL_OVER_AMT_CREDIT", "DAYS_EMPLOYED_OVER_BIRTH", "EXT_MEAN", "EXT_MIN", "EXT_MAX", "EXT_STD", "EXT_COUNT", "AGE_AT_EMPLOYMENT", "ASSUMED_PERIOD_RATE_24", "ASSUMED_PERIOD_RATE_36", "ASSUMED_PERIOD_RATE_60", "TERM_MULTIPLE_6_DISTANCE", "TERM_MULTIPLE_12_DISTANCE"], "features": "finance", "hypothesis": "Test whether the promising proxy block complements column sampling while retaining the resolved MVS bootstrap.", "kind": "cat", "name": "r2_cat_proxies_rsm075", "params": {"bagging_temperature": 1.0, "depth": 5, "l2_leaf_reg": 8, "random_strength": 0.5, "rsm": 0.75}, "source": "improvements/round2/proxy_followup.py"}`

**Runner settings:** `{"allow_writing_files": false, "bagging_temperature": 1.0, "depth": 5, "eval_metric": "AUC", "iterations": 4500, "l2_leaf_reg": 8, "learning_rate": 0.045, "loss_function": "Logloss", "numeric_missing": "sentinel (-999)", "patience": 200, "random_seed": 20261108, "random_strength": 0.5, "rsm": 0.75, "thread_count": 4}`. Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.

**Result:** status `complete`; inner AUC 0.749288; reference `pass1_cat_lean_inner` (0.748493); delta 0.000795; best trees 1293; runtime seconds 154.88.

**CV:** pooled AUC —; fold AUCs `None`; fold tree counts `None`.

**Parent comparison:** `r2_cat_term_proxies` AUC 0.749952; delta -0.000664. This clarifies within-family/component comparisons alongside the common baseline delta.

**Secondary metrics:** AP 0.236247; log loss 0.248435; Brier 0.068237. These are retrospective saved-prediction audits where available.

**Decision / interpretation:** Screened but not advanced by the documented promising/diverse-family shortlist. Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Evidence:** `improvements/round2/artifacts/screen/r2_cat_proxies_rsm075.json`.


## Engineering incidents and fixes

These were implementation/runtime incidents, not evidence that a machine-learning hypothesis failed.

- First-pass extended categorical bins retained missing values as floating NaN inside a string column; vocabulary sorting failed on mixed types. Explicit string missing tokens fixed it before evaluation continued.
- Initial package installation failed inside the network-restricted sandbox. Approved installation into the project venv downloaded software only.
- Notebook execution initially failed because Jupyter loopback ports were restricted. Approved local execution used the project venv and a project-local kernelspec.
- A first-pass staged-CV filter temporarily reused the function argument name as a loop variable, running the spline family instead of the requested family. Renaming the variable fixed it. Singleton blend selection also needed an empty-pair guard.
- Concurrent first-pass staged CV writers could overwrite a cached spline result. The spline CV was rerun; final artifacts and notebooks passed validation. Second-pass results use separate atomic JSON files per trial and a locked event journal.
- A row/batch invariance check exposed integer versus float dtype differences when an employment sentinel was absent from a tiny batch. The employment column now explicitly uses float64; full-dataset feature values were unchanged.
- Saved encoders use dictionaries rather than pickled `__main__` classes, making notebook model reloads independent of how the training script was launched.
- The first-pass audit histogram's density-axis label was corrected, then its new notebook was re-executed. Original supplied notebooks were never changed.

Second-pass execution failures, if any, are recorded per trial above and in their traceback files. Failed runs never acquire invented AUCs.
The first-pass saved CatBoost model resolves bootstrap MVS and maximum categorical-combination complexity 4. These defaults were inspected rather than assumed.
A 300-row, five-tree parameter preflight showed that bagging_temperature alone still resolved to MVS. Its AUC was never used; the explicit Bayesian follow-up corrects the mechanism being tested.

## Evidence and reproduction map

- `improvements/artifacts`: first-pass screening, CV, blending, audit, full-data OOF, checksums and feature importances.
- `improvements/round2/artifacts/candidate_plan.json`: new hypotheses/configurations before runs.
- `improvements/round2/artifacts/events.jsonl`: UTC start/finish/failure chronology.
- `improvements/round2/artifacts/screen`: one JSON result and aligned prediction array per screen.
- `improvements/round2/artifacts/cv`: one result and aligned prediction array per new CV model.
- `improvements/round2/artifacts/complete_experiment_ledger.json` and `.csv`: complete combined machine-readable ledger.
- `improvements/round2/reference`: preserved first-pass report and immutable-file hashes.
- `improvements/round2/round2.py`: exact feature formulas, encoder behavior and candidate/training code.

Refresh this document with `.venv/bin/python improvements/round2/document.py` from `Competition`.


## Final selection and robustness evidence

### First-pass probability versus log-odds averaging

The exact earlier exploratory pair/weights were recomputed from retained OOF arrays for documentation, not newly fitted. Probability averaging was slightly better for all three tested weights. This was not proof that log-odds blending never helps.

```json
{
  "origin": "Retrospective recomputation of the exact first-pass exploratory comparisons recorded in chat; no new fitting or selection",
  "models": [
    "cat_depth4",
    "lgb_tune_12"
  ],
  "split": "original development OOF",
  "comparisons": [
    {
      "cat_weight": 0.5,
      "probability_auc": 0.7605637333149073,
      "log_odds_auc": 0.7605155808750492
    },
    {
      "cat_weight": 0.6666666666666666,
      "probability_auc": 0.760744324000084,
      "log_odds_auc": 0.7607011502958024
    },
    {
      "cat_weight": 0.75,
      "probability_auc": 0.7606692952953855,
      "log_odds_auc": 0.7606259908552975
    }
  ],
  "decision": "Probability averaging beat log-odds averaging for each tested weight. This does not establish universal dominance."
}
```

### Individual strength versus recorded pair complementarity

```json
{
  "lead": "r2_cat_term_proxies",
  "scope": "Recorded primary development weight grid only; no new fitting or secondary-seed search",
  "interpretation": "A higher individual AUC does not guarantee a better mixture; differences can also reflect calibration and correlated errors. These scores do not isolate a causal mechanism.",
  "comparisons": [
    {
      "component": "lgb_tune_15",
      "individual_auc": 0.7573280608933021,
      "best_recorded_pair_auc": 0.7629541355344485,
      "lead_weight": 0.75,
      "component_weight": 0.25
    },
    {
      "component": "r2_xgb_finance",
      "individual_auc": 0.758883318470827,
      "best_recorded_pair_auc": 0.7629482050134669,
      "lead_weight": 0.75,
      "component_weight": 0.25
    },
    {
      "component": "r2_lgb_smooth_cats",
      "individual_auc": 0.7584174292127097,
      "best_recorded_pair_auc": 0.7628906582720832,
      "lead_weight": 0.75,
      "component_weight": 0.25
    },
    {
      "component": "r2_cat_proxies_native",
      "individual_auc": 0.7615744712299796,
      "best_recorded_pair_auc": 0.7625661992967897,
      "lead_weight": 0.6666666666666667,
      "component_weight": 0.3333333333333333
    },
    {
      "component": "cat_lean",
      "individual_auc": 0.7607901174487961,
      "best_recorded_pair_auc": 0.7625408451702681,
      "lead_weight": 0.75,
      "component_weight": 0.25
    },
    {
      "component": "r2_cat_native_missing",
      "individual_auc": 0.7605612895609853,
      "best_recorded_pair_auc": 0.7625170706483542,
      "lead_weight": 0.75,
      "component_weight": 0.25
    }
  ]
}
```

### Balanced helper-weight probe

```json
{
  "hypothesis": "The two helper algorithms have nearly identical best pair AUCs; split their existing total weight while holding the lead CatBoost weight fixed.",
  "selection_scope": "Primary development predictions only; no secondary labels or new fitting",
  "comparisons": [
    {
      "names": [
        "r2_cat_term_proxies",
        "lgb_tune_15",
        "r2_xgb_finance"
      ],
      "weights": [
        0.5,
        0.25,
        0.25
      ],
      "auc": 0.7627977352834495
    },
    {
      "names": [
        "r2_cat_term_proxies",
        "lgb_tune_15",
        "r2_xgb_finance"
      ],
      "weights": [
        0.6666666666666666,
        0.16666666666666669,
        0.16666666666666669
      ],
      "auc": 0.7630706060531564
    },
    {
      "names": [
        "r2_cat_term_proxies",
        "lgb_tune_15",
        "r2_xgb_finance"
      ],
      "weights": [
        0.75,
        0.125,
        0.125
      ],
      "auc": 0.7630434862749185
    },
    {
      "names": [
        "r2_cat_term_proxies",
        "lgb_tune_15",
        "r2_xgb_finance"
      ],
      "weights": [
        0.8,
        0.09999999999999998,
        0.09999999999999998
      ],
      "auc": 0.762970150670747
    },
    {
      "names": [
        "r2_cat_term_proxies",
        "lgb_tune_15",
        "r2_xgb_finance"
      ],
      "weights": [
        0.9,
        0.04999999999999999,
        0.04999999999999999
      ],
      "auc": 0.7627027399167841
    }
  ],
  "current_primary_auc": 0.7630891353395803,
  "best": {
    "names": [
      "r2_cat_term_proxies",
      "lgb_tune_15",
      "r2_xgb_finance"
    ],
    "weights": [
      0.6666666666666666,
      0.16666666666666669,
      0.16666666666666669
    ],
    "auc": 0.7630706060531564
  },
  "increment": -1.8529286423984992e-05,
  "further_validation_warranted": false,
  "note": "This probe does not silently replace the frozen validated candidate. Reopen only for a material primary gain and record a new validation decision."
}
```

### Original primary winner before the prospective complexity check

Source: `improvements/round2/artifacts/primary_original_winner.json`.

```json
{
  "names": [
    "lgb_tune_15",
    "r2_cat_term_proxies",
    "r2_cat_proxies_native"
  ],
  "weights": [
    0.1875,
    0.5625,
    0.25
  ],
  "auc": 0.7630891353395803,
  "method": "retain best primary pair plus a complementary model",
  "baseline_auc": 0.7617724188892933,
  "development_delta": 0.001316716450287081,
  "models": [
    {
      "name": "lgb_tune_15",
      "spec": {
        "name": "lgb_tune_15",
        "kind": "lgb",
        "features": "engineered",
        "groups": true,
        "params": {
          "num_leaves": 21,
          "min_child_samples": 89,
          "colsample_bytree": 0.6846068413999578,
          "subsample": 0.961965333135664,
          "subsample_freq": 1,
          "reg_lambda": 2.1323824335960286,
          "reg_alpha": 3.687185564401245,
          "max_bin": 255,
          "max_depth": -1
        }
      },
      "auc": 0.7573280608933021,
      "iterations": [
        590,
        639,
        523,
        768,
        456
      ],
      "origin": "pass1",
      "prediction_path": "improvements/artifacts/lgb_tune_15_oof.npy"
    },
    {
      "name": "r2_cat_term_proxies",
      "spec": {
        "name": "r2_cat_term_proxies",
        "kind": "cat",
        "features": "finance",
        "params": {
          "depth": 5,
          "l2_leaf_reg": 8,
          "random_strength": 0.5
        },
        "source": "improvements/round2/adaptive.py",
        "hypothesis": "Isolate the redundant nonlinear rate/term representations; test whether quantization alone explains the finance gain.",
        "columns": [
          "NAME_CONTRACT_TYPE",
          "CODE_GENDER",
          "CNT_CHILDREN",
          "AMT_INCOME_TOTAL",
          "AMT_CREDIT",
          "AMT_ANNUITY",
          "AMT_GOODS_PRICE",
          "NAME_INCOME_TYPE",
          "NAME_EDUCATION_TYPE",
          "NAME_FAMILY_STATUS",
          "NAME_HOUSING_TYPE",
          "REGION_POPULATION_RELATIVE",
          "DAYS_BIRTH",
          "DAYS_EMPLOYED",
          "DAYS_REGISTRATION",
          "DAYS_ID_PUBLISH",
          "OWN_CAR_AGE",
          "FLAG_MOBIL",
          "FLAG_EMP_PHONE",
          "FLAG_WORK_PHONE",
          "OCCUPATION_TYPE",
          "CNT_FAM_MEMBERS",
          "REGION_RATING_CLIENT",
          "ORGANIZATION_TYPE",
          "EXT_SOURCE_1",
          "EXT_SOURCE_2",
          "EXT_SOURCE_3",
          "DAYS_LAST_PHONE_CHANGE",
          "AMT_REQ_CREDIT_BUREAU_HOUR",
          "AMT_REQ_CREDIT_BUREAU_MON",
          "AMT_REQ_CREDIT_BUREAU_QRT",
          "AMT_REQ_CREDIT_BUREAU_YEAR",
          "EMPLOYED_SENTINEL",
          "MISSING_COUNT",
          "CREDIT_TERM",
          "CREDIT_GOODS_DIFF_RATIO",
          "INCOME_PER_PERSON",
          "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY",
          "AMT_INCOME_TOTAL_OVER_AMT_CREDIT",
          "DAYS_EMPLOYED_OVER_BIRTH",
          "EXT_MEAN",
          "EXT_MIN",
          "EXT_MAX",
          "EXT_STD",
          "EXT_COUNT",
          "AGE_AT_EMPLOYMENT",
          "ASSUMED_PERIOD_RATE_24",
          "ASSUMED_PERIOD_RATE_36",
          "ASSUMED_PERIOD_RATE_60",
          "TERM_MULTIPLE_6_DISTANCE",
          "TERM_MULTIPLE_12_DISTANCE"
        ]
      },
      "auc": 0.7622544252863716,
      "iterations": [
        1385,
        1332,
        1637,
        1636,
        1568
      ],
      "origin": "pass2",
      "prediction_path": "improvements/round2/artifacts/cv/r2_cat_term_proxies_oof.npy"
    },
    {
      "name": "r2_cat_proxies_native",
      "spec": {
        "name": "r2_cat_proxies_native",
        "kind": "cat",
        "features": "finance",
        "params": {
          "depth": 5,
          "l2_leaf_reg": 8,
          "random_strength": 0.5
        },
        "source": "improvements/round2/proxy_followup.py",
        "hypothesis": "The proxy-only representation improved screening by 0.00146; combine it with the independently promising native missing policy.",
        "columns": [
          "NAME_CONTRACT_TYPE",
          "CODE_GENDER",
          "CNT_CHILDREN",
          "AMT_INCOME_TOTAL",
          "AMT_CREDIT",
          "AMT_ANNUITY",
          "AMT_GOODS_PRICE",
          "NAME_INCOME_TYPE",
          "NAME_EDUCATION_TYPE",
          "NAME_FAMILY_STATUS",
          "NAME_HOUSING_TYPE",
          "REGION_POPULATION_RELATIVE",
          "DAYS_BIRTH",
          "DAYS_EMPLOYED",
          "DAYS_REGISTRATION",
          "DAYS_ID_PUBLISH",
          "OWN_CAR_AGE",
          "FLAG_MOBIL",
          "FLAG_EMP_PHONE",
          "FLAG_WORK_PHONE",
          "OCCUPATION_TYPE",
          "CNT_FAM_MEMBERS",
          "REGION_RATING_CLIENT",
          "ORGANIZATION_TYPE",
          "EXT_SOURCE_1",
          "EXT_SOURCE_2",
          "EXT_SOURCE_3",
          "DAYS_LAST_PHONE_CHANGE",
          "AMT_REQ_CREDIT_BUREAU_HOUR",
          "AMT_REQ_CREDIT_BUREAU_MON",
          "AMT_REQ_CREDIT_BUREAU_QRT",
          "AMT_REQ_CREDIT_BUREAU_YEAR",
          "EMPLOYED_SENTINEL",
          "MISSING_COUNT",
          "CREDIT_TERM",
          "CREDIT_GOODS_DIFF_RATIO",
          "INCOME_PER_PERSON",
          "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY",
          "AMT_INCOME_TOTAL_OVER_AMT_CREDIT",
          "DAYS_EMPLOYED_OVER_BIRTH",
          "EXT_MEAN",
          "EXT_MIN",
          "EXT_MAX",
          "EXT_STD",
          "EXT_COUNT",
          "AGE_AT_EMPLOYMENT",
          "ASSUMED_PERIOD_RATE_24",
          "ASSUMED_PERIOD_RATE_36",
          "ASSUMED_PERIOD_RATE_60",
          "TERM_MULTIPLE_6_DISTANCE",
          "TERM_MULTIPLE_12_DISTANCE"
        ],
        "missing": "native"
      },
      "auc": 0.7615744712299796,
      "iterations": [
        1699,
        807,
        1557,
        1895,
        1540
      ],
      "origin": "pass2",
      "prediction_path": "improvements/round2/artifacts/cv/r2_cat_proxies_native_oof.npy"
    }
  ],
  "status": "provisional: requires fixed-iteration second-seed check",
  "selection_scope": "Original development rows only. Historical audit and public labels never tune weights.",
  "fold_gain": [
    0.001655787864397018,
    0.0019313988523183,
    0.001661494075520964,
    0.00020547751690691562,
    0.0011764302447333508
  ],
  "conditional_gain_ci95": [
    0.0006796493413966153,
    0.0019729709423550066
  ]
}
```

### Prospectively recorded frozen-pair simplification rule

Source: `improvements/round2/artifacts/complexity_check_plan.json`.

```json
{
  "original_primary_names": [
    "lgb_tune_15",
    "r2_cat_term_proxies",
    "r2_cat_proxies_native"
  ],
  "original_primary_weights": [
    0.1875,
    0.5625,
    0.25
  ],
  "original_primary_auc": 0.7630891353395803,
  "frozen_pair": {
    "names": [
      "lgb_tune_15",
      "r2_cat_term_proxies"
    ],
    "weights": [
      0.25,
      0.75
    ],
    "auc": 0.7629541355344485,
    "method": "coarse two-model blend"
  },
  "primary_increment_third": 0.0001349998051318746,
  "rule": "If the third model has nonpositive incremental AUC on the second seed and this frozen pair passes the existing primary/secondary gain gates, select the pair. No secondary weight search. Otherwise keep the original decision.",
  "prospective_guard": "No new-candidate second-seed fold result existed when this rule was recorded."
}
```

### Frozen-pair complexity comparison

Source: `improvements/round2/artifacts/complexity_check_results.json`.

```json
{
  "rule": "If the third model has nonpositive incremental AUC on the second seed and this frozen pair passes the existing primary/secondary gain gates, select the pair. No secondary weight search. Otherwise keep the original decision.",
  "prospective_guard": "No new-candidate second-seed fold result existed when this rule was recorded.",
  "pair": {
    "names": [
      "lgb_tune_15",
      "r2_cat_term_proxies"
    ],
    "weights": [
      0.25,
      0.75
    ],
    "auc": 0.7629541355344485,
    "method": "coarse two-model blend"
  },
  "full_secondary_auc": 0.762875657415778,
  "pair_secondary_auc": 0.7628628611099685,
  "third_model_secondary_increment": 1.2796305809525954e-05,
  "pair_primary_gain": 0.0011817166451552064,
  "pair_secondary_gain": 0.00143899681077031,
  "pair_secondary_fold_gain": [
    0.0013876388473670342,
    0.0020459741215798077,
    0.0010614242886028968,
    0.001602293560160506,
    0.0010079148036487018
  ],
  "pair_passes_original_gates": true,
  "simplified": false,
  "weights_retuned": false,
  "caveat": "Two predeclared frozen recipes are compared on reused development folds; this is model selection, not a fresh independent test."
}
```

### Primary development selection

Source: `improvements/round2/artifacts/provisional_selection.json`.

```json
{
  "names": [
    "lgb_tune_15",
    "r2_cat_term_proxies",
    "r2_cat_proxies_native"
  ],
  "weights": [
    0.1875,
    0.5625,
    0.25
  ],
  "auc": 0.7630891353395803,
  "method": "retain best primary pair plus a complementary model",
  "baseline_auc": 0.7617724188892933,
  "development_delta": 0.001316716450287081,
  "models": [
    {
      "name": "lgb_tune_15",
      "spec": {
        "name": "lgb_tune_15",
        "kind": "lgb",
        "features": "engineered",
        "groups": true,
        "params": {
          "num_leaves": 21,
          "min_child_samples": 89,
          "colsample_bytree": 0.6846068413999578,
          "subsample": 0.961965333135664,
          "subsample_freq": 1,
          "reg_lambda": 2.1323824335960286,
          "reg_alpha": 3.687185564401245,
          "max_bin": 255,
          "max_depth": -1
        }
      },
      "auc": 0.7573280608933021,
      "iterations": [
        590,
        639,
        523,
        768,
        456
      ],
      "origin": "pass1",
      "prediction_path": "improvements/artifacts/lgb_tune_15_oof.npy"
    },
    {
      "name": "r2_cat_term_proxies",
      "spec": {
        "name": "r2_cat_term_proxies",
        "kind": "cat",
        "features": "finance",
        "params": {
          "depth": 5,
          "l2_leaf_reg": 8,
          "random_strength": 0.5
        },
        "source": "improvements/round2/adaptive.py",
        "hypothesis": "Isolate the redundant nonlinear rate/term representations; test whether quantization alone explains the finance gain.",
        "columns": [
          "NAME_CONTRACT_TYPE",
          "CODE_GENDER",
          "CNT_CHILDREN",
          "AMT_INCOME_TOTAL",
          "AMT_CREDIT",
          "AMT_ANNUITY",
          "AMT_GOODS_PRICE",
          "NAME_INCOME_TYPE",
          "NAME_EDUCATION_TYPE",
          "NAME_FAMILY_STATUS",
          "NAME_HOUSING_TYPE",
          "REGION_POPULATION_RELATIVE",
          "DAYS_BIRTH",
          "DAYS_EMPLOYED",
          "DAYS_REGISTRATION",
          "DAYS_ID_PUBLISH",
          "OWN_CAR_AGE",
          "FLAG_MOBIL",
          "FLAG_EMP_PHONE",
          "FLAG_WORK_PHONE",
          "OCCUPATION_TYPE",
          "CNT_FAM_MEMBERS",
          "REGION_RATING_CLIENT",
          "ORGANIZATION_TYPE",
          "EXT_SOURCE_1",
          "EXT_SOURCE_2",
          "EXT_SOURCE_3",
          "DAYS_LAST_PHONE_CHANGE",
          "AMT_REQ_CREDIT_BUREAU_HOUR",
          "AMT_REQ_CREDIT_BUREAU_MON",
          "AMT_REQ_CREDIT_BUREAU_QRT",
          "AMT_REQ_CREDIT_BUREAU_YEAR",
          "EMPLOYED_SENTINEL",
          "MISSING_COUNT",
          "CREDIT_TERM",
          "CREDIT_GOODS_DIFF_RATIO",
          "INCOME_PER_PERSON",
          "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY",
          "AMT_INCOME_TOTAL_OVER_AMT_CREDIT",
          "DAYS_EMPLOYED_OVER_BIRTH",
          "EXT_MEAN",
          "EXT_MIN",
          "EXT_MAX",
          "EXT_STD",
          "EXT_COUNT",
          "AGE_AT_EMPLOYMENT",
          "ASSUMED_PERIOD_RATE_24",
          "ASSUMED_PERIOD_RATE_36",
          "ASSUMED_PERIOD_RATE_60",
          "TERM_MULTIPLE_6_DISTANCE",
          "TERM_MULTIPLE_12_DISTANCE"
        ]
      },
      "auc": 0.7622544252863716,
      "iterations": [
        1385,
        1332,
        1637,
        1636,
        1568
      ],
      "origin": "pass2",
      "prediction_path": "improvements/round2/artifacts/cv/r2_cat_term_proxies_oof.npy"
    },
    {
      "name": "r2_cat_proxies_native",
      "spec": {
        "name": "r2_cat_proxies_native",
        "kind": "cat",
        "features": "finance",
        "params": {
          "depth": 5,
          "l2_leaf_reg": 8,
          "random_strength": 0.5
        },
        "source": "improvements/round2/proxy_followup.py",
        "hypothesis": "The proxy-only representation improved screening by 0.00146; combine it with the independently promising native missing policy.",
        "columns": [
          "NAME_CONTRACT_TYPE",
          "CODE_GENDER",
          "CNT_CHILDREN",
          "AMT_INCOME_TOTAL",
          "AMT_CREDIT",
          "AMT_ANNUITY",
          "AMT_GOODS_PRICE",
          "NAME_INCOME_TYPE",
          "NAME_EDUCATION_TYPE",
          "NAME_FAMILY_STATUS",
          "NAME_HOUSING_TYPE",
          "REGION_POPULATION_RELATIVE",
          "DAYS_BIRTH",
          "DAYS_EMPLOYED",
          "DAYS_REGISTRATION",
          "DAYS_ID_PUBLISH",
          "OWN_CAR_AGE",
          "FLAG_MOBIL",
          "FLAG_EMP_PHONE",
          "FLAG_WORK_PHONE",
          "OCCUPATION_TYPE",
          "CNT_FAM_MEMBERS",
          "REGION_RATING_CLIENT",
          "ORGANIZATION_TYPE",
          "EXT_SOURCE_1",
          "EXT_SOURCE_2",
          "EXT_SOURCE_3",
          "DAYS_LAST_PHONE_CHANGE",
          "AMT_REQ_CREDIT_BUREAU_HOUR",
          "AMT_REQ_CREDIT_BUREAU_MON",
          "AMT_REQ_CREDIT_BUREAU_QRT",
          "AMT_REQ_CREDIT_BUREAU_YEAR",
          "EMPLOYED_SENTINEL",
          "MISSING_COUNT",
          "CREDIT_TERM",
          "CREDIT_GOODS_DIFF_RATIO",
          "INCOME_PER_PERSON",
          "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY",
          "AMT_INCOME_TOTAL_OVER_AMT_CREDIT",
          "DAYS_EMPLOYED_OVER_BIRTH",
          "EXT_MEAN",
          "EXT_MIN",
          "EXT_MAX",
          "EXT_STD",
          "EXT_COUNT",
          "AGE_AT_EMPLOYMENT",
          "ASSUMED_PERIOD_RATE_24",
          "ASSUMED_PERIOD_RATE_36",
          "ASSUMED_PERIOD_RATE_60",
          "TERM_MULTIPLE_6_DISTANCE",
          "TERM_MULTIPLE_12_DISTANCE"
        ],
        "missing": "native"
      },
      "auc": 0.7615744712299796,
      "iterations": [
        1699,
        807,
        1557,
        1895,
        1540
      ],
      "origin": "pass2",
      "prediction_path": "improvements/round2/artifacts/cv/r2_cat_proxies_native_oof.npy"
    }
  ],
  "status": "provisional: requires fixed-iteration second-seed check",
  "selection_scope": "Original development rows only. Historical audit and public labels never tune weights.",
  "fold_gain": [
    0.001655787864397018,
    0.0019313988523183,
    0.001661494075520964,
    0.00020547751690691562,
    0.0011764302447333508
  ],
  "conditional_gain_ci95": [
    0.0006796493413966153,
    0.0019729709423550066
  ]
}
```

### Fixed-iteration second-seed check

Source: `improvements/round2/artifacts/stability_results.json`.

```json
{
  "baseline_auc": 0.7614238642991982,
  "candidate_auc": 0.762875657415778,
  "fold_gain": [
    0.0014734192439502802,
    0.0018189609803044293,
    0.0011588644572408935,
    0.001473888073414975,
    0.0012309024211930586
  ],
  "fold_seed": 20261409,
  "early_stopping_on_validation": false,
  "weights_retuned": false,
  "caveat": "A robustness check on development data, not a new independent test; the same development labels were used earlier in selection.",
  "delta": 0.001451793116579836,
  "recommend_new_submission": true,
  "two_seed_diagnostic": {
    "baseline_primary_auc": 0.7617724188892933,
    "baseline_secondary_auc": 0.7614238642991982,
    "baseline_averaged_auc": 0.7625874941483515,
    "candidate_primary_auc": 0.7630891353395803,
    "candidate_secondary_auc": 0.762875657415778,
    "candidate_averaged_auc": 0.7639709612844672,
    "caveat": "Conditional development diagnostic, not independent evidence. The primary seed uses validation early stopping; the secondary seed uses fixed iterations."
  },
  "recommend_two_seed_bagging": true
}
```

### Final frozen choice

Source: `improvements/round2/artifacts/selection.json`.

```json
{
  "names": [
    "lgb_tune_15",
    "r2_cat_term_proxies",
    "r2_cat_proxies_native"
  ],
  "weights": [
    0.1875,
    0.5625,
    0.25
  ],
  "auc": 0.7630891353395803,
  "method": "retain best primary pair plus a complementary model",
  "baseline_auc": 0.7617724188892933,
  "development_delta": 0.001316716450287081,
  "models": [
    {
      "name": "lgb_tune_15",
      "spec": {
        "name": "lgb_tune_15",
        "kind": "lgb",
        "features": "engineered",
        "groups": true,
        "params": {
          "num_leaves": 21,
          "min_child_samples": 89,
          "colsample_bytree": 0.6846068413999578,
          "subsample": 0.961965333135664,
          "subsample_freq": 1,
          "reg_lambda": 2.1323824335960286,
          "reg_alpha": 3.687185564401245,
          "max_bin": 255,
          "max_depth": -1
        }
      },
      "auc": 0.7573280608933021,
      "iterations": [
        590,
        639,
        523,
        768,
        456
      ],
      "origin": "pass1",
      "prediction_path": "improvements/artifacts/lgb_tune_15_oof.npy"
    },
    {
      "name": "r2_cat_term_proxies",
      "spec": {
        "name": "r2_cat_term_proxies",
        "kind": "cat",
        "features": "finance",
        "params": {
          "depth": 5,
          "l2_leaf_reg": 8,
          "random_strength": 0.5
        },
        "source": "improvements/round2/adaptive.py",
        "hypothesis": "Isolate the redundant nonlinear rate/term representations; test whether quantization alone explains the finance gain.",
        "columns": [
          "NAME_CONTRACT_TYPE",
          "CODE_GENDER",
          "CNT_CHILDREN",
          "AMT_INCOME_TOTAL",
          "AMT_CREDIT",
          "AMT_ANNUITY",
          "AMT_GOODS_PRICE",
          "NAME_INCOME_TYPE",
          "NAME_EDUCATION_TYPE",
          "NAME_FAMILY_STATUS",
          "NAME_HOUSING_TYPE",
          "REGION_POPULATION_RELATIVE",
          "DAYS_BIRTH",
          "DAYS_EMPLOYED",
          "DAYS_REGISTRATION",
          "DAYS_ID_PUBLISH",
          "OWN_CAR_AGE",
          "FLAG_MOBIL",
          "FLAG_EMP_PHONE",
          "FLAG_WORK_PHONE",
          "OCCUPATION_TYPE",
          "CNT_FAM_MEMBERS",
          "REGION_RATING_CLIENT",
          "ORGANIZATION_TYPE",
          "EXT_SOURCE_1",
          "EXT_SOURCE_2",
          "EXT_SOURCE_3",
          "DAYS_LAST_PHONE_CHANGE",
          "AMT_REQ_CREDIT_BUREAU_HOUR",
          "AMT_REQ_CREDIT_BUREAU_MON",
          "AMT_REQ_CREDIT_BUREAU_QRT",
          "AMT_REQ_CREDIT_BUREAU_YEAR",
          "EMPLOYED_SENTINEL",
          "MISSING_COUNT",
          "CREDIT_TERM",
          "CREDIT_GOODS_DIFF_RATIO",
          "INCOME_PER_PERSON",
          "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY",
          "AMT_INCOME_TOTAL_OVER_AMT_CREDIT",
          "DAYS_EMPLOYED_OVER_BIRTH",
          "EXT_MEAN",
          "EXT_MIN",
          "EXT_MAX",
          "EXT_STD",
          "EXT_COUNT",
          "AGE_AT_EMPLOYMENT",
          "ASSUMED_PERIOD_RATE_24",
          "ASSUMED_PERIOD_RATE_36",
          "ASSUMED_PERIOD_RATE_60",
          "TERM_MULTIPLE_6_DISTANCE",
          "TERM_MULTIPLE_12_DISTANCE"
        ]
      },
      "auc": 0.7622544252863716,
      "iterations": [
        1385,
        1332,
        1637,
        1636,
        1568
      ],
      "origin": "pass2",
      "prediction_path": "improvements/round2/artifacts/cv/r2_cat_term_proxies_oof.npy"
    },
    {
      "name": "r2_cat_proxies_native",
      "spec": {
        "name": "r2_cat_proxies_native",
        "kind": "cat",
        "features": "finance",
        "params": {
          "depth": 5,
          "l2_leaf_reg": 8,
          "random_strength": 0.5
        },
        "source": "improvements/round2/proxy_followup.py",
        "hypothesis": "The proxy-only representation improved screening by 0.00146; combine it with the independently promising native missing policy.",
        "columns": [
          "NAME_CONTRACT_TYPE",
          "CODE_GENDER",
          "CNT_CHILDREN",
          "AMT_INCOME_TOTAL",
          "AMT_CREDIT",
          "AMT_ANNUITY",
          "AMT_GOODS_PRICE",
          "NAME_INCOME_TYPE",
          "NAME_EDUCATION_TYPE",
          "NAME_FAMILY_STATUS",
          "NAME_HOUSING_TYPE",
          "REGION_POPULATION_RELATIVE",
          "DAYS_BIRTH",
          "DAYS_EMPLOYED",
          "DAYS_REGISTRATION",
          "DAYS_ID_PUBLISH",
          "OWN_CAR_AGE",
          "FLAG_MOBIL",
          "FLAG_EMP_PHONE",
          "FLAG_WORK_PHONE",
          "OCCUPATION_TYPE",
          "CNT_FAM_MEMBERS",
          "REGION_RATING_CLIENT",
          "ORGANIZATION_TYPE",
          "EXT_SOURCE_1",
          "EXT_SOURCE_2",
          "EXT_SOURCE_3",
          "DAYS_LAST_PHONE_CHANGE",
          "AMT_REQ_CREDIT_BUREAU_HOUR",
          "AMT_REQ_CREDIT_BUREAU_MON",
          "AMT_REQ_CREDIT_BUREAU_QRT",
          "AMT_REQ_CREDIT_BUREAU_YEAR",
          "EMPLOYED_SENTINEL",
          "MISSING_COUNT",
          "CREDIT_TERM",
          "CREDIT_GOODS_DIFF_RATIO",
          "INCOME_PER_PERSON",
          "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY",
          "AMT_INCOME_TOTAL_OVER_AMT_CREDIT",
          "DAYS_EMPLOYED_OVER_BIRTH",
          "EXT_MEAN",
          "EXT_MIN",
          "EXT_MAX",
          "EXT_STD",
          "EXT_COUNT",
          "AGE_AT_EMPLOYMENT",
          "ASSUMED_PERIOD_RATE_24",
          "ASSUMED_PERIOD_RATE_36",
          "ASSUMED_PERIOD_RATE_60",
          "TERM_MULTIPLE_6_DISTANCE",
          "TERM_MULTIPLE_12_DISTANCE"
        ],
        "missing": "native"
      },
      "auc": 0.7615744712299796,
      "iterations": [
        1699,
        807,
        1557,
        1895,
        1540
      ],
      "origin": "pass2",
      "prediction_path": "improvements/round2/artifacts/cv/r2_cat_proxies_native_oof.npy"
    }
  ],
  "status": "selected after stability check",
  "selection_scope": "Original development rows only. Historical audit and public labels never tune weights.",
  "fold_gain": [
    0.001655787864397018,
    0.0019313988523183,
    0.001661494075520964,
    0.00020547751690691562,
    0.0011764302447333508
  ],
  "conditional_gain_ci95": [
    0.0006796493413966153,
    0.0019729709423550066
  ],
  "stability": {
    "baseline_auc": 0.7614238642991982,
    "candidate_auc": 0.762875657415778,
    "fold_gain": [
      0.0014734192439502802,
      0.0018189609803044293,
      0.0011588644572408935,
      0.001473888073414975,
      0.0012309024211930586
    ],
    "fold_seed": 20261409,
    "early_stopping_on_validation": false,
    "weights_retuned": false,
    "caveat": "A robustness check on development data, not a new independent test; the same development labels were used earlier in selection.",
    "delta": 0.001451793116579836,
    "recommend_new_submission": true,
    "two_seed_diagnostic": {
      "baseline_primary_auc": 0.7617724188892933,
      "baseline_secondary_auc": 0.7614238642991982,
      "baseline_averaged_auc": 0.7625874941483515,
      "candidate_primary_auc": 0.7630891353395803,
      "candidate_secondary_auc": 0.762875657415778,
      "candidate_averaged_auc": 0.7639709612844672,
      "caveat": "Conditional development diagnostic, not independent evidence. The primary seed uses validation early stopping; the secondary seed uses fixed iterations."
    },
    "recommend_two_seed_bagging": true
  }
}
```

### Generated submission and diagnostic metrics

Source: `improvements/round2/artifacts/final_results.json`.

```json
{
  "submission": "output/submission_round2.csv",
  "sha256": "ca654e22e1f0e4d807456e666d6fd9562d31979dc0f6ed2195491e9a47da9546",
  "rows": 61500,
  "probability_min": 0.0022076076435753995,
  "probability_max": 0.8098346571250177,
  "probability_mean": 0.08842427562417424,
  "models": [
    {
      "name": "lgb_tune_15",
      "weight": 0.1875,
      "seeds": 2
    },
    {
      "name": "r2_cat_term_proxies",
      "weight": 0.5625,
      "seeds": 2
    },
    {
      "name": "r2_cat_proxies_native",
      "weight": 0.25,
      "seeds": 2
    }
  ],
  "full_oof_auc": 0.764430549858415,
  "full_oof_average_precision": 0.24785660726119904,
  "full_oof_log_loss": 0.244405433235763,
  "full_oof_independent": false,
  "recommended_new_recipe": true,
  "two_seed_bagging": true,
  "public_score": null,
  "public_score_note": "User must submit this new CSV; no public improvement is assumed.",
  "existing_public_score": 0.7654,
  "existing_public_csv": "output/submission_improved.csv",
  "recommendation": "A locally validated candidate; submit to obtain its actual public score."
}
```

### Integrity verification

Source: `improvements/round2/artifacts/verification.json`.

```json
{
  "preserved_files": 19,
  "all_preserved_hashes_match": true,
  "splits_disjoint": true,
  "features_ignore_ID_and_TARGET": true,
  "row_batch_invariance": true,
  "train_test_feature_schema_matches": true,
  "hypothetical_rate_formula_verified": true,
  "observed_scores_strictly_positive": true,
  "unseen_categories_handled": true,
  "numeric_native_missing_preserved": true,
  "final": true,
  "selection_unchanged_after_freeze": true,
  "submission_format_valid": true,
  "saved_model_reproduction_byte_identical": true,
  "new_notebooks_fully_executed": true
}
```


## Interpretation limits

- A method can improve one split and fail across folds; such a result is not erased or converted into a general success claim.
- Rate-only and distance-only ablations must be compared with the joint proxy block; a joint gain does not establish a recovered real interest rate.
- First-pass metadata includes explicit settings and pinned code; resolved internal defaults were not retained for every historical screen. Those missing details are not invented.
- New adaptive screen/CV fold artifacts retain resolved parameters and learning curves where available. A small API probe is not a competition performance experiment.
- The first-pass audit and the public score are historical checks. Second-pass development, repeated-seed and full-data OOF numbers are not fresh independent test estimates.
- A new CSV's public/private performance remains unknown until the actual competition evaluates it.
