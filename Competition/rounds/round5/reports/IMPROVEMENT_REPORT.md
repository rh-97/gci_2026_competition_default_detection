# Competition improvement report — higher-upside experiments

Current consolidated documentation: [PROJECT_REPORT.md](../../../PROJECT_REPORT.md).
It covers the complete data/model history and links all recorded experiments.
See [cleanup and recovery](../../../docs/CLEANUP_REPORT.md) for the Git snapshot and current entry point.

## Latest leaderboard observation

The user's new screenshot shows **0.77029 public AUC**, rank snapshot **364**, for `hasanRocky`: **+0.00205** relative to the previous explicitly attributed 0.76824. The screenshot does not identify the uploaded filename. The higher-upside CSV is the likely file from conversation context, but that attribution remains unconfirmed. This is a public-subset result, not a private/full-test score.

**A better score has not been shown to be unachievable.** The completed experiments establish results for particular recipes; they do not estimate the dataset's optimum. A further **+0.02971** is needed to reach 0.8 from this observation. That larger jump has no supporting result yet and is not promised. Retrieval/profile-based learning and genuinely nested learned combination of the new diverse families remain untested; the earlier inexpensive stacking probe involved older families and did not support expansion at that time. These are research gaps, not predicted gains. More nearby tree settings or seeds are lower priority under the user's preference for substantial progress.

No fitting, blend-weight changes or additional submission were performed in response to this screenshot. Frozen training evidence, notebooks, CSVs and the delivered reproduction ZIP remain unchanged. The following report records the state at candidate creation; its statements that the candidate public score was unknown are historical and remain appropriate while filename attribution is unconfirmed. Observation record: `improvements/high_upside/artifacts/model_public_leaderboard_observation.json`.

---

A new higher-upside candidate passed every declared local gate. Its public score is unknown.

Recommended file: [`output/submission_high_upside.csv`](../../../output/submission_high_upside.csv). SHA-256: `15d050aa8709ae4e2d338b013c03216d4b3f3279348a3faca71080c17e44baed`.
Confirmed previous public score: **0.76824**, rank snapshot **518**, explicitly attributed by the user to `submission_round3_bagged.csv`.
A new CSV has been created and locally reproduced; submit it to measure its public score.

## Goal, constraints and research change

The target is **0.8+**, requiring +0.03176 public AUC over the confirmed score. The user reports top-ten scores displayed as 1 and top-twenty scores above 0.8, with unknown data/method provenance. This is relevant competitive context, not independently verified attainability under the permitted data. The supplied README restricts this task to a subset of Home Credit data; only the supplied train/test rows were used. No online dataset, original history table, recovered labels or pretrained weights were imported. All modeling used the local venv. All ten notebooks existing before this modeling phase are preserved.

The incremental round-four sweep was stopped after seven screens at the user's priority change. Its partial evidence remains in `ROUND4_EXPERIMENT_LOG.md`; it did not produce a submission. The opportunity audit in new notebook 07 found a single-model training-sample AUC 0.8141 versus held-out 0.7652, illustrating a generalization gap. Lower AUC in a missing-score slice did not imply disproportionate global ranking-loss contribution. That motivated new model/representation families rather than another depth/seed sweep. The audit does not estimate the data ceiling.

## Six structural pilots

Four scratch TabM recipes evaluated raw/engineered inputs, piecewise-linear/periodic numerical embeddings and a regularized full TabM recipe. Two learned-feature CatBoost recipes tested fold-safe auxiliary external-score reconstructions and regularized interaction-risk encodings. All retained missingness and trained preprocessing only on their training rows. Neural loss optimizes the mean of individual member BCE losses; inference averages probabilities. Settings, timings, curves, errors, per-trial interpretations and exact software versions are retained.

After the first three CPU pilots, a local hardware probe outside the sandbox revealed a roughly three-times-faster MPS GPU. A prospective amendment moved remaining neural fits to it before any primary CV. Original CPU results and signatures remain unchanged and explicitly checked; new fits have a separately hashed implementation/backend identity. All inference stays on CPU for exact saved-weight replay. No hyperparameter or score gate changed; GPU retraining bit identity is not promised. See `improvements/high_upside/ACCELERATOR_AMENDMENT.md` and executed notebook 08b.

