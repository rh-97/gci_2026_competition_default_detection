# Third-pass experiment journal

Generated from retained evidence. Previous experiments remain in `EXPERIMENT_LOG.md`; this journal documents the new pass.

Last generated: 2026-11-08T20:25:24.260121+00:00

## Public feedback and scope

The user explicitly confirmed submitting `submission_round3_bagged.csv` and supplied a screenshot showing **0.76824, rank 518**. The exact CSV checksum is recorded in `improvements/round3/artifacts/round3_public_result.json`. The gain is **+0.00068** over round two and **+0.00284** over the first pass. Ranks are snapshots; private/full-test performance remains unknown. This feedback was recorded after the recipe was frozen and did not tune this pass. Frozen training-result JSON files and executed notebook outputs retain their pre-submission score fields; the post-submission result is recorded separately. The public gain does not isolate the extra third seed from the other recipe changes.

The plan was written before any third-pass fit: [`PLAN.md`](improvements/round3/PLAN.md). The prospectively recorded quantization amendment is [`FOLLOWUP_PLAN.md`](improvements/round3/FOLLOWUP_PLAN.md). Existing notebooks and prior-pass sources are protected by a SHA-256 manifest. All fits use the project `.venv`; only supplied data are used.

## Screening results

Every configuration uses the same original inner split. This split has been repeatedly explored and is not independent evidence. The reference is the complete frozen round-two mixture. Blend probes use new-model weights 0.10, 0.25, 0.50, 0.75 and 1.00; these are screening probes, not final weights.

| Trial | Status | Individual AUC | Best inner blend AUC | Gain over reference | Iterations | Seconds |
| --- | --- | --- | --- | --- | --- | --- |
| r3_cat_baseline | complete | 0.749952 | 0.751155 | -0.000076 | 1480 | 82.1 |
| r3_cat_depth4 | complete | 0.750398 | 0.751346 | +0.000115 | 2194 | 175.7 |
| r3_cat_depth6 | complete | 0.749610 | 0.751269 | +0.000037 | 1243 | 140.6 |
| r3_cat_depth7 | complete | 0.749315 | 0.751372 | +0.000140 | 1355 | 187.4 |
| r3_cat_slow | complete | 0.749811 | 0.751200 | -0.000031 | 2811 | 282.5 |
| r3_cat_l2_30 | complete | 0.749268 | 0.751194 | -0.000038 | 1835 | 197.3 |
| r3_cat_borders512 | complete | 0.750833 | 0.751488 | +0.000257 | 1621 | 181.5 |
| r3_cat_weight2 | complete | 0.750149 | 0.751354 | +0.000123 | 1335 | 154.9 |
| r3_cat_depthwise | complete | 0.749087 | 0.751386 | +0.000155 | 474 | 56.4 |
| r3_cat_groups | complete | 0.749941 | 0.751459 | +0.000228 | 1998 | 222.2 |
| r3_cat_median | complete | 0.749023 | 0.751398 | +0.000167 | 1488 | 164.7 |
| r3_cat_signed | complete | 0.750907 | 0.751658 | +0.000426 | 1528 | 195.1 |
| r3_cat_rates | complete | 0.749557 | 0.751215 | -0.000016 | 1452 | 168.5 |
| r3_cat_crosses | complete | 0.749644 | 0.751201 | -0.000031 | 1578 | 241.1 |
| r3_cat_engineered_proxy | complete | 0.750087 | 0.751546 | +0.000315 | 1802 | 231.0 |
| r3_lgb_proxy | complete | 0.748054 | 0.751715 | +0.000484 | 757 | 17.4 |
| r3_lgb_proxy_smooth | complete | 0.748929 | 0.751686 | +0.000455 | 876 | 17.4 |
| r3_xgb_proxy | complete | 0.746976 | 0.751379 | +0.000148 | 1494 | 32.5 |
| r3_mlp_small | complete | 0.727176 | 0.750935 | -0.000296 | 15 | 8.8 |
| r3_mlp_wide | complete | 0.734561 | 0.751222 | -0.000009 | 49 | 23.1 |
| r3_cat_borders1024 | complete | 0.750539 | 0.751548 | +0.000316 | 2072 | 194.8 |
| r3_cat_depth4_b512 | complete | 0.750716 | 0.751528 | +0.000297 | 2176 | 168.9 |
| r3_cat_native_b512 | complete | 0.750487 | 0.751489 | +0.000257 | 1973 | 202.0 |
| r3_cat_loan_b512 | complete | 0.750135 | 0.751328 | +0.000097 | 1656 | 173.9 |
| r3_cat_scores_b512 | complete | 0.749516 | 0.751225 | -0.000006 | 1568 | 154.0 |
| r3_cat_signed_only | complete | 0.750268 | 0.751463 | +0.000232 | 1810 | 175.7 |
| r3_cat_term_categories | complete | 0.749123 | 0.751176 | -0.000055 | 1655 | 186.6 |
| r3_cat_feature_b512 | complete | 0.750854 | 0.751707 | +0.000476 | 1851 | 192.8 |

## r3_cat_baseline

**Question:** Exact control: recover the round-two proxy-only screen before evaluating new settings.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_baseline",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "Exact control: recover the round-two proxy-only screen before evaluating new settings.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Outcome and interpretation:** Implementation control; maximum prediction difference from the previous proxy screen is 0.0. This is not a new improvement.

**Evidence:** AUC 0.749952116, AP 0.239172495, log loss 0.248120939, Brier 0.068117452.
Best inner blend: {'new_weight': 0.1, 'auc': 0.7511554735001189}. Correlation with reference: 0.9964145150982497.
Convergence: 1480 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_baseline*`.

## r3_cat_depth4

**Question:** Shallower trees may regularize the successful proxy representation differently.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_depth4",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 4,
    "l2_leaf_reg": 5,
    "random_strength": 0.5
  },
  "hypothesis": "Shallower trees may regularize the successful proxy representation differently.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": 0.0004460335290871198}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.750398150, AP 0.236276060, log loss 0.248291763, Brier 0.068235479.
Best inner blend: {'new_weight': 0.25, 'auc': 0.7513464566758987}. Correlation with reference: 0.9877965770860688.
Convergence: 2194 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_depth4*`.

## r3_cat_depth6

**Question:** More interactions may become useful with the proxy representation.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_depth6",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 6,
    "l2_leaf_reg": 12,
    "random_strength": 0.5
  },
  "hypothesis": "More interactions may become useful with the proxy representation.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Outcome and interpretation:** A small screening gain below the promotion threshold. No reliable improvement is established; selection noise and training variation remain plausible. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": -0.0003422778040172991}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.749609838, AP 0.236196226, log loss 0.248432320, Brier 0.068243535.
Best inner blend: {'new_weight': 0.1, 'auc': 0.7512686312616471}. Correlation with reference: 0.9856817626076254.
Convergence: 1243 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_depth6*`.

## r3_cat_depth7

**Question:** Test a further increase in interaction capacity with stronger shrinkage.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_depth7",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 7,
    "l2_leaf_reg": 20,
    "random_strength": 0.5
  },
  "hypothesis": "Test a further increase in interaction capacity with stronger shrinkage.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": -0.0006375914014721262}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.749314525, AP 0.235630273, log loss 0.248528129, Brier 0.068262033.
Best inner blend: {'new_weight': 0.25, 'auc': 0.7513717778083158}. Correlation with reference: 0.9795591453368303.
Convergence: 1355 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_depth7*`.

## r3_cat_slow

**Question:** Smaller boosting steps may improve the proxy model rather than the old representation.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_slow",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "learning_rate": 0.025
  },
  "hypothesis": "Smaller boosting steps may improve the proxy model rather than the old representation.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Outcome and interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": -0.00014092710148283505}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.749811189, AP 0.236869673, log loss 0.248258740, Brier 0.068194199.
Best inner blend: {'new_weight': 0.1, 'auc': 0.7512001504141931}. Correlation with reference: 0.9925763651701393.
Convergence: 2811 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_slow*`.

## r3_cat_l2_30

**Question:** Test stronger shrinkage with the winning feature block.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_l2_30",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 30,
    "random_strength": 0.5
  },
  "hypothesis": "Test stronger shrinkage with the winning feature block.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Outcome and interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": -0.0006838199963798974}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.749268296, AP 0.235752981, log loss 0.248465969, Brier 0.068244143.
Best inner blend: {'new_weight': 0.1, 'auc': 0.751193610366828}. Correlation with reference: 0.9886590313925279.
Convergence: 1835 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_l2_30*`.

## r3_cat_borders512

**Question:** Finer quantization may preserve loan-proxy and score thresholds.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_borders512",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "border_count": 512
  },
  "hypothesis": "Finer quantization may preserve loan-proxy and score thresholds.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": 0.0008809524258331924}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.750833069, AP 0.235426693, log loss 0.248173813, Brier 0.068224857.
Best inner blend: {'new_weight': 0.5, 'auc': 0.7514878320407334}. Correlation with reference: 0.9873747238052012.
Convergence: 1621 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_borders512*`.

## r3_cat_weight2

**Question:** A moderately weighted objective may learn different useful ranking errors.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_weight2",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "scale_pos_weight": 2.0
  },
  "hypothesis": "A moderately weighted objective may learn different useful ranking errors.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": 0.00019706346586090273}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.750149180, AP 0.237493295, log loss 0.265114844, Brier 0.073150127.
Best inner blend: {'new_weight': 0.25, 'auc': 0.7513540656589492}. Correlation with reference: 0.9804882386236142.
Convergence: 1335 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_weight2*`.

## r3_cat_depthwise

**Question:** Asymmetric trees may model conditional loan/score effects efficiently.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_depthwise",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 6,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "grow_policy": "Depthwise",
    "min_data_in_leaf": 150
  },
  "hypothesis": "Asymmetric trees may model conditional loan/score effects efficiently.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": -0.0008651252813313137}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.749086991, AP 0.237029514, log loss 0.248534237, Brier 0.068246514.
