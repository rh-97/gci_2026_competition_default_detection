# Competition improvement report

## Current result and files

The confirmed public score is **0.7654**, displayed rank **1,094** (`hasanRocky`), for
`output/submission_improved.csv`. This was supplied in a screenshot and explicitly confirmed by the user.
Rank is a snapshot. The private/full-test score remains unknown.

Second-pass recommendation: **A locally validated candidate; submit to obtain its actual public score.**

New CSV: [`output/submission_round2.csv`](output/submission_round2.csv), 61,500 rows.
Its actual public score is **unknown until uploaded**; local AUCs below are not leaderboard scores.
The original 0.7654 CSV and original reproduction ZIP remain unchanged as fallbacks.

The supplied README/tutorial deck gives the deadline as **November 20, 2026, 01:00 UTC (07:00 Bangladesh time)**
and requires a code ZIP for Honors/Outstanding consideration. These are local provided instructions, not a live platform check.
The reviewed deck and extracted text are retained under `improvements/round2/reference`.

The new model recipe passed the declared two-seed gate. The final model bank averages two fold seeds per family, following the declared averaging diagnostic.

Final mixture: **18.75% lgb_tune_15, 56.25% r2_cat_term_proxies, 25.00% r2_cat_proxies_native**.

| Evaluation | Frozen first-pass blend | Provisional second-pass candidate | Difference |
| --- | --- | --- | --- |
| Primary development OOF (selection) | 0.761772 | 0.763089 | +0.001317 |
| Second development fold seed (fixed iterations/weights) | 0.761424 | 0.762876 | +0.001452 |
| Two-seed development averaging (diagnostic) | 0.762587 | 0.763971 | +0.001383 |

Primary per-fold gains: `[0.001655787864397018, 0.0019313988523183, 0.001661494075520964, 0.00020547751690691562, 0.0011764302447333508]`.
Second-seed per-fold gains: `[0.0014734192439502802, 0.0018189609803044293, 0.0011588644572408935, 0.001473888073414975, 0.0012309024211930586]`.
Conditional paired-bootstrap interval for the primary gain: `[0.0006796493413966153, 0.0019729709423550066]`.
This conditions on fitted OOF predictions and excludes training/selection uncertainty.

Full-data final OOF AUC is **0.764431**, a diagnostic after development-based selection.
It is not an independent test estimate. Full-data OOF AP is 0.247857
and log loss is 0.244405.

## What was done

The first pass screened 57 configurations, validated 10 finalists and produced the public-scored CSV.
This pass ran **34 additional screening configurations** (34 completed,
0 execution failures), then 5 new common-fold CV models and the frozen second-seed check.
The combined ledger contains **91 trial records**. It records negative results, not only winners.

The detailed record is [`EXPERIMENT_LOG.md`](EXPERIMENT_LOG.md), with full machine-readable versions in
`improvements/round2/artifacts/complete_experiment_ledger.json` and `.csv`.
Each trial states its hypothesis, exact explicit configuration, representation, source file,
validation reference, score, iteration count, runtime, interpretation and evidence location.
Initial first-pass rationales are explicitly retrospective; second-pass plans/events record hypotheses before their execution.

New notebooks:

- [`03_round2_experiment_journal.ipynb`](03_round2_experiment_journal.ipynb): baseline equivalence, feature formulas, all screens, ablations, defaults, development-only descriptive plots and per-trial interpretation.
- [`04_round2_validation_and_submission.ipynb`](04_round2_validation_and_submission.ipynb): common-fold CV, frozen second-seed check, learning curves, model bank and byte-identical saved-model prediction.

All five notebooks that existed at the start of this pass are preserved unchanged. Only new notebooks were created.
The first-pass report before this pass is preserved in `improvements/round2/reference/pass1_report_before_round2.md`.

## What worked, what did not, and why

### Financial structure: isolate components instead of adding everything

Old compact CatBoost inner AUC: **0.748493**.
Full finance additions: **0.749082**.
Payment-burden/household block alone: **0.747691**.
Rate/term-proxy block alone: **0.749952**.

Screening identified the joint proxy block as promising, rather than justifying every added amount or household ratio.
Rate-only AUC was 0.748473; distance-only AUC was 0.748766.
Neither reproduced the joint block's gain alone. Common-fold and second-seed checks determine whether that recipe is retained.
The proxy block consists of hypothetical rate transforms under assumed 24/36/60 payment periods and distances to 6/12 multiples in credit/annuity.
These do **not** recover actual loan schedules or interest rates. They re-express information already present in the supplied data.
Rate transforms are monotonic functions of the payment ratio; distance features expose non-monotonic patterns.
Finite tree depth and numeric quantization make representations matter even without new information.
That is a plausible learning explanation, not proof of a causal financial mechanism.

Development-only binned default plots show non-monotonic associations, and feature-only development/test KS differences are about 0.007–0.008 for the loan-ratio/distance variables.
The plots and count tables are retained under `improvements/round2/artifacts/loan_structure_*`.
The plots are descriptive after exploration, with no adjustment for confounding or selection.

### Missing data and categorical learning

