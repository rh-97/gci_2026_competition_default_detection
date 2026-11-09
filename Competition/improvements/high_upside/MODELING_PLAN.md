# Higher-upside model pilots and submission gates

Recorded before fitting these candidates. The user has authorized continuing
through training, validation and a submission decision. The prior incremental
round-four controller stays stopped. Current reference is the public-confirmed
round-three bagged CSV (0.76824). No external rows or pretrained weights.

## Six structural pilots

Four scratch TabM recipes: raw inputs with piecewise-linear numerical embeddings;
the successful signed 55-column frame with the same recipe; that frame with
periodic numerical embeddings; and a more regularized full TabM recipe. The first
three use the efficient mini architecture. Common settings: 16 internal members,
128 hidden units, two blocks, eight-dimensional embeddings, AdamW, batch 1,024,
cosine learning-rate schedule, up to 140 epochs, 20-epoch AUC patience. Regularized
recipe uses 180 epochs, learning rate .001 versus .002, dropout .25 versus .10,
and weight decay .003 versus .0003. These are combined recipes; that comparison
does not identify a single parameter effect. Numerical medians/quantile transforms,
category vocabularies, nonconstant column selection and embedding bins fit training
rows only. Explicit numerical missing flags are included. Unknown categories get
a reserved category. Each member's BCE is optimized independently; inference
averages probabilities, as the authors specify.

Two CatBoost pilots hold the successful family settings (depth5, l2=8,
random_strength=.5, learning_rate=.045, max4,500 trees, patience200) fixed:

1. Add three fold-safe reconstructed external scores and observed-score residuals.
   Auxiliary LightGBM regressors use only supplied feature columns, exclude their
   predicted score column and TARGET/ID, and train on observed auxiliary targets.
   Training-row reconstructions are three-fold OOF; validation/test reconstructions
   use regressors fitted only on the outer training rows. Missingness is retained.
   Save auxiliary OOF R2 on observed rows; positive auxiliary R2 is not sufficient
   for acceptance and may not transfer to truly missing cases.
2. Add smoothed cross-fitted risk encodings for predeclared borrower/loan/score
   interactions. Five inner folds generate training encodings; full outer-train
   maps encode validation/test. Two prior strengths (30,100) and support/frequency
   features are a block, not individually selected. Outer validation labels are
   absent from every map and every fit. Cut edges fit only outer training inputs.

Exact specs are written to `artifacts/model_candidate_plan.json` before fitting.
No source edits to the fitting core while any fit process is running. Include
actual source/data/split/package hashes in cache identities. Neural processes use
one OpenMP library via DYLD_LIBRARY_PATH on this Mac; do not suppress duplicate
runtime detection with KMP_DUPLICATE_LIB_OK. Hardware currently exposes CPU only.
Save learning curves, timings, seeds, versions, failures and full predictions.

## Compute allocation and progression

Use the original repeatedly explored inner split to screen all six. Limit each
neural pilot to 25 minutes; stop at the best completed epoch if reached and label
the truncation. This is not a negative claim about an unconverged model. Run neural
models sequentially with four CPU threads. Fit no more than two finalists in
primary common-five-fold development CV: best neural and best learned-feature
CatBoost, each needing >=0.00030 screened blend gain over the entire reference.
Probe new-family weights .10,.25,.50,.75,1.00. If a neural model is truncated before
15 epochs without a useful gain, do not expand it. No random broad sweep.

For the finalists, compare on the original primary five folds (SEED+2). Search a
complete primary-only grid: reference/new and new/new pairs with weights
.10,.25,1/3,.50,2/3,.75,.90; and reference plus both helpers with reference weights
.25,.50,.75 and relative helper shares .25,.50,.75. Probability and log-odds means
only. Freeze the complete winner and fixed median epochs/iterations before any
confirmation. At most two new families.

The ambition for a substantial branch is >=0.002 OOF gain; a smaller robust gain
can still justify a candidate, but will not trigger a bigger sweep or seed bank.
Require >=0.00030 primary gain for submission eligibility. Confirmation uses
SEED+3101 (not any earlier confirmation seed), fixed counts, no validation early
stopping, frozen weights/method, positive pooled gain and >=4/5 positive groups.
Fit matching new-family OOF on the two other existing development seeds
(SEED+301,SEED+1101). Average each family before the frozen blend; require >=0.00030
gain over the complete three-seed reference plus >=4/5 positive primary groups.
These are explored development labels; new partitions are robustness checks,
not an untouched test. Public feedback does not select weights.

If no pilot reaches promotion, complete the negative-result journal and retain
the existing submission; do not create a deceptively relabeled CSV. If a family
fails a later gate, retain its evidence and stop its deployment branch.

## Submission and delivery

A passing recipe reuses the original bank and trains only needed new families on
three full-data five-fold seeds (SEED+3,+302,+602), frozen lengths, with no use of
held-out labels for stopping. Write `output/submission_high_upside.csv`; preserve
all previous CSVs. Reproduce from saved models byte-for-byte, check all61,500 IDs,
schema, finiteness and score range. Full-data OOF is diagnostic and does not retune.
Document the exact score provenance and avoid claiming 0.8 without an actual
submitted score. Create new notebooks only; execute them with the local venv.
Update the report/journal and create a new verified reproduction archive if a new
submission is accepted. Even a failed branch gets executed result documentation.

## References

Methods/code only: https://github.com/yandex-research/tabm and its documented
numerical-embedding dependency. Installed package licenses/versions are recorded.
No repository datasets, pretrained models, original Home Credit tables or labels
are imported. These method references do not predict a gain on this competition.
