# Remaining stored-model complementarity check

The main third-pass recipe is frozen and passed its gates. Before stopping,
check whether any previously fitted development OOF model outside its five
families offers a meaningful additional improvement. This is cheap because
the predictions already exist; no new model is fitted for this probe.

Read first-pass and second-pass common-fold OOF predictions. Verify row count
and recomputed AUC against each saved result to establish label/order alignment.
Exclude families already carrying positive weight in the frozen winner.

Blend each remaining helper into the frozen **third-pass winner**, not the
weaker round-two reference, with helper weights 0.05, 0.10 and 0.25. Test
probability and log-odds averaging. All choices use the primary development
predictions only. Do not consult test predictions or public feedback.

Only a gain >=0.00020 over the frozen third-pass winner warrants a separately
planned validation branch. A smaller/negative gain does not justify more fits.
Do not change the already frozen recipe based only on this primary probe.
Retain every result and decision. This check is adaptive and is explicitly
reported as a late stored-prediction screen, not independent confirmation.
