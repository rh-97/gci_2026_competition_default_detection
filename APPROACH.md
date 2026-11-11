# Approach

How the data was processed, which models were built, how they were validated, and what did or did not help.
Numbers are out-of-fold ROC AUC on the 171,202 training rows unless stated otherwise. Each step has a
notebook with the code and outputs.

## 1. Problem and data

* **Task:** estimate the probability that an applicant has payment difficulties (`TARGET = 1`). Scored by
  ROC AUC, so only the *ranking* of applicants matters.
* **Data:** 171,202 training rows and 61,500 test rows, 32 predictors (24 numeric, 8 categorical): loan amounts,
  income, family, employment and registration dates, region, three external credit scores (`EXT_SOURCE_1..3`)
  and credit-bureau request counts. Default rate 8.07%.
* **Rules:** only the supplied files, no hand labelling, reproducible with fixed seeds.

Key findings from [01_data_exploration](notebooks/01_data_exploration.ipynb):

| Finding | Consequence |
| --- | --- |
| The external scores are by far the strongest signals (single-column AUC 0.56 to 0.66); everything else is weak alone | Summaries and interactions of the scores; models that learn interactions (boosted trees) |
| `EXT_SOURCE_1` is missing for 69%, `EXT_SOURCE_3` for 32%, `OWN_CAR_AGE` for 66% | Keep all rows; let missingness be information; reconstruct missing scores |
| `DAYS_EMPLOYED = 365243` for 18% of rows (a placeholder, mostly pensioners) | Replace by missing and add a flag |
| Credit / annuity has a very spiky distribution (standard loan products) and default rate moves sharply with it | Loan-term and implied-rate features |
| A classifier separates train from test with AUC 0.513 only | Train and test look alike, so random K-fold CV is a fair stand-in for the test set |
| About 3% of rows are probably repeat applications by the same person (identified via date differences) | New "repeat-applicant history" features |

## 2. Validation

* **5-fold stratified cross-validation** on the full training set. Each training row gets an out-of-fold (OOF)
  prediction from the model that did not see it; the test prediction is the average of the 5 fold models.
* **Seeds:** final models use 3 seeds, each with a *different* fold split; predictions are averaged.
* **Two kinds of runs.** A *development* run (seed 0) uses the held-out fold for early stopping to find a good
  number of trees (slightly optimistic). The *final* runs then train for that fixed number of trees, so no
  fold influences its own model.
* **Leakage rules.** IDs are never features. Features that use labels are computed inside each fold from the
  fold's training part only, and a training row never sees its own label.
* **Decisions are made on local CV, not on the public leaderboard.** The public score uses only part of the test
  set; its uncertainty (about ±0.007 AUC) is larger than most improvements here.

## 3. Data processing and features ([02_feature_engineering](notebooks/02_feature_engineering.ipynb))

**Cleaning:** placeholder `DAYS_EMPLOYED` becomes missing plus a flag; numeric gaps stay missing; categories are
kept as text (tree models handle them natively; the neural net uses learned embeddings).

**Base feature set (55 columns).** This is the set that survived validation in the earlier rounds of this project.

| Group | Examples | Idea |
| --- | --- | --- |
| Affordability | income/annuity, income/credit, income per family member, credit vs goods price | payment burden and financed extras |
| Timing | employment length / age, age at employment start | stability relative to life stage |
| External scores | mean, min, max, std, number available | combine the strongest but often missing signals |
| Loan term and price | credit/annuity, signed and absolute distance to the nearest 6/12 multiple, rounded term, rate implied under an assumed 24/36/60-payment term | distinguishes loan products and their price; the implied rate is a proxy, not the true contract rate |
| Missingness | count of missing fields, employment placeholder flag | absence of information is informative |

**Reconstructed external scores (6 columns).** For each external score, a LightGBM regressor predicts it from the
other supplied columns (out-of-fold, fitted on train + test since no default labels are involved). The
prediction fills in where the score is missing, and the **residual** (observed − expected) says whether the
bureau rates the applicant better or worse than their profile suggests. Reconstruction R²: 0.49 / 0.24 / 0.12.

## 4. Models ([03_base_models](notebooks/03_base_models.ipynb))

| Model | Setup |
| --- | --- |
| **LightGBM** | 21 leaves, learning rate 0.035, row/column subsampling, L1/L2 regularisation (tuned with Optuna in round 1) |
| **CatBoost** | depth 5, learning rate 0.045, L2 = 8, random strength 0.5; native categorical handling |
| **CatBoost-recon** | as CatBoost, plus the 6 reconstructed-score columns |
| **TabM** | neural network: 16 weight-sharing MLPs (2 × 128 units) averaged; piecewise-linear embeddings of numbers (48 quantile bins); AdamW, batch 1024, cosine schedule, 40 epochs |

