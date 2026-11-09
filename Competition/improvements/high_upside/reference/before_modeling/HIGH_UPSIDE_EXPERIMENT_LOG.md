# Higher-upside research journal

## Leaderboard context and target

The user reports that the top ten entries display scores of 1 and the top twenty
are above 0.8, while explicitly expressing uncertainty about external-data use.
This observation is recorded in `improvements/high_upside/artifacts/leaderboard_context.json`.
Methods, compliance and private-test performance were not independently verified.
No allegation about other participants is made. The competitive target is **0.8+**;
its attainability using the permitted inputs remains unproven.

## H1: attribute ranking errors before selecting expensive branches

**Why:** The user redirected effort away from incremental tuning. A weak AUC on a
small slice is insufficient evidence that a specialist can materially improve the
whole submission. Attribute errors to the population and pair types they affect.

**How:** Use the frozen round-three three-seed development OOF predictions on
136,961 rows. Compute reversed positive-negative pairs, assigning half-error to
ties. Decompose global `1 - AUC` by positive-group and negative-group membership
for loan contract, income, education, gender, external-score missing count and
pattern, and age band. Verify each matrix sums back to the exact global loss.
Also compare one saved CatBoost model's predictions on a deterministic sample of
20,000 own-training rows with its cached predictions on 34,241 held-out rows.
There is no new fit, model selection or adjustment of predictions in this audit.

**Observed:**

- Complete three-seed development OOF AUC: **0.7648034855**. This is a local
  diagnostic, distinct from the confirmed submitted public score **0.76824**.
- The group missing two external scores has 30,767 rows, 2,791 positives and
  within-group AUC **0.743954**. Its share of positive-centered global ranking
  loss is **23.09%**, compared with **25.24%** of all positive applicants. Lower
  within-group AUC did not identify disproportionate global error contribution.
- **85.26%** of total ranking loss occurs within contract-type groups; cash-loan
  rows account for most of this because they dominate the population. There is
  no obvious tiny contract segment whose correction alone explains a large jump.
- The saved model's own-training sample AUC is **0.8140925** versus held-out AUC
  **0.7651793**. This shows an in-sample/held-out gap for that fit. It does not
  measure the attainable ceiling or isolate why generalization fails.
- Mean calibration residuals for the large missing-count and contract groups are
  small. Global monotone probability calibration would preserve score order and
  cannot increase AUC. Learned interactions may still change relative rankings.

**Decision and reasoning:** Prioritize a different generalization strategy and
learned representation across the population. Simple depth increases, arbitrary
missing-score specialists, hand adjustments and additional seed banks are not
justified by these descriptive results. The first neural pilot should compare a
scratch TabM with numerical embeddings on raw and successful engineered features.
Selected borrower/profile interactions can be tested against the same fixed tree
learner. Missing-score reconstruction remains conditional on auxiliary OOF quality
and downstream ranking gains; observed-score masking may not represent the true
missing population. Retrieval and fully nested stacking require evidence first.
No claim is made that any proposed branch will achieve 0.8.

**Evidence:**

- New notebook: `07_signal_opportunity_audit.ipynb`.
- Recorded audit plan and source: `improvements/high_upside/OPPORTUNITY_AUDIT_PLAN.md`
  and `opportunity_audit.py` in the same directory.
- `artifacts/audit_summary.json`: source, data, split and prediction hashes;
  local-venv provenance and capacity diagnostic.
- `artifacts/pair_loss_cells.csv`, `group_slices.csv`, `within_between_loss.csv`:
  complete numerical results, including sparse groups.
- `artifacts/external_score_pair_loss.png`: pair matrix and group-size comparison.

**Limits:** All development labels have been explored previously. This is a
hypothesis-generation audit, not independent confirmation or a measured upper
bound. Pair-loss cells are descriptive quantities, not automatically attainable
improvements. Group comparisons can reflect differences in case mix.

**Operational correction:** The first execution of the new draft notebook used
`slices.sparse` to access a column, which collided with pandas' sparse-data accessor.
It was corrected to bracket access and the new notebook was rerun. The failed
execution snapshot is preserved under `improvements/high_upside/reference`.
Previously existing notebooks were unchanged. No model or data changed because
of this presentation error. Plot annotation contrast was also improved.

## Next experiment status

The revised strategy is in `HIGH_UPSIDE_PLAN.md`. Exact neural pilot settings,
runtime/memory limits and promotion gates must be recorded before model fitting.
PyTorch was not installed at the time of this audit. No neural pilot has yet run,
and no new submission has been produced. Current recommendation remains the
public-confirmed round-three bagged CSV. The old round-four controller remains
stopped; its seven completed screens remain documented separately.
