# Complete experiment catalog

Generated from the saved unified ledger. All 135 entries are included: 132 main screening configurations and three separately labeled meta-learning probes. Fold refits and software checks are not additional competitive configurations.

**Do not rank this catalog as one common benchmark.** References and evaluation stages differ. A delta may describe standalone performance or the best screened blend; those are labeled separately below. Earlier motives reconstructed from code are distinguished from prospectively recorded hypotheses in the source ledger.

Full raw records: [JSON](../improvements/high_upside/artifacts/model_complete_experiment_ledger.json) and [CSV](../improvements/high_upside/artifacts/model_complete_experiment_ledger.csv).

## previous passes

### 1. tutorial_rf

Type: main screening configuration; status: complete.

**Reason:** Establish a fair, split-safe version of the supplied five-feature tutorial baseline.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.6599833 |
| Reference AUC, when recorded | 0.6599833 |
| Ledger delta versus its recorded reference | 0.0000000 |
| Average precision | 0.1497417 |
| Log loss | 0.2680230 |
| Brier score | 0.0721502 |

**Outcome / interpretation:** A reference point, not a serious attempt to use all available information.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 2. lgb_raw

Type: main screening configuration; status: complete.

**Reason:** Using all original predictors and histogram boosting should improve on the five-feature RF.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7367838 |
| Reference AUC, when recorded | 0.6599833 |
| Ledger delta versus its recorded reference | 0.0768006 |
| Average precision | 0.2225884 |
| Log loss | 0.2519797 |
| Brier score | 0.0689638 |
| Development CV AUC | 0.7499471 |
| Selected epochs/trees | 483.0000000 |
| Recorded call seconds | 5.1360619 |

**Outcome / interpretation:** Algorithm and feature count change jointly; the next raw/engineered comparison is the controlled feature ablation.

**Decision:** Advanced to five-fold development CV

**Recorded recipe/settings:**

