# Cleanup and recovery report

This is the first cleanup record. The later [round-based folder layout](../rounds/README.md) moves notebook/document paths, and [output recovery](OUTPUTS.md) describes files now stored in Git. The statements below about files remaining in place describe that earlier cleanup.

## Saved state

- Snapshot branch: `snapshot/pre-cleanup-2026-11-09`.
- Snapshot commit: `b8d094cc94496a74ec38fc66e69319348b9a4924`.
- Cleanup branch: `cleanup/project-organization`.
- Snapshot includes data, trained weights, notebooks, outputs, logs, sources and
  existing ZIPs. Venv/Python caches were excluded by the pre-existing ignore rules.
- The venv remains in place. No remote or push was created. Local commits use the
  automation identity `Codex <codex@localhost>`.

## Changes and reasons

Removed 71 files totaling 2,023,838 bytes:
five completed background wait/dispatch helpers, OS folder metadata, Python
bytecode, generated kernels and Matplotlib font caches. Source for the completed
helpers remains recoverable from the snapshot and the unchanged delivered ZIP.
The main frozen pipeline executes the same fits sequentially without those helpers.

Added a root README, one local-venv entry point, the consolidated report and the
complete experiment catalog. Added ignore patterns to prevent generated runtime
files from being committed again. Historical report/readme entry links were updated.

Existing notebooks, inputs, saved weights, CSVs, frozen feature/fitting code,
research results, negative evidence, logs and ZIPs remain in place. Older modeling
modules are required by the current pickle/import/feature chain. Moving or
renaming them would require a separately validated model migration, so their
paths are retained. The existing journals are linked as historical evidence.

The cleanup checks passed, including exact saved-model replay and comparison of retained snapshot files. See [cleanup_validation.json](cleanup_validation.json). Byte comparisons confirmed 15 existing notebook files, 198 model/encoder files, 3 input files and 14 outputs unchanged; 1655 retained snapshot files matched overall.

## Recovery

```sh
git show snapshot/pre-cleanup-2026-11-09:Competition/improvements/high_upside/finish_modeling.py
git restore --source=snapshot/pre-cleanup-2026-11-09 -- path/to/removed/file
```

The first command only inspects a snapshot file. The second restores the named
tracked file into the current branch. No discarded Python bytecode needs recovery.
The manifest stores removed-file paths, sizes, SHA-256s and snapshot membership.

## Per-file removal record