| Pilot | Individual inner AUC | Best screened blend gain | Retained epochs/trees | Seconds | Status |
| --- | --- | --- | --- | --- | --- |
| hu_tabm_raw_piecewise | 0.7401112 | +0.0002394 | 28 | 278.6 | complete |
| hu_tabm_signed_piecewise | 0.7508052 | +0.0015386 | 30 | 366.8 | complete |
| hu_tabm_signed_periodic | 0.7481982 | +0.0009184 | 37 | 442.0 | complete |
| hu_tabm_regularized | 0.7501469 | +0.0009786 | 37 | 263.1 | complete |
| hu_cat_score_reconstruction | 0.7507566 | +0.0003659 | 1217 | 112.7 | complete |
| hu_cat_interaction_risk | 0.7453797 | -0.0001325 | 991 | 99.3 | complete |

The inner split is repeatedly explored. It screens hypotheses; it does not establish hidden-test improvement. Promotion allows at most one neural and one learned-feature finalist, with >=0.00030 blend gain. A meaningful branch targets >=0.002 OOF gain; smaller robust gains can qualify a candidate but do not trigger a broad expansion. No new seed-bank sweep was run. The unified ledger contains 135 records, including 132 main configurations and separately labeled auxiliary probes. Software checks and fold refits do not inflate this count.

## Frozen validation and result

Primary choice:
```json
{
  "names": [
    "round3_reference",
    "hu_tabm_signed_piecewise",
    "hu_cat_score_reconstruction"
  ],
  "weights": [
    0.25,
    0.375,
    0.375
  ],
  "method": "probability",
  "auc": 0.7654305267165775,
  "baseline_auc": 0.7637228893732684,
  "gain": 0.001707637343309143,
  "primary_gate_passed": true,
  "substantial_gain": false,
  "fold_gains": [
    0.0025327478961900685,
    0.0021043124935127278,
    0.0017645022537956523,
    0.0027759581462415417,
    0.00024191104338100455
  ],
  "new_families": [
    {
      "name": "hu_tabm_signed_piecewise",
      "spec": {
        "kind": "tabm",
        "architecture": "tabm-mini",
        "dropout": 0.1,
        "learning_rate": 0.002,
        "weight_decay": 0.0003,
        "max_epochs": 140,
        "patience": 20,
        "max_seconds": 1500,
        "name": "hu_tabm_signed_piecewise",
        "features": "signed",
        "embedding": "piecewise",
        "hypothesis": "Same neural recipe with the successful tree representation."
      },
      "origin": "high_upside",
      "counts": [
        29,
        32,
        40,
        40,
        41
      ],
      "fixed_count": 40
    },
    {
      "name": "hu_cat_score_reconstruction",
      "spec": {
        "name": "hu_cat_score_reconstruction",
        "kind": "cat",
        "features": "signed",
        "learned": "score_reconstruction",
        "params": {
          "depth": 5,
          "l2_leaf_reg": 8,
          "random_strength": 0.5
        },
        "max_iterations": 4500,
        "patience": 200,
        "hypothesis": "Use observed external scores as auxiliary supervised targets, with nested OOF reconstructions and residuals."
      },
      "origin": "high_upside",
      "counts": [
        1166,
        848,
        1150,
        1537,
        1085
      ],
      "fixed_count": 1150
    }
  ],
  "confirmation_seed": 20264209,
  "grid_size": 61,
  "best_attempt": {
    "names": [
      "round3_reference",
      "hu_tabm_signed_piecewise",
      "hu_cat_score_reconstruction"
    ],
    "weights": [
      0.25,
      0.375,
      0.375
    ],
    "method": "probability",
    "auc": 0.7654305267165775
  },
  "complexity_policy": "COMPLEXITY_POLICY.md",
  "budget_policy_applied": false,
  "unconstrained_best": {
    "names": [
      "round3_reference",
      "hu_tabm_signed_piecewise",
      "hu_cat_score_reconstruction"
    ],
    "weights": [
      0.25,
      0.375,
      0.375
    ],
    "method": "probability",
    "auc": 0.7654305267165775
  },
  "best_at_most_one_new_family": {
    "names": [
      "round3_reference",
      "hu_tabm_signed_piecewise"
    ],
    "weights": [
      0.6666666666666666,
      0.33333333333333337
    ],
    "method": "probability",
    "auc": 0.7650343253899636
  },
  "second_family_increment": 0.0003962013266138875,
  "minimum_increment_for_second_family": 0.0003
}
```