Best inner blend: {'new_weight': 0.25, 'auc': 0.7513863980899477}. Correlation with reference: 0.9755954701445009.
Convergence: 474 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_depthwise*`.

## r3_cat_groups

**Question:** Training-fold-only frequencies and group-relative financial quantities may complement the compact proxy model.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_groups",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "Training-fold-only frequencies and group-relative financial quantities may complement the compact proxy model.",
  "max_iterations": 4500,
  "patience": 200,
  "groups": true
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": -1.0907741563426221e-05}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.749941209, AP 0.235692596, log loss 0.248531002, Brier 0.068295814.
Best inner blend: {'new_weight': 0.25, 'auc': 0.7514594420284455}. Correlation with reference: 0.9817821051551913.
Convergence: 1998 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_groups*`.

## r3_cat_median

**Question:** Median imputation may improve upon a sentinel or native missing split.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_median",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "Median imputation may improve upon a sentinel or native missing split.",
  "max_iterations": 4500,
  "patience": 200,
  "missing": "median"
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": -0.0009292614224514217}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.749022855, AP 0.237716189, log loss 0.248383559, Brier 0.068195409.
Best inner blend: {'new_weight': 0.25, 'auc': 0.7513980184553011}. Correlation with reference: 0.9750914421714749.
Convergence: 1488 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_median*`.

## r3_cat_signed

**Question:** Signed term residuals and rounded categories may retain structure lost by absolute distances.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_signed",
  "kind": "cat",
  "features": "signed",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "Signed term residuals and rounded categories may retain structure lost by absolute distances.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: advanced to common-fold CV. Common-fold standalone OOF AUC: 0.762850230. Included in the frozen primary recipe; later gates determine deployment.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": 0.000955203227201773}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.750907320, AP 0.238034933, log loss 0.248030590, Brier 0.068158627.
Best inner blend: {'new_weight': 0.5, 'auc': 0.7516576204057203}. Correlation with reference: 0.9848299830189329.
Convergence: 1528 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_signed*`.

## r3_cat_rates

**Question:** Additional assumed-period transforms may expose useful numeric thresholds; these do not recover true rates.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_rates",
  "kind": "cat",
  "features": "rates",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "Additional assumed-period transforms may expose useful numeric thresholds; these do not recover true rates.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Outcome and interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": -0.0003953567824567239}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.749556759, AP 0.236257266, log loss 0.248402911, Brier 0.068226438.
Best inner blend: {'new_weight': 0.1, 'auc': 0.7512148281654851}. Correlation with reference: 0.9894039430751574.
Convergence: 1452 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_rates*`.

## r3_cat_crosses

**Question:** Explicit categorical interactions and age bands may complement native categorical combinations.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_crosses",
  "kind": "cat",
  "features": "crosses",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "Explicit categorical interactions and age bands may complement native categorical combinations.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Outcome and interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": -0.00030799140456183594}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.749644125, AP 0.238120723, log loss 0.248267619, Brier 0.068168880.
Best inner blend: {'new_weight': 0.1, 'auc': 0.7512007710865265}. Correlation with reference: 0.9894873328430696.
Convergence: 1578 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_crosses*`.

## r3_cat_engineered_proxy

**Question:** The proxy block may improve the larger financial/score representation rather than just the compact one.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_engineered_proxy",
  "kind": "cat",
  "features": "engineered_proxy",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "The proxy block may improve the larger financial/score representation rather than just the compact one.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": 0.00013472037814843407}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.750086837, AP 0.239939452, log loss 0.248075140, Brier 0.068117401.
Best inner blend: {'new_weight': 0.25, 'auc': 0.7515459913371613}. Correlation with reference: 0.9772468802063223.
Convergence: 1802 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_engineered_proxy*`.

## r3_lgb_proxy

**Question:** Use the exact compact successful proxy block in the known complementary LightGBM recipe.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_lgb_proxy",
  "kind": "lgb",
  "features": "proxy",
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
  },
  "hypothesis": "Use the exact compact successful proxy block in the known complementary LightGBM recipe."
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: advanced to common-fold CV. Common-fold standalone OOF AUC: 0.759216711.

**Evidence:** AUC 0.748053824, AP 0.237574278, log loss 0.248852509, Brier 0.068269580.
Best inner blend: {'new_weight': 0.25, 'auc': 0.7517154923538455}. Correlation with reference: 0.9631508974275895.
Convergence: 757 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_lgb_proxy*`.

## r3_lgb_proxy_smooth

**Question:** Stronger categorical/leaf smoothing may work differently on the compact proxy representation.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_lgb_proxy_smooth",
  "kind": "lgb",
  "features": "proxy",
  "groups": true,
  "params": {
    "num_leaves": 16,
    "min_child_samples": 150,
    "colsample_bytree": 0.6846068413999578,
    "subsample": 0.961965333135664,
    "subsample_freq": 1,
    "reg_lambda": 2.1323824335960286,
    "reg_alpha": 3.687185564401245,
    "max_bin": 255,
    "max_depth": -1,
    "cat_smooth": 100.0,
    "cat_l2": 30.0
  },
  "hypothesis": "Stronger categorical/leaf smoothing may work differently on the compact proxy representation."
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Evidence:** AUC 0.748929294, AP 0.239568836, log loss 0.248463574, Brier 0.068169481.
Best inner blend: {'new_weight': 0.25, 'auc': 0.7516863667299032}. Correlation with reference: 0.9703244571971257.
Convergence: 876 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_lgb_proxy_smooth*`.

## r3_xgb_proxy

**Question:** Remove the finance burden block that hurt CatBoost and test XGBoost on the successful compact proxy representation.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_xgb_proxy",
  "kind": "xgb",
  "features": "proxy",
  "params": {
    "max_depth": 3,
    "min_child_weight": 30,
    "reg_lambda": 20.0,
    "reg_alpha": 1.0,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "max_bin": 256
  },
  "hypothesis": "Remove the finance burden block that hurt CatBoost and test XGBoost on the successful compact proxy representation."
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Evidence:** AUC 0.746975826, AP 0.236331547, log loss 0.249072433, Brier 0.068305999.
Best inner blend: {'new_weight': 0.1, 'auc': 0.7513789959976748}. Correlation with reference: 0.963978170890197.
Convergence: 1494 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_xgb_proxy*`.

## r3_mlp_small

**Question:** A quantile-normalized neural model trained from scratch may contribute smooth complementary errors; fit preprocessing only on training rows.

**How:** Quantile-normalized numeric values with median imputation/missing indicators, one-hot categoricals, and a scratch-trained neural network; all preprocessing fits on training rows.

**Exact configuration:**
```json
{
  "name": "r3_mlp_small",
  "kind": "mlp",
  "features": "proxy",
  "max_iterations": 80,
  "patience": 12,
  "params": {
    "hidden_layer_sizes": [
      64,
      32
    ],
    "alpha": 0.1
  },
  "hypothesis": "A quantile-normalized neural model trained from scratch may contribute smooth complementary errors; fit preprocessing only on training rows."
}
```

**Outcome and interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Evidence:** AUC 0.727176108, AP 0.204425686, log loss 0.255989939, Brier 0.069689415.
Best inner blend: {'new_weight': 0.1, 'auc': 0.7509350888460263}. Correlation with reference: 0.8673491963280756.
Convergence: 15 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_mlp_small*`.

## r3_mlp_wide

**Question:** A quantile-normalized neural model trained from scratch may contribute smooth complementary errors; fit preprocessing only on training rows.

**How:** Quantile-normalized numeric values with median imputation/missing indicators, one-hot categoricals, and a scratch-trained neural network; all preprocessing fits on training rows.

**Exact configuration:**
```json
{
  "name": "r3_mlp_wide",
  "kind": "mlp",
  "features": "proxy",
  "max_iterations": 80,
  "patience": 12,
  "params": {
    "hidden_layer_sizes": [
      128,
      64
    ],
    "alpha": 1.0
  },
  "hypothesis": "A quantile-normalized neural model trained from scratch may contribute smooth complementary errors; fit preprocessing only on training rows."
}
```

**Outcome and interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Evidence:** AUC 0.734560804, AP 0.214769766, log loss 0.253346115, Brier 0.069182843.
Best inner blend: {'new_weight': 0.1, 'auc': 0.7512223796788753}. Correlation with reference: 0.8988805899356661.
Convergence: 49 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_mlp_wide*`.

## r3_cat_borders1024

**Question:** Follow up the positive 512-border result: test whether finer quantization continues to help.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_borders1024",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "border_count": 1024
  },
  "hypothesis": "Follow up the positive 512-border result: test whether finer quantization continues to help.",
  "max_iterations": 4500,
  "patience": 200,
  "source": "improvements/round3/followup.py"
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": 0.0005868916669772295}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.750539008, AP 0.239398414, log loss 0.248113885, Brier 0.068129307.
Best inner blend: {'new_weight': 0.5, 'auc': 0.7515476464633837}. Correlation with reference: 0.9833237806308454.
Convergence: 2072 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_borders1024*`.

## r3_cat_depth4_b512

**Question:** Combine independently promising shallower trees and finer quantization on the proxy representation.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_depth4_b512",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 4,
    "l2_leaf_reg": 5,
    "random_strength": 0.5,
    "border_count": 512
  },
  "hypothesis": "Combine independently promising shallower trees and finer quantization on the proxy representation.",
  "max_iterations": 4500,
  "patience": 200,
  "source": "improvements/round3/followup.py"
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_depth4", "parent_auc": 0.750398149807957, "individual_auc_delta": 0.00031761182572975777}, {"parent": "r3_cat_borders512", "parent_auc": 0.7508330687047031, "individual_auc_delta": -0.00011730707101631488}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.750715762, AP 0.236522428, log loss 0.248192664, Brier 0.068207733.
Best inner blend: {'new_weight': 0.5, 'auc': 0.751528428608912}. Correlation with reference: 0.9858985242841402.
Convergence: 2176 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_depth4_b512*`.

## r3_cat_native_b512

