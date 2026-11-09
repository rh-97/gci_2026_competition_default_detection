# Third-pass plan, recorded before fitting

The current reference is the complete round-two recipe, not the weaker first-pass
model. The user reports public AUC 0.76756, rank 568. Attribution to
`submission_round2.csv` follows the conversation; the screenshot itself does not
identify a file. Public feedback will not select parameters or ensemble weights.

## Questions and priority

1. Does tuning the successful 51-column loan-proxy representation improve it?
   Test depth, learning rate, shrinkage, split policy, numeric resolution, class
   weighting, missing policy and training-fold group aggregates. Earlier tuning
   mostly preceded this representation.
2. Can a few explicit changes to that representation improve it? Isolate signed
   term distances/coarse categories, additional hypothetical rate transforms,
   categorical interactions, and the larger original feature set. These are
   redundant representations of supplied values, not recovered financial facts.
3. Does a different learner add complementary errors? Test the same compact
   representation in LightGBM, XGBoost and a small neural network trained from
   scratch. Preprocessing and all aggregates fit only the training fold.
4. Can probability, log-odds or training-reference percentile blending improve
   the current recipe? Test using stored OOF predictions before considering any
   learned stacker. A stacking experiment must hold out meta-fitting rows and
   acknowledge that ordinary precomputed OOF features are not fully nested.

## Evaluation rules

- Reuse the original inner split only for inexpensive screening. It is heavily
  explored, so its result is not independent evidence.
- Initially screen the explicit configurations in `candidate_plan.json`.
  Record hypotheses, exact settings, runtime, convergence and all failures.
- Promote at most four new models: up to two best CatBoost screens, the best
  other tree model, and the neural network, only when a coarse blend with the
  complete current reference improves inner AUC by at least 0.00010. Promotions
  may include a weaker individual model if it provides ensemble improvement.
- Compare promoted models with the frozen round-two recipe on its original
  five development folds. Explore a small, recorded blend grid only here.
  Compare methods with the same base model bank; do not confuse seed averaging
  with a feature improvement. Require primary OOF gain >= 0.00020.
- Freeze one winning recipe, weights, iteration counts, inference transform and
  implementation hashes before confirmation. Use a new fold seed with fixed
  iteration counts for candidate and reference. Do not tune on this result.
  Require positive pooled gain and positive gains in at least four of five
  confirmation folds. This changes the partition, not the available labels;
  it is a robustness check, not an untouched test.
- For two-seed final bagging, obtain matching secondary-development OOF for each
  accepted new family. Require averaged-candidate AUC to exceed the complete
  current two-seed recipe by >= 0.00020. Do not drop the current bank's second
  seed merely to make an easier comparison. A failed gate retains round two.
- Fit any accepted final recipe at training lengths frozen from development.
  Full-data OOF remains diagnostic and will not retune selection.

## Follow-ups and stopping

Follow up clear component or parameter improvements with matched controls and
write an amendment before any additional fit. If a phase produces no repeatable
gain, move to the next distinct hypothesis. Record the remaining untested ideas,
practical costs and uncertainty. Do not claim a global optimum or that every
possible method has been exhausted.

Existing notebooks and previous-pass source/model artifacts are immutable.
Only new notebooks will be created, using the project `.venv`. No online data,
pretrained weights, recovered test labels or pseudo-labels will be introduced.

## Deliverables

New executed notebook(s), complete third-pass experiment journal and machine
ledger, updated main report, verified reproduction archive, and either a
locally justified new CSV or an explicit recommendation to retain round two.
