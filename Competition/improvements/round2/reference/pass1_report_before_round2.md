# Competition improvement report

## Result

The frozen improved model scores **0.755506 ROC-AUC** on the untouched 20% audit,
versus **0.666573** for the tutorial-style five-feature random forest:
an absolute gain of **0.088933**. Both use the same audit rows and development training rows.
The improved AUC's conditional bootstrap 95% interval is 0.746458–0.764901;
the paired gain interval is 0.079682–0.097858.
The hidden competition test score is unknown; the CSV has not been uploaded to Omnicampus.

Final model: **67% cat_lean, 33% lgb_tune_15**, with five stratified training folds per selected model.
Development pooled OOF AUC: **0.761772**.
Full-data diagnostic OOF AUC: **0.762061**. Development labels influenced model selection,
so the untouched audit is the independent performance estimate.

## Competition and data

The supplied README defines binary loan payment difficulty prediction, scored by ROC-AUC.
There are 171,202 labeled rows, 61,500 test rows, 32 customer predictors, and an 8.07% positive rate.
The local instructions give a November 20, 2026 deadline at 01:00 UTC (07:00 Bangladesh time)
and say the **last submitted file** determines the final competition entry. They also require reproducible
code for Honors/Outstanding Student. These statements come from the supplied README, without live platform verification.

All dataset rows are from the supplied train/test CSVs. No external dataset, manual labels,
test-target reconstruction, hand-built target-encoded input features, or online reference code was used.
The local tutorial is credited for the five-feature baseline; new modeling code was written for this project.
Software packages were installed into the existing project `.venv`; no online data was fetched.
SHA-256 checks confirm all three original notebooks and all three input CSVs are unchanged.

The data audit found no duplicated training feature rows. Important missing columns include
`EXT_SOURCE_1` (69.5%), `OWN_CAR_AGE` (66.0%), and `EXT_SOURCE_3` (31.9%).
The employment value 365243 is a sentinel, treated as missing with an indicator.
IDs are sequential and non-overlapping between train and test, and are excluded from models.
An adversarial classifier distinguishing train from test, excluding ID, scores **0.518898 AUC**.
This suggests modest feature shift; it does not rule out hidden target or subgroup shift.

## Validation and search

1. Reserve a seeded, stratified 20% audit before tuning (34,241 rows).
2. Screen candidates on a 60% fit / 20% inner-validation split of all labeled rows.
3. Compare finalists using five-fold stratified CV restricted to the 80% development portion.
4. Choose single models or coarse pairwise probability blends using development OOF predictions only.
   Blending must improve OOF AUC by at least 0.00015 to justify additional complexity.
   A small set of family-diverse triples must add a further 0.00015 to justify a third model.
5. Freeze model choice, blend weights and median tree counts; fit on development and evaluate audit once.
6. Train five final folds on all labeled rows at fixed development-selected tree counts, save each model
   and encoder, and average their test probabilities using the frozen weights.

Categorical vocabularies, imputers, scalers, quantile transforms, splines, category frequencies,
and optional group medians are fitted inside training splits. The test set never fits these transformations.
Class imbalance is handled through the scoring metric and stratification, with class weighting tested
as an explicit variant. No row resampling or thresholding is used in the submission.

**57 screened configurations** cover the tutorial RF, raw/engineered/extended/compact feature sets,
24 seeded Optuna LightGBM trials, shallow trees, two class weights, native-categorical CatBoost depths,
three histogram gradient boosting variants, linear logistic regression, nonlinear spline logistic regression,
group-relative features, and feature pruning. 10 finalists/ablations undergo five-fold development validation.

Feature engineering includes income-to-credit and annuity ratios, credit term, credit-versus-goods-price
differences, per-family amounts, employment/age and other lifetime ratios, external-score summaries,
pairwise products and differences, missingness indicators, and fold-fitted category/group summaries.

### Five-fold development results

| Model | OOF AUC | Fold SD | Median trees |
| --- | --- | --- | --- |
| cat_lean | 0.760790 | 0.003068 | 1529 |
| cat_lean_depth6 | 0.760148 | 0.003514 | 1315 |
| cat_depth4 | 0.759728 | 0.003442 | 1404 |
| lgb_tune_12 | 0.757388 | 0.004126 | 601 |
| lgb_tune_15 | 0.757328 | 0.003944 | 590 |
| lgb_top_70 | 0.756960 | 0.004131 | 491 |
| lgb_engineered | 0.756102 | 0.003752 | 375 |
| hgb_20 | 0.753292 | 0.003445 | 250 |
| lgb_raw | 0.749947 | 0.004077 | 356 |
| spline_0.1 | 0.748304 | 0.002872 | 1 |