**Question:** Test the interaction between native missing bins and finer quantization.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_native_b512",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "border_count": 512
  },
  "hypothesis": "Test the interaction between native missing bins and finer quantization.",
  "max_iterations": 4500,
  "patience": 200,
  "source": "improvements/round3/followup.py",
  "missing": "native"
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_borders512", "parent_auc": 0.7508330687047031, "individual_auc_delta": -0.00034579494723974147}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.750487274, AP 0.236257827, log loss 0.248257159, Brier 0.068211735.
Best inner blend: {'new_weight': 0.25, 'auc': 0.7514886710977767}. Correlation with reference: 0.982037957831863.
Convergence: 1973 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_native_b512*`.

## r3_cat_loan_b512

**Question:** Isolate higher resolution for credit term and loan proxies; test whether they explain the global border-count gain.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_loan_b512",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "per_float_feature_quantization": [
      "34:border_count=512",
      "46:border_count=512",
      "47:border_count=512",
      "48:border_count=512",
      "49:border_count=512",
      "50:border_count=512"
    ]
  },
  "hypothesis": "Isolate higher resolution for credit term and loan proxies; test whether they explain the global border-count gain.",
  "max_iterations": 4500,
  "patience": 200,
  "source": "improvements/round3/followup.py"
}
```

**Outcome and interpretation:** A small screening gain below the promotion threshold. No reliable improvement is established; selection noise and training variation remain plausible. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": 0.0001825811114143372}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.750134697, AP 0.237498494, log loss 0.248257254, Brier 0.068209810.
Best inner blend: {'new_weight': 0.25, 'auc': 0.7513282617813839}. Correlation with reference: 0.9879617273481587.
Convergence: 1656 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_loan_b512*`.

## r3_cat_scores_b512

**Question:** Isolate higher resolution for external scores as an alternative explanation for the global border-count gain.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_scores_b512",
  "kind": "cat",
  "features": "proxy",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "per_float_feature_quantization": [
      "24:border_count=512",
      "25:border_count=512",
      "26:border_count=512",
      "40:border_count=512",
      "41:border_count=512",
      "42:border_count=512",
      "43:border_count=512",
      "44:border_count=512"
    ]
  },
  "hypothesis": "Isolate higher resolution for external scores as an alternative explanation for the global border-count gain.",
  "max_iterations": 4500,
  "patience": 200,
  "source": "improvements/round3/followup.py"
}
```

**Outcome and interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_baseline", "parent_auc": 0.7499521162788699, "individual_auc_delta": -0.00043564301446863407}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.749516473, AP 0.237071014, log loss 0.248356980, Brier 0.068214081.
Best inner blend: {'new_weight': 0.1, 'auc': 0.7512251267286472}. Correlation with reference: 0.9885636080663195.
Convergence: 1568 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_scores_b512*`.

## r3_cat_signed_only

**Question:** Decompose the positive joint term representation: keep signed residual additions and ignore rounded category additions.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_signed_only",
  "kind": "cat",
  "features": "signed",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "ignored_features": [
      52,
      54
    ]
  },
  "hypothesis": "Decompose the positive joint term representation: keep signed residual additions and ignore rounded category additions.",
  "max_iterations": 4500,
  "patience": 200,
  "source": "improvements/round3/followup.py"
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_signed", "parent_auc": 0.7509073195060717, "individual_auc_delta": -0.0006394993942008265}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.750267820, AP 0.239424863, log loss 0.248092801, Brier 0.068108869.
Best inner blend: {'new_weight': 0.25, 'auc': 0.7514634993864769}. Correlation with reference: 0.9832045932805912.
Convergence: 1810 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_signed_only*`.

## r3_cat_term_categories

**Question:** Decompose the positive joint term representation: keep rounded category additions and ignore signed residual additions.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_term_categories",
  "kind": "cat",
  "features": "signed",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "ignored_features": [
      51,
      53
    ]
  },
  "hypothesis": "Decompose the positive joint term representation: keep rounded category additions and ignore signed residual additions.",
  "max_iterations": 4500,
  "patience": 200,
  "source": "improvements/round3/followup.py"
}
```

**Outcome and interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Reference comparisons:** `[{"parent": "r3_cat_signed", "parent_auc": 0.7509073195060717, "individual_auc_delta": -0.0017846743311578095}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.749122645, AP 0.235416497, log loss 0.248606844, Brier 0.068287481.
Best inner blend: {'new_weight': 0.1, 'auc': 0.7511759326992575}. Correlation with reference: 0.9891558137229962.
Convergence: 1655 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_term_categories*`.

## r3_cat_feature_b512

**Question:** Combine the eligible best new feature block (r3_cat_signed) with finer quantization under the recorded rule.

**How:** Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.

**Exact configuration:**
```json
{
  "name": "r3_cat_feature_b512",
  "kind": "cat",
  "features": "signed",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "border_count": 512
  },
  "hypothesis": "Combine the eligible best new feature block (r3_cat_signed) with finer quantization under the recorded rule.",
  "max_iterations": 4500,
  "patience": 200,
  "source": "improvements/round3/followup.py"
}
```

**Outcome and interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: advanced to common-fold CV. Common-fold standalone OOF AUC: 0.762661887. Included in the frozen primary recipe; later gates determine deployment.

**Reference comparisons:** `[{"parent": "r3_cat_signed", "parent_auc": 0.7509073195060717, "individual_auc_delta": -5.294105125430715e-05}, {"parent": "r3_cat_borders512", "parent_auc": 0.7508330687047031, "individual_auc_delta": 2.1309750114273385e-05}]`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.

**Evidence:** AUC 0.750854378, AP 0.235407197, log loss 0.248290318, Brier 0.068264620.
Best inner blend: {'new_weight': 0.5, 'auc': 0.7517070328198198}. Correlation with reference: 0.9808761970033321.
Convergence: 1851 retained iterations; saturated=False.
Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/r3_cat_feature_b512*`.

## Implementation incidents and corrections

```json
[
  {
    "stage": "early diagnostic",
    "issue": "The shared module name validate resolved to the previous-pass module after importing round3.",
    "impact": "The diagnostic stopped before computing or saving results; no training result was affected.",
    "fix": "Put the current round-three source directory first on sys.path after loading the read-only prior-pass dependency.",
    "verification": "Reran diagnostic successfully; the probability reference exactly matches the recorded 0.7630891353395803 primary AUC."
  },
  {
    "stage": "pipeline preparation",
    "issue": "The waiting pipeline had imported source modules before the prospective quantization controls were finalized.",
    "impact": "No follow-up, CV or confirmation phase had started.",
    "fix": "Stopped and restarted the waiting process so it loads the final prospective source.",
    "verification": "No followup_plan.json existed when restarted; all follow-up specs are generated from the finalized source."
  },
  {
    "stage": "screening provenance",
    "aliases": {
      "a94c490794f8063519012e4e4cb798164bbd5446c725516785a93e6dfa8882a1": "a1e121c4ca79cef4ac80c526a939528f09a2c74e0d63d9262dbe29e2aa81f01f"
    },
    "canonical_implementation_hash": "a1e121c4ca79cef4ac80c526a939528f09a2c74e0d63d9262dbe29e2aa81f01f",
    "core_functions": [
      "features",
      "NeuralEncoder",
      "fit"
    ],
    "core_ast_sha256": "d1f3cf122b23055b84059a8ec602b8157d17980f77441721745589581f824290",
    "source_files": {
      "reference/round3_initial_source.py": "ef4370974c252d527954a5b4e68e00150c85932e9c21691844a96a883ec1e548",
      "reference/round3_source_after_import_fix.py": "a4e83b9c7f768fa734a9792dc8e4d92eaccc160d0447db573d6cb6bacacb8036"
    },
    "cause": "An import-path-only insertion shifted source line numbers while the initial screening process was alive. inspect.getsource on the already loaded functions read the wrong source spans. Compiling the original source against the shifted filename exactly reproduces the recorded phantom hash.",
    "effect": "Feature functions, neural encoder and fitting functions have identical ASTs. No training logic or predictions changed. The original baseline control also reproduced prior predictions exactly.",
    "resolution": "Retain every raw record and signature; recognize this single proven metadata alias when validating screening caches. Later CV and follow-ups loaded the final source and use the canonical hash."
  },
  {
    "stage": "primary blend-grid review",
    "recorded_utc": "2026-11-08T16:09:06.606061+00:00",
    "reason": "Primary recipe review found the grid omitted direct blends between new finalists (and direct old/new family replacements). It only added one helper to the current composite or shared helper weight equally. This could miss replacing the old CatBoost/LightGBM pair with a better new pair.",
    "decision": "Extend only the coarse primary grid to direct pairs. Stop the original confirmation without using its results; preserve its evidence separately. Use a fresh confirmation fold seed SEED+1101 after freezing the corrected primary winner.",
    "new_pair_weights": [
      0.1,
      0.25,
      0.3333333333333333,
      0.5,
      0.6666666666666666,
      0.75,
      0.9
    ],
    "methods": [
      "probability",
      "log_odds",
      "percentile"
    ],
    "confirmation_results_consulted": false,
    "new_confirmation_seed": 20262209,
    "original_source_reconstructed_and_hash_verified": true
  }
]
```

## Primary pair-grid correction before fresh confirmation

```json
{
  "recorded_utc": "2026-11-08T16:09:06.606061+00:00",
  "reason": "Primary recipe review found the grid omitted direct blends between new finalists (and direct old/new family replacements). It only added one helper to the current composite or shared helper weight equally. This could miss replacing the old CatBoost/LightGBM pair with a better new pair.",
  "decision": "Extend only the coarse primary grid to direct pairs. Stop the original confirmation without using its results; preserve its evidence separately. Use a fresh confirmation fold seed SEED+1101 after freezing the corrected primary winner.",
  "new_pair_weights": [
    0.1,
    0.25,
    0.3333333333333333,
    0.5,
    0.6666666666666666,
    0.75,
    0.9
  ],
  "methods": [
    "probability",
    "log_odds",
    "percentile"
  ],
  "confirmation_results_consulted": false,
  "new_confirmation_seed": 20262209
}
```

## Early saved-prediction blend diagnostic

```json
[
  {
    "method": "probability",
    "primary_auc": 0.7630891353395803,
    "previous_secondary_auc": 0.762875657415778,
    "note": "Diagnostic only; previous secondary labels have already been inspected."
  },
  {
    "method": "log_odds",
    "primary_auc": 0.7630436019258241,
    "previous_secondary_auc": 0.7628523447791584,
    "note": "Diagnostic only; previous secondary labels have already been inspected."
  },
  {
    "method": "percentile",
    "primary_auc": 0.7630256264707563,
    "previous_secondary_auc": 0.7628561339625616,
    "note": "Diagnostic only; previous secondary labels have already been inspected."
  }
]
```