```json
{
  "name": "lgb_raw",
  "kind": "lgb",
  "features": "raw",
  "params": {
    "num_leaves": 24,
    "max_depth": -1,
    "min_child_samples": 100,
    "colsample_bytree": 0.9,
    "subsample": 0.85,
    "subsample_freq": 1,
    "reg_lambda": 10,
    "reg_alpha": 0.1,
    "max_bin": 127
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 3. lgb_engineered

Type: main screening configuration; status: complete.

**Reason:** Loan/income ratios, age/employment ratios and external-score summaries may simplify useful interactions.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7440631 |
| Reference AUC, when recorded | 0.7367838 |
| Ledger delta versus its recorded reference | 0.0072793 |
| Average precision | 0.2326303 |
| Log loss | 0.2500309 |
| Brier score | 0.0684857 |
| Development CV AUC | 0.7561022 |
| Selected epochs/trees | 662.0000000 |
| Recorded call seconds | 9.0067079 |

**Outcome / interpretation:** Same-settings five-fold CV confirms a gain from 0.749947 to 0.756102, supporting this feature family.

**Decision:** Advanced to five-fold development CV

**Recorded recipe/settings:**

```json
{
  "name": "lgb_engineered",
  "kind": "lgb",
  "features": "engineered",
  "params": {
    "num_leaves": 24,
    "max_depth": -1,
    "min_child_samples": 100,
    "colsample_bytree": 0.9,
    "subsample": 0.85,
    "subsample_freq": 1,
    "reg_lambda": 10,
    "reg_alpha": 0.1,
    "max_bin": 127
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 4. lgb_extended

Type: main screening configuration; status: complete.

**Reason:** Additional categorical crosses, log features, age bands and optional group summaries may expose further structure.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7375499 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0065133 |
| Average precision | 0.2239787 |
| Log loss | 0.2520395 |
| Brier score | 0.0689272 |
| Selected epochs/trees | 486.0000000 |
| Recorded call seconds | 9.6748250 |

**Outcome / interpretation:** The broader representation screened worse; added split opportunities or sparse category combinations may introduce noise.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_extended",
  "kind": "lgb",
  "features": "extended",
  "params": {
    "num_leaves": 24,
    "max_depth": -1,
    "min_child_samples": 100,
    "colsample_bytree": 0.9,
    "subsample": 0.85,
    "subsample_freq": 1,
    "reg_lambda": 10,
    "reg_alpha": 0.1,
    "max_bin": 127
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 5. lgb_grouped

Type: main screening configuration; status: complete.

**Reason:** Additional categorical crosses, log features, age bands and optional group summaries may expose further structure.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7373983 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0066648 |
| Average precision | 0.2244680 |
| Log loss | 0.2519703 |
| Brier score | 0.0688948 |
| Selected epochs/trees | 459.0000000 |
| Recorded call seconds | 11.6373971 |

**Outcome / interpretation:** The broader representation screened worse; added split opportunities or sparse category combinations may introduce noise.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_grouped",
  "kind": "lgb",
  "features": "extended",
  "groups": true,
  "params": {
    "num_leaves": 24,
    "max_depth": -1,
    "min_child_samples": 100,
    "colsample_bytree": 0.9,
    "subsample": 0.85,
    "subsample_freq": 1,
    "reg_lambda": 10,
    "reg_alpha": 0.1,
    "max_bin": 127
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 6. lgb_tune_00

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7436435 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0004197 |
| Average precision | 0.2329525 |
| Log loss | 0.2502113 |
| Brier score | 0.0685275 |
| Selected epochs/trees | 435.0000000 |
| Recorded call seconds | 10.3765440 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_00",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 45,
    "min_child_samples": 148,
    "colsample_bytree": 0.7652330811644328,
    "subsample": 0.8271190783202719,
    "subsample_freq": 1,
    "reg_lambda": 0.652583271652393,
    "reg_alpha": 0.018170180928652968,
    "max_bin": 255,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 7. lgb_tune_01

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7387116 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0053516 |
| Average precision | 0.2267722 |
| Log loss | 0.2514480 |
| Brier score | 0.0688011 |
| Selected epochs/trees | 339.0000000 |
| Recorded call seconds | 7.6909690 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_01",
  "kind": "lgb",
  "features": "extended",
  "groups": true,
  "params": {
    "num_leaves": 20,
    "min_child_samples": 349,
    "colsample_bytree": 0.8967196619343512,
    "subsample": 0.9890245833565928,
    "subsample_freq": 1,
    "reg_lambda": 8.310860102624094,
    "reg_alpha": 0.6732698427206649,
    "max_bin": 127,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 8. lgb_tune_02

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7430297 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0010334 |
| Average precision | 0.2312014 |
| Log loss | 0.2500058 |
| Brier score | 0.0684850 |
| Selected epochs/trees | 259.0000000 |
| Recorded call seconds | 6.4498808 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_02",
  "kind": "lgb",
  "features": "engineered",
  "groups": false,
  "params": {
    "num_leaves": 47,
    "min_child_samples": 204,
    "colsample_bytree": 0.725046618438576,
    "subsample": 0.8572834631300237,
    "subsample_freq": 1,
    "reg_lambda": 13.320793623704482,
    "reg_alpha": 6.045311521986175,
    "max_bin": 63,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 9. lgb_tune_03

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7357151 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0083481 |
| Average precision | 0.2228402 |
| Log loss | 0.2524195 |
| Brier score | 0.0689751 |
| Selected epochs/trees | 335.0000000 |
| Recorded call seconds | 8.3812780 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_03",
  "kind": "lgb",
  "features": "extended",
  "groups": true,
  "params": {
    "num_leaves": 42,
    "min_child_samples": 52,
    "colsample_bytree": 0.8877509010778653,
    "subsample": 0.7129799526301828,
    "subsample_freq": 1,
    "reg_lambda": 0.6853497491826263,
    "reg_alpha": 0.002578254216781311,
    "max_bin": 127,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 10. lgb_tune_04

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7388008 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0052623 |
| Average precision | 0.2255307 |
| Log loss | 0.2513364 |
| Brier score | 0.0687702 |
| Selected epochs/trees | 317.0000000 |
| Recorded call seconds | 8.5409932 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_04",
  "kind": "lgb",
  "features": "extended",
  "groups": true,
  "params": {
    "num_leaves": 30,
    "min_child_samples": 160,
    "colsample_bytree": 0.6824704554254913,
    "subsample": 0.8238561240836021,
    "subsample_freq": 1,
    "reg_lambda": 4.0749466913192975,
    "reg_alpha": 0.008450124590987818,
    "max_bin": 63,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 11. lgb_tune_05

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7428564 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0012068 |
| Average precision | 0.2304751 |
| Log loss | 0.2504384 |
| Brier score | 0.0685989 |
| Selected epochs/trees | 350.0000000 |
| Recorded call seconds | 11.1955421 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_05",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 37,
    "min_child_samples": 234,
    "colsample_bytree": 0.9624419798590104,
    "subsample": 0.8168366720016197,
    "subsample_freq": 1,
    "reg_lambda": 3.386424244493785,
    "reg_alpha": 0.04330527884780594,
    "max_bin": 63,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 12. lgb_tune_06

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7433577 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0007054 |
| Average precision | 0.2325327 |
| Log loss | 0.2500575 |
| Brier score | 0.0684645 |
| Selected epochs/trees | 564.0000000 |
| Recorded call seconds | 10.5338819 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_06",
  "kind": "lgb",
  "features": "engineered",
  "groups": false,
  "params": {
    "num_leaves": 20,
    "min_child_samples": 294,
    "colsample_bytree": 0.8198210636755052,
    "subsample": 0.9148380294892694,
    "subsample_freq": 1,
    "reg_lambda": 0.3808158557191752,
    "reg_alpha": 0.00190476335724297,
    "max_bin": 63,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 13. lgb_tune_07

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7395693 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0044939 |
| Average precision | 0.2269390 |
| Log loss | 0.2512720 |
| Brier score | 0.0687676 |
| Selected epochs/trees | 297.0000000 |
| Recorded call seconds | 11.9626980 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_07",
  "kind": "lgb",
  "features": "extended",
  "groups": false,
  "params": {
    "num_leaves": 45,
    "min_child_samples": 176,
    "colsample_bytree": 0.7313531708890701,
    "subsample": 0.9899086313887235,
    "subsample_freq": 1,
    "reg_lambda": 14.16537350976517,
    "reg_alpha": 7.043741573368013,
    "max_bin": 127,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 14. lgb_tune_08

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7435078 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0005554 |
| Average precision | 0.2315462 |
| Log loss | 0.2500829 |
| Brier score | 0.0685050 |
| Selected epochs/trees | 782.0000000 |
| Recorded call seconds | 14.3347461 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_08",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 13,
    "min_child_samples": 97,
    "colsample_bytree": 0.9200665023873321,
    "subsample": 0.6784069253819305,
    "subsample_freq": 1,
    "reg_lambda": 0.45177078769529433,
    "reg_alpha": 5.17238600396412,
    "max_bin": 255,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 15. lgb_tune_09

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7444408 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0003776 |
| Average precision | 0.2324412 |
| Log loss | 0.2499914 |
| Brier score | 0.0685029 |
| Selected epochs/trees | 456.0000000 |
| Recorded call seconds | 13.7315803 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_09",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 38,
    "min_child_samples": 162,
    "colsample_bytree": 0.7634614881240677,
    "subsample": 0.9631927502349246,
    "subsample_freq": 1,
    "reg_lambda": 0.23470730903827638,
    "reg_alpha": 0.17481947281502147,
    "max_bin": 255,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 16. lgb_tune_10

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7447465 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0006834 |
| Average precision | 0.2322923 |
| Log loss | 0.2497982 |
| Brier score | 0.0684725 |
| Selected epochs/trees | 793.0000000 |
| Recorded call seconds | 15.1419518 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_10",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 14,
    "min_child_samples": 131,
    "colsample_bytree": 0.8530873294402385,
    "subsample": 0.9555468612325263,
    "subsample_freq": 1,
    "reg_lambda": 0.6587863894843841,
    "reg_alpha": 0.21547047510160577,
    "max_bin": 255,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 17. lgb_tune_11

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7450017 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0009386 |
| Average precision | 0.2341463 |
| Log loss | 0.2496761 |
| Brier score | 0.0684036 |
| Selected epochs/trees | 728.0000000 |
| Recorded call seconds | 16.7352030 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_11",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 17,
    "min_child_samples": 100,
    "colsample_bytree": 0.8000881291780853,
    "subsample": 0.933325997310737,
    "subsample_freq": 1,
    "reg_lambda": 0.36604656775974564,
    "reg_alpha": 0.22552926805304213,
    "max_bin": 255,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 18. lgb_tune_12

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7465781 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0025150 |
| Average precision | 0.2350551 |
| Log loss | 0.2492637 |
| Brier score | 0.0683387 |
| Development CV AUC | 0.7573877 |
| Selected epochs/trees | 849.0000000 |
| Recorded call seconds | 18.4151020 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Advanced to five-fold development CV

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_12",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 16,
    "min_child_samples": 76,
    "colsample_bytree": 0.7016450200644813,
    "subsample": 0.960384200459015,
    "subsample_freq": 1,
    "reg_lambda": 0.5703637874410369,
    "reg_alpha": 1.6865703875308493,
    "max_bin": 255,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 19. lgb_tune_13

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7456064 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0015433 |
| Average precision | 0.2317256 |
| Log loss | 0.2496295 |
| Brier score | 0.0684488 |
| Selected epochs/trees | 939.0000000 |
| Recorded call seconds | 16.9548087 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_13",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 13,
    "min_child_samples": 73,
    "colsample_bytree": 0.7191764739632918,
    "subsample": 0.9783878685095276,
    "subsample_freq": 1,
    "reg_lambda": 1.1129906076406433,
    "reg_alpha": 0.3383552094629685,
    "max_bin": 255,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 20. lgb_tune_14

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7454358 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0013727 |
| Average precision | 0.2328327 |
| Log loss | 0.2495147 |
| Brier score | 0.0684133 |
| Selected epochs/trees | 746.0000000 |
| Recorded call seconds | 14.9626129 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_14",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 15,
    "min_child_samples": 61,
    "colsample_bytree": 0.6489502246662009,
    "subsample": 0.9877070624071099,
    "subsample_freq": 1,
    "reg_lambda": 0.2174410134760038,
    "reg_alpha": 1.6993246668017472,
    "max_bin": 255,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 21. lgb_tune_15

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7471511 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0030880 |
| Average precision | 0.2370331 |
| Log loss | 0.2490666 |
| Brier score | 0.0682602 |
| Development CV AUC | 0.7573281 |
| Selected epochs/trees | 844.0000000 |
| Recorded call seconds | 19.1572728 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Retained in the first-pass public-scored ensemble (confirmed public AUC 0.7654)

**Recorded recipe/settings:**

```json
{
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
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 22. lgb_tune_16

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7452127 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0011496 |
| Average precision | 0.2348879 |
| Log loss | 0.2494210 |
| Brier score | 0.0683703 |
| Selected epochs/trees | 544.0000000 |
| Recorded call seconds | 14.0118630 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_16",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 19,
    "min_child_samples": 161,
    "colsample_bytree": 0.6148105309759075,
    "subsample": 0.999529777296887,
    "subsample_freq": 1,
    "reg_lambda": 0.751447868942907,
    "reg_alpha": 5.253642888313459,
    "max_bin": 255,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 23. lgb_tune_17

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7455600 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0014969 |
| Average precision | 0.2361203 |
| Log loss | 0.2494675 |
| Brier score | 0.0683454 |
| Selected epochs/trees | 561.0000000 |
| Recorded call seconds | 20.2769358 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_17",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 32,
    "min_child_samples": 126,
    "colsample_bytree": 0.6887299521210465,
    "subsample": 0.931150306878146,
    "subsample_freq": 1,
    "reg_lambda": 1.2958348142896836,
    "reg_alpha": 1.9062509287974798,
    "max_bin": 255,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 24. lgb_tune_18

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7404705 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0035927 |
| Average precision | 0.2295137 |
| Log loss | 0.2508841 |
| Brier score | 0.0686766 |
| Selected epochs/trees | 373.0000000 |
| Recorded call seconds | 14.7728119 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_18",
  "kind": "lgb",
  "features": "extended",
  "groups": true,
  "params": {
    "num_leaves": 21,
    "min_child_samples": 73,
    "colsample_bytree": 0.6380710940932686,
    "subsample": 0.9932795302337665,
    "subsample_freq": 1,
    "reg_lambda": 7.012900547344847,
    "reg_alpha": 0.8430223434949234,
    "max_bin": 255,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 25. lgb_tune_19

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7433811 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0006820 |
| Average precision | 0.2337387 |
| Log loss | 0.2498536 |
| Brier score | 0.0684164 |
| Selected epochs/trees | 567.0000000 |
| Recorded call seconds | 15.2675328 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_19",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 16,
    "min_child_samples": 87,
    "colsample_bytree": 0.7485195977745238,
    "subsample": 0.8392543286099333,
    "subsample_freq": 1,
    "reg_lambda": 1.4293683811585762,
    "reg_alpha": 8.836681679932243,
    "max_bin": 63,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 26. lgb_tune_20

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7458653 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0018022 |
| Average precision | 0.2331723 |
| Log loss | 0.2495197 |
| Brier score | 0.0684063 |
| Selected epochs/trees | 561.0000000 |
| Recorded call seconds | 18.1308520 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_20",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 25,
    "min_child_samples": 51,
    "colsample_bytree": 0.6966732598524357,
    "subsample": 0.9213050927267354,
    "subsample_freq": 1,
    "reg_lambda": 0.31190183790323456,
    "reg_alpha": 0.1442947960154403,
    "max_bin": 255,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 27. lgb_tune_21

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7459210 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0018579 |
| Average precision | 0.2346500 |
| Log loss | 0.2493688 |
| Brier score | 0.0683529 |
| Selected epochs/trees | 821.0000000 |
| Recorded call seconds | 22.7874389 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_21",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 17,
    "min_child_samples": 92,
    "colsample_bytree": 0.742825268226029,
    "subsample": 0.9793438469230858,
    "subsample_freq": 1,
    "reg_lambda": 7.9483221299740014,
    "reg_alpha": 2.7972741874288203,
    "max_bin": 255,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 28. lgb_tune_22

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7461071 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0020439 |
| Average precision | 0.2340214 |
| Log loss | 0.2494003 |
| Brier score | 0.0683883 |
| Selected epochs/trees | 695.0000000 |
| Recorded call seconds | 20.7644160 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_22",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 21,
    "min_child_samples": 105,
    "colsample_bytree": 0.7485499123045329,
    "subsample": 0.9704195474219368,
    "subsample_freq": 1,
    "reg_lambda": 4.911744732892914,
    "reg_alpha": 2.16467625438755,
    "max_bin": 255,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 29. lgb_tune_23

Type: main screening configuration; status: complete.

**Reason:** Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7433510 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0007122 |
| Average precision | 0.2331564 |
| Log loss | 0.2499476 |
| Brier score | 0.0684496 |
| Selected epochs/trees | 428.0000000 |
| Recorded call seconds | 16.0487497 |

**Outcome / interpretation:** This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_tune_23",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 27,
    "min_child_samples": 123,
    "colsample_bytree": 0.7861038803344867,
    "subsample": 0.992629081235298,
    "subsample_freq": 1,
    "reg_lambda": 7.902003345019391,
    "reg_alpha": 3.88832071957301,
    "max_bin": 63,
    "max_depth": -1
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 30. cat_depth4

Type: main screening configuration; status: complete.

**Reason:** Native categorical learning and a different boosting implementation may outperform the LightGBM family. Compare depths 4–7 and leaf regularization to control capacity.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7489588 |
| Reference AUC, when recorded | 0.7476596 |
| Ledger delta versus its recorded reference | 0.0012992 |
| Average precision | 0.2364049 |
| Log loss | 0.2484197 |
| Brier score | 0.0682004 |
| Development CV AUC | 0.7597278 |
| Selected epochs/trees | 1828.0000000 |
| Recorded call seconds | 163.1956291 |

**Outcome / interpretation:** Depth and regularization were changed jointly, so the depth effect is not perfectly isolated.

**Decision:** Advanced to five-fold development CV

**Recorded recipe/settings:**

```json
{
  "name": "cat_depth4",
  "kind": "cat",
  "features": "engineered",
  "params": {
    "depth": 4,
    "l2_leaf_reg": 5,
    "random_strength": 0.5
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 31. cat_depth5

Type: main screening configuration; status: complete.

**Reason:** Native categorical learning and a different boosting implementation may outperform the LightGBM family. Compare depths 4–7 and leaf regularization to control capacity.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7476596 |
| Reference AUC, when recorded | 0.7476596 |
| Ledger delta versus its recorded reference | 0.0000000 |
| Average precision | 0.2336103 |
| Log loss | 0.2488242 |
| Brier score | 0.0682895 |
| Selected epochs/trees | 1464.0000000 |
| Recorded call seconds | 128.3121839 |

**Outcome / interpretation:** Depth and regularization were changed jointly, so the depth effect is not perfectly isolated.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "cat_depth5",
  "kind": "cat",
  "features": "engineered",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 32. cat_depth6

Type: main screening configuration; status: complete.

**Reason:** Native categorical learning and a different boosting implementation may outperform the LightGBM family. Compare depths 4–7 and leaf regularization to control capacity.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7472115 |
| Reference AUC, when recorded | 0.7476596 |
| Ledger delta versus its recorded reference | -0.0004481 |
| Average precision | 0.2352353 |
| Log loss | 0.2488433 |
| Brier score | 0.0682643 |
| Selected epochs/trees | 1016.0000000 |
| Recorded call seconds | 155.8995688 |

**Outcome / interpretation:** Depth and regularization were changed jointly, so the depth effect is not perfectly isolated.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "cat_depth6",
  "kind": "cat",
  "features": "engineered",
  "params": {
    "depth": 6,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 33. cat_depth7

Type: main screening configuration; status: complete.

**Reason:** Native categorical learning and a different boosting implementation may outperform the LightGBM family. Compare depths 4–7 and leaf regularization to control capacity.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7473374 |
| Reference AUC, when recorded | 0.7476596 |
| Ledger delta versus its recorded reference | -0.0003223 |
| Average precision | 0.2328820 |
| Log loss | 0.2488726 |
| Brier score | 0.0683166 |
| Selected epochs/trees | 932.0000000 |
| Recorded call seconds | 162.3585439 |

**Outcome / interpretation:** Depth and regularization were changed jointly, so the depth effect is not perfectly isolated.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "cat_depth7",
  "kind": "cat",
  "features": "engineered",
  "params": {
    "depth": 7,
    "l2_leaf_reg": 12,
    "random_strength": 0.5
  }
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 34. logistic_0.01

Type: main screening configuration; status: complete.

**Reason:** A regularized linear classifier may generalize well or diversify boosted models.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7329595 |
| Reference AUC, when recorded | 0.7323117 |
| Ledger delta versus its recorded reference | 0.0006478 |
| Average precision | 0.2162716 |
| Log loss | 0.2529808 |
| Brier score | 0.0691446 |

**Outcome / interpretation:** Linear effects may be insufficient for nonlinear score and payment interactions; this is an explanation, not a proven mechanism.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "C": 0.01
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 35. logistic_0.1

Type: main screening configuration; status: complete.

**Reason:** A regularized linear classifier may generalize well or diversify boosted models.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7323117 |
| Reference AUC, when recorded | 0.7323117 |
| Ledger delta versus its recorded reference | 0.0000000 |
| Average precision | 0.2170715 |
| Log loss | 0.2532306 |
| Brier score | 0.0691886 |

**Outcome / interpretation:** Linear effects may be insufficient for nonlinear score and payment interactions; this is an explanation, not a proven mechanism.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "C": 0.1
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 36. logistic_1.0

Type: main screening configuration; status: complete.

**Reason:** A regularized linear classifier may generalize well or diversify boosted models.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7317958 |
| Reference AUC, when recorded | 0.7323117 |
| Ledger delta versus its recorded reference | -0.0005159 |
| Average precision | 0.2163243 |
| Log loss | 0.2534477 |
| Brier score | 0.0692375 |

**Outcome / interpretation:** Linear effects may be insufficient for nonlinear score and payment interactions; this is an explanation, not a proven mechanism.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "C": 1.0
}
```

**Evidence:** [improvements/artifacts/screen_results.json](../improvements/artifacts/screen_results.json)

### 37. hgb_10

Type: main screening configuration; status: complete.

**Reason:** Native-categorical histogram gradient boosting offers a separate implementation and leaf-complexity tradeoff.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7412823 |
| Reference AUC, when recorded | 0.7416091 |
| Ledger delta versus its recorded reference | -0.0003268 |
| Average precision | 0.2265416 |
| Log loss | 0.2507479 |
| Brier score | 0.0686823 |
| Selected epochs/trees | 383.0000000 |
| Recorded call seconds | 10.3100188 |

**Outcome / interpretation:** This family was competitive enough to validate, but did not match CatBoost or tuned LightGBM.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "hgb_10",
  "kind": "hgb",
  "features": "engineered",
  "params": {
    "max_leaf_nodes": 10,
    "min_samples_leaf": 100,
    "l2_regularization": 15.0
  }
}
```

**Evidence:** [improvements/artifacts/supplement_results.json](../improvements/artifacts/supplement_results.json)

### 38. hgb_20

Type: main screening configuration; status: complete.

**Reason:** Native-categorical histogram gradient boosting offers a separate implementation and leaf-complexity tradeoff.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7416091 |
| Reference AUC, when recorded | 0.7416091 |
| Ledger delta versus its recorded reference | 0.0000000 |
| Average precision | 0.2304575 |
| Log loss | 0.2507083 |
| Brier score | 0.0686145 |
| Development CV AUC | 0.7532918 |
| Selected epochs/trees | 422.0000000 |
| Recorded call seconds | 15.5847461 |

**Outcome / interpretation:** This family was competitive enough to validate, but did not match CatBoost or tuned LightGBM.

**Decision:** Advanced to five-fold development CV

**Recorded recipe/settings:**

```json
{
  "name": "hgb_20",
  "kind": "hgb",
  "features": "engineered",
  "params": {
    "max_leaf_nodes": 20,
    "min_samples_leaf": 100,
    "l2_regularization": 15.0
  }
}
```

**Evidence:** [improvements/artifacts/supplement_results.json](../improvements/artifacts/supplement_results.json)

### 39. hgb_31

Type: main screening configuration; status: complete.

**Reason:** Native-categorical histogram gradient boosting offers a separate implementation and leaf-complexity tradeoff.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7413035 |
| Reference AUC, when recorded | 0.7416091 |
| Ledger delta versus its recorded reference | -0.0003056 |
| Average precision | 0.2287025 |
| Log loss | 0.2506191 |
| Brier score | 0.0686172 |
| Selected epochs/trees | 186.0000000 |
| Recorded call seconds | 10.4521248 |

**Outcome / interpretation:** This family was competitive enough to validate, but did not match CatBoost or tuned LightGBM.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "hgb_31",
  "kind": "hgb",
  "features": "engineered",
  "params": {
    "max_leaf_nodes": 31,
    "min_samples_leaf": 100,
    "l2_regularization": 15.0
  }
}
```

**Evidence:** [improvements/artifacts/supplement_results.json](../improvements/artifacts/supplement_results.json)

### 40. spline_0.01

Type: main screening configuration; status: complete.

**Reason:** Quantile transforms and smooth univariate splines may recover nonlinear signal with less tree variance.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7360169 |
| Reference AUC, when recorded | 0.7365373 |
| Ledger delta versus its recorded reference | -0.0005205 |
| Average precision | 0.2203776 |
| Log loss | 0.2519700 |
| Brier score | 0.0689618 |
| Selected epochs/trees | 1.0000000 |
| Recorded call seconds | 11.0069709 |

**Outcome / interpretation:** Smooth additive effects remain weaker than the tree models; cross-feature interactions are one plausible missing component.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "spline_0.01",
  "kind": "spline",
  "features": "engineered",
  "params": {
    "C": 0.01
  }
}
```

**Evidence:** [improvements/artifacts/supplement_results.json](../improvements/artifacts/supplement_results.json)

### 41. spline_0.1

Type: main screening configuration; status: complete.

**Reason:** Quantile transforms and smooth univariate splines may recover nonlinear signal with less tree variance.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7365373 |
| Reference AUC, when recorded | 0.7365373 |
| Ledger delta versus its recorded reference | 0.0000000 |
| Average precision | 0.2237328 |
| Log loss | 0.2518486 |
| Brier score | 0.0688768 |
| Development CV AUC | 0.7483044 |
| Selected epochs/trees | 1.0000000 |
| Recorded call seconds | 12.7584238 |

**Outcome / interpretation:** Smooth additive effects remain weaker than the tree models; cross-feature interactions are one plausible missing component.

**Decision:** Advanced to five-fold development CV

**Recorded recipe/settings:**

```json
{
  "name": "spline_0.1",
  "kind": "spline",
  "features": "engineered",
  "params": {
    "C": 0.1
  }
}
```

**Evidence:** [improvements/artifacts/supplement_results.json](../improvements/artifacts/supplement_results.json)

### 42. spline_1.0

Type: main screening configuration; status: complete.

**Reason:** Quantile transforms and smooth univariate splines may recover nonlinear signal with less tree variance.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7359303 |
| Reference AUC, when recorded | 0.7365373 |
| Ledger delta versus its recorded reference | -0.0006070 |
| Average precision | 0.2241576 |
| Log loss | 0.2520676 |
| Brier score | 0.0689016 |
| Selected epochs/trees | 1.0000000 |
| Recorded call seconds | 16.5795579 |

**Outcome / interpretation:** Smooth additive effects remain weaker than the tree models; cross-feature interactions are one plausible missing component.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "spline_1.0",
  "kind": "spline",
  "features": "engineered",
  "params": {
    "C": 1.0
  }
}
```

**Evidence:** [improvements/artifacts/supplement_results.json](../improvements/artifacts/supplement_results.json)

### 43. lgb_engineered_groups

Type: main screening configuration; status: complete.

**Reason:** Fold-fitted category frequencies and group-relative financial/score values may normalize peer groups.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7450358 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0009726 |
| Average precision | 0.2335948 |
| Log loss | 0.2496147 |
| Brier score | 0.0684041 |
| Selected epochs/trees | 681.0000000 |
| Recorded call seconds | 20.7150569 |

**Outcome / interpretation:** Several settings change together; the result does not isolate a single causal mechanism.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_engineered_groups",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 16,
    "max_depth": -1,
    "min_child_samples": 200,
    "colsample_bytree": 1.0,
    "subsample": 0.9,
    "subsample_freq": 1,
    "reg_lambda": 20,
    "reg_alpha": 1.0,
    "max_bin": 127
  }
}
```

**Evidence:** [improvements/artifacts/supplement_results.json](../improvements/artifacts/supplement_results.json)

### 44. lgb_lean

Type: main screening configuration; status: complete.

**Reason:** A compact feature subset may remove redundant interactions and reduce variance.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7432963 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0007668 |
| Average precision | 0.2312502 |
| Log loss | 0.2500847 |
| Brier score | 0.0685231 |
| Selected epochs/trees | 560.0000000 |
| Recorded call seconds | 13.2106652 |

**Outcome / interpretation:** These LightGBM variants did not beat its engineered feature set; feature selection is model dependent.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_lean",
  "kind": "lgb",
  "features": "lean",
  "params": {
    "num_leaves": 16,
    "max_depth": -1,
    "min_child_samples": 200,
    "colsample_bytree": 1.0,
    "subsample": 0.9,
    "subsample_freq": 1,
    "reg_lambda": 20.0,
    "reg_alpha": 1.0,
    "max_bin": 127
  }
}
```

**Evidence:** [improvements/artifacts/refine_results.json](../improvements/artifacts/refine_results.json)

### 45. lgb_scores

Type: main screening configuration; status: complete.

**Reason:** A compact feature subset may remove redundant interactions and reduce variance.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7389122 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | -0.0051510 |
| Average precision | 0.2255917 |
| Log loss | 0.2514263 |
| Brier score | 0.0688014 |
| Selected epochs/trees | 670.0000000 |
| Recorded call seconds | 11.9284060 |

**Outcome / interpretation:** These LightGBM variants did not beat its engineered feature set; feature selection is model dependent.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_scores",
  "kind": "lgb",
  "features": "scores",
  "params": {
    "num_leaves": 16,
    "max_depth": -1,
    "min_child_samples": 200,
    "colsample_bytree": 1.0,
    "subsample": 0.9,
    "subsample_freq": 1,
    "reg_lambda": 20.0,
    "reg_alpha": 1.0,
    "max_bin": 127
  }
}
```

**Evidence:** [improvements/artifacts/refine_results.json](../improvements/artifacts/refine_results.json)

### 46. lgb_small_8

Type: main screening configuration; status: complete.

**Reason:** Shallower trees with strong regularization may improve generalization.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7451259 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0010628 |
| Average precision | 0.2316587 |
| Log loss | 0.2498275 |
| Brier score | 0.0684867 |
| Selected epochs/trees | 1371.0000000 |
| Recorded call seconds | 18.9370067 |

**Outcome / interpretation:** Several settings change together; the result does not isolate a single causal mechanism.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_small_8",
  "kind": "lgb",
  "features": "engineered",
  "params": {
    "num_leaves": 8,
    "max_depth": -1,
    "min_child_samples": 200,
    "colsample_bytree": 1.0,
    "subsample": 0.9,
    "subsample_freq": 1,
    "reg_lambda": 20.0,
    "reg_alpha": 1.0,
    "max_bin": 255
  }
}
```

**Evidence:** [improvements/artifacts/refine_results.json](../improvements/artifacts/refine_results.json)

### 47. lgb_small_12

Type: main screening configuration; status: complete.

**Reason:** Shallower trees with strong regularization may improve generalization.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7454156 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0013524 |
| Average precision | 0.2334102 |
| Log loss | 0.2495918 |
| Brier score | 0.0684099 |
| Selected epochs/trees | 839.0000000 |
| Recorded call seconds | 14.9284260 |

**Outcome / interpretation:** Several settings change together; the result does not isolate a single causal mechanism.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_small_12",
  "kind": "lgb",
  "features": "engineered",
  "params": {
    "num_leaves": 12,
    "max_depth": -1,
    "min_child_samples": 200,
    "colsample_bytree": 1.0,
    "subsample": 0.9,
    "subsample_freq": 1,
    "reg_lambda": 20.0,
    "reg_alpha": 1.0,
    "max_bin": 255
  }
}
```

**Evidence:** [improvements/artifacts/refine_results.json](../improvements/artifacts/refine_results.json)

### 48. lgb_weight_2.0

Type: main screening configuration; status: complete.

**Reason:** Increasing positive-class weight may prioritize minority-class ranking.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7441755 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0001124 |
| Average precision | 0.2308080 |
| Log loss | 0.2670192 |
| Brier score | 0.0738256 |
| Selected epochs/trees | 672.0000000 |
| Recorded call seconds | 13.3171630 |

**Outcome / interpretation:** Class weighting did not beat the best unweighted candidates; it can also shift probability calibration. Imbalance alone is not evidence weighting will help AUC.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_weight_2.0",
  "kind": "lgb",
  "features": "engineered",
  "params": {
    "num_leaves": 16,
    "max_depth": -1,
    "min_child_samples": 200,
    "colsample_bytree": 1.0,
    "subsample": 0.9,
    "subsample_freq": 1,
    "reg_lambda": 20.0,
    "reg_alpha": 1.0,
    "max_bin": 127,
    "scale_pos_weight": 2.0
  }
}
```

**Evidence:** [improvements/artifacts/refine_results.json](../improvements/artifacts/refine_results.json)

### 49. lgb_weight_5.0

Type: main screening configuration; status: complete.

**Reason:** Increasing positive-class weight may prioritize minority-class ranking.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7449651 |
| Reference AUC, when recorded | 0.7440631 |
| Ledger delta versus its recorded reference | 0.0009020 |
| Average precision | 0.2285107 |
| Log loss | 0.3590243 |
| Brier score | 0.1077476 |
| Selected epochs/trees | 673.0000000 |
| Recorded call seconds | 13.2733481 |

**Outcome / interpretation:** Class weighting did not beat the best unweighted candidates; it can also shift probability calibration. Imbalance alone is not evidence weighting will help AUC.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_weight_5.0",
  "kind": "lgb",
  "features": "engineered",
  "params": {
    "num_leaves": 16,
    "max_depth": -1,
    "min_child_samples": 200,
    "colsample_bytree": 1.0,
    "subsample": 0.9,
    "subsample_freq": 1,
    "reg_lambda": 20.0,
    "reg_alpha": 1.0,
    "max_bin": 127,
    "scale_pos_weight": 5.0
  }
}
```

**Evidence:** [improvements/artifacts/refine_results.json](../improvements/artifacts/refine_results.json)

### 50. cat_raw

Type: main screening configuration; status: complete.

**Reason:** Test whether CatBoost can learn sufficient relationships from the original columns without derived ratios.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7416556 |
| Reference AUC, when recorded | 0.7476596 |
| Ledger delta versus its recorded reference | -0.0060041 |
| Average precision | 0.2267268 |
| Log loss | 0.2504222 |
| Brier score | 0.0686612 |
| Selected epochs/trees | 1285.0000000 |
| Recorded call seconds | 96.9629140 |

**Outcome / interpretation:** Lower AUC supports retaining derived financial and score features for this model.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "cat_raw",
  "kind": "cat",
  "features": "raw",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  }
}
```

**Evidence:** [improvements/artifacts/refine_results.json](../improvements/artifacts/refine_results.json)

### 51. cat_lean

Type: main screening configuration; status: complete.

**Reason:** A compact set of strong financial/score features may reduce distracting split opportunities.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7484926 |
| Reference AUC, when recorded | 0.7476596 |
| Ledger delta versus its recorded reference | 0.0008330 |
| Average precision | 0.2339938 |
| Log loss | 0.2487278 |
| Brier score | 0.0683022 |
| Development CV AUC | 0.7607901 |
| Selected epochs/trees | 1670.0000000 |
| Recorded call seconds | 170.8672302 |

**Outcome / interpretation:** The compact depth-5 representation won development CV; deeper trees did not help overall. The feature explanation is plausible, not causal proof.

**Decision:** Retained in the first-pass public-scored ensemble (confirmed public AUC 0.7654)

**Recorded recipe/settings:**

```json
{
  "name": "cat_lean",
  "kind": "cat",
  "features": "lean",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  }
}
```

**Evidence:** [improvements/artifacts/refine_results.json](../improvements/artifacts/refine_results.json)

### 52. lgb_top_25

Type: main screening configuration; status: complete.

**Reason:** Remove weaker original/derived columns using development-only gain rankings.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7381651 |
| Reference AUC, when recorded | 0.7471511 |
| Ledger delta versus its recorded reference | -0.0089860 |
| Average precision | 0.2314082 |
| Log loss | 0.2510906 |
| Brier score | 0.0685992 |
| Selected epochs/trees | 430.0000000 |
| Recorded call seconds | 13.5240772 |

**Outcome / interpretation:** Pruning failed to improve the tuned reference; correlated weak features can still help an ensemble of trees.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_top_25",
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
  },
  "columns": [
    "EXT_MEAN",
    "ORGANIZATION_TYPE",
    "AMT_CREDIT_OVER_AMT_ANNUITY",
    "OCCUPATION_TYPE",
    "EXT_SUM",
    "EXT_MIN",
    "EXT_SOURCE_3",
    "AMT_CREDIT_OVER_AMT_GOODS_PRICE",
    "EXT_2_3_PRODUCT",
    "DAYS_EMPLOYED",
    "AMT_ANNUITY_OVER_AMT_GOODS_PRICE",
    "DAYS_ID_PUBLISH",
    "AGE_AT_EMPLOYMENT",
    "CAR_OVER_AGE",
    "CREDIT_TERM",
    "EXT_STD",
    "CREDIT_GOODS_DIFF",
    "EMPLOYED_YEARS",
    "DAYS_LAST_PHONE_CHANGE",
    "EXT_MEAN_TIMES_TERM",
    "DAYS_EMPLOYED_OVER_BIRTH",
    "EXT_MAX",
    "DAYS_REGISTRATION",
    "DAYS_REGISTRATION_OVER_BIRTH",
    "REGION_POPULATION_RELATIVE"
  ]
}
```

**Evidence:** [improvements/artifacts/feature_selection_results.json](../improvements/artifacts/feature_selection_results.json)

### 53. lgb_top_40

Type: main screening configuration; status: complete.

**Reason:** Remove weaker original/derived columns using development-only gain rankings.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7428896 |
| Reference AUC, when recorded | 0.7471511 |
| Ledger delta versus its recorded reference | -0.0042615 |
| Average precision | 0.2324984 |
| Log loss | 0.2500459 |
| Brier score | 0.0684704 |
| Selected epochs/trees | 470.0000000 |
| Recorded call seconds | 18.0606642 |

**Outcome / interpretation:** Pruning failed to improve the tuned reference; correlated weak features can still help an ensemble of trees.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_top_40",
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
  },
  "columns": [
    "EXT_MEAN",
    "ORGANIZATION_TYPE",
    "AMT_CREDIT_OVER_AMT_ANNUITY",
    "OCCUPATION_TYPE",
    "EXT_SUM",
    "EXT_MIN",
    "EXT_SOURCE_3",
    "AMT_CREDIT_OVER_AMT_GOODS_PRICE",
    "EXT_2_3_PRODUCT",
    "DAYS_EMPLOYED",
    "AMT_ANNUITY_OVER_AMT_GOODS_PRICE",
    "DAYS_ID_PUBLISH",
    "AGE_AT_EMPLOYMENT",
    "CAR_OVER_AGE",
    "CREDIT_TERM",
    "EXT_STD",
    "CREDIT_GOODS_DIFF",
    "EMPLOYED_YEARS",
    "DAYS_LAST_PHONE_CHANGE",
    "EXT_MEAN_TIMES_TERM",
    "DAYS_EMPLOYED_OVER_BIRTH",
    "EXT_MAX",
    "DAYS_REGISTRATION",
    "DAYS_REGISTRATION_OVER_BIRTH",
    "REGION_POPULATION_RELATIVE",
    "DAYS_BIRTH",
    "CREDIT_GOODS_DIFF_RATIO",
    "EXT_2_3_DIFF",
    "AGE_YEARS",
    "EXT_SOURCE_2",
    "EXT_MEAN_OVER_AGE",
    "PHONE_OVER_EMPLOYED",
    "CODE_GENDER",
    "DAYS_ID_PUBLISH_OVER_BIRTH",
    "ANNUITY_PER_PERSON",
    "DAYS_LAST_PHONE_CHANGE_OVER_BIRTH",
    "AMT_GOODS_PRICE",
    "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY",
    "EDUCATION_RANK",
    "CREDIT_PER_PERSON"
  ]
}
```

**Evidence:** [improvements/artifacts/feature_selection_results.json](../improvements/artifacts/feature_selection_results.json)

### 54. lgb_top_55

Type: main screening configuration; status: complete.

**Reason:** Remove weaker original/derived columns using development-only gain rankings.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7459224 |
| Reference AUC, when recorded | 0.7471511 |
| Ledger delta versus its recorded reference | -0.0012287 |
| Average precision | 0.2358318 |
| Log loss | 0.2493976 |
| Brier score | 0.0683450 |
| Selected epochs/trees | 727.0000000 |
| Recorded call seconds | 29.1296620 |

**Outcome / interpretation:** Pruning failed to improve the tuned reference; correlated weak features can still help an ensemble of trees.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "lgb_top_55",
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
  },
  "columns": [
    "EXT_MEAN",
    "ORGANIZATION_TYPE",
    "AMT_CREDIT_OVER_AMT_ANNUITY",
    "OCCUPATION_TYPE",
    "EXT_SUM",
    "EXT_MIN",
    "EXT_SOURCE_3",
    "AMT_CREDIT_OVER_AMT_GOODS_PRICE",
    "EXT_2_3_PRODUCT",
    "DAYS_EMPLOYED",
    "AMT_ANNUITY_OVER_AMT_GOODS_PRICE",
    "DAYS_ID_PUBLISH",
    "AGE_AT_EMPLOYMENT",
    "CAR_OVER_AGE",
    "CREDIT_TERM",
    "EXT_STD",
    "CREDIT_GOODS_DIFF",
    "EMPLOYED_YEARS",
    "DAYS_LAST_PHONE_CHANGE",
    "EXT_MEAN_TIMES_TERM",
    "DAYS_EMPLOYED_OVER_BIRTH",
    "EXT_MAX",
    "DAYS_REGISTRATION",
    "DAYS_REGISTRATION_OVER_BIRTH",
    "REGION_POPULATION_RELATIVE",
    "DAYS_BIRTH",
    "CREDIT_GOODS_DIFF_RATIO",
    "EXT_2_3_DIFF",
    "AGE_YEARS",
    "EXT_SOURCE_2",
    "EXT_MEAN_OVER_AGE",
    "PHONE_OVER_EMPLOYED",
    "CODE_GENDER",
    "DAYS_ID_PUBLISH_OVER_BIRTH",
    "ANNUITY_PER_PERSON",
    "DAYS_LAST_PHONE_CHANGE_OVER_BIRTH",
    "AMT_GOODS_PRICE",
    "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY",
    "EDUCATION_RANK",
    "CREDIT_PER_PERSON",
    "OWN_CAR_AGE",
    "EXT_SOURCE_1",
    "INCOME_AFTER_ANNUITY",
    "INCOME_PER_PERSON",
    "EXT_1_2_PRODUCT",
    "AMT_ANNUITY",
    "AMT_INCOME_TOTAL_OVER_AMT_GOODS_PRICE",
    "AMT_INCOME_TOTAL_OVER_AMT_CREDIT",
    "EXT_1_2_DIFF",
    "AMT_REQ_CREDIT_BUREAU_YEAR",
    "BUREAU_SUM",
    "NAME_FAMILY_STATUS",
    "NAME_EDUCATION_TYPE",
    "REGION_RATING_CLIENT",
    "AMT_CREDIT"
  ]
}
```

**Evidence:** [improvements/artifacts/feature_selection_results.json](../improvements/artifacts/feature_selection_results.json)

### 55. lgb_top_70

Type: main screening configuration; status: complete.

**Reason:** Remove weaker original/derived columns using development-only gain rankings.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7463364 |
| Reference AUC, when recorded | 0.7471511 |
| Ledger delta versus its recorded reference | -0.0008147 |
| Average precision | 0.2353816 |
| Log loss | 0.2492955 |
| Brier score | 0.0683335 |
| Development CV AUC | 0.7569596 |
| Selected epochs/trees | 709.0000000 |
| Recorded call seconds | 31.6503191 |

**Outcome / interpretation:** Pruning failed to improve the tuned reference; correlated weak features can still help an ensemble of trees.

**Decision:** Advanced to five-fold development CV

**Recorded recipe/settings:**

```json
{
  "name": "lgb_top_70",
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
  },
  "columns": [
    "EXT_MEAN",
    "ORGANIZATION_TYPE",
    "AMT_CREDIT_OVER_AMT_ANNUITY",
    "OCCUPATION_TYPE",
    "EXT_SUM",
    "EXT_MIN",
    "EXT_SOURCE_3",
    "AMT_CREDIT_OVER_AMT_GOODS_PRICE",
    "EXT_2_3_PRODUCT",
    "DAYS_EMPLOYED",
    "AMT_ANNUITY_OVER_AMT_GOODS_PRICE",
    "DAYS_ID_PUBLISH",
    "AGE_AT_EMPLOYMENT",
    "CAR_OVER_AGE",
    "CREDIT_TERM",
    "EXT_STD",
    "CREDIT_GOODS_DIFF",
    "EMPLOYED_YEARS",
    "DAYS_LAST_PHONE_CHANGE",
    "EXT_MEAN_TIMES_TERM",
    "DAYS_EMPLOYED_OVER_BIRTH",
    "EXT_MAX",
    "DAYS_REGISTRATION",
    "DAYS_REGISTRATION_OVER_BIRTH",
    "REGION_POPULATION_RELATIVE",
    "DAYS_BIRTH",
    "CREDIT_GOODS_DIFF_RATIO",
    "EXT_2_3_DIFF",
    "AGE_YEARS",
    "EXT_SOURCE_2",
    "EXT_MEAN_OVER_AGE",
    "PHONE_OVER_EMPLOYED",
    "CODE_GENDER",
    "DAYS_ID_PUBLISH_OVER_BIRTH",
    "ANNUITY_PER_PERSON",
    "DAYS_LAST_PHONE_CHANGE_OVER_BIRTH",
    "AMT_GOODS_PRICE",
    "AMT_INCOME_TOTAL_OVER_AMT_ANNUITY",
    "EDUCATION_RANK",
    "CREDIT_PER_PERSON",
    "OWN_CAR_AGE",
    "EXT_SOURCE_1",
    "INCOME_AFTER_ANNUITY",
    "INCOME_PER_PERSON",
    "EXT_1_2_PRODUCT",
    "AMT_ANNUITY",
    "AMT_INCOME_TOTAL_OVER_AMT_GOODS_PRICE",
    "AMT_INCOME_TOTAL_OVER_AMT_CREDIT",
    "EXT_1_2_DIFF",
    "AMT_REQ_CREDIT_BUREAU_YEAR",
    "BUREAU_SUM",
    "NAME_FAMILY_STATUS",
    "NAME_EDUCATION_TYPE",
    "REGION_RATING_CLIENT",
    "AMT_CREDIT",
    "EXT_1_3_DIFF",
    "AMT_REQ_CREDIT_BUREAU_QRT",
    "EXT_PRODUCT",
    "NAME_CONTRACT_TYPE",
    "CONTACT_FLAGS_SUM",
    "EXT_1_3_PRODUCT",
    "AMT_INCOME_TOTAL",
    "FLAG_WORK_PHONE",
    "MISSING_COUNT",
    "AMT_REQ_CREDIT_BUREAU_MON",
    "NAME_HOUSING_TYPE",
    "NAME_INCOME_TYPE",
    "CNT_FAM_MEMBERS",
    "CHILDREN_FRACTION",
    "CNT_CHILDREN"
  ]
}
```

**Evidence:** [improvements/artifacts/feature_selection_results.json](../improvements/artifacts/feature_selection_results.json)

### 56. cat_lean_depth4

Type: main screening configuration; status: complete.

**Reason:** A compact set of strong financial/score features may reduce distracting split opportunities.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7476149 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0008777 |
| Average precision | 0.2348429 |
| Log loss | 0.2487328 |
| Brier score | 0.0682469 |
| Selected epochs/trees | 1494.0000000 |
| Recorded call seconds | 158.9942291 |

**Outcome / interpretation:** The compact depth-5 representation won development CV; deeper trees did not help overall. The feature explanation is plausible, not causal proof.

**Decision:** Not advanced individually; retained as a screening/ablation result

**Recorded recipe/settings:**

```json
{
  "name": "cat_lean_depth4",
  "kind": "cat",
  "features": "lean",
  "params": {
    "depth": 4,
    "l2_leaf_reg": 5,
    "random_strength": 0.5
  }
}
```

**Evidence:** [improvements/artifacts/cat_refine_results.json](../improvements/artifacts/cat_refine_results.json)

### 57. cat_lean_depth6

Type: main screening configuration; status: complete.

**Reason:** A compact set of strong financial/score features may reduce distracting split opportunities.

**Rationale provenance:** Retrospective reconstruction from retained source, not a contemporaneous preregistration

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7480283 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0004643 |
| Average precision | 0.2342447 |
| Log loss | 0.2488274 |
| Brier score | 0.0683188 |
| Development CV AUC | 0.7601480 |
| Selected epochs/trees | 1395.0000000 |
| Recorded call seconds | 188.1582520 |

**Outcome / interpretation:** The compact depth-5 representation won development CV; deeper trees did not help overall. The feature explanation is plausible, not causal proof.

**Decision:** Advanced to five-fold development CV

**Recorded recipe/settings:**

```json
{
  "name": "cat_lean_depth6",
  "kind": "cat",
  "features": "lean",
  "params": {
    "depth": 6,
    "l2_leaf_reg": 12,
    "random_strength": 0.5
  }
}
```

**Evidence:** [improvements/artifacts/cat_refine_results.json](../improvements/artifacts/cat_refine_results.json)

### 58. r2_cat_baseline

Type: main screening configuration; status: complete.

**Reason:** Reproduce the first-pass compact CatBoost to verify implementation equivalence.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7484926 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | 0.0000000 |
| Average precision | 0.2339938 |
| Log loss | 0.2487278 |
| Brier score | 0.0683022 |
| Selected epochs/trees | 1670.0000000 |
| Recorded call seconds | 85.4579759 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Decision:** Implementation/stopping-budget control; used to interpret other trials, not claimed as a new recipe

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_baseline",
  "kind": "cat",
  "features": "lean",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "Reproduce the first-pass compact CatBoost to verify implementation equivalence.",
  "max_iterations": 3000,
  "patience": 150
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_baseline.json](../improvements/round2/artifacts/screen/r2_cat_baseline.json)

### 59. r2_cat_risk

Type: main screening configuration; status: complete.

**Reason:** Smooth score summaries and score/age/term interactions may help shallow trees model risk.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7468125 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0016800 |
| Average precision | 0.2320274 |
| Log loss | 0.2491946 |
| Brier score | 0.0684096 |
| Selected epochs/trees | 1493.0000000 |
| Recorded call seconds | 146.7034059 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_risk",
  "kind": "cat",
  "features": "risk",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "Smooth score summaries and score/age/term interactions may help shallow trees model risk."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_risk.json](../improvements/round2/artifacts/screen/r2_cat_risk.json)

