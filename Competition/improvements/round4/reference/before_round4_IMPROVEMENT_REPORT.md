# Competition improvement report

## Current recommendation

**The submitted round-three bagged recipe achieved public AUC 0.76824, displayed rank 518.**

| Submission | Reported public AUC | Rank snapshot | Gain over previous |
| --- | --- | --- | --- |
| First pass | 0.76540 | 1,094 | — |
| Round two | 0.76756 | 568 | +0.00216 |
| Round three, bagged | 0.76824 | 518 | +0.00068 |

The user explicitly confirmed submitting `output/submission_round3_bagged.csv` and supplied the leaderboard screenshot. Its local SHA-256 matches the frozen prediction file. The public-score gain is **+0.00068** over round two and **+0.00284** over the first pass. Ranks are snapshots. Attribution of the round-two score to its CSV follows the earlier conversation; the round-three filename is explicitly confirmed. The private/full-test score remains unknown. This feedback was recorded after model selection, final fitting and submission generation; it did not tune parameters or weights. Evidence is in `improvements/round3/artifacts/round3_public_result.json`. The observed gain supports the entire submitted recipe; it does not isolate the marginal contribution of the third seed.

Recommended CSV: [`output/submission_round3_bagged.csv`](output/submission_round3_bagged.csv).
SHA-256: `7d933ea1e9bffea4e3bf034a81a8ece315655dcebdeb9408682d159d60bbfb02`.

The recommended bank contains **75 model instances**. This pass fitted 45 new instances and reused 30 existing instances. Family weights are fixed; folds and seeds are averaged equally within each family.

Executed notebooks and frozen training-result JSON files retain their pre-submission score fields. Post-submission
feedback is recorded separately so those historical records remain unchanged.

All seven notebooks present before this pass, prior-pass source, supplied CSVs and prior submissions are unchanged.
The project `.venv` was used throughout. No external rows, pretrained weights, recovered labels or pseudo-labels were used.

## Why another pass was warranted

The prior stopping statement was too strong: finishing planned experiments did not exhaust every reasonable approach.
Most earlier parameter tuning preceded discovery of the better loan-proxy representation.
This pass retunes that representation, isolates further transformations, tests compact-representation alternative learners,
and compares prediction-combination methods. The plan and promotion/gating rules were recorded before fitting.
Quantization/component follow-ups respond to initial screens; the pair-grid correction and seed-averaging check
are separately recorded amendments. These are adaptive research decisions, with their timing and evidence retained.

Plan: [`improvements/round3/PLAN.md`](improvements/round3/PLAN.md).
Full third-pass journal: [`ROUND3_EXPERIMENT_LOG.md`](ROUND3_EXPERIMENT_LOG.md).
Earlier experiment journal: [`EXPERIMENT_LOG.md`](EXPERIMENT_LOG.md).
The complete earlier report is preserved at [`improvements/round3/reference/before_round3_IMPROVEMENT_REPORT.md`](improvements/round3/reference/before_round3_IMPROVEMENT_REPORT.md).

## What was tested and how decisions were made

This pass screened **28 configurations**: 28 completed, 0 failed.
The prior passes screened 91 configurations; the running screening total is **119** including controls.
Prediction-combination grids and validation refits are recorded separately, rather than inflated into the configuration count.
The combined machine ledger is `improvements/round3/artifacts/complete_experiment_ledger.json` (and `.csv`);
the three auxiliary meta-learning probes are explicitly labeled separately from the main screening configurations.

The exact previous proxy control reproduced its inner predictions with maximum absolute difference **0.0**.
All screens used the original, repeatedly explored inner split. Promotion required an inner blend gain >=0.00010 over
the **complete** current mixture, with at most two CatBoost, one other tree and one neural finalist.
Promoted: `['r3_cat_feature_b512', 'r3_cat_signed', 'r3_lgb_proxy']`.