## Cross-fitted learned-combination feasibility probe

```json
{
  "reference_auc": 0.7630891353395803,
  "results": [
    {
      "spec": {
        "name": "logits_c01",
        "C": 0.1,
        "groups": false
      },
      "auc": 0.7629430826121688,
      "average_precision": 0.24785304164242797,
      "log_loss": 0.24470073299978587,
      "brier": 0.0675765176847183,
      "seconds": 1.2335708141326904,
      "fold_coefficients": [
        {
          "features": [
            "logits__lgb_tune_15",
            "logits__r2_cat_term_proxies",
            "logits__r2_cat_proxies_native"
          ],
          "weights": [
            0.30255409454323023,
            0.37623356972339717,
            0.3321368568409929
          ],
          "intercept": 0.045910254206098074
        },
        {
          "features": [
            "logits__lgb_tune_15",
            "logits__r2_cat_term_proxies",
            "logits__r2_cat_proxies_native"
          ],
          "weights": [
            0.30215139301609834,
            0.36419686769068804,
            0.3392237018173269
          ],
          "intercept": 0.0327058038713467
        },
        {
          "features": [
            "logits__lgb_tune_15",
            "logits__r2_cat_term_proxies",
            "logits__r2_cat_proxies_native"
          ],
          "weights": [
            0.30355575707640686,
            0.3672775949754211,
            0.33960395845906693
          ],
          "intercept": 0.04353759341437587
        },
        {
          "features": [
            "logits__lgb_tune_15",
            "logits__r2_cat_term_proxies",
            "logits__r2_cat_proxies_native"
          ],
          "weights": [
            0.32460645481432904,
            0.360159236290862,
            0.3392406380106527
          ],
          "intercept": 0.07282783663343789
        },
        {
          "features": [
            "logits__lgb_tune_15",
            "logits__r2_cat_term_proxies",
            "logits__r2_cat_proxies_native"
          ],
          "weights": [
            0.30971776749600505,
            0.3676386941390729,
            0.32966433530306566
          ],
          "intercept": 0.03614018005895611
        }
      ],
      "blends": [
        {
          "new_weight": 0.1,
          "auc": 0.7630916279398474,
          "average_precision": 0.2474257479076001,
          "log_loss": 0.2447146351410342,
          "brier": 0.06759194377297545
        },
        {
          "new_weight": 0.25,
          "auc": 0.7630892775686446,
          "average_precision": 0.2475626191467833,
          "log_loss": 0.24470403858359036,
          "brier": 0.06758724733321596
        },
        {
          "new_weight": 0.5,
          "auc": 0.7630659419455095,
          "average_precision": 0.24769442734868669,
          "log_loss": 0.2446937475864429,
          "brier": 0.06758130920032789
        },
        {
          "new_weight": 0.75,
          "auc": 0.76301656260039,
          "average_precision": 0.24782691089042386,
          "log_loss": 0.24469264875625868,
          "brier": 0.06757773265082867
        },
        {
          "new_weight": 1.0,
          "auc": 0.7629430826121688,
          "average_precision": 0.24785304164242797,
          "log_loss": 0.24470073299978587,
          "brier": 0.0675765176847183
        }
      ],
      "best_blend": {
        "new_weight": 0.1,
        "auc": 0.7630916279398474,
        "average_precision": 0.2474257479076001,
        "log_loss": 0.2447146351410342,
        "brier": 0.06759194377297545
      },
      "gain": 2.4926002670788705e-06
    },
    {
      "spec": {
        "name": "logits_c1",
        "C": 1.0,
        "groups": false
      },
      "auc": 0.7629434503964156,
      "average_precision": 0.2478515590494525,
      "log_loss": 0.24470073782438545,
      "brier": 0.06757668814548601,
      "seconds": 1.0804829597473145,
      "fold_coefficients": [
        {
          "features": [
            "logits__lgb_tune_15",
            "logits__r2_cat_term_proxies",
            "logits__r2_cat_proxies_native"
          ],
          "weights": [
            0.30239952976565915,
            0.37674923443965386,
            0.33225578916753
          ],
          "intercept": 0.04692906412303429
        },
        {
          "features": [
            "logits__lgb_tune_15",
            "logits__r2_cat_term_proxies",
            "logits__r2_cat_proxies_native"
          ],
          "weights": [
            0.30200540081843563,
            0.36461584712221196,
            0.3394180317592541
          ],
          "intercept": 0.033694854159463564
        },
        {
          "features": [
            "logits__lgb_tune_15",
            "logits__r2_cat_term_proxies",
            "logits__r2_cat_proxies_native"
          ],
          "weights": [
            0.30341123732983566,
            0.3677091733941954,
            0.339788693150301
          ],
          "intercept": 0.04453516050636558
        },
        {
          "features": [
            "logits__lgb_tune_15",
            "logits__r2_cat_term_proxies",
            "logits__r2_cat_proxies_native"
          ],
          "weights": [
            0.32461587091783106,
            0.3604741535398376,
            0.3393833081925652
          ],
          "intercept": 0.07380710730751999
        },
        {
          "features": [
            "logits__lgb_tune_15",
            "logits__r2_cat_term_proxies",
            "logits__r2_cat_proxies_native"
          ],
          "weights": [
            0.30963731095637803,
            0.3680829584480135,
            0.3297685382058567
          ],
          "intercept": 0.03713007398120673
        }
      ],
      "blends": [
        {
          "new_weight": 0.1,
          "auc": 0.7630916071083178,
          "average_precision": 0.24742564326931943,
          "log_loss": 0.2447146183686438,
          "brier": 0.06759195217803042
        },
        {
          "new_weight": 0.25,
          "auc": 0.7630892495538288,
          "average_precision": 0.24756324306078178,
          "log_loss": 0.24470400376033793,
          "brier": 0.06758727194627916
        },
        {
          "new_weight": 0.5,
          "auc": 0.7630660188066706,
          "average_precision": 0.24769417488154852,
          "log_loss": 0.24469370176488026,
          "brier": 0.06758137042787343
        },
        {
          "new_weight": 0.75,
          "auc": 0.7630167795356293,
          "average_precision": 0.2478257165086751,
          "log_loss": 0.2446926160411722,
          "brier": 0.06757784249427572
        },
        {
          "new_weight": 1.0,
          "auc": 0.7629434503964156,
          "average_precision": 0.2478515590494525,
          "log_loss": 0.24470073782438545,
          "brier": 0.06757668814548601
        }
      ],
      "best_blend": {
        "new_weight": 0.1,
        "auc": 0.7630916071083178,
        "average_precision": 0.24742564326931943,
        "log_loss": 0.2447146183686438,
        "brier": 0.06759195217803042
      },
      "gain": 2.471768737466462e-06
    },
    {
      "spec": {
        "name": "logits_groups_c01",
        "C": 0.1,
        "groups": true
      },
      "auc": 0.7628490476508512,
      "average_precision": 0.24742936969550644,
      "log_loss": 0.24474725106132128,
      "brier": 0.06759162563085698,
      "seconds": 1.7060048580169678,
      "fold_coefficients": [
        {
          "features": [
            "logits__lgb_tune_15",
            "logits__r2_cat_term_proxies",
            "logits__r2_cat_proxies_native",
            "groups__EXT_MISSING_COUNT_0",
            "groups__EXT_MISSING_COUNT_1",
            "groups__EXT_MISSING_COUNT_2",
            "groups__EXT_MISSING_COUNT_3",
            "groups__CONTRACT_Cash loans",
            "groups__CONTRACT_Revolving loans",
            "groups__AGE_BAND_(0, 30]",
            "groups__AGE_BAND_(30, 40]",
            "groups__AGE_BAND_(40, 50]",
            "groups__AGE_BAND_(50, 60]",
            "groups__AGE_BAND_(60, 100]"
          ],
          "weights": [
            0.28936324029216837,
            0.39780754106965804,
            0.32458299697134557,
            0.023298370304419634,
            0.0018264991480587641,
            -0.002728443112751072,
            -0.0019111540891869059,
            0.022352268259665395,
            -0.0018669960090803225,
            -0.015404077314875813,
            0.0074481302718721115,
            0.007429018264667955,
            -0.0103841092223841,
            0.031396310251207704
          ],
          "intercept": 0.02054494486588347
        },
        {
          "features": [
            "logits__lgb_tune_15",
            "logits__r2_cat_term_proxies",
            "logits__r2_cat_proxies_native",
            "groups__EXT_MISSING_COUNT_0",
            "groups__EXT_MISSING_COUNT_1",
            "groups__EXT_MISSING_COUNT_2",
            "groups__EXT_MISSING_COUNT_3",
            "groups__CONTRACT_Cash loans",
            "groups__CONTRACT_Revolving loans",
            "groups__AGE_BAND_(0, 30]",
            "groups__AGE_BAND_(30, 40]",
            "groups__AGE_BAND_(40, 50]",
            "groups__AGE_BAND_(50, 60]",
            "groups__AGE_BAND_(60, 100]"
          ],
          "weights": [
            0.2951117441821714,
            0.371983109066165,
            0.3386824526725375,
            9.56673441081155e-05,
            0.011093619297106273,
            -0.006180772443394898,
            -0.004135078682707925,
            0.039226866706107144,
            -0.038353431191174604,
            -0.026243197998074626,
            -0.0005327860694501381,
            -0.01477482885094468,
            -0.005116083435236769,
            0.0475403318689498
          ],
          "intercept": 0.0005258296733402959
        },
        {
          "features": [
            "logits__lgb_tune_15",
            "logits__r2_cat_term_proxies",
            "logits__r2_cat_proxies_native",
            "groups__EXT_MISSING_COUNT_0",
            "groups__EXT_MISSING_COUNT_1",
            "groups__EXT_MISSING_COUNT_2",
            "groups__EXT_MISSING_COUNT_3",
            "groups__CONTRACT_Cash loans",
            "groups__CONTRACT_Revolving loans",
            "groups__AGE_BAND_(0, 30]",
            "groups__AGE_BAND_(30, 40]",
            "groups__AGE_BAND_(40, 50]",
            "groups__AGE_BAND_(50, 60]",
            "groups__AGE_BAND_(60, 100]"
          ],
          "weights": [
            0.29414099341599775,
            0.38252778599684073,
            0.3382971925508349,
            0.04688015322496934,
            0.0014046397898344561,
            -0.017079638440625322,
            -0.0004278022236610965,
            0.017906771168702346,
            0.012870581181650603,
            -0.013960686592495174,
            -0.0026130540583103098,
            -0.0026848830806972287,
            -0.005368269091359512,
            0.05540424517351261
          ],
          "intercept": 0.031028890424842047
        },
        {
          "features": [
            "logits__lgb_tune_15",
            "logits__r2_cat_term_proxies",
            "logits__r2_cat_proxies_native",
            "groups__EXT_MISSING_COUNT_0",
            "groups__EXT_MISSING_COUNT_1",
            "groups__EXT_MISSING_COUNT_2",
            "groups__EXT_MISSING_COUNT_3",
            "groups__CONTRACT_Cash loans",
            "groups__CONTRACT_Revolving loans",
            "groups__AGE_BAND_(0, 30]",
            "groups__AGE_BAND_(30, 40]",
            "groups__AGE_BAND_(40, 50]",
            "groups__AGE_BAND_(50, 60]",
            "groups__AGE_BAND_(60, 100]"
          ],
          "weights": [
            0.3205422469238284,
            0.3650134081895141,
            0.3369000310749739,
            0.006715804297731319,
            0.015376768610602535,
            0.0033113419776177213,
            -0.009103788936616987,
            0.04318723676757125,
            -0.026887110818394712,
            -0.014349281837682573,
            0.009740601805079597,
            0.01845140608258359,
            -0.010618901906526108,
            0.01307630180601613
          ],
          "intercept": 0.016426920193123817
        },
        {
          "features": [
            "logits__lgb_tune_15",
            "logits__r2_cat_term_proxies",
            "logits__r2_cat_proxies_native",
            "groups__EXT_MISSING_COUNT_0",
            "groups__EXT_MISSING_COUNT_1",
            "groups__EXT_MISSING_COUNT_2",
            "groups__EXT_MISSING_COUNT_3",
            "groups__CONTRACT_Cash loans",
            "groups__CONTRACT_Revolving loans",
            "groups__AGE_BAND_(0, 30]",
            "groups__AGE_BAND_(30, 40]",
            "groups__AGE_BAND_(40, 50]",
            "groups__AGE_BAND_(50, 60]",
            "groups__AGE_BAND_(60, 100]"
          ],
          "weights": [
            0.29997429830700245,
            0.38215507876846255,
            0.3221571987951088,
            -0.005096087506556191,
            0.0127228685545059,
            0.00020075864705612978,
            -0.006575630996622081,
            0.030042635119913747,
            -0.028790726421691632,
            -0.006850143443026471,
            0.007001328286448071,
            -0.010380164912953606,
            -0.026794595315149394,
            0.038275484083200785
          ],
          "intercept": 0.0009163942128084784
        }
      ],
      "blends": [
        {
          "new_weight": 0.1,
          "auc": 0.7630850401481903,
          "average_precision": 0.24739113487553244,
          "log_loss": 0.24471841360072116,
          "brier": 0.06759331009146935
        },
        {
          "new_weight": 0.25,
          "auc": 0.7630728493933968,
          "average_precision": 0.24743720099014022,
          "log_loss": 0.24471385148918018,
          "brier": 0.06759072332783399
        },
        {
          "new_weight": 0.5,
          "auc": 0.76302859532289,
          "average_precision": 0.24750536209223972,
          "log_loss": 0.2447145897993919,
          "brier": 0.06758846185084172
        },
        {
          "new_weight": 0.75,
          "auc": 0.762951877827636,
          "average_precision": 0.24749127611477434,
          "log_loss": 0.24472572773010706,
          "brier": 0.06758876261851604
        },
        {
          "new_weight": 1.0,
          "auc": 0.7628490476508512,
          "average_precision": 0.24742936969550644,
          "log_loss": 0.24474725106132128,
          "brier": 0.06759162563085698
        }
      ],
      "best_blend": {
        "new_weight": 0.1,
        "auc": 0.7630850401481903,
        "average_precision": 0.24739113487553244,
        "log_loss": 0.24471841360072116,
        "brier": 0.06759331009146935
      },
      "gain": -4.0951913899967e-06
    }
  ],
  "warrants_nested_followup": false,
  "best_gain": 2.4926002670788705e-06,
  "caveat": "Meta folds hold out their own meta targets, but precomputed base OOF features are not fully nested. Screening evidence only; never deploy from this probe."
}
```