Fresh-fold confirmation:
```json
{
  "baseline": {
    "auc": 0.7627263204899741,
    "average_precision": 0.24775138426099164,
    "log_loss": 0.2447785588143546,
    "brier": 0.06758934274011608
  },
  "candidate": {
    "auc": 0.7642283520726878,
    "average_precision": 0.24943991449967523,
    "log_loss": 0.2443028793338643,
    "brier": 0.06749568766964958
  },
  "gain": 0.0015020315827136699,
  "fold_gains": [
    0.001609001821388234,
    0.0019942993998888214,
    0.0009308454819668688,
    0.000983059043299872,
    0.002170197363790871
  ],
  "positive_folds": 5,
  "passed": true,
  "weights_retuned": false,
  "validation_early_stopping": false,
  "caveat": "Fresh partition of repeatedly explored labels; not an untouched test."
}
```

Matching three-seed check:
```json
{
  "baseline": {
    "auc": 0.7648034854637242,
    "average_precision": 0.25007404217161094,
    "log_loss": 0.24417548816405393,
    "brier": 0.06746233457930292
  },
  "candidate": {
    "auc": 0.7662609426013722,
    "average_precision": 0.2520906983798925,
    "log_loss": 0.24371664207520882,
    "brier": 0.06737021878880448
  },
  "gain": 0.0014574571376479994,
  "fold_gains": [
    0.0014812109333846024,
    0.001834659175215192,
    0.001729208257228887,
    0.0018530695296581357,
    0.00047769980193235195
  ],
  "passed": true,
  "substantial_gain": false,
  "weights_retuned": false,
  "caveat": "Matching three-seed development comparison. Selection and fitting uncertainty are not removed."
}
```

Final result:
```json
{
  "accepted": true,
  "new_submission_created": true,
  "submission": "output/submission_high_upside.csv",
  "sha256": "15d050aa8709ae4e2d338b013c03216d4b3f3279348a3faca71080c17e44baed",
  "public_score": null,
  "rows": 61500,
  "full_oof": {
    "auc": 0.766714324202899,
    "average_precision": 0.25059665387214314,
    "log_loss": 0.24369573497604352,
    "brier": 0.06739773971111182
  },
  "full_oof_independent": false,
  "new_models": 30,
  "baseline_models": 75,
  "probability_min": 0.0020452367452790336,
  "probability_max": 0.7723455048775054,
  "probability_mean": 0.08895300053329237,
  "recommendation": "Passed local gates; public score unknown. The 0.8 target is not an achieved score."
}
```

Deployment counts, including auxiliary models inside the saved predictor bundles:
```json
{
  "primary_new_predictor_bundles": 30,
  "auxiliary_reconstruction_regressors": 45,
  "neural_shared_internal_members": 240,
  "legacy_primary_models": 75,
  "note": "Each reconstructed-score primary bundle also contains three auxiliary regressors. TabM internal members share weights and are not separate saved fold models. new_models in the final result counts primary fold predictor bundles."
}
```

Conditional uncertainty on frozen predictions:
```json
{
  "primary_frozen": {
    "gain": 0.001707637343309143,
    "ci95": [
      0.0010390022242385,
      0.002375515218320242
    ],
    "replicates": 400
  },
  "caveat": "Paired stratified row resampling conditions on fitted OOF predictions. It omits fitting and search uncertainty; not a search-adjusted significance test or an independent test. Does not alter any gate or prediction.",
  "confirmation": {
    "gain": 0.0015020315827136699,
    "ci95": [
      0.0008133889646946863,
      0.0022310427240533667
    ],
    "replicates": 400
  },
  "three_seed": {
    "gain": 0.0014574571376479994,
    "ci95": [
      0.0009880384437517375,
      0.0020329388462262204
    ],
    "replicates": 400
  }
}
```

