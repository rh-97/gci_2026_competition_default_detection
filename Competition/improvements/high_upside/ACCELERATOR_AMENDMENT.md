# Prospective local-GPU amendment

Timing: after the first three CPU pilots completed, before the regularized neural
pilot completed and before any primary CV, recipe selection or confirmation.
No score gate, candidate hyperparameter or weight grid changes.

The sandbox reported MPS unavailable. A separate local hardware check outside the
sandbox reported MPS available. A randomly initialized representative network
measured 0.10265 seconds/batch on CPU and 0.03308 on MPS, approximately three times
faster. This is a throughput probe, not a competitive model or dataset.
`artifacts/model_neural_hardware_check.json` records the result.

The CPU worker and waiting delivery worker were stopped. The first three complete
CPU model/prediction/curve/metric artifacts remain byte-identical; their hashes,
specs, original identity and reuse reason are recorded in
`reference/cpu_stage_reuse.json`. The interrupted regularized model has no final
pilot record and is not counted as a scientific negative. Its partial learning
curve and the original runner/logs are preserved under `reference/cpu_stage`.

New `h_accel.py` trains subsequent neural fits on the local MPS GPU. It reuses the
unchanged encoder, feature functions and predictor classes from the original
fitting core. Initial weights and shuffle order are seeded on CPU, with MPS seeded
too. Architecture, losses, optimizer, learning-rate schedule, stopping budgets and
validation gates remain those in the original plan. Trees and preprocessing remain
on CPU. GPU validation can have small float32 differences; retained predictions
and all saved-model inference are generated on CPU. Exact saved-weight replay on
CPU is checked; bit-identical GPU retraining is not promised.

The current engine identity includes the separately hashed GPU implementation and
this amendment. Historical CPU pilot results retain their original signatures.
They are reused only as recorded stage evidence after checking their complete
artifact hashes, exact specs, unchanged original core/data/package identity and
explicit CPU diagnostics. They are not silently relabeled as GPU results or
asserted to equal a new GPU fit. All new CV/final results use the new identity.

This mixed-hardware pilot stage compares complete recipes. It does not isolate
architecture or regularization effects from hardware numerical differences.
All newly selected families are validated on the same current backend through
the unchanged downstream gates. Source/recipe freezes still precede confirmation.
No outside data, cloud resources, pretrained weights or transfers are involved.
