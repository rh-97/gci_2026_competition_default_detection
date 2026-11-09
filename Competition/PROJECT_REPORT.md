# Competition project report

The latest generated file is [submission_high_upside.csv](output/submission_high_upside.csv).
It combines the previous ensemble, a TabM neural model trained from scratch, and
a CatBoost model with learned external-score reconstruction features. Matched
three-seed development AUC rose from **0.76480 to
0.76626** (**+0.00146**). All five group
comparisons improved. Saved-model inference reproduced the CSV byte for byte.

The user's latest screenshot shows **0.77029 public AUC**, rank
snapshot **364**, versus the earlier explicitly attributed
0.76824. The screenshot does not identify the uploaded filename; attribution to
the latest file is likely from context, but **not explicitly confirmed**. A public
subset result and local cross-validation are different evaluations. No private
score is known. The 0.8 goal remains an aspiration, not an achieved result or an
estimated data ceiling.

This report consolidates the work. The [complete catalog](docs/EXPERIMENT_CATALOG.md)
contains every recorded competitive configuration and auxiliary meta probe, with
settings, reasons, metrics, decisions and evidence links. The original journals
retain the longer operational history. No additional models were trained during
repository cleanup.

## 1. Competition and permitted inputs

The supplied competition is the GCI Home Credit Default Risk task. Predict the
probability of `TARGET=1` for each test applicant. The evaluation metric is ROC
AUC, so ranking defaults above non-defaults is the primary objective. Log loss,
average precision and Brier score were retained as secondary diagnostics.

Only `input/train.csv` and `input/test.csv` supply modeling data. The sample
submission defines the output schema; the column-description workbook supports
interpretation. The original Home Credit historical tables, recovered test
labels, outside rows, hand-assigned predictions and pretrained weights were not
used. Method implementations and software packages are distinct from additional
training data; their provenance is recorded in
[SOURCE_ATTRIBUTION.md](improvements/high_upside/SOURCE_ATTRIBUTION.md).

| Dataset property | Finding |
| --- | --- |
| Training rows / columns | 171,202 / 34, including ID and target |
| Test rows / columns | 61,500 / 33, including ID |
| Supplied predictors | 32: 24 numeric and 8 categorical in the loaded data |
| Default cases / prevalence | 13,821 / 8.0729% |
| Repeated IDs within train or test | None |
| Train/test ID overlap | None |
| Exact duplicate training predictor profiles | None |
| Largest missingness | EXT_SOURCE_1 69.47%; OWN_CAR_AGE 66.00%; EXT_SOURCE_3 31.88% |
| DAYS_EMPLOYED sentinel 365243 | 30,898 training rows; 10,565 test rows |

The employment sentinel is not a plausible duration. It was converted to missing;
engineered representations retain a sentinel flag. Missing data were not handled
by deleting the many affected applicants. The external scores and their missing
patterns carry useful signal, so observed scores were retained and missingness
was represented explicitly where appropriate. No synthetic default labels or
resampled rows were added.

An adversarial train-versus-test classifier achieved AUC **0.518898**. That model
found limited separation; it does not prove identical distributions. Broad drift
weighting was therefore a lower priority. The supplied subset and unknown
methods behind other leaderboard entries do not establish attainable performance
under these data restrictions.

## 2. Data processing and feature experiments

All representations remove `SK_ID_CURR` and `TARGET` before fitting. ID remains
only for output alignment and integrity checks. Zero denominators become missing,
and infinite derived values are replaced by missing. Categorical vocabularies,
medians, aggregate maps, quantile transforms, bins and learned encoders fit only
their permitted training rows.