Any row-bootstrap intervals condition on fitted predictions and exclude fitting/search uncertainty; they are not independent or search-adjusted significance tests and do not change gates.

The complete pair/helper grid and winning recipe were frozen before confirmation. Primary and matching-three-seed eligibility require >=0.00030 gain; confirmation requires positive pooled gain and four positive groups out of five. Epoch/tree counts, weights and combination methods stay fixed. Confirmation seed 20264209 is a new partition of already explored development labels, not an untouched test. Historical audit and public scores did not tune the candidate. Final full-data OOF, if produced, is diagnostic and did not change selection.

A budget-aware selection amendment was recorded after neural CV and while tree CV was incomplete, before the full joint-grid choice and any confirmation. A second new family must add >=0.00030 primary AUC over the best one-family addition to earn the later training cost; otherwise the simpler recipe is selected. The complete unconstrained grid and both maxima remain recorded. This is an adaptive compute-allocation decision, not a significance claim. Fitting code/inputs were unchanged and completed caches were retained; only the selection controller changed while both workers were stopped. See `improvements/high_upside/COMPLEXITY_POLICY.md`.

## Documentation and reproduction

- [HIGH_UPSIDE_EXPERIMENT_LOG.md](HIGH_UPSIDE_EXPERIMENT_LOG.md): complete audit and modeling journal, why/how, failures and negative results.
- [HIGH_UPSIDE_PLAN.md](../plans/HIGH_UPSIDE_PLAN.md), and `improvements/high_upside/MODELING_PLAN.md`: strategy and exact pre-fit rules.
- [07_signal_opportunity_audit.ipynb](../notebooks/07_signal_opportunity_audit.ipynb): executed opportunity audit.
- [08_high_upside_modeling_plan.ipynb](../notebooks/08_high_upside_modeling_plan.ipynb): executed plan created before fitting.
- [08b_local_gpu_amendment.ipynb](../notebooks/08b_local_gpu_amendment.ipynb): prospective accelerator amendment before primary validation.
- [08c_compute_budget_policy.ipynb](../notebooks/08c_compute_budget_policy.ipynb): budget-aware selection rule recorded before recipe freeze.
- [09_high_upside_results_reproduction.ipynb](../notebooks/09_high_upside_results_reproduction.ipynb): executed results and reproduction evidence.
- `improvements/high_upside/artifacts/model_complete_experiment_ledger.json` and `.csv`: combined trial records.
- [REPRODUCTION_README.md](../../../REPRODUCTION_README.md): local-venv inference and full phase commands.
- [output/competition_high_upside_reproduction.zip](../../../docs/OUTPUTS.md): new source/model/evidence archive, excluding the supplied input directory and venv.

All protected old file hashes and new notebook execution are checked. The recommended file has 61,500 finite scores in original sample/test ID order. For an accepted new candidate, saved-model replay is byte-identical on the recorded local runtime; the retained reference has its earlier exact replay evidence and unchanged checksum. Cross-platform numerical equivalence is subject to the pinned runtime/hardware. Prior reports and archives remain unchanged as historical evidence, apart from the current living report/readme; pre-modeling snapshots are under `improvements/high_upside/reference/before_modeling`.

## Stopping and remaining uncertainty

These six structural hypotheses and their declared gates were evaluated. Completing this pass does not establish a global optimum. Fully nested stacking, retrieval models, stronger auxiliary tasks and larger neural budgets remain possible directions, conditional on evidence and compute. A failure here does not prove those directions ineffective. A new architecture alone is no guarantee of a 0.03 AUC jump. The report distinguishes actual results from the 0.8 target and from other entrants' unverified methods.

The supplied competition documents give November 20, 2026, 01:00 UTC (07:00 Bangladesh) as the deadline and say the last submitted file determines the entry; this is the local-document record, not a live platform check. Code ZIP reproduction is needed for Honors/Outstanding consideration.