### Best inner-screen scores

| Model | Inner AUC |
| --- | --- |
| cat_depth4 | 0.748959 |
| cat_lean | 0.748493 |
| cat_lean_depth6 | 0.748028 |
| cat_depth5 | 0.747660 |
| cat_lean_depth4 | 0.747615 |
| cat_depth7 | 0.747337 |
| cat_depth6 | 0.747212 |
| lgb_tune_15 | 0.747151 |
| lgb_tune_12 | 0.746578 |
| lgb_top_70 | 0.746336 |
| lgb_tune_22 | 0.746107 |
| lgb_top_55 | 0.745922 |

Inner-screen scores are used for tuning, not as independent claims of generalization. Detailed
trials, fold scores, selection configuration and prediction arrays are in `improvements/artifacts`.
The unengineered/engineered ablation uses the same base LightGBM settings so its fold comparison
isolates the feature change more fairly than comparing separately tuned models.

## Diagnostics and stopping decision

The same-settings feature ablation improves five-fold OOF AUC from
0.749947 to 0.756102.
Compact depth-5 CatBoost scores 0.760790, above the larger-feature
depth-4 version (0.759728) and the deeper compact version
(0.760148). Its strongest final-fold importance features are
external-score mean, credit-to-annuity term, external-score minimum/maximum and customer age.
The best three-model blend scores 0.761845, only
0.000072 above the selected two-model blend, below the additional-model threshold.

The new notebooks contain missingness and distribution checks, ROC/precision-recall curves,
calibration plots, subgroup audit metrics and mean-fold feature importances. Average precision,
log loss and Brier score are recorded alongside AUC. Subgroup results are descriptive and may be noisy.

The search tested substantially different models, representations and regularization choices,
then checked whether simple blends improved five-fold OOF performance. Class weights,
categorical interactions, compact features and feature pruning were evaluated rather than assumed helpful.
After these comparisons, further small tuning gains would be difficult to distinguish from development
overfitting. The independent audit was evaluated only after selection; no post-audit tuning was performed.
This is a defensible stopping point, not proof of a global optimum or a guaranteed leaderboard result.

## Deliverables and verification

- `output/submission_improved.csv`: 61,500 rows, exact sample ID order, finite model probabilities in [0,1].
- `01_competition_data_audit.ipynb`: executed competition/data audit.
- `02_improved_models_and_submission.ipynb`: executed experiment report and exact model-based reproduction.
- `improvements/experiment.py` and companion scripts: complete reproducible training/search workflow.
- `improvements/models`: persisted fold models and training-fitted encoders.
- `improvements/requirements-modeling.txt`: portable pinned modeling dependencies.
- `output/competition_improved_reproduction.zip`: new notebooks, source, models, evidence and submission.

Submission SHA-256: `71cd8588031deef62dadd8eeddb8e33965cbe42b6e0fc25c41e673271b08c616`.
The modeling notebook reloads all saved models and reproduces the submission byte-for-byte.
Both new notebooks execute successfully in the project venv. Integrity checks cover unchanged
originals, disjoint splits, feature independence from labels and IDs, row/batch invariance,
unseen categories, CSV structure and exact reproduction.

## Reproduction

Place the supplied `input` folder and column dictionary under `Competition`; neither training data nor
the venv is duplicated into the ZIP. Use the existing local venv, or recreate a Python 3.12 environment
and install `improvements/requirements-modeling.txt`. The original conda environment files are also retained.
Then run from `Competition`:

```sh
.venv/bin/python improvements/experiment.py screen --trials 24
.venv/bin/python improvements/supplement.py
.venv/bin/python improvements/refine.py
.venv/bin/python improvements/select_features.py
.venv/bin/python improvements/refine_cat.py
.venv/bin/python improvements/experiment.py cv
.venv/bin/python improvements/experiment.py audit
.venv/bin/python improvements/experiment.py final
```

For fast prediction-only reproduction, execute the second new notebook. To use the supplied kernelspec,
`improvements/execute_notebook.py` runs it in the project venv without changing global Jupyter settings.
The complete raw `pip freeze` includes conda build paths; use the portable modeling requirements for a new environment.

Upload the improved CSV to Omnicampus and check that its scoring timestamp updates. Upload the reproduction
ZIP as code evidence if required. The local test data have no labels, so local validation cannot reveal the hidden test AUC.