### 60. r2_cat_finance

Type: main screening configuration; status: complete.

**Reason:** Payment burden, per-adult amounts and hypothetical payment-period rates may expose financial structure.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7490824 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | 0.0005898 |
| Average precision | 0.2369513 |
| Log loss | 0.2484910 |
| Brier score | 0.0682272 |
| Selected epochs/trees | 1841.0000000 |
| Recorded call seconds | 177.3465118 |

**Outcome / interpretation:** Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_finance",
  "kind": "cat",
  "features": "finance",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "Payment burden, per-adult amounts and hypothetical payment-period rates may expose financial structure."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_finance.json](../improvements/round2/artifacts/screen/r2_cat_finance.json)

### 61. r2_cat_missing

Type: main screening configuration; status: complete.

**Reason:** Joint missing-score patterns and coarse organization groups may expose data-collection segments.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7475893 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0009033 |
| Average precision | 0.2333701 |
| Log loss | 0.2489450 |
| Brier score | 0.0683471 |
| Selected epochs/trees | 1541.0000000 |
| Recorded call seconds | 185.9676971 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_missing",
  "kind": "cat",
  "features": "missing",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "Joint missing-score patterns and coarse organization groups may expose data-collection segments."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_missing.json](../improvements/round2/artifacts/screen/r2_cat_missing.json)

