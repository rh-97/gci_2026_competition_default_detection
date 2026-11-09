# Revised research priority: pursue substantial gains

Status: opportunity audit, after the user's November 9 priority change. The incremental
round-four search and its downstream controller have been stopped. Seven screens
completed; partial work and all evidence are retained. No new submission or
round-four validation conclusion has been produced. The current confirmed public
reference remains **0.76824**, `output/submission_round3_bagged.csv`.

The first descriptive audit is recorded in `HIGH_UPSIDE_EXPERIMENT_LOG.md` and
the new `07_signal_opportunity_audit.ipynb`. Its results favor population-wide
generalization experiments over a simple depth increase or an unsupported small
segment specialist. No new model or submission has been trained in this phase.

## Target and evidence

Reaching 0.80000 requires **+0.03176 absolute public AUC**. This is an aspiration,
not a forecast. No measured upper bound on this dataset's attainable AUC exists.
Failure of several models does not establish a ceiling; neither does choosing a
larger architecture establish that the target is achievable.

The supplied README explicitly says this competition uses a subset of the original
Home Credit datasets. Local inventory contains only train, test and sample submission
CSVs; there are 32 supplied predictors. Scores or solutions using original history
tables are not directly comparable and those rows cannot be imported. Prior audit
train-versus-test classification AUC was 0.518898: this particular classifier found
little separation, not proof of identical distributions. Broad drift weighting is
therefore a lower priority without stronger slice-specific evidence.

The existing bank is tree-dominated. The two earlier neural experiments were small
scikit-learn MLP configurations, not a comprehensive test of modern tabular neural
methods. Existing categorical/group and ratio-feature tests also do not exhaust
carefully nested supervised representations. These are research gaps, not evidence
of a likely 0.03 gain.

## Ordered plan and reasons

1. **Locate an opportunity before another broad sweep.** Review current three-seed
   OOF errors against external-score availability, loan type, amount/annuity and
   applicant profiles. Quantify which sufficiently large slices contribute most
   ranking errors; lower slice AUC alone is not a reason to fit a specialist.
   Audit source-column definitions, invalid values, rounding structure and missing
   signals. Examine near-duplicate feature profiles without recovering identities
   or external labels. Compare per-slice ranking error and uncertainty, not just
   feature importance or mean calibration. Outcome: a small hypothesis list tied
   to a measurable error pattern; drop unsupported avenues.

2. **Test learned representations that differ from another arithmetic ratio.**
   Prioritize a small number of train-only, heavily regularized interaction-risk
   encodings and neighbor/profile summaries, motivated by step 1. Every supervised
   transform must be cross-fitted within the outer training fold; validation and
   test targets never enter any fit or reference pool. Compare each block at the
   same learner/settings to isolate its contribution. CatBoost already performs
   categorical target statistics, so ordinary target encoding alone is not assumed
   novel. Missing external-score reconstruction is conditional on demonstrable
   out-of-fold predictive quality and downstream ranking gains; never fabricate
   observed scores or treat imputation as additional ground truth.

3. **Test a substantially different model family, trained from scratch.** Start
   with a compact TabM model with numerical embeddings and explicit missingness,
   using the authors' documented implementation and citations. TabM shares weights
   across multiple jointly trained predictors; this is a materially different
   experiment from the earlier two MLPs. Compare raw and successful engineered
   representations, with a small declared optimization budget. A retrieval-based
   TabR experiment is conditional on usable neighbor signal and feasible runtime,
   rather than automatically launching another expensive architecture. All learned
   weights are initialized locally and trained only on supplied training rows.
   No pretrained checkpoints, downloaded benchmark datasets or external history.

4. **Use complementary models only after they earn the cost.** If a new family
   shows meaningful common-fold standalone or ensemble gains, evaluate a genuinely
   nested learned combiner or a model-learned segment gate. Segment specialists need
   enough positive cases and consistent held-out evidence. An outer validation
   row's target must be absent from every base fit, transform, neighbor pool and
   combiner fit. Do not stack already reused OOF predictions and call that fully
   nested. Do not add seed banks before a structural improvement is demonstrated.

## Compute and decision policy

The local machine reports ARM64 and eight logical CPUs; PyTorch is not installed
in the project venv. Any required software belongs in that venv, with versions and
licenses recorded. Installing software is distinct from adding external data.
Accelerator availability and one-model memory/runtime should be checked before a
large neural run. No cloud resources, costs or data transfers are assumed authorized.

The experiment unit is a new hypothesis/representation/model family, not a list of
nearby hyperparameters. Begin with matched inexpensive pilots and learning curves;
allocate full validation only to useful evidence. Aim for **0.002 or more absolute
OOF gain** for a substantial branch. This is a budget/promotion target, not a
prediction of attainable gain. Small gains can be retained cheaply but should not
trigger hours of further tuning or larger banks under the new priority. Freeze
the exact metric rules and full combination grid before new confirmation fits.

Use the current complete three-seed reference and matching row/fold groups. Fresh
partitions test robustness on previously explored labels; no retrospective split
can be presented as an untouched test. Require direction and slice/fold consistency,
report uncertainty and distinguish selection from confirmation. Public scores
measure final candidates; they do not select dozens of configurations.

Before fitting, record exact pilot specs, fold membership, compute limits, early
stopping and promotion criteria in a new notebook and machine-readable plan. Keep
every existing notebook and submission unchanged. Continue the why/how/negative
result journal, local-venv execution and saved-model reproduction requirements.

## Leaderboard context supplied by the user

The user reports that the top ten have displayed scores of 1 and the top twenty
are above 0.8. The user is uncertain whether external data was used. This is
user-reported leaderboard context, not independently verified score provenance.
It makes 0.8+ a relevant competitive target, but does not establish that those
scores are achievable using only the allowed columns and labels. No inference
of misconduct is made. Public-subset ranking is distinct from full/private-test
performance. These observations do not change the data restrictions, validation
rules or model-selection weights.

## Method references (code/methods only; no datasets or weights fetched)

- [Official TabM implementation and training guidance](https://github.com/yandex-research/tabm).
- [Official TabR implementation](https://github.com/yandex-research/tabular-dl-tabr).

These references establish how the candidate architectures work, not that either
will outperform the current bank on this competition.