Parameter tests covered depth, step size, shrinkage, numeric quantization, positive-class weighting,
asymmetric tree growth, missing-value treatment and fold-fitted group aggregates.
Feature tests isolated signed term residuals/categories, extra assumed payment periods, categorical crosses,
and the larger original feature set. Extra rate transforms and term categories are representations of supplied values;
they do not recover actual interest rates or schedules.

The scratch-trained neural models used training-fold median imputation/missing indicators, quantile normalization,
one-hot categoricals and small ReLU networks. Alternative models were evaluated for complementary errors,
not only individual AUC. Every exact configuration, metric, learning curve, resolved setting and interpretation is retained.

### Every screen

| Experiment | Individual inner AUC | Best inner blend gain | Retained iterations | Seconds |
| --- | --- | --- | --- | --- |
| r3_lgb_proxy | 0.748054 | +0.000484 | 757 | 17.4 |
| r3_cat_feature_b512 | 0.750854 | +0.000476 | 1851 | 192.8 |
| r3_lgb_proxy_smooth | 0.748929 | +0.000455 | 876 | 17.4 |
| r3_cat_signed | 0.750907 | +0.000426 | 1528 | 195.1 |
| r3_cat_borders1024 | 0.750539 | +0.000316 | 2072 | 194.8 |
| r3_cat_engineered_proxy | 0.750087 | +0.000315 | 1802 | 231.0 |
| r3_cat_depth4_b512 | 0.750716 | +0.000297 | 2176 | 168.9 |
| r3_cat_native_b512 | 0.750487 | +0.000257 | 1973 | 202.0 |
| r3_cat_borders512 | 0.750833 | +0.000257 | 1621 | 181.5 |
| r3_cat_signed_only | 0.750268 | +0.000232 | 1810 | 175.7 |
| r3_cat_groups | 0.749941 | +0.000228 | 1998 | 222.2 |
| r3_cat_median | 0.749023 | +0.000167 | 1488 | 164.7 |
| r3_cat_depthwise | 0.749087 | +0.000155 | 474 | 56.4 |
| r3_xgb_proxy | 0.746976 | +0.000148 | 1494 | 32.5 |
| r3_cat_depth7 | 0.749315 | +0.000140 | 1355 | 187.4 |
| r3_cat_weight2 | 0.750149 | +0.000123 | 1335 | 154.9 |
| r3_cat_depth4 | 0.750398 | +0.000115 | 2194 | 175.7 |
| r3_cat_loan_b512 | 0.750135 | +0.000097 | 1656 | 173.9 |
| r3_cat_depth6 | 0.749610 | +0.000037 | 1243 | 140.6 |
| r3_cat_scores_b512 | 0.749516 | -0.000006 | 1568 | 154.0 |
| r3_mlp_wide | 0.734561 | -0.000009 | 49 | 23.1 |
| r3_cat_rates | 0.749557 | -0.000016 | 1452 | 168.5 |
| r3_cat_crosses | 0.749644 | -0.000031 | 1578 | 241.1 |
| r3_cat_slow | 0.749811 | -0.000031 | 2811 | 282.5 |
| r3_cat_l2_30 | 0.749268 | -0.000038 | 1835 | 197.3 |
| r3_cat_term_categories | 0.749123 | -0.000055 | 1655 | 186.6 |
| r3_cat_baseline | 0.749952 | -0.000076 | 1480 | 82.1 |
| r3_mlp_small | 0.727176 | -0.000296 | 15 | 8.8 |

### Common-fold validation

| New model | Development OOF AUC | Fold SD | Median iterations |
| --- | --- | --- | --- |
| r3_cat_signed | 0.762850 | 0.003098 | 1312 |
| r3_cat_feature_b512 | 0.762662 | 0.003567 | 1619 |
| r3_lgb_proxy | 0.759217 | 0.003562 | 517 |

### What worked and what did not