### 62. r2_cat_combined

Type: main screening configuration; status: complete.

**Reason:** The three targeted feature families may be complementary; their combination may also add noise.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7486700 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | 0.0001774 |
| Average precision | 0.2325287 |
| Log loss | 0.2488617 |
| Brier score | 0.0683930 |
| Selected epochs/trees | 1576.0000000 |
| Recorded call seconds | 196.5467632 |

**Outcome / interpretation:** Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_combined",
  "kind": "cat",
  "features": "combined",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "The three targeted feature families may be complementary; their combination may also add noise."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_combined.json](../improvements/round2/artifacts/screen/r2_cat_combined.json)

### 63. r2_cat_slow

Type: main screening configuration; status: complete.

**Reason:** Smaller boosting steps may improve the bias/variance tradeoff.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7485719 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | 0.0000793 |
| Average precision | 0.2343099 |
| Log loss | 0.2486057 |
| Brier score | 0.0682697 |
| Selected epochs/trees | 2392.0000000 |
| Recorded call seconds | 232.2389350 |

**Outcome / interpretation:** Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_slow",
  "kind": "cat",
  "features": "lean",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "learning_rate": 0.025
  },
  "hypothesis": "Smaller boosting steps may improve the bias/variance tradeoff.",
  "max_iterations": 5000
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_slow.json](../improvements/round2/artifacts/screen/r2_cat_slow.json)

### 64. r2_cat_strong_l2

Type: main screening configuration; status: complete.

**Reason:** Stronger leaf shrinkage may reduce overfitting in sparse categorical groups.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7476634 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0008291 |
| Average precision | 0.2328982 |
| Log loss | 0.2489499 |
| Brier score | 0.0683545 |
| Selected epochs/trees | 1829.0000000 |
| Recorded call seconds | 179.2984903 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_strong_l2",
  "kind": "cat",
  "features": "lean",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 30,
    "random_strength": 1.0
  },
  "hypothesis": "Stronger leaf shrinkage may reduce overfitting in sparse categorical groups.",
  "max_iterations": 5000
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_strong_l2.json](../improvements/round2/artifacts/screen/r2_cat_strong_l2.json)

### 65. r2_cat_weak_l2

Type: main screening configuration; status: complete.

**Reason:** Less shrinkage may recover useful signal suppressed by the first-pass settings.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7475690 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0009236 |
| Average precision | 0.2339434 |
| Log loss | 0.2489220 |
| Brier score | 0.0683197 |
| Selected epochs/trees | 1276.0000000 |
| Recorded call seconds | 150.5965619 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_weak_l2",
  "kind": "cat",
  "features": "lean",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 2,
    "random_strength": 0.1
  },
  "hypothesis": "Less shrinkage may recover useful signal suppressed by the first-pass settings.",
  "max_iterations": 5000
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_weak_l2.json](../improvements/round2/artifacts/screen/r2_cat_weak_l2.json)

### 66. r2_cat_onehot10

Type: main screening configuration; status: complete.