| Representation / operation | Why it was tested | Result and retained use |
| --- | --- | --- |
| Raw 32 predictors | Establish the value of the supplied columns before engineering | LightGBM inner AUC 0.7367838; useful control, weaker than engineered inputs |
| Numeric and categorical missing handling | Preserve applicants and information about unavailable fields | Missing categories get a token; CatBoost sentinel/native/median alternatives were compared; a native-missing proxy family survived validation |
| Affordability ratios and household features | Express payment burden, credit versus goods price, income per person/adult and family composition | Broad engineered LightGBM reached 0.7440631 inner AUC; selected features enter the lean frame |
| Age/employment timing and ratios | Compare employment and other durations relative to applicant age | Retained in the lean representation when validated; they are descriptive transformations, not reconstructed histories |
| External-score aggregates and interactions | Combine observed scores, disagreement and availability | Means/min/max/std/count and selected interactions contributed to the successful feature frames |
| Broad extended/categorical/group blocks | Test logs, category crosses and group-relative summaries | Mixed/negative results; extended LightGBM 0.7375499 was below the engineered control; more columns were not automatically retained |
| Lean frame, 46 columns | Reduce redundant or noisy derived features while preserving important raw information | Successful CatBoost representation; inner AUC 0.7484926 versus raw CatBoost 0.7416556 |
| Hypothetical payment-rate transforms and term distances, 51-column proxy frame | Expose nonlinear loan/payment structure | Proxy CatBoost inner AUC 0.7499521; survived common-fold validation and remained in the reference ensemble |
| Signed term residuals and rounded term categories, 55 columns | Preserve which side of a term boundary an applicant falls on | Joint signed representation reached 0.7509073 inner AUC and survived validation; separate ablations were less useful |
| Importance-based top-25/40/55/70 subsets | Test whether feature removal improves generalization | Did not replace the stronger final full-frame recipe; top-25 inner AUC was 0.7381651 |
| Fold-safe external-score reconstruction, 61 columns | Learn additional representations from supplied auxiliary score targets | Adds three predictions and three observed-minus-predicted residuals; positive downstream ensemble evidence, retained |
| Cross-fitted interaction-risk encodings | Learn regularized borrower/loan group risks | Latest screened blend gain -0.0001325; rejected |

The hypothetical payment-rate columns are mathematical proxies under assumed
period counts, not verified contractual interest rates. Likewise, reconstructed
external scores are learned features, not recovered truth. Their residuals use
observed values only; genuinely missing values remain missing.

The initial engineered blocks also included bureau-request totals, contact-flag
counts, an education-rank mapping, amount logarithms, categorical crosses,
age/employment bins, external-score products/differences and score-by-age/term
interactions. Second-pass blocks tested score logits, geometric/harmonic/weighted
means, conservative-score summaries, missing-pattern categories, organization
families and income/credit amounts per adult. Not all of these survived feature
selection. Exact formulas and retained column lists are preserved in the
[first-pass feature builder](improvements/experiment.py),
[second-pass builder](improvements/round2/round2.py),
[third-pass builder](improvements/round3/round3.py), and
[learned-feature builder](improvements/high_upside/h_features.py).

For reconstruction, each of the three external-score regressors excludes its own
score column and uses the raw supplied feature frame. Three inner folds produce
training-row predictions; teachers fitted on the outer training rows predict
validation/test rows. LightGBM teachers use 300 trees, learning rate 0.04,
15 leaves, minimum child count 100 and L2 regularization 20. Pilot auxiliary OOF
R2 was approximately **0.4828 / 0.2356 / 0.1157** for scores 1/2/3. These values
describe observed-score reconstruction, not performance on genuinely missing
scores or default ranking. Downstream validation justified deployment.

The rejected risk block used five inner folds, eight predeclared interactions,
prior strengths 30 and 100, support/frequency information, and outer-training
maps for validation/test. Cross-fitting controls direct own-label leakage; it
does not guarantee useful extra signal or eliminate model-selection bias.

## 3. Validation and leakage controls

The original frozen split contains **136,961 development** and **34,241 audit**
rows. The development screen uses **102,720 inner-fit** and **34,241 inner-valid**
rows. Promising models were compared using common stratified five-fold splits.
The split arrays remain in [splits.npz](improvements/artifacts/splits.npz).

The first-pass audit AUC improved from **0.6665727** for the baseline to
**0.7555056** for the improved recipe. That audit was subsequently inspected and
is no longer an untouched test. Fresh fold partitions in later rounds are
robustness checks on explored development labels, not independent new labels.

Screening and primary CV may select epochs/trees. Before confirmation, the latest
family choices, probability-blend weights and median training counts were frozen.
Confirmation and final models use those counts without validation early stopping.
Final full-data OOF scores are diagnostic after model selection. Public feedback
was recorded after delivery and did not select the frozen blend weights.

Latest deployment gates:

1. Complete six structural pilots; advance at most one neural and one learned-feature
   family with at least 0.00030 screened blend gain.
2. Compare finalists on common development folds and the declared blend grid.
3. Freeze the recipe before fixed-count confirmation; require positive pooled gain
   and at least four positive fold groups out of five.
4. Match the reference's three-seed averaging; require at least 0.00030 gain and
   at least four positive groups. Both later checks improved all five groups.
5. Train only the chosen families on three full-data five-fold seeds; verify ID
   order, schema, finite probabilities in [0,1], source hashes and saved-model replay.

The budget amendment also required at least 0.00030 primary incremental gain to
justify a second new family. The actual second-family contribution was
**0.0003962**, so the unconstrained winner already
passed this cost criterion. The GPU and budget amendments, timing and earlier
CPU evidence remain documented rather than treated as pre-existing choices.

## 4. Model progression and decisions

The first rounds tested Random Forest, LightGBM, CatBoost, XGBoost, logistic
regression, spline/logistic models, histogram boosting and small MLPs, along with
feature sets, regularization, missing-value methods, class weights and blends.
The complete catalog separates individual model AUC from ensemble contribution.

**First pass.** Engineered/tuned LightGBM and lean CatBoost formed the selected
two-family ensemble. The tuned LightGBM pilot reached 0.7471511 inner AUC versus
0.7440631 for the untuned engineered control. CatBoost supplied stronger ranking
and complementary errors. The selected development OOF mixture reached 0.7617724.
Logistic/spline and histogram models were weaker; XGBoost and later linear-tree
variants did not earn a final place. Class-weight variants were tested but did
not displace the selected unweighted ranking models.

**Second pass.** Finance/proxy features and native-missing variants were evaluated
against matched CatBoost controls. Two retained CatBoost families were combined
with LightGBM at weights **0.5625 / 0.25 / 0.1875**, respectively. Two-seed averaging
reduced partition/initialization variation. Control experiments distinguished
longer training budgets from actual feature improvements.

**Third pass.** Signed loan-term structure and a selected 512-border CatBoost
variant added useful complementary ranking. The reference mixture ultimately
contained LightGBM, proxy CatBoost, native-missing proxy CatBoost, feature-selected
512-border CatBoost and signed-feature CatBoost. Their expanded weights were
**0.09375 / 0.28125 / 0.125 / 0.25 / 0.25**. Three seeds and five folds produced
75 primary saved models. The best public-confirmed older file is
`submission_round3_bagged.csv`, AUC **0.76824**.

Two small MLPs scored approximately 0.72718 and 0.73456 on the inner split and
were not adopted. An inexpensive learned-logit stacking probe over the older
families added only **0.00000249** at its best screened blend, below the 0.00020
threshold for an expensive nested run. Its base OOF features were not fully nested;
it was feasibility evidence, not deployable validation. Neither result rules out
modern tabular neural methods or nested combinations of the newer families.

**Stopped round four.** Seven incremental CatBoost screens finished before the
user changed priority toward larger gains. The strongest recorded blend increment
was about 0.0002437, below the substantial-branch target. The run was stopped;
it produced no submission and no completed downstream validation conclusion.

**Opportunity audit.** A saved single-model training sample AUC of 0.8141 versus
held-out 0.7652 showed a generalization gap, not evidence that test AUC 0.8 was
attainable. Missing-score slices with lower AUC did not disproportionately dominate
global ranking error. This favored population-wide model/representation changes
over unsupported manual adjustments or narrow specialists.

**Latest structural pass.** Four scratch TabM recipes and two learned-feature
CatBoost recipes were screened:

| Pilot | Standalone inner AUC | Best screened blend gain | Decision |
| --- | --- | --- | --- |
| hu_tabm_raw_piecewise | 0.7401112 | +0.0002394 | Not advanced |
| hu_tabm_signed_piecewise | 0.7508052 | +0.0015386 | Advanced |
| hu_tabm_signed_periodic | 0.7481982 | +0.0009184 | Not advanced |
| hu_tabm_regularized | 0.7501469 | +0.0009786 | Not advanced |
| hu_cat_score_reconstruction | 0.7507566 | +0.0003659 | Advanced |
| hu_cat_interaction_risk | 0.7453797 | -0.0001325 | Not advanced |