The neural network is weaker alone but ranks applicants differently from the trees, which helps the blend.

## 5. New ideas tested ([04_new_ideas](notebooks/04_new_ideas.ipynb))

Each idea was screened with LightGBM on two seeds against a control using the same folds. The rule, fixed before
running: keep an idea only if it gains at least 0.0002 AUC.

| Idea | What it adds | LightGBM AUC | Gain | Decision |
| --- | --- | --- | --- | --- |
| Control | base features | 0.76288 | | |
| A. Population statistics | category frequencies, amounts relative to the group median, popularity of exact amounts, repeat-group size (computed over train + test) | 0.76272 | −0.00016 | dropped |
| B. **Repeat-applicant history** | for applications by the same probable person: how many are labelled, how many defaulted, the rate | **0.76423** | **+0.00135** | **kept** |
| C. Neighbour default rate | default rate of the 100 / 500 most similar applicants by scores and loan term | 0.76294 | +0.00006 | dropped |

**How repeat applicants are found.** `DAYS_*` columns count back from the application date, so for the same
person applying twice, birth date, ID-publication date and registration date all shift by the same amount. Rows
sharing (gender, birth − ID publish, birth − registration) are treated as the same probable person. When one
application in such a group defaulted, another one defaulted 25% of the time (base rate 8%). The key is not
perfect, so it is used as a model input, never as a rule. A row's own label is always excluded.

The neighbour default rate is strong on its own (AUC 0.72), but boosted trees already capture the same
information from the scores, so it added nothing. Confirmation on CatBoost-recon: 0.76329 → 0.76439 (seed 0).

## 6. Ensemble and submission ([05_ensemble_and_submission](notebooks/05_ensemble_and_submission.ipynb))

The repeat-applicant history was added to all three model types (LightGBM, CatBoost-recon, TabM), each trained
on 3 seeds. Then three ways of combining OOF predictions were compared. Each is fitted on 4/5 of the rows and
scored on the other 1/5, so no method is scored on the rows it was fitted to. Predictions are combined on the
logit scale.

| Single model (out-of-fold AUC) | Base features | + repeat history |
| --- | --- | --- |
| LightGBM | 0.76330 | 0.76438 |
| CatBoost | 0.76484 | |
| CatBoost-recon | 0.76504 | **0.76613** |
| TabM | 0.76127 (1 seed) | 0.76515 |

| Blend (nested AUC) | Equal weights | Optimised weights | Logistic stacking |
| --- | --- | --- | --- |
| Previous recipe rebuilt (LightGBM, CatBoost, CatBoost-recon, TabM) | 0.76667 | 0.76667 | 0.76672 |
| All seven models | 0.76756 | 0.76790 | 0.76812 |
| **Models with repeat history** | 0.76795 | 0.76815 | **0.76815** |

**Final submission:** logistic stacking of LightGBM-new (weight 0.14), CatBoost-recon-new (0.47) and TabM-new
(0.39), with nested AUC **0.76815**. That is +0.0014 over the rebuilt previous recipe; the gain is slightly
generous because the baseline TabM has 1 seed instead of 3.

* TabM's large weight despite its lower score comes from its different errors. Its predictions correlate about
  0.94 with the tree models', while the tree models correlate 0.97 to 0.99 with each other.
* The new submission's rank correlation with the earlier submission (public score 0.77029) is 0.997.
* Optimised weights and stacking performed the same, so the blend is not sensitive to the method.

Local CV and the public leaderboard are different evaluations. Expect the public score to move around the
local number by a few thousandths.

## 7. What did not work (earlier rounds)

These were tested in the earlier rounds of this project (135 recorded trials) and are not part of the final code:

* Random forest, logistic/spline regression, histogram boosting, XGBoost, small MLPs: weaker and added little to the blend.
* Broader feature sets (logs, category crosses, age bins, many extra ratios): more columns did not help; the compact base set did better.
* Class weighting and importance-based feature removal: did not beat the unweighted, full-feature models.
* Cross-fitted target encodings of category interactions, and a learned stacking model over the older ensemble: no meaningful gain.
* Several CatBoost variants (512 borders, native-missing handling, signed-term-only features) were blended in the old
  7-model ensemble. Here they are merged into one CatBoost and one CatBoost-recon to keep the code compact.

## 8. Expectations

The test data has only 32 of the original competition's ~120 application columns and none of its side tables
(credit history, previous applications). Those were the main source of scores above 0.80 in the original
competition and count as outside data here. Improvements in this project shrank from about +0.01 to about
+0.001 per round, which suggests the remaining headroom with these columns is small.