**Reason:** One-hot splits for low-cardinality categories may outperform ordered target statistics.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7480037 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0004889 |
| Average precision | 0.2340427 |
| Log loss | 0.2487984 |
| Brier score | 0.0683046 |
| Selected epochs/trees | 1299.0000000 |
| Recorded call seconds | 96.0454049 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_onehot10",
  "kind": "cat",
  "features": "lean",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "one_hot_max_size": 10
  },
  "hypothesis": "One-hot splits for low-cardinality categories may outperform ordered target statistics.",
  "max_iterations": 5000
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_onehot10.json](../improvements/round2/artifacts/screen/r2_cat_onehot10.json)

### 67. r2_cat_onehot64

Type: main screening configuration; status: complete.

**Reason:** One-hot splits for every raw category may avoid noisy target statistics, at the cost of expressiveness.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7481928 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0002998 |
| Average precision | 0.2342184 |
| Log loss | 0.2488290 |
| Brier score | 0.0683141 |
| Selected epochs/trees | 1783.0000000 |
| Recorded call seconds | 49.4620221 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_onehot64",
  "kind": "cat",
  "features": "lean",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "one_hot_max_size": 64
  },
  "hypothesis": "One-hot splits for every raw category may avoid noisy target statistics, at the cost of expressiveness.",
  "max_iterations": 5000
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_onehot64.json](../improvements/round2/artifacts/screen/r2_cat_onehot64.json)

### 68. r2_cat_borders512

Type: main screening configuration; status: complete.

**Reason:** Finer numeric quantization may preserve useful external-score and loan-term thresholds.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7477310 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0007616 |
| Average precision | 0.2329339 |
| Log loss | 0.2489782 |
| Brier score | 0.0683663 |
| Selected epochs/trees | 1350.0000000 |
| Recorded call seconds | 166.8634601 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_borders512",
  "kind": "cat",
  "features": "lean",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "border_count": 512
  },
  "hypothesis": "Finer numeric quantization may preserve useful external-score and loan-term thresholds.",
  "max_iterations": 5000
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_borders512.json](../improvements/round2/artifacts/screen/r2_cat_borders512.json)

### 69. r2_cat_rsm075

Type: main screening configuration; status: complete.

**Reason:** Column sampling and Bayesian bootstrap may diversify trees and improve generalization.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7486073 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | 0.0001147 |
| Average precision | 0.2356402 |
| Log loss | 0.2485663 |
| Brier score | 0.0682389 |
| Selected epochs/trees | 1540.0000000 |
| Recorded call seconds | 168.2867780 |

**Outcome / interpretation:** Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation. A parameter preflight resolved bootstrap_type=MVS despite bagging_temperature=1; this is not evidence for a Bayesian-bootstrap effect. The explicit Bayesian follow-up tests that separately.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_rsm075",
  "kind": "cat",
  "features": "lean",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "rsm": 0.75,
    "bagging_temperature": 1.0
  },
  "hypothesis": "Column sampling and Bayesian bootstrap may diversify trees and improve generalization.",
  "max_iterations": 5000
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_rsm075.json](../improvements/round2/artifacts/screen/r2_cat_rsm075.json)

### 70. r2_cat_ordered

Type: main screening configuration; status: complete.

**Reason:** Ordered boosting may reduce prediction shift from fitting residuals on the training rows.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7477317 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0007609 |
| Average precision | 0.2372321 |
| Log loss | 0.2484658 |
| Brier score | 0.0681420 |
| Selected epochs/trees | 840.0000000 |
| Recorded call seconds | 244.1815760 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_ordered",
  "kind": "cat",
  "features": "lean",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "boosting_type": "Ordered",
    "learning_rate": 0.06
  },
  "hypothesis": "Ordered boosting may reduce prediction shift from fitting residuals on the training rows.",
  "max_iterations": 3500
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_ordered.json](../improvements/round2/artifacts/screen/r2_cat_ordered.json)

### 71. r2_cat_native_missing

Type: main screening configuration; status: complete.

**Reason:** Native numeric missing bins may handle absence differently from the -999 sentinel.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7489813 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | 0.0004887 |
| Average precision | 0.2351966 |
| Log loss | 0.2485515 |
| Brier score | 0.0682611 |
| Development CV AUC | 0.7605613 |
| Selected epochs/trees | 1660.0000000 |
| Recorded call seconds | 225.4343071 |

**Outcome / interpretation:** Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Decision:** Validated on common folds; not retained in the current blend

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_native_missing",
  "kind": "cat",
  "features": "lean",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "Native numeric missing bins may handle absence differently from the -999 sentinel.",
  "missing": "native"
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_native_missing.json](../improvements/round2/artifacts/screen/r2_cat_native_missing.json)

### 72. r2_xgb_d3

Type: main screening configuration; status: complete.

**Reason:** A separate histogram-boosting implementation may improve individual AUC or add complementary ensemble errors.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7455421 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0029505 |
| Average precision | 0.2315639 |
| Log loss | 0.2495598 |
| Brier score | 0.0684166 |
| Selected epochs/trees | 1117.0000000 |
| Recorded call seconds | 46.8974671 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_xgb_d3",
  "kind": "xgb",
  "features": "engineered",
  "params": {
    "max_depth": 3,
    "min_child_weight": 30,
    "reg_lambda": 20.0,
    "reg_alpha": 1.0,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "max_bin": 256
  },
  "hypothesis": "A separate histogram-boosting implementation may improve individual AUC or add complementary ensemble errors."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_xgb_d3.json](../improvements/round2/artifacts/screen/r2_xgb_d3.json)

### 73. r2_xgb_d4

Type: main screening configuration; status: complete.

**Reason:** A separate histogram-boosting implementation may improve individual AUC or add complementary ensemble errors.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7451604 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0033322 |
| Average precision | 0.2329235 |
| Log loss | 0.2495763 |
| Brier score | 0.0683810 |
| Selected epochs/trees | 707.0000000 |
| Recorded call seconds | 34.6917231 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_xgb_d4",
  "kind": "xgb",
  "features": "engineered",
  "params": {
    "max_depth": 4,
    "min_child_weight": 30,
    "reg_lambda": 20.0,
    "reg_alpha": 1.0,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "max_bin": 256
  },
  "hypothesis": "A separate histogram-boosting implementation may improve individual AUC or add complementary ensemble errors."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_xgb_d4.json](../improvements/round2/artifacts/screen/r2_xgb_d4.json)

### 74. r2_xgb_d5

Type: main screening configuration; status: complete.

**Reason:** A separate histogram-boosting implementation may improve individual AUC or add complementary ensemble errors.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7445444 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0039482 |
| Average precision | 0.2325073 |
| Log loss | 0.2497924 |
| Brier score | 0.0684309 |
| Selected epochs/trees | 599.0000000 |
| Recorded call seconds | 32.9529860 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_xgb_d5",
  "kind": "xgb",
  "features": "engineered",
  "params": {
    "max_depth": 5,
    "min_child_weight": 30,
    "reg_lambda": 20.0,
    "reg_alpha": 1.0,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "max_bin": 256
  },
  "hypothesis": "A separate histogram-boosting implementation may improve individual AUC or add complementary ensemble errors."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_xgb_d5.json](../improvements/round2/artifacts/screen/r2_xgb_d5.json)

### 75. r2_xgb_lean

Type: main screening configuration; status: complete.

**Reason:** The compact representation may also reduce noise for XGBoost.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7452149 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0032776 |
| Average precision | 0.2331871 |
| Log loss | 0.2496316 |
| Brier score | 0.0684202 |
| Selected epochs/trees | 888.0000000 |
| Recorded call seconds | 27.4315708 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_xgb_lean",
  "kind": "xgb",
  "features": "lean",
  "params": {
    "max_depth": 4,
    "min_child_weight": 30,
    "reg_lambda": 20.0,
    "reg_alpha": 1.0,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "max_bin": 256
  },
  "hypothesis": "The compact representation may also reduce noise for XGBoost."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_xgb_lean.json](../improvements/round2/artifacts/screen/r2_xgb_lean.json)

### 76. r2_lgb_smooth_cats

Type: main screening configuration; status: complete.

**Reason:** Stronger categorical smoothing may improve group-relative LightGBM generalization.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7476579 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0008347 |
| Average precision | 0.2385559 |
| Log loss | 0.2486614 |
| Brier score | 0.0681731 |
| Development CV AUC | 0.7584174 |
| Selected epochs/trees | 713.0000000 |
| Recorded call seconds | 18.0214038 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Decision:** Validated on common folds; not retained in the current blend

**Recorded recipe/settings:**

```json
{
  "name": "r2_lgb_smooth_cats",
  "kind": "lgb",
  "features": "engineered",
  "groups": true,
  "params": {
    "num_leaves": 16,
    "min_child_samples": 150,
    "colsample_bytree": 0.8,
    "subsample": 0.9,
    "subsample_freq": 1,
    "reg_lambda": 10.0,
    "reg_alpha": 1.0,
    "max_bin": 255,
    "cat_smooth": 100.0,
    "cat_l2": 30.0
  },
  "hypothesis": "Stronger categorical smoothing may improve group-relative LightGBM generalization."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_lgb_smooth_cats.json](../improvements/round2/artifacts/screen/r2_lgb_smooth_cats.json)

### 77. r2_lgb_linear

Type: main screening configuration; status: complete.

**Reason:** Linear models inside leaves may model smooth financial relationships more efficiently than constant leaves.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7437656 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0047270 |
| Average precision | 0.2316144 |
| Log loss | 0.2499283 |
| Brier score | 0.0684755 |
| Selected epochs/trees | 450.0000000 |
| Recorded call seconds | 9.0602670 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_lgb_linear",
  "kind": "lgb",
  "features": "lean",
  "max_iterations": 1500,
  "patience": 100,
  "params": {
    "num_leaves": 16,
    "min_child_samples": 150,
    "colsample_bytree": 0.8,
    "subsample": 0.9,
    "subsample_freq": 1,
    "reg_lambda": 10.0,
    "reg_alpha": 1.0,
    "max_bin": 127,
    "linear_tree": true,
    "linear_lambda": 10.0
  },
  "hypothesis": "Linear models inside leaves may model smooth financial relationships more efficiently than constant leaves."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_lgb_linear.json](../improvements/round2/artifacts/screen/r2_lgb_linear.json)

### 78. r2_cat_burden

Type: main screening configuration; status: complete.

**Reason:** Isolate the payment-burden and household-amount block from the hypothetical rate/term proxies.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7476912 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0008014 |
| Average precision | 0.2329163 |
| Log loss | 0.2489953 |
| Brier score | 0.0683586 |
| Selected epochs/trees | 1695.0000000 |
| Recorded call seconds | 223.8365388 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_burden",
  "kind": "cat",
  "features": "finance",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "source": "improvements/round2/adaptive.py",
  "hypothesis": "Isolate the payment-burden and household-amount block from the hypothetical rate/term proxies.",
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
    "INCOME_MINUS_12_ANNUITIES",
    "MARGIN_PER_PERSON",
    "INCOME_PER_ADULT",
    "CREDIT_PER_ADULT",
    "GOODS_OVER_INCOME",
    "CREDIT_COST_AMOUNT"
  ]
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_burden.json](../improvements/round2/artifacts/screen/r2_cat_burden.json)

### 79. r2_cat_term_proxies

Type: main screening configuration; status: complete.

**Reason:** Isolate the redundant nonlinear rate/term representations; test whether quantization alone explains the finance gain.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7499521 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | 0.0014595 |
| Average precision | 0.2391725 |
| Log loss | 0.2481209 |
| Brier score | 0.0681175 |
| Development CV AUC | 0.7622544 |
| Selected epochs/trees | 1480.0000000 |
| Recorded call seconds | 197.4004507 |

**Outcome / interpretation:** Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Decision:** Retained in the final frozen ensemble at weight 0.562500

**Recorded recipe/settings:**

```json
{
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
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_term_proxies.json](../improvements/round2/artifacts/screen/r2_cat_term_proxies.json)

### 80. r2_cat_finance_native

Type: main screening configuration; status: complete.

**Reason:** Test whether native missing bins and financial features provide complementary gains.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7492352 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | 0.0007426 |
| Average precision | 0.2353887 |
| Log loss | 0.2484279 |
| Brier score | 0.0682387 |
| Selected epochs/trees | 1467.0000000 |
| Recorded call seconds | 206.9872241 |

**Outcome / interpretation:** Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_finance_native",
  "kind": "cat",
  "features": "finance",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "source": "improvements/round2/adaptive.py",
  "hypothesis": "Test whether native missing bins and financial features provide complementary gains.",
  "missing": "native"
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_finance_native.json](../improvements/round2/artifacts/screen/r2_cat_finance_native.json)

### 81. r2_cat_finance_tuned

Type: main screening configuration; status: complete.

**Reason:** Combine the finance representation with the best screened alternative CatBoost parameter recipe (r2_cat_rsm075); this tests interaction rather than assuming additive gains.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7492733 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | 0.0007807 |
| Average precision | 0.2367265 |
| Log loss | 0.2485129 |
| Brier score | 0.0682416 |
| Selected epochs/trees | 1694.0000000 |
| Recorded call seconds | 209.0178490 |

**Outcome / interpretation:** Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_finance_tuned",
  "kind": "cat",
  "features": "finance",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "rsm": 0.75,
    "bagging_temperature": 1.0
  },
  "source": "improvements/round2/adaptive.py",
  "max_iterations": 5000,
  "hypothesis": "Combine the finance representation with the best screened alternative CatBoost parameter recipe (r2_cat_rsm075); this tests interaction rather than assuming additive gains."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_finance_tuned.json](../improvements/round2/artifacts/screen/r2_cat_finance_tuned.json)

### 82. r2_cat_ctr1

Type: main screening configuration; status: complete.

**Reason:** The saved baseline resolves max_ctr_complexity=4. Restricting categorical-combination complexity may reduce variance.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7478273 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0006653 |
| Average precision | 0.2349628 |
| Log loss | 0.2488278 |
| Brier score | 0.0682933 |
| Selected epochs/trees | 1470.0000000 |
| Recorded call seconds | 122.0503559 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_ctr1",
  "kind": "cat",
  "features": "lean",
  "source": "improvements/round2/adaptive.py",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "max_ctr_complexity": 1
  },
  "hypothesis": "The saved baseline resolves max_ctr_complexity=4. Restricting categorical-combination complexity may reduce variance."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_ctr1.json](../improvements/round2/artifacts/screen/r2_cat_ctr1.json)

### 83. r2_cat_ctr2

Type: main screening configuration; status: complete.