Signed-input TabM with piecewise embeddings was the best neural addition. Its
standalone primary CV AUC was only about 0.7606962, but its ranking errors were
usefully complementary to the tree ensemble. Periodic embeddings and stronger
full-TabM regularization did not beat its screened contribution. This does not
isolate individual hyperparameter effects because some recipes changed several
settings jointly.

The selected neural recipe uses TabM-mini, 16 shared internal members, two blocks,
width 128, eight-dimensional piecewise embeddings with up to 48 bins, dropout 0.1,
AdamW at learning rate 0.002 and weight decay 0.0003, batch size 1,024, gradient
clipping and a cosine learning-rate schedule. Fold-trained preprocessing includes
medians, missing flags, constant-column removal, normal quantiles and reserved
unknown categories. Member BCE losses are averaged; inference averages member
probabilities. Primary best epochs [29,32,40,40,41] fixed later training at **40**.

The selected reconstruction CatBoost uses depth 5, learning rate 0.045, L2 leaf
regularization 8 and random strength 0.5. Primary selected tree counts
[1166,848,1150,1537,1085] fixed later fits at **1,150 trees**. Exact library-resolved
parameters and neural structures are retained in
[model_resolved_settings.json](improvements/high_upside/artifacts/model_resolved_settings.json).

## 5. Results: keep the evaluation sources separate

| Latest local comparison | Reference AUC | Candidate AUC | Gain |
| --- | --- | --- | --- |
| Primary CV; selected on these predictions | 0.7637229 | 0.7654305 | +0.0017076 |
| New partition; frozen counts and weights | 0.7627263 | 0.7642284 | +0.0015020 |
| Matching three-seed development averaging | 0.7648035 | 0.7662609 | +0.0014575 |

The three-seed comparison also improved average precision **0.2500740 to 0.2520907**,
log loss **0.2441755 to 0.2437166**, and Brier score **0.0674623 to 0.0673702**.
The 400-replicate paired row-bootstrap interval for its AUC gain was approximately
[0.0009880, 0.0020329]. It conditions on already fitted predictions, omits fitting
and search uncertainty, and is not a search-adjusted significance test.

| Delivered stage | Full-data OOF AUC, diagnostic | Public observation | Attribution |
| --- | --- | --- | --- |
| First improved ensemble | 0.7620608 | 0.76540 | Explicitly confirmed |
| Round two, two-seed mixture | 0.7644305 | 0.76756 | Filename inferred from conversation |
| Round three, three-seed bagged | 0.7650709 | 0.76824 | Explicitly confirmed |
| Latest structural candidate | 0.7667143 | 0.77029, rank 364 | Screenshot confirmed; filename not explicit |

The public observations indicate progress, but public/full-test behavior and the
marginal effects of individual changes are not established by this table. No
comparison here proves a global optimum. Reaching 0.8 from 0.77029 requires another
**0.02971** absolute public AUC, for which no tested recipe currently provides
support. Retrieval/profile learning and genuinely nested combination of the new
families remain untested directions; they are not promised improvements.

## 6. Final recipe, implementation and reproduction

The frozen probability blend is **25% older three-seed ensemble + 37.5% signed
TabM + 37.5% reconstruction CatBoost**. Each new family has 15 saved fold bundles
(three seeds × five folds). There are 75 legacy primary models, 30 new primary
bundles, and 45 auxiliary regressors inside the reconstruction bundles. The
240 neural internal members share parameters and are not 240 separate saved models.

The first three neural pilots ran on CPU. A local hardware check then exposed MPS
outside the sandbox, with roughly threefold representative-batch speedup. After
stopping workers, a prospective amendment introduced a separately hashed MPS
implementation before primary CV. Original CPU pilot signatures and checkpoints
remain preserved and explicitly reused; GPU retraining is not promised bit-identical.
All retained inference uses CPU. Package versions were pinned in the project venv.
A duplicate OpenMP-runtime import issue was resolved by selecting the venv torch
library before launching, without disabling duplicate-runtime checks.

No frozen fitter, feature builder, selection rule or saved model was rewritten
during cleanup. Earlier encoders/modules are still required by Python pickles and
the feature/import chain. They retain their original paths. One-time background
dispatch helpers were removed after their completed results had been preserved;
sequential phase commands remain available.