The joint signed-residual/rounded-category block scored **0.750907**,
versus the proxy control **0.749952**. Signed residuals alone scored
**0.750268** and rounded categories alone **0.749123**.
The joint result is not explained by categories alone. A plausible mechanism is that coarse categorical buckets
and within-bucket residuals expose interactions to finite trees; this is an interpretation, not a causal finding
or evidence of real payment schedules.

Global 512-border quantization scored **0.750833**. Applying 512 borders only to
loan features scored **0.750135**, and only to score features **0.749516**.
Neither reproduced the global gain. Raising all borders to 1024 scored **0.750539**;
more resolution was not uniformly better. The joint term block with 512 borders screened slightly below
the default-border version individually, and their CV ordering also favored the default-border model.
Both can still contribute because their prediction errors differ. The retained recipe is chosen by common-fold
blend performance, not by an isolated interpretation of the screen.

The compact LightGBM finalist improved its individual development score over the old LightGBM helper,
but did not enter the winning primary recipe. Individual strength and contribution to an existing ensemble
are different comparisons. The two neural recipes were much weaker and failed to improve a screened blend.
Their learning curves stopped before the epoch cap, so this run does not attribute the weak result simply
to hitting the configured maximum. It also does not rule out better neural architectures or optimization.

Depth-four/depth-seven tree recipes also changed shrinkage, and the neural recipes changed both width and
regularization; those comparisons cannot isolate a single parameter's causal effect. Exact parent comparisons,
settings, retention decisions and negative results are recorded for each trial in the journal.

### Blend methods using existing predictions

| Method; same current families and weights | Primary OOF AUC | Previously inspected secondary OOF AUC |
| --- | --- | --- |
| probability | 0.763089 | 0.762876 |
| log_odds | 0.763044 | 0.762852 |
| percentile | 0.763026 | 0.762856 |

This checks the method on the same family bank and weights. Probability averaging beat these two alternative
methods in the initial diagnostic. Additional recorded blend probes with new finalists are in
`improvements/round3/artifacts/blend_candidates.json`.
Percentile scores are ranking transforms, not calibrated default probabilities. Their primary OOF empirical CDFs
use predictions only and are frozen for later checks and inference.

Three cross-fitted logistic meta-model probes were also tested. Best screened blend gain: +0.000002. Fully nested follow-up warranted under its recorded rule: False. These probes are not fully nested: the base OOF features can indirectly use other meta-validation targets. They cannot justify a submission. Exact coefficients and diagnostics are retained in `stacking_probe.json`.

A late read-only check tested 12 previously fitted OOF helpers against the frozen third-pass winner, using six fixed blends each. The best helper was `r2_xgb_finance`, with primary gain +0.000092. It did not reach the predeclared 0.00020 threshold for a new validation branch. Older histogram boosting, spline, CatBoost, LightGBM and XGBoost predictions were therefore examined rather than silently discarded. Every blend and its alignment check is retained in `stored_helper_probe.json`; the prospective late plan is `STORED_HELPER_PLAN.md`. This adaptive check is not independent evidence and did not alter the frozen recipe.

## Frozen decision and evidence

Chosen representation of predictions: `probability`.
Names: `['round2_reference', 'r3_cat_feature_b512', 'r3_cat_signed']`. Weights: `[0.5, 0.25, 0.25]`.
The atomic `round2_reference` is 18.750% lgb_tune_15, 56.250% r2_cat_term_proxies, 25.000% r2_cat_proxies_native.
Expanded family weights: 9.375% lgb_tune_15, 28.125% r2_cat_term_proxies, 12.500% r2_cat_proxies_native, 25.000% r3_cat_feature_b512, 25.000% r3_cat_signed.
The primary advantage over the best recorded recipe with fewer new families was +0.000135. That alternative uses a different prediction transform, so this is not a clean one-factor ablation. The margin is small and does not establish a separately significant benefit for every additional family. The whole frozen recipe, not each marginal component, is subject to the deployment gates. With that simpler primary recipe held fixed, descriptive winner-minus-simpler gains were fixed_confirmation +0.000188, secondary +0.000414, two_seed_average +0.000196. These diagnostics did not change selection.