**Reason:** The saved baseline resolves max_ctr_complexity=4. Restricting categorical-combination complexity may reduce variance.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7480951 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0003975 |
| Average precision | 0.2349834 |
| Log loss | 0.2487988 |
| Brier score | 0.0682879 |
| Selected epochs/trees | 1664.0000000 |
| Recorded call seconds | 215.7564042 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_ctr2",
  "kind": "cat",
  "features": "lean",
  "source": "improvements/round2/adaptive.py",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "max_ctr_complexity": 2
  },
  "hypothesis": "The saved baseline resolves max_ctr_complexity=4. Restricting categorical-combination complexity may reduce variance."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_ctr2.json](../improvements/round2/artifacts/screen/r2_cat_ctr2.json)

### 84. r2_cat_bayesian_rsm075

Type: main screening configuration; status: complete.

**Reason:** Explicitly switch bootstrap from the resolved MVS default to Bayesian; compare against the column-sampling trial whose bootstrap remained MVS.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7471481 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0013445 |
| Average precision | 0.2357865 |
| Log loss | 0.2488236 |
| Brier score | 0.0682770 |
| Selected epochs/trees | 1685.0000000 |
| Recorded call seconds | 215.4881821 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_bayesian_rsm075",
  "kind": "cat",
  "features": "lean",
  "source": "improvements/round2/adaptive.py",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "rsm": 0.75,
    "bootstrap_type": "Bayesian",
    "bagging_temperature": 1.0
  },
  "hypothesis": "Explicitly switch bootstrap from the resolved MVS default to Bayesian; compare against the column-sampling trial whose bootstrap remained MVS."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_bayesian_rsm075.json](../improvements/round2/artifacts/screen/r2_cat_bayesian_rsm075.json)

### 85. r2_xgb_finance

Type: main screening configuration; status: complete.

**Reason:** Check whether the financial representation also helps the best screened XGBoost recipe.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7472249 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0012677 |
| Average precision | 0.2354409 |
| Log loss | 0.2490898 |
| Brier score | 0.0683353 |
| Development CV AUC | 0.7588833 |
| Selected epochs/trees | 1515.0000000 |
| Recorded call seconds | 82.8176811 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Decision:** Validated on common folds; not retained in the current blend

**Recorded recipe/settings:**

```json
{
  "name": "r2_xgb_finance",
  "kind": "xgb",
  "features": "finance",
  "params": {
    "max_depth": 3,
    "min_child_weight": 30,
    "reg_lambda": 20.0,
    "reg_alpha": 1.0,
    "subsample": 0.85,
    "colsample_bytree": 0.85,
    "max_bin": 256
  },
  "source": "improvements/round2/adaptive.py",
  "hypothesis": "Check whether the financial representation also helps the best screened XGBoost recipe."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_xgb_finance.json](../improvements/round2/artifacts/screen/r2_xgb_finance.json)

### 86. r2_lgb_finance

Type: main screening configuration; status: complete.

**Reason:** Check whether the finance representation improves the known complementary LightGBM configuration.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7464873 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0020053 |
| Average precision | 0.2379704 |
| Log loss | 0.2491663 |
| Brier score | 0.0682790 |
| Selected epochs/trees | 697.0000000 |
| Recorded call seconds | 19.0002849 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority. Different algorithms may still help a blend through complementary errors.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_lgb_finance",
  "kind": "lgb",
  "features": "finance",
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
  "groups": true,
  "source": "improvements/round2/adaptive.py",
  "hypothesis": "Check whether the finance representation improves the known complementary LightGBM configuration."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_lgb_finance.json](../improvements/round2/artifacts/screen/r2_lgb_finance.json)

### 87. r2_cat_budget_control

Type: main screening configuration; status: complete.

**Reason:** Hold features and all model parameters fixed while increasing patience 150→200 and the cap 3000→4500. Test whether the changed stopping budget explains apparent gains from other trials.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7484926 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | 0.0000000 |
| Average precision | 0.2339938 |
| Log loss | 0.2487278 |
| Brier score | 0.0683022 |
| Selected epochs/trees | 1670.0000000 |
| Recorded call seconds | 139.7612541 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Decision:** Implementation/stopping-budget control; used to interpret other trials, not claimed as a new recipe

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_budget_control",
  "kind": "cat",
  "features": "lean",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "source": "improvements/round2/budget_control.py",
  "hypothesis": "Hold features and all model parameters fixed while increasing patience 150\u2192200 and the cap 3000\u21924500. Test whether the changed stopping budget explains apparent gains from other trials."
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_budget_control.json](../improvements/round2/artifacts/screen/r2_cat_budget_control.json)

### 88. r2_cat_proxies_native

Type: main screening configuration; status: complete.

**Reason:** The proxy-only representation improved screening by 0.00146; combine it with the independently promising native missing policy.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7496474 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | 0.0011548 |
| Average precision | 0.2367750 |
| Log loss | 0.2483980 |
| Brier score | 0.0682178 |
| Development CV AUC | 0.7615745 |
| Selected epochs/trees | 1724.0000000 |
| Recorded call seconds | 226.0162840 |

**Outcome / interpretation:** Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Decision:** Retained in the final frozen ensemble at weight 0.250000

**Recorded recipe/settings:**

```json
{
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
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_proxies_native.json](../improvements/round2/artifacts/screen/r2_cat_proxies_native.json)

### 89. r2_cat_rates_only

Type: main screening configuration; status: complete.

**Reason:** Separate the hypothetical positive-rate transforms from the term-rounding distances.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7484734 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | -0.0000191 |
| Average precision | 0.2355793 |
| Log loss | 0.2486122 |
| Brier score | 0.0682483 |
| Selected epochs/trees | 1497.0000000 |
| Recorded call seconds | 199.5187900 |

**Outcome / interpretation:** Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_rates_only",
  "kind": "cat",
  "features": "finance",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "source": "improvements/round2/proxy_followup.py",
  "hypothesis": "Separate the hypothetical positive-rate transforms from the term-rounding distances.",
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
    "ASSUMED_PERIOD_RATE_60"
  ]
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_rates_only.json](../improvements/round2/artifacts/screen/r2_cat_rates_only.json)

### 90. r2_cat_distances_only

Type: main screening configuration; status: complete.

**Reason:** Separate the 6/12-period term-distance transforms from hypothetical rates.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7487658 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | 0.0002732 |
| Average precision | 0.2348054 |
| Log loss | 0.2487502 |
| Brier score | 0.0683320 |
| Selected epochs/trees | 1953.0000000 |
| Recorded call seconds | 229.3369761 |

**Outcome / interpretation:** Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_distances_only",
  "kind": "cat",
  "features": "finance",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "source": "improvements/round2/proxy_followup.py",
  "hypothesis": "Separate the 6/12-period term-distance transforms from hypothetical rates.",
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
    "TERM_MULTIPLE_6_DISTANCE",
    "TERM_MULTIPLE_12_DISTANCE"
  ]
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_distances_only.json](../improvements/round2/artifacts/screen/r2_cat_distances_only.json)

### 91. r2_cat_proxies_rsm075

Type: main screening configuration; status: complete.

**Reason:** Test whether the promising proxy block complements column sampling while retaining the resolved MVS bootstrap.

**Rationale provenance:** Written in the candidate plan before this trial started

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7492881 |
| Reference AUC, when recorded | 0.7484926 |
| Ledger delta versus its recorded reference | 0.0007955 |
| Average precision | 0.2362470 |
| Log loss | 0.2484353 |
| Brier score | 0.0682367 |
| Selected epochs/trees | 1293.0000000 |
| Recorded call seconds | 154.8756423 |

**Outcome / interpretation:** Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.

**Decision:** Screened but not advanced by the documented promising/diverse-family shortlist

**Recorded recipe/settings:**

```json
{
  "name": "r2_cat_proxies_rsm075",
  "kind": "cat",
  "features": "finance",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "rsm": 0.75,
    "bagging_temperature": 1.0
  },
  "source": "improvements/round2/proxy_followup.py",
  "hypothesis": "Test whether the promising proxy block complements column sampling while retaining the resolved MVS bootstrap.",
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
}
```

**Evidence:** [improvements/round2/artifacts/screen/r2_cat_proxies_rsm075.json](../improvements/round2/artifacts/screen/r2_cat_proxies_rsm075.json)

## third pass

### 92. r3_cat_baseline

Type: main screening configuration; status: complete.

**Reason:** Exact control: recover the round-two proxy-only screen before evaluating new settings.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7499521 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7511555 |
| Explicit standalone gain versus reference | -0.0012792 |
| Average precision | 0.2391725 |
| Log loss | 0.2481209 |
| Brier score | 0.0681175 |
| Selected epochs/trees | 1480.0000000 |
| Recorded call seconds | 82.0904093 |

**Outcome / interpretation:** Implementation control; maximum prediction difference from the previous proxy screen is 0.0. This is not a new improvement.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 93. r3_cat_depth4

Type: main screening configuration; status: complete.

**Reason:** Shallower trees may regularize the successful proxy representation differently.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7503981 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7513465 |
| Explicit standalone gain versus reference | -0.0008331 |
| Average precision | 0.2362761 |
| Log loss | 0.2482918 |
| Brier score | 0.0682355 |
| Selected epochs/trees | 2194.0000000 |
| Recorded call seconds | 175.6745222 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 94. r3_cat_depth6

Type: main screening configuration; status: complete.

**Reason:** More interactions may become useful with the proxy representation.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7496098 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7512686 |
| Explicit standalone gain versus reference | -0.0016215 |
| Average precision | 0.2361962 |
| Log loss | 0.2484323 |
| Brier score | 0.0682435 |
| Selected epochs/trees | 1243.0000000 |
| Recorded call seconds | 140.6111751 |

**Outcome / interpretation:** A small screening gain below the promotion threshold. No reliable improvement is established; selection noise and training variation remain plausible. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 95. r3_cat_depth7

Type: main screening configuration; status: complete.

**Reason:** Test a further increase in interaction capacity with stronger shrinkage.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7493145 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7513718 |
| Explicit standalone gain versus reference | -0.0019168 |
| Average precision | 0.2356303 |
| Log loss | 0.2485281 |
| Brier score | 0.0682620 |
| Selected epochs/trees | 1355.0000000 |
| Recorded call seconds | 187.3707149 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 96. r3_cat_slow

Type: main screening configuration; status: complete.

**Reason:** Smaller boosting steps may improve the proxy model rather than the old representation.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7498112 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7512002 |
| Explicit standalone gain versus reference | -0.0014201 |
| Average precision | 0.2368697 |
| Log loss | 0.2482587 |
| Brier score | 0.0681942 |
| Selected epochs/trees | 2811.0000000 |
| Recorded call seconds | 282.4830301 |

**Outcome / interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 97. r3_cat_l2_30

Type: main screening configuration; status: complete.

**Reason:** Test stronger shrinkage with the winning feature block.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7492683 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7511936 |
| Explicit standalone gain versus reference | -0.0019630 |
| Average precision | 0.2357530 |
| Log loss | 0.2484660 |
| Brier score | 0.0682441 |
| Selected epochs/trees | 1835.0000000 |
| Recorded call seconds | 197.2804010 |

**Outcome / interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 98. r3_cat_borders512

Type: main screening configuration; status: complete.

**Reason:** Finer quantization may preserve loan-proxy and score thresholds.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7508331 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7514878 |
| Explicit standalone gain versus reference | -0.0003982 |
| Average precision | 0.2354267 |
| Log loss | 0.2481738 |
| Brier score | 0.0682249 |
| Selected epochs/trees | 1621.0000000 |
| Recorded call seconds | 181.5368111 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 99. r3_cat_weight2

Type: main screening configuration; status: complete.

**Reason:** A moderately weighted objective may learn different useful ranking errors.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7501492 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7513541 |
| Explicit standalone gain versus reference | -0.0010821 |
| Average precision | 0.2374933 |
| Log loss | 0.2651148 |
| Brier score | 0.0731501 |
| Selected epochs/trees | 1335.0000000 |
| Recorded call seconds | 154.9092340 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 100. r3_cat_depthwise

Type: main screening configuration; status: complete.

**Reason:** Asymmetric trees may model conditional loan/score effects efficiently.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7490870 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7513864 |
| Explicit standalone gain versus reference | -0.0021443 |
| Average precision | 0.2370295 |
| Log loss | 0.2485342 |
| Brier score | 0.0682465 |
| Selected epochs/trees | 474.0000000 |
| Recorded call seconds | 56.3537920 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 101. r3_cat_groups

Type: main screening configuration; status: complete.

**Reason:** Training-fold-only frequencies and group-relative financial quantities may complement the compact proxy model.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7499412 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7514594 |
| Explicit standalone gain versus reference | -0.0012901 |
| Average precision | 0.2356926 |
| Log loss | 0.2485310 |
| Brier score | 0.0682958 |
| Selected epochs/trees | 1998.0000000 |
| Recorded call seconds | 222.1873920 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 102. r3_cat_median

Type: main screening configuration; status: complete.

**Reason:** Median imputation may improve upon a sentinel or native missing split.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7490229 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7513980 |
| Explicit standalone gain versus reference | -0.0022084 |
| Average precision | 0.2377162 |
| Log loss | 0.2483836 |
| Brier score | 0.0681954 |
| Selected epochs/trees | 1488.0000000 |
| Recorded call seconds | 164.6572888 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 103. r3_cat_signed

Type: main screening configuration; status: complete.

**Reason:** Signed term residuals and rounded categories may retain structure lost by absolute distances.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7509073 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7516576 |
| Explicit standalone gain versus reference | -0.0003240 |
| Average precision | 0.2380349 |
| Log loss | 0.2480306 |
| Brier score | 0.0681586 |
| Development CV AUC | 0.7628502 |
| Selected epochs/trees | 1528.0000000 |
| Recorded call seconds | 195.1429870 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: advanced to common-fold CV. Common-fold standalone OOF AUC: 0.762850230. Included in the frozen primary recipe; later gates determine deployment.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 104. r3_cat_rates

Type: main screening configuration; status: complete.

**Reason:** Additional assumed-period transforms may expose useful numeric thresholds; these do not recover true rates.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7495568 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7512148 |
| Explicit standalone gain versus reference | -0.0016745 |
| Average precision | 0.2362573 |
| Log loss | 0.2484029 |
| Brier score | 0.0682264 |
| Selected epochs/trees | 1452.0000000 |
| Recorded call seconds | 168.4995229 |

**Outcome / interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 105. r3_cat_crosses

Type: main screening configuration; status: complete.

