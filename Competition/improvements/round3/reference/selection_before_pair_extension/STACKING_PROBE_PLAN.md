# Learned-combination feasibility probe

This is a low-cost screen before committing to a much larger, fully nested
stacking run. It does not add a new recipe directly to the finalist pool.

Use only the previous three families' primary development OOF predictions.
Test logistic regression on their clipped logits at C=0.1 and C=1.0. Separately,
test C=0.1 with those logits plus coarse external-score missing count, contract
type and age band. Categorical vocabularies fit only the meta-training rows;
rare categories receive regularization, not manual corrections. No test data.

Evaluate meta-model predictions by five-fold cross-fitting (seed SEED+701).
Record AUC, log loss, coefficients and coarse blends with the current recipe.
The meta-validation rows are not used to fit their own meta-model, but the
precomputed base OOF models can indirectly use other meta-validation targets.
Thus this is NOT fully nested validation and cannot justify a submission.

Only if the best cross-fitted probe gains >=0.00020 over the complete current
primary recipe should a separate, prospectively planned fully nested comparison
be undertaken. Otherwise record the negative/weak probe and do not spend dozens
of extra base fits to pursue it. Do not transfer learned coefficients directly
into a submission based only on this approximation.
