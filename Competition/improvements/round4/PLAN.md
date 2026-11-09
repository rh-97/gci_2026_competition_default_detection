# Round four: recorded plan and acceptance rules

The frozen reference is `output/submission_round3_bagged.csv`, SHA-256
`7d933ea1e9bffea4e3bf034a81a8ece315655dcebdeb9408682d159d60bbfb02`.
The user explicitly confirmed its public AUC **0.76824**, rank snapshot **518**.
Public feedback will not tune this pass. Private/full-test performance is unknown.
All nine existing notebooks, prior source, model banks, submissions and input
CSVs are protected by `reference/preserved_hashes.json`. Use only the supplied
rows and project `.venv`. No online data, pretrained weights or hand labeling.

## Stage A: retune the successful 55-column representation

Earlier broad tuning used 51 columns. The later successful joint signed-term /
rounded-category representation was primarily evaluated at depth 5 and two
quantization resolutions. Test the following on that exact 55-column frame:

- Exact default and 512-border controls, reproducing both previous screens.
- Depth 4, 6, 7 with the baseline shrinkage held fixed (unlike some older tests).
- Leaf shrinkage 2, 24, 64; learning rate 0.025 and 0.075.
- Random-strength 0 and 2; numeric borders 128 and 1024.
- Column sampling, restricted categorical interactions, native missing bins,
  training-fold group aggregates, broader one-hot treatment, asymmetric growth.
- Two LightGBM recipes and one XGBoost recipe on the same 55 columns.

This is **23 initial parameter/model configurations**, including two controls.
Exact settings, rationale, stopping budgets and seeds are written to
`artifacts/candidate_plan.json` before any fitting. No core source edits while a
fit process is alive: capture its actual source hash at import and assert it
still matches before/after fitting. Cache keys also include dependency/data and
package identities. This avoids the previous source-line introspection error.

## Stage B: small, separate loan-representation ablations

Six baseline-parameter CatBoost screens add: 3-unit term structure; 24-unit term
structure; both; goods-price/annuity ratio alone; that ratio with signed/rounded
structure; and their combination. These are redundant row-local transforms of
provided values, NOT recovered schedules, principal balances or interest rates.
Do not fit any preprocessing statistics on test or validation rows.

Follow up at most three combinations, with exact specs recorded before their
fits: combine the best eligible feature block with the best parameter recipe;
combine independently positive depth/shrinkage settings; or combine a positive
native-missing policy with the best eligible feature block. A component must
beat the control individually by 0.00020 or improve its screened blend with the
complete current reference by 0.00015, as specified by the follow-up generator.
If there is no eligible evidence, do not invent a combination to fill the quota.

## Screening and promotion

Use only the original inner development split. It is repeatedly explored and
does not provide independent confirmation. The screening reference is the exact
round-three *recipe* fitted on that split, not its lead model. This is a
single-screen proxy; it does not represent all 75 final fold models.

Probe helper weights 0.10, 0.25, 0.50, 0.75 and 1.00. Promote at most four:
the best parameter CatBoost and best feature CatBoost with blend gain >=0.00010,
then the best remaining CatBoost and best other-family model with gain >=0.00015.
Do not promote the exact controls as new configurations. Use shared original
five-fold development splits; save full predictions, learning curves, metrics,
resolved parameters and timing. Record every negative result and failure.

## Stage C: training fraction, with a budget control

Start with only the fixed round-three `r3_cat_signed` family, its original
parameters and frozen 1,312 trees. This isolates the proposed data-use change
from parameter search. Construct ten folds by stratifying each of the original
five validation groups into two. The ten-fold models train on about 90% rather
than 80% of development rows; every row's own label stays excluded. Pair the
model random seed within each five-fold parent group; no validation early stop.

First compare against a five-fold, fixed-iteration control on the same parent
groups. Continue only if the ten-fold family gains >=0.00020 and inserting it
into the frozen primary recipe gains >=0.00010 over the corresponding control.
Then fit a second random-seed model on each five-fold training group. Compare
its two-model OOF average (10 final models) with the ten-fold OOF (also 10 final
models). Promotion additionally requires >=0.00010 recipe gain and positive
gains in at least four of the five parent row groups.

The budget control has two OOF predictions per row versus one for ten folds,
which favors variance reduction in the control. This is a conservative
end-to-end comparison, not a perfectly isolated causal estimate of row count.
Report both comparisons and the final inference/training cost explicitly.
If the feasibility gate fails, record it and stop that branch.

If promoted, include the ten-fold family as one candidate in the primary pool.
If it enters the final frozen recipe, repeat its ten-fold OOF on both remaining
development seeds. At each seed obtain the second five-fold random-seed control
(reuse existing fixed-iteration first controls where exact signatures match).
The ten-fold three-seed family and six-repeat five-fold control each imply 30
final models. Require the ten-fold recipe to beat this model-count control by
>=0.00010 and to beat the original reference by >=0.00020 before deploying it.

## Complete primary grid, freeze, and confirmation

The pool includes all five reference families, the complete reference as an
atomic predictor, promoted new models, and any promoted ten-fold candidate.
Evaluate direct old/new and new/new pairs at weights 0.10, 0.25, 1/3, 0.50, 2/3,
0.75, 0.90 with probability, log-odds and frozen-prediction-percentile averaging.
Also evaluate the reference plus two helpers with reference weight 0.25, 0.50,
0.75 and helper shares 0.25, 0.50, 0.75. Permit at most two positive-weight new
families. No continuous optimizer or later weight search.

Require primary OOF gain >=0.00020. Freeze the complete winning recipe, CDFs,
iteration counts, core/controller source and all plans before any confirmation
fit. Confirmation uses new fold seed SEED+2101, fixed iteration counts, frozen
weights, positive pooled gain and at least four positive parent groups out of
five. Never revise a grid or weights after viewing this confirmation.

Then obtain matching OOF for accepted new families on the two other existing
development seeds (SEED+301 and SEED+1101). Average each family over three seeds
before the frozen transform. Require >=0.00020 gain over the complete public-
scored round-three three-seed reference, plus four positive primary row groups.
The new seed is a partition robustness check on already explored labels, not an
untouched independent test. The historical audit is not used as a fresh test.

## Final bank, documentation and stopping

Only a recipe passing every applicable gate gets a new submission. Otherwise
retain the 0.76824 file. Reuse the prior 75-instance bank where needed; fit new
families on three full-data fold seeds (SEED+3, +302, +602), with the frozen
development training lengths and five or nested-ten folds as selected.
Full-data OOF is diagnostic and will not retune the chosen policy. No fourth
seed-bank expansion or public-score-driven adjustments in this pass.

Create only new notebooks 07 and 08. Execute them with the local venv, inspect
their plots, verify all protected hashes and submission/schema/order invariants,
and reproduce the recommended CSV byte-for-byte from saved models. Produce the
complete journal, combined machine ledger, updated report and checked code/model
ZIP. Keep data and venv outside the archive. Record what remains untested and why
the pass stopped; never claim every possible improvement has been exhausted.