**Reason:** Explicit categorical interactions and age bands may complement native categorical combinations.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7496441 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7512008 |
| Explicit standalone gain versus reference | -0.0015872 |
| Average precision | 0.2381207 |
| Log loss | 0.2482676 |
| Brier score | 0.0681689 |
| Selected epochs/trees | 1578.0000000 |
| Recorded call seconds | 241.1004641 |

**Outcome / interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 106. r3_cat_engineered_proxy

Type: main screening configuration; status: complete.

**Reason:** The proxy block may improve the larger financial/score representation rather than just the compact one.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7500868 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7515460 |
| Explicit standalone gain versus reference | -0.0011445 |
| Average precision | 0.2399395 |
| Log loss | 0.2480751 |
| Brier score | 0.0681174 |
| Selected epochs/trees | 1802.0000000 |
| Recorded call seconds | 230.9717839 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 107. r3_lgb_proxy

Type: main screening configuration; status: complete.

**Reason:** Use the exact compact successful proxy block in the known complementary LightGBM recipe.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7480538 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7517155 |
| Explicit standalone gain versus reference | -0.0031775 |
| Average precision | 0.2375743 |
| Log loss | 0.2488525 |
| Brier score | 0.0682696 |
| Development CV AUC | 0.7592167 |
| Selected epochs/trees | 757.0000000 |
| Recorded call seconds | 17.4289489 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: advanced to common-fold CV. Common-fold standalone OOF AUC: 0.759216711.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 108. r3_lgb_proxy_smooth

Type: main screening configuration; status: complete.

**Reason:** Stronger categorical/leaf smoothing may work differently on the compact proxy representation.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7489293 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7516864 |
| Explicit standalone gain versus reference | -0.0023020 |
| Average precision | 0.2395688 |
| Log loss | 0.2484636 |
| Brier score | 0.0681695 |
| Selected epochs/trees | 876.0000000 |
| Recorded call seconds | 17.3984900 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 109. r3_xgb_proxy

Type: main screening configuration; status: complete.

**Reason:** Remove the finance burden block that hurt CatBoost and test XGBoost on the successful compact proxy representation.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7469758 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7513790 |
| Explicit standalone gain versus reference | -0.0042555 |
| Average precision | 0.2363315 |
| Log loss | 0.2490724 |
| Brier score | 0.0683060 |
| Selected epochs/trees | 1494.0000000 |
| Recorded call seconds | 32.5165708 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 110. r3_mlp_small

Type: main screening configuration; status: complete.

**Reason:** A quantile-normalized neural model trained from scratch may contribute smooth complementary errors; fit preprocessing only on training rows.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7271761 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7509351 |
| Explicit standalone gain versus reference | -0.0240552 |
| Average precision | 0.2044257 |
| Log loss | 0.2559899 |
| Brier score | 0.0696894 |
| Selected epochs/trees | 15.0000000 |
| Recorded call seconds | 8.7562160 |

**Outcome / interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 111. r3_mlp_wide

Type: main screening configuration; status: complete.

**Reason:** A quantile-normalized neural model trained from scratch may contribute smooth complementary errors; fit preprocessing only on training rows.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7345608 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7512224 |
| Explicit standalone gain versus reference | -0.0166705 |
| Average precision | 0.2147698 |
| Log loss | 0.2533461 |
| Brier score | 0.0691828 |
| Selected epochs/trees | 49.0000000 |
| Recorded call seconds | 23.1464419 |

**Outcome / interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 112. r3_cat_borders1024

Type: main screening configuration; status: complete.

**Reason:** Follow up the positive 512-border result: test whether finer quantization continues to help.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7505390 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7515476 |
| Explicit standalone gain versus reference | -0.0006923 |
| Average precision | 0.2393984 |
| Log loss | 0.2481139 |
| Brier score | 0.0681293 |
| Selected epochs/trees | 2072.0000000 |
| Recorded call seconds | 194.7775719 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 113. r3_cat_depth4_b512

Type: main screening configuration; status: complete.

**Reason:** Combine independently promising shallower trees and finer quantization on the proxy representation.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7507158 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7515284 |
| Explicit standalone gain versus reference | -0.0005155 |
| Average precision | 0.2365224 |
| Log loss | 0.2481927 |
| Brier score | 0.0682077 |
| Selected epochs/trees | 2176.0000000 |
| Recorded call seconds | 168.9334822 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 114. r3_cat_native_b512

Type: main screening configuration; status: complete.

**Reason:** Test the interaction between native missing bins and finer quantization.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7504873 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7514887 |
| Explicit standalone gain versus reference | -0.0007440 |
| Average precision | 0.2362578 |
| Log loss | 0.2482572 |
| Brier score | 0.0682117 |
| Selected epochs/trees | 1973.0000000 |
| Recorded call seconds | 202.0113201 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 115. r3_cat_loan_b512

Type: main screening configuration; status: complete.

**Reason:** Isolate higher resolution for credit term and loan proxies; test whether they explain the global border-count gain.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7501347 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7513283 |
| Explicit standalone gain versus reference | -0.0010966 |
| Average precision | 0.2374985 |
| Log loss | 0.2482573 |
| Brier score | 0.0682098 |
| Selected epochs/trees | 1656.0000000 |
| Recorded call seconds | 173.9494121 |

**Outcome / interpretation:** A small screening gain below the promotion threshold. No reliable improvement is established; selection noise and training variation remain plausible. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 116. r3_cat_scores_b512

Type: main screening configuration; status: complete.

**Reason:** Isolate higher resolution for external scores as an alternative explanation for the global border-count gain.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7495165 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7512251 |
| Explicit standalone gain versus reference | -0.0017148 |
| Average precision | 0.2370710 |
| Log loss | 0.2483570 |
| Brier score | 0.0682141 |
| Selected epochs/trees | 1568.0000000 |
| Recorded call seconds | 153.9823139 |

**Outcome / interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 117. r3_cat_signed_only

Type: main screening configuration; status: complete.

**Reason:** Decompose the positive joint term representation: keep signed residual additions and ignore rounded category additions.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7502678 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7514635 |
| Explicit standalone gain versus reference | -0.0009635 |
| Average precision | 0.2394249 |
| Log loss | 0.2480928 |
| Brier score | 0.0681089 |
| Selected epochs/trees | 1810.0000000 |
| Recorded call seconds | 175.7093341 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 118. r3_cat_term_categories

Type: main screening configuration; status: complete.

**Reason:** Decompose the positive joint term representation: keep rounded category additions and ignore signed residual additions.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7491226 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7511759 |
| Explicit standalone gain versus reference | -0.0021087 |
| Average precision | 0.2354165 |
| Log loss | 0.2486068 |
| Brier score | 0.0682875 |
| Selected epochs/trees | 1655.0000000 |
| Recorded call seconds | 186.5578642 |

**Outcome / interpretation:** No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective. Promotion decision: did not advance under the recorded threshold and finalist cap.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 119. r3_cat_feature_b512

Type: main screening configuration; status: complete.

**Reason:** Combine the eligible best new feature block (r3_cat_signed) with finer quantization under the recorded rule.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7508544 |
| Reference AUC, when recorded | 0.7512313 |
| Best screened blend AUC | 0.7517070 |
| Explicit standalone gain versus reference | -0.0003769 |
| Average precision | 0.2354072 |
| Log loss | 0.2482903 |
| Brier score | 0.0682646 |
| Development CV AUC | 0.7626619 |
| Selected epochs/trees | 1851.0000000 |
| Recorded call seconds | 192.8398299 |

**Outcome / interpretation:** Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement. Promotion decision: advanced to common-fold CV. Common-fold standalone OOF AUC: 0.762661887. Included in the frozen primary recipe; later gates determine deployment.

**Recorded recipe/settings:**

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

**Evidence:** See the complete machine-readable ledger.

### 120. logits_c01

Type: auxiliary meta-learning probe; status: complete.

**Reason:** Test cross-fitted learned prediction combination before considering fully nested stacking.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7629431 |
| Reference AUC, when recorded | not recorded |
| Best screened blend AUC | 0.7630916 |
| Explicit probe gain | 0.0000025 |
| Average precision | 0.2478530 |
| Log loss | 0.2447007 |
| Brier score | 0.0675765 |
| Recorded call seconds | 1.2335708 |

**Outcome / interpretation:** Screening only: precomputed base OOF features are not fully nested. Gain below the recorded threshold does not warrant a larger nested run.

**Recorded recipe/settings:**

```json
{
  "name": "logits_c01",
  "C": 0.1,
  "groups": false
}
```

**Evidence:** See the complete machine-readable ledger.

### 121. logits_c1

Type: auxiliary meta-learning probe; status: complete.

**Reason:** Test cross-fitted learned prediction combination before considering fully nested stacking.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7629435 |
| Reference AUC, when recorded | not recorded |
| Best screened blend AUC | 0.7630916 |
| Explicit probe gain | 0.0000025 |
| Average precision | 0.2478516 |
| Log loss | 0.2447007 |
| Brier score | 0.0675767 |
| Recorded call seconds | 1.0804830 |

**Outcome / interpretation:** Screening only: precomputed base OOF features are not fully nested. Gain below the recorded threshold does not warrant a larger nested run.

**Recorded recipe/settings:**

```json
{
  "name": "logits_c1",
  "C": 1.0,
  "groups": false
}
```

**Evidence:** See the complete machine-readable ledger.

### 122. logits_groups_c01

Type: auxiliary meta-learning probe; status: complete.

**Reason:** Test cross-fitted learned prediction combination before considering fully nested stacking.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7628490 |
| Reference AUC, when recorded | not recorded |
| Best screened blend AUC | 0.7630850 |
| Explicit probe gain | -0.0000041 |
| Average precision | 0.2474294 |
| Log loss | 0.2447473 |
| Brier score | 0.0675916 |
| Recorded call seconds | 1.7060049 |

**Outcome / interpretation:** Screening only: precomputed base OOF features are not fully nested. Gain below the recorded threshold does not warrant a larger nested run.

**Recorded recipe/settings:**

```json
{
  "name": "logits_groups_c01",
  "C": 0.1,
  "groups": true
}
```

**Evidence:** See the complete machine-readable ledger.

## round4

### 123. r4_cat_control

Type: main screening configuration; status: complete.

**Reason:** Reproduce the exact round-three 55-column default model before trusting any new comparison.

**Rationale provenance:** Plan recorded before fitting

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7509073 |
| Reference AUC, when recorded | 0.7518409 |
| Best screened blend AUC | 0.7518468 |
| Ledger delta versus its recorded reference | 0.0000059 |
| Average precision | 0.2380349 |
| Log loss | 0.2480306 |
| Brier score | 0.0681586 |
| Selected epochs/trees | 1528.0000000 |
| Recorded call seconds | 101.5505600 |

**Outcome / interpretation:** Exact reproduction control: maximum prediction difference is 0.0. This validates the shared split, representation, fitting path and environment; it is not a new improvement.

**Recorded recipe/settings:**

```json
{
  "name": "r4_cat_control",
  "kind": "cat",
  "features": "final55",
  "stage": "A",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "Reproduce the exact round-three 55-column default model before trusting any new comparison.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Evidence:** [improvements/round4/artifacts/screen/r4_cat_control.json](../improvements/round4/artifacts/screen/r4_cat_control.json)

### 124. r4_cat_control512

Type: main screening configuration; status: complete.

**Reason:** Reproduce the exact round-three 55-column 512-border model.

**Rationale provenance:** Plan recorded before fitting

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7508544 |
| Reference AUC, when recorded | 0.7518409 |
| Best screened blend AUC | 0.7518478 |
| Ledger delta versus its recorded reference | 0.0000069 |
| Average precision | 0.2354072 |
| Log loss | 0.2482903 |
| Brier score | 0.0682646 |
| Selected epochs/trees | 1851.0000000 |
| Recorded call seconds | 154.3598940 |

**Outcome / interpretation:** Exact reproduction control: maximum prediction difference is 0.0. This validates the shared split, representation, fitting path and environment; it is not a new improvement.

**Recorded recipe/settings:**

```json
{
  "name": "r4_cat_control512",
  "kind": "cat",
  "features": "final55",
  "stage": "A",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5,
    "border_count": 512
  },
  "hypothesis": "Reproduce the exact round-three 55-column 512-border model.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Evidence:** [improvements/round4/artifacts/screen/r4_cat_control512.json](../improvements/round4/artifacts/screen/r4_cat_control512.json)

### 125. r4_cat_depth4

Type: main screening configuration; status: complete.

**Reason:** Change depth on the successful 55-column representation while holding shrinkage fixed.

**Rationale provenance:** Plan recorded before fitting

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7500805 |
| Reference AUC, when recorded | 0.7518409 |
| Best screened blend AUC | 0.7517971 |
| Ledger delta versus its recorded reference | -0.0000438 |
| Average precision | 0.2365049 |
| Log loss | 0.2482572 |
| Brier score | 0.0681962 |
| Selected epochs/trees | 1838.0000000 |
| Recorded call seconds | 198.2380161 |

**Outcome / interpretation:** No positive screened blend gain over the current recipe. Promotion has not been evaluated; the search is incomplete. The standalone AUC and blend gain answer different questions; correlated ranking errors can make a weaker individual model useful. The hypothesized bias/variance or encoding mechanism is not causally identified by this score alone. The selected iteration was below the configured cap; the observed result is not explained simply by exhausting that cap. This repeatedly explored split cannot establish hidden-test improvement or universal ineffectiveness.

**Recorded recipe/settings:**