## Late stored-model combination check

```json
{
  "reference": "Frozen third-pass primary winner",
  "baseline_auc": 0.7637228893732684,
  "results": [
    {
      "name": "lgb_tune_12",
      "origin": "first pass",
      "helper_auc": 0.7573877195207913,
      "best": {
        "helper_weight": 0.1,
        "method": "probability",
        "auc": 0.7637922303520547,
        "gain": 6.934097878630308e-05
      },
      "blends": [
        {
          "helper_weight": 0.05,
          "method": "probability",
          "auc": 0.7637774291911023,
          "gain": 5.453981783387629e-05
        },
        {
          "helper_weight": 0.05,
          "method": "log_odds",
          "auc": 0.7637733469296274,
          "gain": 5.045755635901816e-05
        },
        {
          "helper_weight": 0.1,
          "method": "probability",
          "auc": 0.7637922303520547,
          "gain": 6.934097878630308e-05
        },
        {
          "helper_weight": 0.1,
          "method": "log_odds",
          "auc": 0.7637849587115635,
          "gain": 6.206933829511208e-05
        },
        {
          "helper_weight": 0.25,
          "method": "probability",
          "auc": 0.7635845285085833,
          "gain": -0.00013836086468510533
        },
        {
          "helper_weight": 0.25,
          "method": "log_odds",
          "auc": 0.7635801186892635,
          "gain": -0.00014277068400492254
        }
      ],
      "alignment_verified": true
    },
    {
      "name": "lgb_top_70",
      "origin": "first pass",
      "helper_auc": 0.756959629432316,
      "best": {
        "helper_weight": 0.05,
        "method": "probability",
        "auc": 0.7637504911500019,
        "gain": 2.7601776733554573e-05
      },
      "blends": [
        {
          "helper_weight": 0.05,
          "method": "probability",
          "auc": 0.7637504911500019,
          "gain": 2.7601776733554573e-05
        },
        {
          "helper_weight": 0.05,
          "method": "log_odds",
          "auc": 0.76374105374876,
          "gain": 1.8164375491624973e-05
        },
        {
          "helper_weight": 0.1,
          "method": "probability",
          "auc": 0.7637337303886089,
          "gain": 1.0841015340545823e-05
        },
        {
          "helper_weight": 0.1,
          "method": "log_odds",
          "auc": 0.7637196008649043,
          "gain": -3.2885083640632473e-06
        },
        {
          "helper_weight": 0.25,
          "method": "probability",
          "auc": 0.7634528868896904,
          "gain": -0.0002700024835780024
        },
        {
          "helper_weight": 0.25,
          "method": "log_odds",
          "auc": 0.7634272073603098,
          "gain": -0.00029568201295859797
        }
      ],
      "alignment_verified": true
    },
    {
      "name": "lgb_engineered",
      "origin": "first pass",
      "helper_auc": 0.7561021821237018,
      "best": {
        "helper_weight": 0.05,
        "method": "probability",
        "auc": 0.7637461244303985,
        "gain": 2.3235057130088776e-05
      },
      "blends": [
        {
          "helper_weight": 0.05,
          "method": "probability",
          "auc": 0.7637461244303985,
          "gain": 2.3235057130088776e-05
        },
        {
          "helper_weight": 0.05,
          "method": "log_odds",
          "auc": 0.7637367725102606,
          "gain": 1.3883136992243195e-05
        },
        {
          "helper_weight": 0.1,
          "method": "probability",
          "auc": 0.7637238871317038,
          "gain": 9.977584354281532e-07
        },
        {
          "helper_weight": 0.1,
          "method": "log_odds",
          "auc": 0.7637080630708147,
          "gain": -1.4826302453641027e-05
        },
        {
          "helper_weight": 0.25,
          "method": "probability",
          "auc": 0.7633960318987554,
          "gain": -0.0003268574745129982
        },
        {
          "helper_weight": 0.25,
          "method": "log_odds",
          "auc": 0.763366814600984,
          "gain": -0.0003560747722843871
        }
      ],
      "alignment_verified": true
    },
    {
      "name": "lgb_raw",
      "origin": "first pass",
      "helper_auc": 0.7499471346061496,
      "best": {
        "helper_weight": 0.05,
        "method": "probability",
        "auc": 0.7637810272990961,
        "gain": 5.813792582776145e-05
      },
      "blends": [
        {
          "helper_weight": 0.05,
          "method": "probability",
          "auc": 0.7637810272990961,
          "gain": 5.813792582776145e-05
        },
        {
          "helper_weight": 0.05,
          "method": "log_odds",
          "auc": 0.7637793679600133,
          "gain": 5.647858674495687e-05
        },
        {
          "helper_weight": 0.1,
          "method": "probability",
          "auc": 0.763754403167597,
          "gain": 3.151379432864143e-05
        },
        {
          "helper_weight": 0.1,
          "method": "log_odds",
          "auc": 0.7637591333614757,
          "gain": 3.624398820734065e-05
        },
        {
          "helper_weight": 0.25,
          "method": "probability",
          "auc": 0.7632129536416118,
          "gain": -0.0005099357316565856
        },
        {
          "helper_weight": 0.25,
          "method": "log_odds",
          "auc": 0.7632501020055356,
          "gain": -0.0004727873677328187
        }
      ],
      "alignment_verified": true
    },
    {
      "name": "cat_depth4",
      "origin": "first pass",
      "helper_auc": 0.7597278157513098,
      "best": {
        "helper_weight": 0.05,
        "method": "probability",
        "auc": 0.7637086377337007,
        "gain": -1.425163956769726e-05
      },
      "blends": [
        {
          "helper_weight": 0.05,
          "method": "probability",
          "auc": 0.7637086377337007,
          "gain": -1.425163956769726e-05
        },
        {
          "helper_weight": 0.05,
          "method": "log_odds",
          "auc": 0.7637044915409795,
          "gain": -1.8397832288852278e-05
        },
        {
          "helper_weight": 0.1,
          "method": "probability",
          "auc": 0.7636733663624276,
          "gain": -4.9523010840824e-05
        },
        {
          "helper_weight": 0.1,
          "method": "log_odds",
          "auc": 0.7636667290060966,
          "gain": -5.616036717182027e-05
        },
        {
          "helper_weight": 0.25,
          "method": "probability",
          "auc": 0.763451980358988,
          "gain": -0.00027090901428039604
        },
        {
          "helper_weight": 0.25,
          "method": "log_odds",
          "auc": 0.7634431837068637,
          "gain": -0.00027970566640467265
        }
      ],
      "alignment_verified": true
    },
    {
      "name": "cat_lean",
      "origin": "first pass",
      "helper_auc": 0.7607901174487961,
      "best": {
        "helper_weight": 0.05,
        "method": "probability",
        "auc": 0.7637142708666387,
        "gain": -8.61850662969843e-06
      },
      "blends": [
        {
          "helper_weight": 0.05,
          "method": "probability",
          "auc": 0.7637142708666387,
          "gain": -8.61850662969843e-06
        },
        {
          "helper_weight": 0.05,
          "method": "log_odds",
          "auc": 0.7637091312254538,
          "gain": -1.3758147814568744e-05
        },
        {
          "helper_weight": 0.1,
          "method": "probability",
          "auc": 0.7636889734880772,
          "gain": -3.3915885191193595e-05
        },
        {
          "helper_weight": 0.1,
          "method": "log_odds",
          "auc": 0.7636789721988784,
          "gain": -4.3917174390006863e-05
        },
        {
          "helper_weight": 0.25,
          "method": "probability",
          "auc": 0.7635298565182856,
          "gain": -0.00019303285498273315
        },
        {
          "helper_weight": 0.25,
          "method": "log_odds",
          "auc": 0.7635137752957551,
          "gain": -0.0002091140775132283
        }
      ],
      "alignment_verified": true
    },
    {
      "name": "hgb_20",
      "origin": "first pass",
      "helper_auc": 0.7532917904073893,
      "best": {
        "helper_weight": 0.05,
        "method": "probability",
        "auc": 0.7637152887382752,
        "gain": -7.600634993165656e-06
      },
      "blends": [
        {
          "helper_weight": 0.05,
          "method": "probability",
          "auc": 0.7637152887382752,
          "gain": -7.600634993165656e-06
        },
        {
          "helper_weight": 0.05,
          "method": "log_odds",
          "auc": 0.7637146659473726,
          "gain": -8.223425895792502e-06
        },
        {
          "helper_weight": 0.1,
          "method": "probability",
          "auc": 0.7636497721409937,
          "gain": -7.311723227465539e-05
        },
        {
          "helper_weight": 0.1,
          "method": "log_odds",
          "auc": 0.7636507224897411,
          "gain": -7.21668835272915e-05
        },
        {
          "helper_weight": 0.25,
          "method": "probability",
          "auc": 0.7631233859659026,
          "gain": -0.000599503407365809
        },
        {
          "helper_weight": 0.25,
          "method": "log_odds",
          "auc": 0.7631320957002655,
          "gain": -0.000590793673002854
        }
      ],
      "alignment_verified": true
    },
    {
      "name": "spline_0.1",
      "origin": "first pass",
      "helper_auc": 0.7483044119007489,
      "best": {
        "helper_weight": 0.05,
        "method": "probability",
        "auc": 0.7636223650313128,
        "gain": -0.00010052434195562121
      },
      "blends": [
        {
          "helper_weight": 0.05,
          "method": "probability",
          "auc": 0.7636223650313128,
          "gain": -0.00010052434195562121
        },
        {
          "helper_weight": 0.05,
          "method": "log_odds",
          "auc": 0.7636180004666951,
          "gain": -0.00010488890657323058
        },
        {
          "helper_weight": 0.1,
          "method": "probability",
          "auc": 0.7634468162946304,
          "gain": -0.0002760730786379728
        },
        {
          "helper_weight": 0.1,
          "method": "log_odds",
          "auc": 0.7634425515776891,
          "gain": -0.000280337795579233
        },
        {
          "helper_weight": 0.25,
          "method": "probability",
          "auc": 0.7624984185277384,
          "gain": -0.0012244708455300124
        },
        {
          "helper_weight": 0.25,
          "method": "log_odds",
          "auc": 0.7625124575420384,
          "gain": -0.00121043183122993
        }
      ],
      "alignment_verified": true
    },
    {
      "name": "cat_lean_depth6",
      "origin": "first pass",
      "helper_auc": 0.7601479927318477,
      "best": {
        "helper_weight": 0.05,
        "method": "probability",
        "auc": 0.7637041783497068,
        "gain": -1.8711023561546192e-05
      },
      "blends": [
        {
          "helper_weight": 0.05,
          "method": "probability",
          "auc": 0.7637041783497068,
          "gain": -1.8711023561546192e-05
        },
        {
          "helper_weight": 0.05,
          "method": "log_odds",
          "auc": 0.763699976845683,
          "gain": -2.291252758535034e-05
        },
        {
          "helper_weight": 0.1,
          "method": "probability",
          "auc": 0.7636678416971091,
          "gain": -5.5047676159269976e-05
        },
        {
          "helper_weight": 0.1,
          "method": "log_odds",
          "auc": 0.7636596735825162,
          "gain": -6.32157907521913e-05
        },
        {
          "helper_weight": 0.25,
          "method": "probability",
          "auc": 0.7634601606851673,
          "gain": -0.000262728688101066
        },
        {
          "helper_weight": 0.25,
          "method": "log_odds",
          "auc": 0.7634461317274677,
          "gain": -0.00027675764580070705
        }
      ],
      "alignment_verified": true
    },
    {
      "name": "r2_cat_native_missing",
      "origin": "second pass",
      "helper_auc": 0.7605612895609853,
      "best": {
        "helper_weight": 0.05,
        "method": "probability",
        "auc": 0.7637059195782507,
        "gain": -1.696979501764062e-05
      },
      "blends": [
        {
          "helper_weight": 0.05,
          "method": "probability",
          "auc": 0.7637059195782507,
          "gain": -1.696979501764062e-05
        },
        {
          "helper_weight": 0.05,
          "method": "log_odds",
          "auc": 0.763704719251148,
          "gain": -1.8170122120353405e-05
        },
        {
          "helper_weight": 0.1,
          "method": "probability",
          "auc": 0.7636725582427444,
          "gain": -5.033113052399507e-05
        },
        {
          "helper_weight": 0.1,
          "method": "log_odds",
          "auc": 0.763670171955111,
          "gain": -5.2717418157377516e-05
        },
        {
          "helper_weight": 0.25,
          "method": "probability",
          "auc": 0.7634803924103906,
          "gain": -0.00024249696287781397
        },
        {
          "helper_weight": 0.25,
          "method": "log_odds",
          "auc": 0.7634787079298064,
          "gain": -0.0002441814434619438
        }
      ],
      "alignment_verified": true
    },
    {
      "name": "r2_lgb_smooth_cats",
      "origin": "second pass",
      "helper_auc": 0.7584174292127097,
      "best": {
        "helper_weight": 0.1,
        "method": "probability",
        "auc": 0.7637711833238623,
        "gain": 4.829395059391395e-05
      },
      "blends": [
        {
          "helper_weight": 0.05,
          "method": "probability",
          "auc": 0.7637650322759986,
          "gain": 4.214290273019117e-05
        },
        {
          "helper_weight": 0.05,
          "method": "log_odds",
          "auc": 0.7637613508418862,
          "gain": 3.8461468617856376e-05
        },
        {
          "helper_weight": 0.1,
          "method": "probability",
          "auc": 0.7637711833238623,
          "gain": 4.829395059391395e-05
        },
        {
          "helper_weight": 0.1,
          "method": "log_odds",
          "auc": 0.7637650588541568,
          "gain": 4.2169480888420985e-05
        },
        {
          "helper_weight": 0.25,
          "method": "probability",
          "auc": 0.7635860456186019,
          "gain": -0.00013684375466649357
        },
        {
          "helper_weight": 0.25,
          "method": "log_odds",
          "auc": 0.7635807687766529,
          "gain": -0.00014212059661544707
        }
      ],
      "alignment_verified": true
    },
    {
      "name": "r2_xgb_finance",
      "origin": "second pass",
      "helper_auc": 0.758883318470827,
      "best": {
        "helper_weight": 0.1,
        "method": "log_odds",
        "auc": 0.7638145983865559,
        "gain": 9.17090132874776e-05
      },
      "blends": [
        {
          "helper_weight": 0.05,
          "method": "probability",
          "auc": 0.7637802673074295,
          "gain": 5.7377934161162436e-05
        },
        {
          "helper_weight": 0.05,
          "method": "log_odds",
          "auc": 0.7637864233835938,
          "gain": 6.353401032543893e-05
        },
        {
          "helper_weight": 0.1,
          "method": "probability",
          "auc": 0.7638002706041558,
          "gain": 7.738123088740778e-05
        },
        {
          "helper_weight": 0.1,
          "method": "log_odds",
          "auc": 0.7638145983865559,
          "gain": 9.17090132874776e-05
        },
        {
          "helper_weight": 0.25,
          "method": "probability",
          "auc": 0.7636719634666576,
          "gain": -5.0925906610821414e-05
        },
        {
          "helper_weight": 0.25,
          "method": "log_odds",
          "auc": 0.7637033249753213,
          "gain": -1.9564397947036127e-05
        }
      ],
      "alignment_verified": true
    }
  ],
  "helpers": 12,
  "best_helper": "r2_xgb_finance",
  "best_gain": 9.17090132874776e-05,
  "warrants_new_validation_branch": false,
  "seconds": 11.115429878234863,
  "note": "Late adaptive primary-only screening on stored OOF predictions. It does not alter frozen weights or independently confirm a new model."
}
```

