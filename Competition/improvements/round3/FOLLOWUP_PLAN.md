# Quantization follow-up, recorded during the initial screen

Observed trigger: `r3_cat_borders512` inner AUC 0.7508330687 versus the
matched proxy CatBoost 0.7499521163 (+0.0008809524). Its best coarse blend
with the complete current recipe scored 0.7514878320, about +0.000257.
The old lean-feature 512-border trial had been negative. This supports testing
parameter/representation interaction rather than assuming the old result transfers.

After the initial twenty screens finish, test:

1. 1024 borders, otherwise identical to the proxy baseline: is there a useful
   quantization trend, or did the single finer grid happen to fit this split?
2. Depth four plus 512 borders: does the separately promising shallower tree
   complement the finer representation?
3. Native missing bins plus 512 borders: does this complement quantization or
   change the useful numeric thresholds adversely?
4. If a new feature block (`signed`, `rates`, `crosses`, `engineered_proxy`)
   beats the matched baseline individually and gains >=0.00010 in a blend,
   combine the highest blend-scoring such block with 512 borders. Otherwise,
   do not invent a feature-combination experiment after seeing it fail.
5. Increase resolution only for the original credit/annuity ratio and five new
   loan-proxy columns, keeping all other columns at the default. This separates
   the hypothesized loan-threshold mechanism from a global border-count change.
6. Increase resolution only for the original/aggregate external-score columns.
   This is a matched alternative explanation for the global quantization gain.

Items 5–6 were added before any follow-up fit, after checking the installed
CatBoost parameter documentation for per-column quantization. Column indexes
are generated from the actual encoded schema, not guessed or learned from test
data. These controls can weaken a proposed explanation even if the global
512-border recipe remains useful.

The subsequently completed `r3_cat_signed` screen scored 0.7509073195,
with best-blend AUC 0.7516576204 (about +0.000426 over the full reference).
Before any follow-up fit, add two component controls using CatBoost's explicit
ignored-feature mechanism on the exact same 55-column frame:

7. Keep only the two signed residual additions; ignore rounded categories.
8. Keep only the two rounded category additions; ignore signed residuals.

This tests which part of the joint term representation is useful. Neither the
feature-function implementation nor the previous screening caches are changed.

Exact generated specs are frozen in `artifacts/followup_plan.json` before
any of these follow-up fits. Include all completed follow-ups in the same
promotion ranking and retain the original finalist limits and validation gates.
Do not use confirmation feedback to add another search cycle.
