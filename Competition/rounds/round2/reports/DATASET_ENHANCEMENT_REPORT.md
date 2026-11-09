# Dataset enhancement: what changed, why, how, and what worked

**Main conclusion:** we improved how the supplied information was represented.
We did not enlarge the dataset, invent labels or import outside rows. Original
CSVs still contain 171,202 training applicants and 61,500 test applicants, with
32 supplied predictors. Derived columns are constructed for the models in memory.

The most useful additions were compact financial/score summaries, loan-structure
proxies, signed term-pattern features, and a later learned score-reconstruction
block. Several broader feature sets failed. The table results below are saved
observations, not newly trained experiments.

Read [the EDA report](../../round1/reports/EDA_REPORT.md) for the observations that
motivated these choices, and [model selection](../../round5/reports/MODEL_SELECTION_REPORT.md)
for the later acceptance tests. This report answers **what inputs we created**.

## 1. What does “enhancement” mean here?

A feature is an input the model receives. For example, income and payment amount
are supplied columns; income divided by payment is a derived feature. It gives
the learner a direct view of a relationship already present in the data.

Enhancement did not guarantee improvement. The reason to keep a feature recipe
was its performance in matched comparisons, including how it contributed to an
ensemble. An explanation such as “this may express affordability” is a hypothesis,
not proof of a causal mechanism. Some early rationales were reconstructed from
the code after the trials; the original ledger retains that provenance. Later
structural recipes were explicitly recorded before fitting.

| Model-input representation | Columns before model-specific encoders | Construction |
| --- | --- | --- |
| Original columns | 32 | Necessary cleaning, no hand-crafted financial block |
| Broad engineered frame | 76 | Original columns plus the first broad set of ratios and summaries |
| Extended frame | 86 | Adds logs, crosses and bands to the broad frame; did not win |
| Lean frame | 46 | Original 32 plus 14 selected derived columns |
| Loan-proxy frame | 51 | Lean plus three assumed-rate transforms and two term distances |
| Signed frame | 55 | Proxy frame plus two signed residuals and two rounded categories |
| Score reconstruction | 61 | Signed frame plus three auxiliary predictions and three residuals |

These counts are not neural hidden-unit counts. Group-statistic encoders,
missing indicators, one-hot encoders and numerical embeddings can change the
actual encoded matrix dimensions. [Named base-frame sizes](enhancement/representation_sizes.csv)
and [exact column membership](enhancement/feature_inventory.csv) are provided.
The inventory covers those base frames and the six reconstruction column names;
per-trial subsets/ignored columns and encoder expansions are recorded separately
in the trial catalog. Round 2's `risk` frame means score-summary formulas; it is
different from the later learned interaction-risk block.

## 2. Safe preparation before engineering

**What:** exclude `SK_ID_CURR` and `TARGET` from predictors, mask the employment
placeholder 365243, represent blank categories explicitly, and prevent undefined
ratios. **Why:** identifiers are for alignment, TARGET is the answer, the employment
value represents roughly a thousand years, and division by zero is unusable.
**How:** copy the input frame; replace that employment code with missing; give
blank categories a missing token; replace zero denominators and infinities with
missing. Original source files are not edited.

`EMPLOYED_SENTINEL` records whether the original placeholder appeared. The
`MISSING_COUNT` feature counts raw blank fields, excluding ID/TARGET; it is separate
from the employment flag because the placeholder is not an empty cell. Missing car
age is not automatically interpreted as “does not own a car.”

The original 8.07% default-label prevalence was retained. No SMOTE, duplicated
default rows, random deletion of repayers, pseudo-labeling or extra outside data
was used. Class-weight experiments changed model losses, not the dataset's rows.

## 3. Financial and household comparisons

**Why:** the same loan amount can mean different things relative to income,
payments, the financed goods and household size. Ratios expose those relationships
directly. They are descriptive inputs, not verified affordability decisions.