## Probability, log-odds and percentile blending

```json
{
  "reference_auc": 0.7630891353395803,
  "results": [
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
      "method": "log_odds",
      "auc": 0.7630436019258241,
      "why": "Same current families/weights, change only prediction combination."
    },
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
      "method": "percentile",
      "auc": 0.7630256264707563,
      "why": "Same current families/weights, change only prediction combination."
    }
  ],
  "percentile_note": "Primary OOF empirical CDFs use predictions only, no target fitting. They are frozen and transferred to subsequent checks and inference. This is a ranking transform, not calibrated probability estimation. Primary score remains a selection diagnostic."
}
```

## Screening promotion decisions

```json
{
  "rule": "At most 2 CatBoost, 1 other tree, 1 neural model; inner-blend gain >=0.00010.",
  "chosen": [
    {
      "name": "r3_cat_feature_b512",
      "spec": {
        "name": "r3_cat_feature_b512",
        "kind": "cat",
        "features": "signed",
        "params": {
          "depth": 5,
          "l2_leaf_reg": 8,
          "random_strength": 0.5,
          "border_count": 512
        },
        "hypothesis": "Combine the eligible best new feature block (r3_cat_signed) with finer quantization under the recorded rule.",
        "max_iterations": 4500,
        "patience": 200,
        "source": "improvements/round3/followup.py"
      },
      "origin": "round3",
      "screen_auc": 0.7508543784548174,
      "screen_blend": {
        "new_weight": 0.5,
        "auc": 0.7517070328198198
      }
    },
    {
      "name": "r3_cat_signed",
      "spec": {
        "name": "r3_cat_signed",
        "kind": "cat",
        "features": "signed",
        "params": {
          "depth": 5,
          "l2_leaf_reg": 8,
          "random_strength": 0.5
        },
        "hypothesis": "Signed term residuals and rounded categories may retain structure lost by absolute distances.",
        "max_iterations": 4500,
        "patience": 200
      },
      "origin": "round3",
      "screen_auc": 0.7509073195060717,
      "screen_blend": {
        "new_weight": 0.5,
        "auc": 0.7516576204057203
      }
    },
    {
      "name": "r3_lgb_proxy",
      "spec": {
        "name": "r3_lgb_proxy",
        "kind": "lgb",
        "features": "proxy",
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
        },
        "hypothesis": "Use the exact compact successful proxy block in the known complementary LightGBM recipe."
      },
      "origin": "round3",
      "screen_auc": 0.7480538244288999,
      "screen_blend": {
        "new_weight": 0.25,
        "auc": 0.7517154923538455
      }
    }
  ],
  "decisions": [
    {
      "name": "r3_cat_borders1024",
      "promoted": false,
      "inner_gain": 0.0003163474931986432
    },
    {
      "name": "r3_cat_borders512",
      "promoted": false,
      "inner_gain": 0.0002565330705484037
    },
    {
      "name": "r3_cat_crosses",
      "promoted": false,
      "inner_gain": -3.052788365853765e-05
    },
    {
      "name": "r3_cat_depth4",
      "promoted": false,
      "inner_gain": 0.00011515770571368655
    },
    {
      "name": "r3_cat_depth4_b512",
      "promoted": false,
      "inner_gain": 0.0002971296387269673
    },
    {
      "name": "r3_cat_depth6",
      "promoted": false,
      "inner_gain": 3.733229146207773e-05
    },
    {
      "name": "r3_cat_depth7",
      "promoted": false,
      "inner_gain": 0.00014047883813073092
    },
    {
      "name": "r3_cat_depthwise",
      "promoted": false,
      "inner_gain": 0.00015509911976263613
    },
    {
      "name": "r3_cat_engineered_proxy",
      "promoted": false,
      "inner_gain": 0.0003146923669762325
    },
    {
      "name": "r3_cat_feature_b512",
      "promoted": true,
      "inner_gain": 0.00047573384963472964
    },
    {
      "name": "r3_cat_groups",
      "promoted": false,
      "inner_gain": 0.000228143058260466
    },
    {
      "name": "r3_cat_l2_30",
      "promoted": false,
      "inner_gain": -3.76886033570667e-05
    },
    {
      "name": "r3_cat_loan_b512",
      "promoted": false,
      "inner_gain": 9.696281119886407e-05
    },
    {
      "name": "r3_cat_median",
      "promoted": false,
      "inner_gain": 0.0001667194851160403
    },
    {
      "name": "r3_cat_native_b512",
      "promoted": false,
      "inner_gain": 0.0002573721275916929
    },
    {
      "name": "r3_cat_rates",
      "promoted": false,
      "inner_gain": -1.647080469990847e-05
    },
    {
      "name": "r3_cat_scores_b512",
      "promoted": false,
      "inner_gain": -6.17224153787177e-06
    },
    {
      "name": "r3_cat_signed",
      "promoted": true,
      "inner_gain": 0.0004263214355352263
    },
    {
      "name": "r3_cat_signed_only",
      "promoted": false,
      "inner_gain": 0.00023220041629190558
    },
    {
      "name": "r3_cat_slow",
      "promoted": false,
      "inner_gain": -3.114855599195554e-05
    },
    {
      "name": "r3_cat_term_categories",
      "promoted": false,
      "inner_gain": -5.536627092750379e-05
    },
    {
      "name": "r3_cat_weight2",
      "promoted": false,
      "inner_gain": 0.0001227666887642087
    },
    {
      "name": "r3_lgb_proxy",
      "promoted": true,
      "inner_gain": 0.0004841933836604584
    },
    {
      "name": "r3_lgb_proxy_smooth",
      "promoted": false,
      "inner_gain": 0.00045506775971815294
    },
    {
      "name": "r3_mlp_small",
      "promoted": false,
      "inner_gain": -0.0002962101241587023
    },
    {
      "name": "r3_mlp_wide",
      "promoted": false,
      "inner_gain": -8.919291309750221e-06
    },
    {
      "name": "r3_xgb_proxy",
      "promoted": false,
      "inner_gain": 0.0001476970274897349
    }
  ]
}
```