Candidate SHA-256: `15d050aa8709ae4e2d338b013c03216d4b3f3279348a3faca71080c17e44baed`.

Run from the repository root with the existing local venv:

```sh
Competition/.venv/bin/python Competition/project.py status
Competition/.venv/bin/python Competition/project.py verify
Competition/.venv/bin/python Competition/project.py reproduce
Competition/.venv/bin/python Competition/project.py report
```

`reproduce` loads saved models and recreates the 61,500-row candidate. It does not
train. `report` rebuilds this report and the complete catalog from saved evidence;
it does not edit notebooks. The original detailed commands and dependency setup
remain in [REPRODUCTION_README.md](REPRODUCTION_README.md). The previously delivered
[reproduction ZIP](output/competition_high_upside_reproduction.zip) remains unchanged
as a historical, hash/CRC-checked package; it predates the cleanup and public-result
addendum. Git records the current organization and documentation.

## 7. Repository cleanup and recovery

The pre-cleanup snapshot branch is **`snapshot/pre-cleanup-2026-11-09`**, commit
`b8d094cc94496a74ec38fc66e69319348b9a4924`. It contains 1,674 tracked files, including supplied
data, trained weights, notebooks, predictions and existing ZIPs. The pre-existing
ignore rules excluded the local venv and Python caches. Automated local commits
use the identity `Codex <codex@localhost>`; no global Git identity was changed.
No remote was configured and nothing was pushed.

Cleanup is on **`cleanup/project-organization`**. It removed **71
files / 2,023,838 bytes** from the working tree: regenerated
runtime files and five completed background orchestration scripts. Of those,
**16** were in the snapshot; the rest were ignored
Python cache files. These are organizational savings, not a claim of reducing
Git's historical storage: the snapshot deliberately keeps tracked recovery copies.
The 2 GB venv remains installed and ignored. Data, every existing notebook, trained
models, predictions, evidence logs and reproduction ZIPs were retained.

The cleanup checks passed, including exact saved-model replay and comparison of retained snapshot files. See [cleanup_validation.json](docs/cleanup_validation.json). Byte comparisons confirmed 15 existing notebook files, 198 model/encoder files, 3 input files and 14 outputs unchanged; 1655 retained snapshot files matched overall.

The [cleanup report](docs/CLEANUP_REPORT.md) and
[per-file manifest](docs/cleanup_manifest.json) give reasons and recovery details.
The new root README and `project.py` identify the current commands so that completed
experimental runners are not mistaken for required prediction steps.

## 8. Complete evidence index

| Ledger group | Record type | Count |
| --- | --- | --- |
| previous passes | main screening configuration | 91 |
| third pass | main screening configuration | 28 |
| third pass | auxiliary meta-learning probe | 3 |
| round4 | main screening configuration | 7 |
| higher_upside | main screening configuration | 6 |

- [Every trial, rationale, recipe and outcome](docs/EXPERIMENT_CATALOG.md).
- [First/second-pass journal](EXPERIMENT_LOG.md), [third-pass journal](ROUND3_EXPERIMENT_LOG.md),
  [stopped fourth-pass journal](ROUND4_EXPERIMENT_LOG.md),
  [structural-model journal and post-delivery observation](HIGH_UPSIDE_EXPERIMENT_LOG.md).
- [Detailed latest improvement report](IMPROVEMENT_REPORT.md),
  [recorded strategy](HIGH_UPSIDE_PLAN.md),
  [exact modeling rules](improvements/high_upside/MODELING_PLAN.md).
- [Executed latest results notebook](09_high_upside_results_reproduction.ipynb).
  All supplied and earlier notebooks remain unchanged.
- [Current model manifest](improvements/high_upside/artifacts/model_manifest.json),
  [exact replay record](improvements/high_upside/artifacts/model_reproduction.json),
  [integrity checks](improvements/high_upside/artifacts/model_verification.json),
  [leaderboard observation and attribution](improvements/high_upside/artifacts/model_public_leaderboard_observation.json).

Mechanisms described above explain why a feature or model was plausible; they
are not causal findings. Each retained change earned its place through the
recorded validation comparisons. Negative results apply to their tested settings,
not every possible version of that idea.