Native numeric missing bins screened at **0.748981**, versus the old -999-sentinel policy at **0.748493**.
Finance plus native missing bins scored **0.749235**.
Improvements were not simply additive. A -999 sentinel can collide with real negative date offsets, and bin construction can differ with native missing values; the score does not isolate those mechanisms.

The saved baseline actually uses MVS bootstrap and categorical-combination complexity 4.
A five-tree, 300-row parameter preflight found that bagging_temperature alone still resolved to MVS.
The explicitly Bayesian follow-up scored **0.747148** and did not beat the column-sampling MVS variant.
One-hot threshold changes and restricting categorical combinations were tested rather than assumed better.
Resolved parameters and learning curves are preserved where available.

### Other algorithms and regularization

XGBoost was added as an independent algorithm family. Its best original/compact screen was weaker than CatBoost,
but finance features raised its score to **0.747225**.
It was retained for common-fold and complementarity checks rather than dismissed solely on individual AUC.
Linear-leaf LightGBM did not improve its screen. Stronger/weaker CatBoost leaf shrinkage,
more numeric borders, Ordered boosting, column sampling and explicit Bayesian bootstrap were all recorded, including the negative outcomes.

The following are the best **recorded primary-grid** pairs with the lead proxy CatBoost:

| Helper | Individual AUC | Best recorded pair AUC | Helper weight |
| --- | --- | --- | --- |
| lgb_tune_15 | 0.757328 | 0.762954 | 25.00% |
| r2_xgb_finance | 0.758883 | 0.762948 | 25.00% |
| r2_lgb_smooth_cats | 0.758417 | 0.762891 | 25.00% |
| r2_cat_proxies_native | 0.761574 | 0.762566 | 33.33% |
| cat_lean | 0.760790 | 0.762541 | 25.00% |
| r2_cat_native_missing | 0.760561 | 0.762517 | 25.00% |

The old LightGBM and XGBoost helpers were effectively tied at this precision. Individual AUC alone did not determine the best mixture;
calibration and correlated errors can also matter. This comparison does not establish universal algorithm superiority.
A balanced-helper probe also tested sharing helper weight between LightGBM and XGBoost while preserving the lead model's weight.
It did not beat the frozen primary candidate and did not trigger another validation cycle.

The patience/cap control scored **0.748493**.
Its maximum prediction difference from the original compact CatBoost was **0.0**.
This checks whether a longer stopping budget, rather than the intended feature/parameter change, accounts for the gain.

### Common-fold results

| Model | OOF AUC | Fold SD | Median trees |
| --- | --- | --- | --- |
| r2_cat_term_proxies | 0.762254 | 0.003154 | 1568 |
| r2_cat_proxies_native | 0.761574 | 0.003320 | 1557 |
| r2_cat_native_missing | 0.760561 | 0.003161 | 1496 |
| r2_xgb_finance | 0.758883 | 0.003739 | 1119 |
| r2_lgb_smooth_cats | 0.758417 | 0.003887 | 605 |

### Every new screening result

| Experiment | Inner AUC | Delta vs old CatBoost | Seconds |
| --- | --- | --- | --- |
| r2_cat_term_proxies | 0.749952 | +0.001460 | 197.4 |
| r2_cat_proxies_native | 0.749647 | +0.001155 | 226.0 |
| r2_cat_proxies_rsm075 | 0.749288 | +0.000795 | 154.9 |
| r2_cat_finance_tuned | 0.749273 | +0.000781 | 209.0 |
| r2_cat_finance_native | 0.749235 | +0.000743 | 207.0 |
| r2_cat_finance | 0.749082 | +0.000590 | 177.3 |
| r2_cat_native_missing | 0.748981 | +0.000489 | 225.4 |
| r2_cat_distances_only | 0.748766 | +0.000273 | 229.3 |
| r2_cat_combined | 0.748670 | +0.000177 | 196.5 |
| r2_cat_rsm075 | 0.748607 | +0.000115 | 168.3 |
| r2_cat_slow | 0.748572 | +0.000079 | 232.2 |
| r2_cat_baseline | 0.748493 | +0.000000 | 85.5 |
| r2_cat_budget_control | 0.748493 | +0.000000 | 139.8 |
| r2_cat_rates_only | 0.748473 | -0.000019 | 199.5 |
| r2_cat_onehot64 | 0.748193 | -0.000300 | 49.5 |
| r2_cat_ctr2 | 0.748095 | -0.000397 | 215.8 |
| r2_cat_onehot10 | 0.748004 | -0.000489 | 96.0 |
| r2_cat_ctr1 | 0.747827 | -0.000665 | 122.1 |
| r2_cat_ordered | 0.747732 | -0.000761 | 244.2 |
| r2_cat_borders512 | 0.747731 | -0.000762 | 166.9 |
| r2_cat_burden | 0.747691 | -0.000801 | 223.8 |
| r2_cat_strong_l2 | 0.747663 | -0.000829 | 179.3 |
| r2_lgb_smooth_cats | 0.747658 | -0.000835 | 18.0 |
| r2_cat_missing | 0.747589 | -0.000903 | 186.0 |
| r2_cat_weak_l2 | 0.747569 | -0.000924 | 150.6 |
| r2_xgb_finance | 0.747225 | -0.001268 | 82.8 |
| r2_cat_bayesian_rsm075 | 0.747148 | -0.001345 | 215.5 |
| r2_cat_risk | 0.746813 | -0.001680 | 146.7 |
| r2_lgb_finance | 0.746487 | -0.002005 | 19.0 |
| r2_xgb_d3 | 0.745542 | -0.002951 | 46.9 |
| r2_xgb_lean | 0.745215 | -0.003278 | 27.4 |
| r2_xgb_d4 | 0.745160 | -0.003332 | 34.7 |
| r2_xgb_d5 | 0.744544 | -0.003948 | 33.0 |
| r2_lgb_linear | 0.743766 | -0.004727 | 9.1 |