## Primary development selection

```json
{
  "names": [
    "round2_reference",
    "r3_cat_feature_b512",
    "r3_cat_signed"
  ],
  "weights": [
    0.5,
    0.25,
    0.25
  ],
  "method": "probability",
  "auc": 0.7637228893732684,
  "why": "Two complementary helpers with equal new-model weights.",
  "baseline_auc": 0.7630891353395803,
  "gain": 0.0006337540336880387,
  "primary_gate_passed": true,
  "fold_gains": [
    0.0007927774701395052,
    0.00044416551709702823,
    0.0005978425830635015,
    0.0004573670883321057,
    0.0009047157033553743
  ],
  "new_families": [
    {
      "name": "r3_cat_feature_b512",
      "spec": {
        "name": "r3_cat_feature_b512",
        "kind": "cat",
        "features": "signed",
        "params": {
          "depth": 5,
          "l2_leaf_reg": 8,
          "random_strength": 0.5,
          "border_count": 512
        },
        "hypothesis": "Combine the eligible best new feature block (r3_cat_signed) with finer quantization under the recorded rule.",
        "max_iterations": 4500,
        "patience": 200,
        "source": "improvements/round3/followup.py"
      },
      "origin": "round3",
      "iterations": [
        1619,
        1056,
        1041,
        1677,
        1742
      ],
      "fixed_iterations": 1619
    },
    {
      "name": "r3_cat_signed",
      "spec": {
        "name": "r3_cat_signed",
        "kind": "cat",
        "features": "signed",
        "params": {
          "depth": 5,
          "l2_leaf_reg": 8,
          "random_strength": 0.5
        },
        "hypothesis": "Signed term residuals and rounded categories may retain structure lost by absolute distances.",
        "max_iterations": 4500,
        "patience": 200
      },
      "origin": "round3",
      "iterations": [
        1240,
        1320,
        1120,
        1979,
        1312
      ],
      "fixed_iterations": 1312
    }
  ],
  "confirmation_seed": 20262209,
  "status": "frozen before confirmation"
}
```

## Frozen-winner marginal complexity

```json
{
  "winner_names": [
    "round2_reference",
    "r3_cat_feature_b512",
    "r3_cat_signed"
  ],
  "winner_weights": [
    0.5,
    0.25,
    0.25
  ],
  "winner_auc": 0.7637228893732684,
  "best_recorded_primary_recipe_with_fewer_new_families": {
    "names": [
      "round2_reference",
      "r3_cat_signed"
    ],
    "weights": [
      0.5,
      0.5
    ],
    "method": "percentile",
    "auc": 0.7635881880336729,
    "why": "Coarse blend with the complete current recipe."
  },
  "primary_marginal_gain": 0.0001347013395954777,
  "correlations": [
    {
      "a": "r3_cat_feature_b512",
      "b": "r3_cat_signed",
      "pearson": 0.9841872886860308
    }
  ],
  "note": "Descriptive complexity check on a frozen primary recipe. It does not retune weights, change gates, remove a model, or establish a separately significant marginal benefit.",
  "later_descriptive_comparisons": {
    "fixed_confirmation": {
      "frozen_winner_auc": 0.7634378860333852,
      "frozen_primary_simpler_recipe_auc": 0.7632495079477774,
      "difference": 0.0001883780856078987
    },
    "secondary": {
      "frozen_winner_auc": 0.7637168798361402,
      "frozen_primary_simpler_recipe_auc": 0.7633031588339598,
      "difference": 0.00041372100218040053
    },
    "two_seed_average": {
      "frozen_winner_auc": 0.7645840648073541,
      "frozen_primary_simpler_recipe_auc": 0.7643883148744145,
      "difference": 0.00019574993293958176
    }
  }
}
```

## Frozen new-fold-seed confirmation

