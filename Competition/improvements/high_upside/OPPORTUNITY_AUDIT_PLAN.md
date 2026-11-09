# Opportunity audit, before new model fitting

Reference: the frozen three-seed round-three development OOF predictions, aligned
to the unchanged development rows. The same labels have been explored before;
these are descriptive hypothesis-generation results, not independent validation.
No model fitting, learned combiner or prediction adjustment occurs in this audit.

Questions:

1. Which sufficiently large supplied-data groups account for lost positive-negative
   pair orderings? Decompose `1 - AUC` into disjoint positive-group / negative-group
   cells for external-score absence, contract, income, education and age groups.
   Sum cells back to the exact global pair loss. This avoids selecting a small
   group merely because its within-group AUC looks poor.
2. Is the error mainly within a group or between groups? Report both and the
   share of total loss. Any theoretical removable pair loss is only an optimistic
   descriptive bound; it is not an attainable prediction rule or a model forecast.
3. Do group means exhibit substantial calibration residuals, and are scores
   missing in the high-contribution groups? Sparse groups are flagged. This can
   motivate a learned representation or segment model, never hand-labeling.
4. Is obvious missing capacity a plausible explanation? On a saved CatBoost model,
   compare a deterministic sample of its own training rows with its cached held-out
   rows. This single-model in-sample diagnostic is not a performance estimate and
   cannot establish a statistical ceiling.

Output: exact evidence tables, code/data/prediction hashes, a new notebook and
shortlist of hypotheses with measured motivation. No additional data, external
labels, recovered identities, pretrained weights or changes to older notebooks.

Leaderboard feedback is recorded separately as user-reported and unverified with
respect to methods/rule compliance: top ten displayed 1; top twenty above 0.8.