```json
{
  "name": "r4_cat_depth4",
  "kind": "cat",
  "features": "final55",
  "stage": "A",
  "params": {
    "depth": 4,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "Change depth on the successful 55-column representation while holding shrinkage fixed.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Evidence:** [improvements/round4/artifacts/screen/r4_cat_depth4.json](../improvements/round4/artifacts/screen/r4_cat_depth4.json)

### 126. r4_cat_depth6

Type: main screening configuration; status: complete.

**Reason:** Change depth on the successful 55-column representation while holding shrinkage fixed.

**Rationale provenance:** Plan recorded before fitting

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7498035 |
| Reference AUC, when recorded | 0.7518409 |
| Best screened blend AUC | 0.7518468 |
| Ledger delta versus its recorded reference | 0.0000059 |
| Average precision | 0.2356308 |
| Log loss | 0.2484611 |
| Brier score | 0.0682594 |
| Selected epochs/trees | 1513.0000000 |
| Recorded call seconds | 228.1593599 |

**Outcome / interpretation:** Best screened blend improved the current recipe by +0.0000059 AUC. Promotion has not been evaluated; the search is incomplete. The standalone AUC and blend gain answer different questions; correlated ranking errors can make a weaker individual model useful. The hypothesized bias/variance or encoding mechanism is not causally identified by this score alone. The selected iteration was below the configured cap; the observed result is not explained simply by exhausting that cap. This repeatedly explored split cannot establish hidden-test improvement or universal ineffectiveness.

**Recorded recipe/settings:**

```json
{
  "name": "r4_cat_depth6",
  "kind": "cat",
  "features": "final55",
  "stage": "A",
  "params": {
    "depth": 6,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "Change depth on the successful 55-column representation while holding shrinkage fixed.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Evidence:** [improvements/round4/artifacts/screen/r4_cat_depth6.json](../improvements/round4/artifacts/screen/r4_cat_depth6.json)

### 127. r4_cat_depth7

Type: main screening configuration; status: complete.

**Reason:** Change depth on the successful 55-column representation while holding shrinkage fixed.

**Rationale provenance:** Plan recorded before fitting

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7496954 |
| Reference AUC, when recorded | 0.7518409 |
| Best screened blend AUC | 0.7519773 |
| Ledger delta versus its recorded reference | 0.0001364 |
| Average precision | 0.2377312 |
| Log loss | 0.2483875 |
| Brier score | 0.0681846 |
| Selected epochs/trees | 1402.0000000 |
| Recorded call seconds | 232.8031459 |

**Outcome / interpretation:** Best screened blend improved the current recipe by +0.0001364 AUC. Promotion has not been evaluated; the search is incomplete. The standalone AUC and blend gain answer different questions; correlated ranking errors can make a weaker individual model useful. The hypothesized bias/variance or encoding mechanism is not causally identified by this score alone. The selected iteration was below the configured cap; the observed result is not explained simply by exhausting that cap. This repeatedly explored split cannot establish hidden-test improvement or universal ineffectiveness.

**Recorded recipe/settings:**

```json
{
  "name": "r4_cat_depth7",
  "kind": "cat",
  "features": "final55",
  "stage": "A",
  "params": {
    "depth": 7,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "hypothesis": "Change depth on the successful 55-column representation while holding shrinkage fixed.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Evidence:** [improvements/round4/artifacts/screen/r4_cat_depth7.json](../improvements/round4/artifacts/screen/r4_cat_depth7.json)

### 128. r4_cat_l2_2

Type: main screening configuration; status: complete.

**Reason:** Retune leaf shrinkage after the signed/category representation changed.

**Rationale provenance:** Plan recorded before fitting

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7503000 |
| Reference AUC, when recorded | 0.7518409 |
| Best screened blend AUC | 0.7519012 |
| Ledger delta versus its recorded reference | 0.0000603 |
| Average precision | 0.2368761 |
| Log loss | 0.2482994 |
| Brier score | 0.0682104 |
| Selected epochs/trees | 1756.0000000 |
| Recorded call seconds | 209.7664208 |

**Outcome / interpretation:** Best screened blend improved the current recipe by +0.0000603 AUC. Promotion has not been evaluated; the search is incomplete. The standalone AUC and blend gain answer different questions; correlated ranking errors can make a weaker individual model useful. The hypothesized bias/variance or encoding mechanism is not causally identified by this score alone. The selected iteration was below the configured cap; the observed result is not explained simply by exhausting that cap. This repeatedly explored split cannot establish hidden-test improvement or universal ineffectiveness.

**Recorded recipe/settings:**

```json
{
  "name": "r4_cat_l2_2",
  "kind": "cat",
  "features": "final55",
  "stage": "A",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 2,
    "random_strength": 0.5
  },
  "hypothesis": "Retune leaf shrinkage after the signed/category representation changed.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Evidence:** [improvements/round4/artifacts/screen/r4_cat_l2_2.json](../improvements/round4/artifacts/screen/r4_cat_l2_2.json)

### 129. r4_cat_l2_24

Type: main screening configuration; status: complete.

**Reason:** Retune leaf shrinkage after the signed/category representation changed.

**Rationale provenance:** Plan recorded before fitting

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7513138 |
| Reference AUC, when recorded | 0.7518409 |
| Best screened blend AUC | 0.7520846 |
| Ledger delta versus its recorded reference | 0.0002437 |
| Average precision | 0.2381177 |
| Log loss | 0.2480652 |
| Brier score | 0.0681726 |
| Selected epochs/trees | 2496.0000000 |
| Recorded call seconds | 268.6665742 |

**Outcome / interpretation:** Best screened blend improved the current recipe by +0.0002437 AUC. Promotion has not been evaluated; the search is incomplete. The standalone AUC and blend gain answer different questions; correlated ranking errors can make a weaker individual model useful. The hypothesized bias/variance or encoding mechanism is not causally identified by this score alone. The selected iteration was below the configured cap; the observed result is not explained simply by exhausting that cap. This repeatedly explored split cannot establish hidden-test improvement or universal ineffectiveness.

**Recorded recipe/settings:**

```json
{
  "name": "r4_cat_l2_24",
  "kind": "cat",
  "features": "final55",
  "stage": "A",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 24,
    "random_strength": 0.5
  },
  "hypothesis": "Retune leaf shrinkage after the signed/category representation changed.",
  "max_iterations": 4500,
  "patience": 200
}
```

**Evidence:** [improvements/round4/artifacts/screen/r4_cat_l2_24.json](../improvements/round4/artifacts/screen/r4_cat_l2_24.json)

## higher_upside

### 130. hu_tabm_raw_piecewise

Type: main screening configuration; status: complete.

**Reason:** Numerical embeddings and joint shared-weight ensembling on supplied raw predictors.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7401112 |
| Reference AUC, when recorded | 0.7518409 |
| Best screened blend AUC | 0.7520803 |
| Ledger delta versus its recorded reference | 0.0002394 |
| Average precision | 0.2256159 |
| Log loss | 0.2517290 |
| Brier score | 0.0688863 |
| Selected epochs/trees | 28.0000000 |
| Recorded call seconds | 278.6324921 |

**Outcome / interpretation:** Standalone inner AUC 0.7401112; best blend gain +0.0002394 against the complete current reference. Did not advance under the recorded promotion rule. Retained epoch 28 of 48 completed; stopping reason: AUC patience. This tests this embedding/shared-ensemble recipe, not all neural architectures. A time-truncated fit cannot rule out useful convergence. Mechanisms are hypotheses, not causal findings. Repeatedly explored selection labels cannot establish hidden-test improvement.

**Recorded recipe/settings:**

```json
{
  "kind": "tabm",
  "architecture": "tabm-mini",
  "dropout": 0.1,
  "learning_rate": 0.002,
  "weight_decay": 0.0003,
  "max_epochs": 140,
  "patience": 20,
  "max_seconds": 1500,
  "name": "hu_tabm_raw_piecewise",
  "features": "raw",
  "embedding": "piecewise",
  "hypothesis": "Numerical embeddings and joint shared-weight ensembling on supplied raw predictors."
}
```

**Evidence:** [improvements/high_upside/artifacts/pilots/hu_tabm_raw_piecewise.json](../improvements/high_upside/artifacts/pilots/hu_tabm_raw_piecewise.json)

### 131. hu_tabm_signed_piecewise

Type: main screening configuration; status: complete.

**Reason:** Same neural recipe with the successful tree representation.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7508052 |
| Reference AUC, when recorded | 0.7518409 |
| Best screened blend AUC | 0.7533795 |
| Ledger delta versus its recorded reference | 0.0015386 |
| Average precision | 0.2386177 |
| Log loss | 0.2480192 |
| Brier score | 0.0681150 |
| Development CV AUC | 0.7606962 |
| Selected epochs/trees | 30.0000000 |
| Recorded call seconds | 366.7608521 |

**Outcome / interpretation:** Standalone inner AUC 0.7508052; best blend gain +0.0015386 against the complete current reference. Promoted to common-fold CV. Retained epoch 30 of 50 completed; stopping reason: AUC patience. This tests this embedding/shared-ensemble recipe, not all neural architectures. A time-truncated fit cannot rule out useful convergence. Mechanisms are hypotheses, not causal findings. Repeatedly explored selection labels cannot establish hidden-test improvement.

**Recorded recipe/settings:**

```json
{
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
}
```

**Evidence:** [improvements/high_upside/artifacts/pilots/hu_tabm_signed_piecewise.json](../improvements/high_upside/artifacts/pilots/hu_tabm_signed_piecewise.json)

### 132. hu_tabm_signed_periodic

Type: main screening configuration; status: complete.

**Reason:** Periodic numerical embeddings can expose different smooth thresholds and interactions.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7481982 |
| Reference AUC, when recorded | 0.7518409 |
| Best screened blend AUC | 0.7527593 |
| Ledger delta versus its recorded reference | 0.0009184 |
| Average precision | 0.2351287 |
| Log loss | 0.2499705 |
| Brier score | 0.0686429 |
| Selected epochs/trees | 37.0000000 |
| Recorded call seconds | 442.0144639 |

**Outcome / interpretation:** Standalone inner AUC 0.7481982; best blend gain +0.0009184 against the complete current reference. Did not advance under the recorded promotion rule. Retained epoch 37 of 57 completed; stopping reason: AUC patience. This tests this embedding/shared-ensemble recipe, not all neural architectures. A time-truncated fit cannot rule out useful convergence. Mechanisms are hypotheses, not causal findings. Repeatedly explored selection labels cannot establish hidden-test improvement.

**Recorded recipe/settings:**

```json
{
  "kind": "tabm",
  "architecture": "tabm-mini",
  "dropout": 0.1,
  "learning_rate": 0.002,
  "weight_decay": 0.0003,
  "max_epochs": 140,
  "patience": 20,
  "max_seconds": 1500,
  "name": "hu_tabm_signed_periodic",
  "features": "signed",
  "embedding": "periodic",
  "hypothesis": "Periodic numerical embeddings can expose different smooth thresholds and interactions."
}
```

**Evidence:** [improvements/high_upside/artifacts/pilots/hu_tabm_signed_periodic.json](../improvements/high_upside/artifacts/pilots/hu_tabm_signed_periodic.json)

### 133. hu_tabm_regularized

Type: main screening configuration; status: complete.

**Reason:** A full TabM recipe with stronger regularization tests a different generalization tradeoff; several settings change jointly.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7501469 |
| Reference AUC, when recorded | 0.7518409 |
| Best screened blend AUC | 0.7528195 |
| Ledger delta versus its recorded reference | 0.0009786 |
| Average precision | 0.2384082 |
| Log loss | 0.2498388 |
| Brier score | 0.0685599 |
| Selected epochs/trees | 37.0000000 |
| Recorded call seconds | 263.0843961 |

**Outcome / interpretation:** Standalone inner AUC 0.7501469; best blend gain +0.0009786 against the complete current reference. Did not advance under the recorded promotion rule. Retained epoch 37 of 57 completed; stopping reason: AUC patience. This tests this embedding/shared-ensemble recipe, not all neural architectures. A time-truncated fit cannot rule out useful convergence. Mechanisms are hypotheses, not causal findings. Repeatedly explored selection labels cannot establish hidden-test improvement.

**Recorded recipe/settings:**

```json
{
  "kind": "tabm",
  "architecture": "tabm",
  "dropout": 0.25,
  "learning_rate": 0.001,
  "weight_decay": 0.003,
  "max_epochs": 180,
  "patience": 20,
  "max_seconds": 1500,
  "name": "hu_tabm_regularized",
  "features": "signed",
  "embedding": "piecewise",
  "hypothesis": "A full TabM recipe with stronger regularization tests a different generalization tradeoff; several settings change jointly."
}
```

**Evidence:** [improvements/high_upside/artifacts/pilots/hu_tabm_regularized.json](../improvements/high_upside/artifacts/pilots/hu_tabm_regularized.json)

### 134. hu_cat_score_reconstruction

Type: main screening configuration; status: complete.

**Reason:** Use observed external scores as auxiliary supervised targets, with nested OOF reconstructions and residuals.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7507566 |
| Reference AUC, when recorded | 0.7518409 |
| Best screened blend AUC | 0.7522068 |
| Ledger delta versus its recorded reference | 0.0003659 |
| Average precision | 0.2362315 |
| Log loss | 0.2480471 |
| Brier score | 0.0681653 |
| Development CV AUC | 0.7630882 |
| Selected epochs/trees | 1217.0000000 |
| Recorded call seconds | 112.7011180 |

**Outcome / interpretation:** Standalone inner AUC 0.7507566; best blend gain +0.0003659 against the complete current reference. Promoted to common-fold CV. Auxiliary score R2 measures reconstruction on observed rows, not default ranking or quality on genuinely missing scores. Downstream validation determines usefulness. Mechanisms are hypotheses, not causal findings. Repeatedly explored selection labels cannot establish hidden-test improvement.

**Recorded recipe/settings:**

```json
{
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
}
```

**Evidence:** [improvements/high_upside/artifacts/pilots/hu_cat_score_reconstruction.json](../improvements/high_upside/artifacts/pilots/hu_cat_score_reconstruction.json)

### 135. hu_cat_interaction_risk

Type: main screening configuration; status: complete.

**Reason:** Use regularized OOF borrower/loan/score interaction risks to expose nonlinear population structure.

**Rationale provenance:** Original trial record; consult its recorded plan and journal for timing.

| Measurement | Recorded value |
| --- | --- |
| Recorded AUC (stage-specific) | 0.7453797 |
| Reference AUC, when recorded | 0.7518409 |
| Best screened blend AUC | 0.7517084 |
| Ledger delta versus its recorded reference | -0.0001325 |
| Average precision | 0.2339519 |
| Log loss | 0.2494574 |
| Brier score | 0.0683434 |
| Selected epochs/trees | 991.0000000 |
| Recorded call seconds | 99.3102670 |

**Outcome / interpretation:** Standalone inner AUC 0.7453797; best blend gain -0.0001325 against the complete current reference. Did not advance under the recorded promotion rule. Inner OOF risk maps prevent direct own-target encoding; their extra supervised representation can still add noise, selection bias or redundant signal already available to CatBoost. Mechanisms are hypotheses, not causal findings. Repeatedly explored selection labels cannot establish hidden-test improvement.

**Recorded recipe/settings:**

```json
{
  "name": "hu_cat_interaction_risk",
  "kind": "cat",
  "features": "signed",
  "learned": "interaction_risk",
  "params": {
    "depth": 5,
    "l2_leaf_reg": 8,
    "random_strength": 0.5
  },
  "max_iterations": 4500,
  "patience": 200,
  "hypothesis": "Use regularized OOF borrower/loan/score interaction risks to expose nonlinear population structure."
}
```

**Evidence:** [improvements/high_upside/artifacts/pilots/hu_cat_interaction_risk.json](../improvements/high_upside/artifacts/pilots/hu_cat_interaction_risk.json)