```json
{
  "baseline_auc": 0.762591670510874,
  "candidate_auc": 0.7634378860333852,
  "gain": 0.0008462155225112955,
  "fold_gains": [
    0.0005013251976125899,
    0.0007489511800685689,
    0.0009191706230518015,
    0.001275702852999716,
    0.0007524485548534576
  ],
  "positive_folds": 5,
  "passed": true,
  "fold_seed": 20262209,
  "validation_early_stopping": false,
  "weights_retuned": false,
  "caveat": "A new partition of previously explored development labels, not an independent untouched test."
}
```

## Comparison against the complete two-seed reference

```json
{
  "baseline_two_seed_auc": 0.7639709612844672,
  "candidate_two_seed_auc": 0.7645840648073541,
  "gain": 0.0006131035228869042,
  "passed": true,
  "candidate_primary_auc": 0.7637228893732684,
  "candidate_secondary_auc": 0.7637168798361402,
  "secondary_gain_vs_round2": 0.0008412224203622198,
  "primary_fold_gains": [
    0.0009319686410713679,
    0.0005371153553833663,
    0.0005365944770625575,
    0.0005989921076337001,
    0.00047067982138015996
  ],
  "averaging": "Average matching family predictions across the two development seeds before the frozen blend transform.",
  "caveat": "Selection/averaging diagnostic on development rows; no new independent labels."
}
```

## Original two-seed submission or fallback

```json
{
  "accepted": true,
  "new_submission_created": true,
  "submission": "output/submission_round3.csv",
  "sha256": "59f35bb06c11f10cf3ed8a2223fdf1bc4761d8a06b0f27e795d6d7703513cfb5",
  "rows": 61500,
  "full_oof": {
    "auc": 0.7650940891573292,
    "average_precision": 0.24803950024378554,
    "log_loss": 0.24425980213492984,
    "brier": 0.06752379979226311
  },
  "full_oof_independent": false,
  "public_score": null,
  "recommendation": "Locally validated third-pass candidate; upload to measure its public score.",
  "probability_min": 0.0021992436660287287,
  "probability_max": 0.8139739220823835,
  "probability_mean": 0.08846170078087252,
  "new_saved_models": 20,
  "baseline_saved_models": 30,
  "inference_method": "probability"
}
```

## Prospective three-seed averaging check

```json
{
  "passed": true,
  "reference_two_seed": {
    "auc": 0.7639709612844672,
    "average_precision": 0.24961659654110502,
    "log_loss": 0.24435931684195786,
    "brier": 0.06749072319513301
  },
  "reference_three_seed": {
    "auc": 0.7641962032758703,
    "average_precision": 0.25012185409994864,
    "log_loss": 0.2442864391747145,
    "brier": 0.06747106274719959
  },
  "candidate_two_seed": {
    "auc": 0.7645840648073541,
    "average_precision": 0.24943312367136428,
    "log_loss": 0.24425825341011867,
    "brier": 0.06748653279473298
  },
  "candidate_three_seed": {
    "auc": 0.7648034854637242,
    "average_precision": 0.25007404217161094,
    "log_loss": 0.24417548816405393,
    "brier": 0.06746233457930292
  },
  "reference_increment": 0.00022524199140316892,
  "candidate_increment": 0.00021942065637015062,
  "recipe_gain_at_three_seeds": 0.0006072821878538859,
  "reference_fold_increments": [
    0.0005496552159472978,
    -2.3241949901775527e-05,
    0.0002221635844950054,
    0.00035100014295430526,
    2.669747079608875e-05
  ],
  "candidate_fold_increments": [
    0.0006577693951486108,
    8.980660703872267e-06,
    0.00018974339935362572,
    0.0002309287093421597,
    -4.1294003250147426e-07
  ],
  "note": "Conditional development averaging diagnostic. No weights, transforms or seed subsets were retuned."
}
```

## Three-seed extension decision

```json
{
  "accepted": true,
  "new_submission_created": true,
  "submission": "output/submission_round3_bagged.csv",
  "sha256": "7d933ea1e9bffea4e3bf034a81a8ece315655dcebdeb9408682d159d60bbfb02",
  "rows": 61500,
  "full_oof": {
    "auc": 0.7650709143402641,
    "average_precision": 0.248402241005085,
    "log_loss": 0.24424449387026184,
    "brier": 0.06751501960492942
  },
  "full_oof_independent": false,
  "public_score": null,
  "recommendation": "Third-pass recipe plus prospectively validated three-seed averaging; public score unknown until uploaded.",
  "probability_min": 0.002241952921346727,
  "probability_max": 0.8128047091418165,
  "probability_mean": 0.0884137868529318,
  "new_saved_models": 30,
  "baseline_saved_models": 45,
  "inference_method": "probability",
  "seeds_per_family": 3,
  "additional_third_seed_models": 25
}
```

## Integrity and reproduction checks

```json
{
  "final": true,
  "local_venv": true,
  "protected_files_checked": 31,
  "protected_hashes_match": true,
  "omitted_from_code_archive": [],
  "splits_disjoint": true,
  "features_ignore_target_ID": true,
  "row_batch_invariance": true,
  "train_test_schema_matches": true,
  "hypothetical_rate_formula_verified": true,
  "neural_unseen_categories_finite": true,
  "fitted_encoder_batch_invariance": true,
  "screening_signatures_verified_with_documented_metadata_alias": true,
  "recommended_submission_sha256": "7d933ea1e9bffea4e3bf034a81a8ece315655dcebdeb9408682d159d60bbfb02",
  "three_seed_extension_freeze_and_reproduction_verified": true,
  "selection_and_source_freeze_intact": true,
  "submission_schema_and_order_valid": true,
  "saved_model_reproduction_verified": true,
  "new_notebooks_fully_executed": true
}
```

## Post-submission public result

```json
{
  "score": 0.76824,
  "rank": 518,
  "username": "hasanRocky",
  "observed_date_bangladesh": "2026-11-09",
  "submission": "output/submission_round3_bagged.csv",
  "sha256": "7d933ea1e9bffea4e3bf034a81a8ece315655dcebdeb9408682d159d60bbfb02",
  "source": "User explicitly confirmed submitting round 3 bagged and supplied a leaderboard screenshot.",
  "file_attribution": "Explicitly confirmed by user; local CSV identity verified by SHA-256.",
  "previous_round2_score": 0.76756,
  "previous_round2_rank_snapshot": 568,
  "gain_vs_round2": 0.00068,
  "first_pass_score": 0.7654,
  "gain_vs_first_pass": 0.00284,
  "rank_is_snapshot": true,
  "private_full_test_score": null,
  "used_for_model_selection": false,
  "interpretation": "Observed overall public-score gain for the frozen round-three bagged recipe. It does not isolate the marginal benefit of the third seed or establish private/full-test improvement."
}
```

## Common-fold development validation

| Model | OOF AUC | Fold AUCs | Iterations | Seconds |
| --- | --- | --- | --- | --- |
| r3_cat_feature_b512 | 0.762661887 | [0.7580250631001172, 0.765108610045002, 0.7626256190122456, 0.7606695413043127, 0.7670705280030794] | [1619, 1056, 1041, 1677, 1742] | 475.5 |
| r3_cat_signed | 0.762850230 | [0.7583912545503287, 0.7651902981347654, 0.7624314032438613, 0.7620548441405436, 0.766348511333229] | [1240, 1320, 1120, 1979, 1312] | 457.5 |
| r3_lgb_proxy | 0.759216711 | [0.7544512449575741, 0.7625559470465041, 0.7601162427983408, 0.7567239419079855, 0.7623564764078381] | [517, 722, 523, 498, 475] | 34.0 |

## Fixed-iteration new-seed model results

| Model | OOF AUC | Fold AUCs | Iterations | Seconds |
| --- | --- | --- | --- | --- |
| lgb_tune_15 | 0.757591374 | [0.7579192289775013, 0.7631491915312872, 0.7644103097913036, 0.749541586664696, 0.7532803417563526] | [590, 590, 590, 590, 590] | 28.6 |
| r2_cat_proxies_native | 0.761593845 | [0.7641420958553025, 0.7667635841608519, 0.7693175044518481, 0.7553140679840686, 0.7525333511914936] | [1557, 1557, 1557, 1557, 1557] | 388.6 |
| r2_cat_term_proxies | 0.761446485 | [0.7641738909750907, 0.7672138385659063, 0.7680261572879021, 0.7545969263042134, 0.7534403470419849] | [1568, 1568, 1568, 1568, 1568] | 403.0 |
| r3_cat_feature_b512 | 0.762721274 | [0.7640600676778244, 0.7683261652393792, 0.769402120237001, 0.7567688092888627, 0.7552328299534491] | [1619, 1619, 1619, 1619, 1619] | 507.8 |
| r3_cat_signed | 0.762738842 | [0.7645333140683512, 0.7677509000373254, 0.7702967018110455, 0.7561550709363529, 0.7550886959281957] | [1312, 1312, 1312, 1312, 1312] | 389.6 |

## Matching secondary-seed model results

| Model | OOF AUC | Fold AUCs | Iterations | Seconds |
| --- | --- | --- | --- | --- |
| r3_cat_feature_b512 | 0.763326145 | [0.768523036075953, 0.756567660450415, 0.7682904222097774, 0.760604790740637, 0.7631262863979708] | [1619, 1619, 1619, 1619, 1619] | 463.4 |
| r3_cat_signed | 0.762552994 | [0.7668597976329494, 0.7571787225660348, 0.7671270674221844, 0.76022275343429, 0.7617774626666303] | [1312, 1312, 1312, 1312, 1312] | 377.5 |

## Exploratory error slices

Two-seed development OOF was summarized by external-score missing count, contract, income type, age band and gender. The large slices show small average calibration residuals; low slice AUC alone does not justify a specialist. Tiny categories are unstable and will not receive manually adjusted predictions. Counts, rates, residuals, AUC and loss are in `improvements/round3/artifacts/current_model_slice_diagnostic.csv`.

## Limits and stopping

The primary validation labels have already been explored. A new fold seed changes training/validation assignment, not the available evidence. Conditional bootstrap intervals do not include the uncertainty introduced by searching. Full-data OOF is diagnostic after selection. Public/private performance of a new file remains unknown until it is evaluated.

A failed gate retains the existing submission. No global-optimum or exhaustive-search claim is made. The final report records which hypotheses were tested, which remain untested, and why the pass stopped.
