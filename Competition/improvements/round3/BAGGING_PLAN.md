# Three-seed averaging check, recorded before confirmation

The previous pass benefited from averaging two fold seeds. The third-pass
confirmation already produces a third development OOF prediction for every
family in the frozen recipe and the complete current reference. Those saved
predictions permit a low-cost, prospective test of diminishing averaging gains.

Only run this check if the original third-pass primary, confirmation and
two-seed gates all pass. Keep its recipe, weights and prediction transform fixed.
Average matching family predictions over the original primary seed, previous
secondary seed and new confirmation seed, before applying the frozen transform.

Train a third final seed only if ALL of these predeclared conditions hold:

- The current reference gains at least 0.00020 AUC from two to three seeds.
- The candidate gains at least 0.00020 AUC from two to three seeds.
- The three-seed candidate still beats the three-seed current reference by at
  least 0.00020, so a feature gain is not confused with additional averaging.
- Both candidate and reference improve in at least four of five primary-fold
  row groups. These groups summarize the gains; they are not independent tests.

If the gate fails, retain the original two-seed decision and stop expanding the
seed bank. No search over seed subsets, unequal seed weights or four-seed run.
This is a conditional development diagnostic, not new independent evidence.

If it passes, freeze the probe/source/recipe before any additional full-data fit.
Use final fold seed SEED+602, model seeds SEED+900+k, and the same frozen median
iteration counts. Reuse all original two-seed model instances. Preserve the
two-seed CSV and create a separately named three-seed CSV. Verify saved-model
replay and report the incremental gain separately.