| Evaluation | Current round-two recipe | Frozen third-pass recipe | Gain |
| --- | --- | --- | --- |
| Primary development selection | 0.763089 | 0.763723 | +0.000634 |
| New fold seed; fixed iterations | 0.762592 | 0.763438 | +0.000846 |
| Matching two-seed bank | 0.763971 | 0.764584 | +0.000613 |
| Matching three-seed diagnostic | 0.764196 | 0.764803 | +0.000607 |
| Proposed bank vs current bank (development) | 0.763971 | 0.764803 | +0.000833 |

| Prediction comparison | Observed gain | Conditional paired 95% interval |
| --- | --- | --- |
| primary | +0.000634 | [+0.000306, +0.000990] |
| confirmation | +0.000846 | [+0.000517, +0.001156] |
| two_seed | +0.000613 | [+0.000334, +0.000858] |

Primary per-fold gains: `[0.0007927774701395052, 0.00044416551709702823, 0.0005978425830635015, 0.0004573670883321057, 0.0009047157033553743]`.
Confirmation per-fold gains: `[0.0005013251976125899, 0.0007489511800685689, 0.0009191706230518015, 0.001275702852999716, 0.0007524485548534576]`.

The primary selection gate required >=0.00020 AUC improvement.
The new-fold-seed check used fixed iteration counts, no validation early stopping, and frozen weights/transforms;
it required positive pooled gain and at least four positive folds out of five.
The matching two-seed comparison additionally required >=0.00020 gain over the current two-seed recipe.
Earlier failing gates prevent unnecessary final fitting.

A primary-grid review added missing direct new/new and old/new family pairs before the corrected winner's
confirmation. The interrupted first confirmation was not consulted; its evidence and exact original source/freeze
are retained under `improvements/round3/reference/selection_before_pair_extension`. The corrected primary winner was frozen before
using the fresh confirmation seed `20262209`. These seed values are random integers, not dates.

The prospective three-seed averaging gate passed. Reference increment +0.000225, candidate increment +0.000219. The rule required >=0.00020 increment for both banks, >=0.00020 recipe gain at three seeds, and positive increments in at least four of five primary row groups for both. No seed subsets or weights were searched. The recommended CSV uses three equally weighted seeds per family; the two-seed CSV is preserved. Plan and evidence: `BAGGING_PLAN.md`, `bagging_probe.json` and `bagging_final_results.json`.

Final full-data OOF metrics (diagnostic after selection): `{"auc": 0.7650709143402641, "average_precision": 0.248402241005085, "log_loss": 0.24424449387026184, "brier": 0.06751501960492942}`. These are not independent test scores. The preserved [two-seed CSV](output/submission_round3.csv) has full-data OOF AUC 0.765094089, versus 0.765070914 for three seeds (difference -0.000023175). This essentially tied diagnostic does not confirm an extra full-data AUC benefit from the third seed. AP, log loss and Brier improve slightly with three seeds. The recommendation follows the predeclared development gate; this diagnostic did not retune the policy. Both new CSVs remain available.

Confirmation changes the partition of previously explored labels; it is a robustness check, not an untouched test.
The historical audit is not used as a fresh test. Full-data OOF does not retune selection.
Conditional paired-bootstrap diagnostics, if present, are in `conditional_uncertainty.json`; they condition on fitted
predictions and exclude search/fitting uncertainty. They are not search-adjusted significance tests.

## Error analysis, interpretation and stopping

Exploratory two-seed OOF slices covered external-score missing count, contract, income type, age and gender.
Large slices showed small mean calibration residuals. Sparse categories were unstable; no manual prediction
adjustments or specialist models were justified by those slices alone. Raw slice metrics are retained.

