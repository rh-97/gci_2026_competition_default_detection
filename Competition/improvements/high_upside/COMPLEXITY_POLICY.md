# Budget-aware recipe selection, before freeze and confirmation

Timing: the neural primary CV and a read-only neural/reference pair preview were
complete; tree primary CV was still running. The complete joint grid, selected
recipe and any confirmation results had not been observed. Both workers were
stopped before changing the selection controller. The original runner/log/state
are preserved under `reference/before_complexity_policy`. Completed fits remain
unchanged, and no fitting source, hyperparameter, data or cached prediction changes.

The user explicitly prioritized larger steps over spending time on negligible
improvements. Apply this additional compute-allocation rule to the already-declared
primary grid: a recipe using two new families must gain **at least 0.00030 AUC**
over the best recipe using at most one new family. Otherwise choose the best
one-family addition. The reference alone is eligible as the simpler candidate.
The rule controls future training cost; it is not a significance test.

Keep the entire unconstrained grid, its maximum, the simpler maximum and the
incremental contribution in the selection record. Do not erase a more complex
candidate's score or the tree finalist's CV. Existing overall >=0.00030 eligibility,
fresh confirmation and matching-three-seed gates remain unchanged. No new methods,
weights or family configurations are introduced. The chosen recipe is frozen
before any confirmation; no simplification or reweighting occurs afterwards.

Fit cache identities stay unchanged because fitting code/inputs are unchanged.
The selection freeze additionally hashes this policy and amended controller.
Cold reproduction therefore applies the same explicit budget-aware rule.
This amendment is an adaptive budget decision with its timing recorded, rather
than presented as part of the original pre-pilot plan.