| Feature/block | How it was computed | Intended information |
| --- | --- | --- |
| Income/payment | `AMT_INCOME_TOTAL / AMT_ANNUITY` | Income relative to payment size |
| Income/loan | `AMT_INCOME_TOTAL / AMT_CREDIT` | Income relative to borrowing |
| Loan/payment, named CREDIT_TERM | `AMT_CREDIT / AMT_ANNUITY` | Payment/loan structure; not a known actual term |
| Loan/goods difference ratio | `(AMT_CREDIT - AMT_GOODS_PRICE) / AMT_GOODS_PRICE` | Difference between financing and goods amounts |
| Income per person | `AMT_INCOME_TOTAL / CNT_FAM_MEMBERS` | Income relative to household size |
| Other explored household blocks | Credit/payment per person; adults = family members − children; per-adult amounts; child fraction; income after payment proxies | Alternative household and cash-flow representations |

For a made-up applicant, income 60,000 and payment 10,000 give an income/payment
ratio of 6. With the same payment but income 20,000, it is 2. The model learns
whether that difference is predictive; we do not assign a manual default label.

**Other explored additions:** amount logarithms; bureau-request totals;
contact-flag totals; education-rank mapping; and age/employment category bands.
The larger engineered frame contained these and other combinations. Only a
subset survived in the lean frame, while the selected LightGBM uses a broader
engineered representation with fold-trained group statistics.

## 4. Time and external-score summaries

Age was derived as `-DAYS_BIRTH / 365.25`, employment years similarly after
masking the placeholder, and approximate age at employment as age minus employment
years. Ratios compared employment, registration, ID and phone-change durations
with birth duration. Negative day values follow the dataset's reference-date
encoding; they were not all treated as errors.

The supplied `EXT_SOURCE_1/2/3` columns were summarized using mean, minimum,
maximum, standard deviation and number observed. Broader frames also tested sums,
products, pairwise differences/products and interactions with age or loan/payment.
For example, scores 0.2/0.6/0.7 and 0.5/0.5/0.5 have the same mean of 0.5 but
different disagreement. A variability feature makes that distinction available.

Round 2 also tested logit, geometric, harmonic, weighted and conservative score
summaries, explicit missing-pattern categories and organization-family labels.
They were plausible hypotheses, not automatically useful additions. “External”
is part of the original column names; it does not mean we imported extra data.

## 5. What did the basic comparisons show?

The following use the same initial inner-validation applicants. They compare
feature recipes within each model family, not leaderboard results:

| Model recipe | Original-column AUC | Engineered-input AUC | Difference |
| --- | --- | --- | --- |
| LightGBM | 0.7367838 | 0.7440631 | +0.0072793 |
| CatBoost | 0.7416556 | 0.7484926 | +0.0068370 |
| TabM-mini, piecewise embeddings | 0.7401112 | 0.7508052 | +0.0106940 |

TabM's original-column recipe still used automatic median/missing-value handling,
quantile preprocessing and numerical embeddings. “Raw” excludes our hand-crafted
financial feature block; it does not mean no preprocessing at all.

The LightGBM result also held up in five-fold development CV: **0.7499471** for
original columns versus **0.7561022** for engineered inputs. The broader extended
LightGBM frame scored only **0.7375499** in the inner screen, below
the ordinary engineered frame's **0.7440631**. More features could
add noisy or redundant split opportunities, so that larger block was not assumed
better. This is a plausible explanation, not an isolated causal finding.

## 6. Loan-structure features and their ablations

Round 2's development-only EDA found non-monotonic default-label patterns across
loan/payment groups and distances from multiples of 6 and 12. That motivated a
small proxy block rather than retaining every finance transformation.

For `t = loan/payment`, the absolute distance features are:

```text
distance_6  = abs(t / 6  - round(t / 6))
distance_12 = abs(t / 12 - round(t / 12))
```

Three more columns solve a hypothetical annuity relationship for assumed period
counts n = 24, 36 and 60:

```text
p = payment / loan
p = r / (1 - (1 + r)^(-n))
```

The implementation uses 28 binary-search steps over r in [0,1], only when the
assumptions admit a solution; otherwise the proxy is missing. These are nonlinear
representations of supplied amounts. They are **not reconstructed contractual
interest rates**, and n is not a verified loan duration.

The matched CatBoost screens were:

| Feature recipe with comparable CatBoost settings | Inner-screen AUC | What happened |
| --- | --- | --- |
| Lean control | 0.7484926 | Reference |
| Extra score-risk summaries | 0.7468125 | Not advanced |
| Broad finance block | 0.7490824 | Positive screen; compact proxy follow-up preferred |
| Extra missingness block | 0.7475893 | Not advanced |
| Combined blocks | 0.7486700 | Not advanced |
| Only assumed-rate additions | 0.7484734 | No gain over lean control |
| Only term-distance additions | 0.7487658 | Small gain; not sufficient alone |
| Three rate proxies plus two distances | 0.7499521 | Retained after CV |
| Same proxy frame, native numeric missingness | 0.7496474 | Retained as complementary family |

The compact combined proxy block reached pooled development CV **0.7622544**;
its native-missing variant reached **0.7615745**. Both survived as complementary
families. By contrast, the broad native-missing lean model reached **0.7605613**
and was not retained in the final round-two blend. Missing-value handling and
feature content were evaluated as recipes, not universal rules.

**Round 3 refinement:** the absolute distance treats ratios 23.8 and 24.2 alike
around 24. Signed residuals distinguish the two sides:

```text
signed_n   = t / n - round(t / n)
category_n = string(round(t / n))       # n = 6 or 12
```

For n=6 those residuals are approximately −0.0333 and +0.0333. The joint signed
and rounded-category frame scored **0.7509073** in the inner screen,
compared with **0.7502678** for signed additions alone and
**0.7491226** for rounded categories alone. The joint recipe
advanced; the individual ablations did not. A further model combined that frame
with 512 CatBoost quantization borders. Its name `r3_cat_feature_b512` refers to
the selected feature block plus finer quantization, **not top-k column pruning**.

Additional assumed-period transforms for n=12,18,48,72,84 were tested in
`r3_cat_rates` (inner AUC **0.7495568**) and were not advanced. This
records an unsuccessful extension rather than assuming more period assumptions
always improve the representation.

## 7. Category interactions, group statistics and pruning

**What/why:** test category crosses such as occupation × income type, age bands,
category frequencies and amounts relative to a category's typical amount.
**How:** the group encoder learns category shares and numeric medians on training
rows only. It adds frequency or `value / group_median` columns; unseen groups
receive missing derived values rather than statistics fitted on validation/test.
Group fields included organization, occupation, education and income type, plus
an age bin where that representation provided one.

Broad crosses were not consistently useful. Some group statistics remained in
the selected LightGBM, while the broader CatBoost group recipe did not earn a new
final place. High-cardinality crosses can create small groups; that is a reason
to test regularization, not proof of why a particular trial lost.

Importance-based LightGBM pruning also failed to improve its tuned reference:

| LightGBM input subset | Inner-screen AUC |
| --- | --- |
| lgb_tune_15 | 0.7471511 |
| lgb_top_25 | 0.7381651 |
| lgb_top_40 | 0.7428896 |
| lgb_top_55 | 0.7459224 |
| lgb_top_70 | 0.7463364 |

The top-70 version was checked in CV but did not beat the retained tuned model.
Low individual importance does not prove a feature is useless jointly, and this
experiment does not establish that every possible selection method would fail.

## 8. Model-specific preprocessing

| Learner | What/how | Why |
| --- | --- | --- |
| LightGBM | Fold-trained category vocabularies; unseen levels map to missing; optional group statistics; numeric missing values retained | Match category semantics and preserve missingness |
| CatBoost | Categorical strings; numeric sentinel −999, native missingness and fold-median alternatives tested | Let validation choose a useful missing-data recipe |
| Logistic/spline/early MLP | Fold-trained median imputation, indicators and numeric scaling/quantiles; one-hot categories | Put numerical inputs on usable scales and represent categories |
| TabM | Training medians; normal-quantile transform; missing flags; removal of constant encoded columns; category vocabulary with unknown code 0; numerical embeddings | Support a neural representation with explicit missingness and stable inputs |

Normal quantiles map values using their rank distribution learned from training
data. Piecewise embeddings let the network learn flexible responses across
numeric ranges; periodic embeddings were tested as an alternative. These are
model inputs/learned representations, not added applicants. The better signed
piecewise TabM recipe was retained; periodic and stronger-regularized variants
did not beat its screened ensemble contribution.