The journal distinguishes observed score changes from tentative mechanisms. More complex features and models
can change quantization, interactions, calibration and correlated errors even without adding information.
A screen result does not identify which mechanism caused it, or establish performance on hidden labels.

This pass stops after its declared model/feature/combination directions and frozen gates have been assessed.
It does **not** exhaust every possible improvement. Larger neural searches, fully nested learned stacking,
specialist models, additional carefully designed interactions and larger seed banks remain possible research directions.
Their benefit is unproven; further small gains on the same repeatedly used selection labels can be misleading.
The retained evidence explains the stopping decision rather than claiming a global optimum.

## Notebooks, integrity and reproduction

- [`05_round3_hypotheses_and_experiments.ipynb`](05_round3_hypotheses_and_experiments.ipynb): hypotheses, definitions, all screens, convergence, negative results and interpretation.
- [`06_round3_validation_and_reproduction.ipynb`](06_round3_validation_and_reproduction.ipynb): frozen validation decisions, final result and saved-model replay.
- [`output/competition_round3_reproduction.zip`](output/competition_round3_reproduction.zip): source, all notebooks, required model banks, documentation, manifests and evidence.

Both new notebooks executed successfully. Feature checks cover target/ID independence, row/batch invariance,
train/test schema, hypothetical-rate equations and unseen neural categories. Protected file hashes and selection/source
freezes are checked. The recommended CSV has 61,500 finite scores in the sample ID order.
Saved-model replay is byte-identical for an accepted new CSV; a fallback is checked against its preserved checksum.
Some initial raw screening hashes reflect a source-line-offset recording error after an import-path-only edit.
The original/current core ASTs are identical and the phantom hash was exactly reproduced. Raw records are retained;
cache validation recognizes only this proven alias. Evidence and source snapshots are in
`improvements/round3/reference/signature_alias_proof.json`, with the correction documented in the journal.

From `Competition`, use the project interpreter and supplied `input` directory:

```sh
.venv/bin/python improvements/round3/round3.py screen
.venv/bin/python improvements/round3/followup.py
.venv/bin/python improvements/round3/stacking_probe.py
.venv/bin/python improvements/round3/validate.py cv
.venv/bin/python improvements/round3/validate.py select
.venv/bin/python improvements/round3/validate.py confirmation
.venv/bin/python improvements/round3/validate.py averaging
.venv/bin/python improvements/round3/finalize.py train_final
.venv/bin/python improvements/round3/finalize.py reproduce
.venv/bin/python improvements/round3/bagging.py probe
.venv/bin/python improvements/round3/bagging.py train
.venv/bin/python improvements/round3/bagging.py reproduce
.venv/bin/python improvements/round3/stored_helpers.py
.venv/bin/python improvements/round3/complementarity.py
.venv/bin/python improvements/round3/diagnostics.py
.venv/bin/python improvements/round3/importance.py
.venv/bin/python improvements/round3/document.py
.venv/bin/python improvements/round3/execute_notebook.py 05_round3_hypotheses_and_experiments.ipynb
.venv/bin/python improvements/round3/execute_notebook.py 06_round3_validation_and_reproduction.ipynb
.venv/bin/python improvements/round3/verify.py --final
.venv/bin/python improvements/round3/document.py
.venv/bin/python improvements/round3/package.py
```

Full reproduction reuses matching cached evidence; delete only third-pass cache artifacts to deliberately refit.
The source also references the preserved earlier-pass artifacts included in the archive.
The archive excludes input CSVs, the venv, kernel/cache directories and earlier ZIPs. Retain the originally supplied data.
Exact installed software versions are in `improvements/round3/requirements-round3.txt`.

The supplied README/tutorial gives a deadline of **November 20, 2026, 01:00 UTC (07:00 Bangladesh)** and says the
**last submitted file** determines the final entry; this is a local-document statement, not a live platform check.
A code ZIP is required for Honors/Outstanding consideration. Upload only the intended CSV and record its actual
public score against its checksum before claiming a further leaderboard improvement.