| Removed path | Bytes | Reason | Recovery |
| --- | --- | --- | --- |
| `.DS_Store` | 8,196 | OS folder metadata. | Snapshot branch |
| `Competition/.DS_Store` | 8,196 | OS folder metadata. | Snapshot branch |
| `Competition/improvements/__pycache__/build_notebooks.cpython-312.pyc` | 18,587 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/__pycache__/execute_notebook.cpython-312.pyc` | 2,232 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/__pycache__/experiment.cpython-312.pyc` | 47,235 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/__pycache__/package_results.cpython-312.pyc` | 17,027 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/__pycache__/refine.cpython-312.pyc` | 2,500 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/__pycache__/select_features.cpython-312.pyc` | 2,936 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/__pycache__/supplement.cpython-312.pyc` | 2,325 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/__pycache__/verify.cpython-312.pyc` | 6,070 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/artifacts/kernels/competition-local/kernel.json` | 395 | Machine-specific generated kernel specification or plotting font cache. | Snapshot branch |
| `Competition/improvements/artifacts/matplotlib/fontlist-v3.11.0.json` | 298,003 | Machine-specific generated kernel specification or plotting font cache. | Snapshot branch |
| `Competition/improvements/high_upside/__pycache__/execute_model_notebook.cpython-312.pyc` | 3,415 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/high_upside/__pycache__/finish_modeling.cpython-312.pyc` | 2,748 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/high_upside/__pycache__/h_accel.cpython-312.pyc` | 10,716 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/high_upside/__pycache__/h_features.cpython-312.pyc` | 11,218 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/high_upside/__pycache__/h_models.cpython-312.pyc` | 16,217 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/high_upside/__pycache__/h_parallel_later.cpython-312.pyc` | 8,966 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/high_upside/__pycache__/h_pipeline.cpython-312.pyc` | 50,701 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/high_upside/__pycache__/h_report.cpython-312.pyc` | 30,791 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/high_upside/__pycache__/h_results_notebook.cpython-312.pyc` | 10,539 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/high_upside/__pycache__/h_uncertainty.cpython-312.pyc` | 5,705 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/high_upside/__pycache__/h_verify_package.cpython-312.pyc` | 12,754 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/high_upside/artifacts/kernels/competition-local/kernel.json` | 451 | Machine-specific generated kernel specification or plotting font cache. | Snapshot branch |
| `Competition/improvements/high_upside/artifacts/matplotlib/fontlist-v3.11.0.json` | 298,003 | Machine-specific generated kernel specification or plotting font cache. | Snapshot branch |
| `Competition/improvements/high_upside/artifacts/model_kernels/competition-local/kernel.json` | 420 | Machine-specific generated kernel specification or plotting font cache. | Snapshot branch |
| `Competition/improvements/high_upside/finish_modeling.py` | 1,770 | Completed background orchestration; sequential frozen pipeline remains available. | Snapshot branch |
| `Competition/improvements/high_upside/h_parallel_confirmation.py` | 2,920 | Completed background orchestration; sequential frozen pipeline remains available. | Snapshot branch |
| `Competition/improvements/high_upside/h_parallel_confirmation_remaining.py` | 2,972 | Completed background orchestration; sequential frozen pipeline remains available. | Snapshot branch |
| `Competition/improvements/high_upside/h_parallel_later.py` | 4,827 | Completed background orchestration; sequential frozen pipeline remains available. | Snapshot branch |
| `Competition/improvements/high_upside/h_schedule_later.py` | 2,101 | Completed background orchestration; sequential frozen pipeline remains available. | Snapshot branch |
| `Competition/improvements/round2/__pycache__/adaptive.cpython-312.pyc` | 11,797 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round2/__pycache__/check_complexity.cpython-312.pyc` | 8,858 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round2/__pycache__/document.cpython-312.pyc` | 40,571 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round2/__pycache__/execute_new_notebook.cpython-312.pyc` | 2,232 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round2/__pycache__/finalize.cpython-312.pyc` | 17,987 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round2/__pycache__/notebooks.cpython-312.pyc` | 18,873 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round2/__pycache__/package_round2.cpython-312.pyc` | 25,711 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round2/__pycache__/proxy_followup.cpython-312.pyc` | 3,378 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round2/__pycache__/round2.cpython-312.pyc` | 25,551 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round2/__pycache__/secondary_metrics.cpython-312.pyc` | 4,726 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round2/__pycache__/validate.cpython-312.pyc` | 26,208 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round2/artifacts/kernels/competition-local/kernel.json` | 412 | Machine-specific generated kernel specification or plotting font cache. | Snapshot branch |
| `Competition/improvements/round2/artifacts/matplotlib/fontlist-v3.11.0.json` | 298,003 | Machine-specific generated kernel specification or plotting font cache. | Snapshot branch |
| `Competition/improvements/round3/__pycache__/bagging.cpython-312.pyc` | 20,470 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round3/__pycache__/diagnostics.cpython-312.pyc` | 3,670 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round3/__pycache__/document.cpython-312.pyc` | 19,799 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round3/__pycache__/execute_notebook.cpython-312.pyc` | 3,444 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round3/__pycache__/finalize.cpython-312.pyc` | 17,130 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round3/__pycache__/followup.cpython-312.pyc` | 6,754 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round3/__pycache__/notebooks.cpython-312.pyc` | 14,075 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round3/__pycache__/package.cpython-312.pyc` | 35,602 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round3/__pycache__/round3.cpython-312.pyc` | 25,700 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round3/__pycache__/stored_helpers.cpython-312.pyc` | 6,511 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round3/__pycache__/validate.cpython-312.pyc` | 29,557 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round3/__pycache__/verify.cpython-312.pyc` | 12,663 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round3/artifacts/kernels/competition-local/kernel.json` | 441 | Machine-specific generated kernel specification or plotting font cache. | Snapshot branch |
| `Competition/improvements/round3/artifacts/matplotlib/fontlist-v3.11.0.json` | 298,003 | Machine-specific generated kernel specification or plotting font cache. | Snapshot branch |
| `Competition/improvements/round4/__pycache__/r4_cv.cpython-312.pyc` | 11,790 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round4/__pycache__/r4_diagnostics.cpython-312.pyc` | 7,666 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round4/__pycache__/r4_document.cpython-312.pyc` | 24,965 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round4/__pycache__/r4_exact_reference.cpython-312.pyc` | 937 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round4/__pycache__/r4_execute_notebook.cpython-312.pyc` | 3,379 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round4/__pycache__/r4_final.cpython-312.pyc` | 19,239 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round4/__pycache__/r4_followup.cpython-312.pyc` | 7,311 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round4/__pycache__/r4_fraction.cpython-312.pyc` | 11,228 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round4/__pycache__/r4_notebooks.cpython-312.pyc` | 13,771 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round4/__pycache__/r4_package.cpython-312.pyc` | 4,800 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round4/__pycache__/r4_validate.cpython-312.pyc` | 16,031 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round4/__pycache__/r4_verify.cpython-312.pyc` | 7,622 | Regenerable Python or notebook cache. | Regenerable cache |
| `Competition/improvements/round4/__pycache__/round4.cpython-312.pyc` | 26,037 | Regenerable Python or notebook cache. | Regenerable cache |