## 9. Learned reconstruction of the supplied scores

**Question:** can other supplied columns predict an external score well enough
to expose useful extra patterns? **How:** for each score, train a LightGBM
regressor on observed values, exclude that same score from its raw inputs, and
generate training-row predictions using three inner folds. Refit the auxiliary
teacher on outer-training observed rows to transform outer-validation/test rows.
TARGET and ID are not auxiliary predictor columns.

Each score adds a reconstructed value and `observed - reconstructed` residual.
Original score columns are retained; missing residuals remain missing before
normal model preprocessing. These six extra columns expand 55 to 61. We did not
replace unknown values with supposedly recovered truth or acquire outside scores.

Pilot reconstruction R2 was approximately **0.4828, 0.2356 and 0.1157** for scores
1, 2 and 3. R2 describes reconstruction on rows whose scores are observed. It is
not default-classification accuracy or a guarantee for truly missing scores.
The auxiliary teachers used 300 trees, learning rate .04, 15 leaves, minimum child
count 100 and L2 penalty 20. Downstream default-ranking comparisons decided use.

The reconstruction CatBoost's best screened blend added **0.0003659 AUC** over
the complete screen reference. The final two-addition recipe also improved primary
AUC by **0.0003962** over the best at-most-one-addition recipe. That comparison
includes blend selection; it does not isolate a causal effect for each new column.
The frozen combined recipe then passed later validation.

## 10. Learned interaction risks: a rejected enhancement

Eight predeclared borrower/loan/score pairs were tested: contract × rounded term;
education × age band; income type × occupation; gender × age band; score-2 bin ×
age band; mean-score bin × missing-score pattern; credit bin × term bin; and term
bin × contract. Bin edges fit outer-training inputs only.

Five inner folds generated training-row risk maps without using that row's target.
Validation/test encodings used maps fitted on all outer-training rows. Smoothed
risk was `(group_defaults + prior * training_default_rate) / (group_size + prior)`,
with prior strengths 30 and 100, plus log-support and frequency. Unseen groups
fall back to the learned training rate. Eight interactions × four outputs add
32 columns to the signed frame.

For an illustrative group with 2 defaults among 10 people and a global rate .08,
prior 30 gives (2 + 30×.08)/(10+30) = .11 instead of the unstable raw .20. This
shows the intended regularization. It is not an actual group from our data.

The screened blend **lost 0.0001325 AUC**, so this block was rejected. Its intended
benefit may have been redundant with CatBoost or outweighed by noise; the result
does not establish the exact cause or rule out all target-encoding methods.

## 11. Final decisions and safeguards

- Keep supplied observations and labels unchanged; no external-data enlargement.
- Keep a compact successful frame for several trees and the neural addition;
  the selected older LightGBM retains its own broader engineered/group frame.
- Retain signed term structure and learned score-reconstruction inputs where
  downstream comparisons supported them.
- Reject automatic “more columns is better,” failed broad blocks, unsupported
  pruning and the latest interaction-risk block.
- Fit all learned medians, vocabularies, maps, bins and auxiliary teachers inside
  permitted training data. Test rows are transformed, not used to fit these maps.
- Freeze feature/model recipes before confirmation; do not manually adjust any
  applicant's test prediction from these observations.

The reports document tested decisions, not proof that every retained column is
individually necessary. Joint blocks and model changes limit causal attribution.

## Evidence and reproducibility

- [full experiment catalog](../../../docs/EXPERIMENT_CATALOG.md): every recorded trial and rationale provenance.
- [Exact feature membership](enhancement/feature_inventory.csv) and
  [frame sizes](enhancement/representation_sizes.csv).
- [Source hashes and report scope](enhancement/report_evidence.json).
- Actual builders: [first pass](../../../improvements/experiment.py),
  [round two](../../../improvements/round2/round2.py),
  [round three](../../../improvements/round3/round3.py),
  [learned features](../../../improvements/high_upside/h_features.py).
- [Report builder](../../../tools/build_decision_reports.py).

```sh
# From the repository root; no model training:
Competition/.venv/bin/python Competition/tools/build_decision_reports.py
```