## Validation discipline and stopping decision

All screening, feature choices and weights use the original development rows only.
Common primary folds use validation AUC early stopping. New recipes must improve primary pooled OOF AUC by at least 0.0002.
The second fold seed fixes both weights and median tree counts, passes no validation labels to training/early stopping,
and requires positive pooled gain with at least three positive folds. This is a robustness check on reused development rows, not a fresh untouched test.

The previously evaluated 20% audit remains historical: first-pass AUC **0.755506** versus **0.666573** for the tutorial RF,
with paired gain interval **0.079682–0.097858**. It was not used for second-pass tuning or given a new independence claim.
Public feedback is the single known 0.7654 score, not a sequence of per-trial leaderboard probes.

The two-seed averaging diagnostic is recorded in `stability_results.json`. It had to beat the better individual seed by more than 0.00015 for both baseline and candidate before doubling the final bank.
When the third model's primary increment was below 0.00015, a prospective rule compared the frozen best pair with the triple.
The rule could simplify only if the third model's secondary increment was nonpositive and the pair passed the original gain gates.
This chooses between two fixed recipes, without a secondary weight search; original winner snapshots are preserved.
The third model's incremental second-seed AUC was **+0.00001280**,
so it was retained under the recorded rule. This margin is tiny and is not evidence of a statistically established additional benefit.
Most of the recipe gain comes from the term-proxy representation; the frozen pair remains a nearly tied, simpler alternative.
The entire choice was frozen before full-data fitting. Final OOF scores were not used to retune it.

This pass followed the positive feature hypothesis into component ablations and combinations,
tested materially different model families and regularization, and checked whether the gains survived changed folds.
Further tiny gains on the same selection data could be noise. The result is a locally justified candidate or explicit fallback,
not a guarantee of a global optimum or higher hidden public/private AUC.

## Integrity, constraints and reproducibility

- Only the supplied train/test rows were used. No online dataset, recovered test labels, pretrained weights or manual predictions.
- All training and notebook execution used the project `.venv`. XGBoost was a software-only dependency installation.
- Original CSVs, all pre-existing notebooks, first-pass source, the public-scored CSV and its ZIP are checked against preserved SHA-256 hashes.
- Feature tests cover ID/target independence, row/batch invariance, train/test schema, unknown categories, native missing values and the hypothetical-rate equation.
- The final 61,500 probabilities are finite, in [0,1], and match the exact sample ID order.
- Saved-model prediction reproduces the new CSV byte-for-byte. Both new notebooks execute successfully.
- The new selection checksum and implementation hash are frozen before final fitting.

New CSV SHA-256: `ca654e22e1f0e4d807456e666d6fd9562d31979dc0f6ed2195491e9a47da9546`.
Original public-scored CSV SHA-256: `71cd8588031deef62dadd8eeddb8e33965cbe42b6e0fc25c41e673271b08c616`.

### Reproduce the complete pass

From `Competition`, retaining the supplied `input` directory and first-pass artifacts:

```sh
.venv/bin/python improvements/round2/round2.py screen
.venv/bin/python improvements/round2/adaptive.py
.venv/bin/python improvements/round2/budget_control.py
.venv/bin/python improvements/round2/proxy_followup.py
.venv/bin/python improvements/round2/secondary_metrics.py
.venv/bin/python improvements/round2/proxy_eda.py
.venv/bin/python improvements/round2/validate.py cv
.venv/bin/python improvements/round2/validate.py select
.venv/bin/python improvements/round2/complementarity.py
.venv/bin/python improvements/round2/balanced_probe.py
.venv/bin/python improvements/round2/validate.py stability
.venv/bin/python improvements/round2/check_complexity.py
.venv/bin/python improvements/round2/finalize.py train_final
.venv/bin/python improvements/round2/finalize.py reproduce
.venv/bin/python improvements/round2/document.py
```

For fast prediction-only replay, run notebook 04 or `finalize.py reproduce`.
`requirements-round2.txt` and `artifacts/environment.json` record exact package versions.
The new reproduction ZIP includes source, notebooks, models, documentation, evidence and the preserved original ZIP for provenance.
It excludes the venv and input CSVs; use the originally supplied data when reproducing.

Upload only the intended CSV to Omnicampus and check the scoring timestamp. The supplied competition README says the **last submitted file** determines the final entry.
Report the new public score against this exact CSV checksum before treating it as a leaderboard improvement.
