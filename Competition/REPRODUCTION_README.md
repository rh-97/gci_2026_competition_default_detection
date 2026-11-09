# Reproducing the recommended submission

Files are now [grouped by round](rounds/README.md). Only the latest CSV remains in `output/`; [older outputs and historical ZIPs are recoverable from Git](docs/OUTPUTS.md). The current `project.py verify` supports moved notebooks and archived outputs. `project.py reproduce` removes the identical duplicate replay CSV after checking it. Original commands below can create additional generated output files.

Current project entry point, from the repository root:

```sh
Competition/.venv/bin/python Competition/project.py status
Competition/.venv/bin/python Competition/project.py verify
Competition/.venv/bin/python Competition/project.py reproduce
```

See [PROJECT_REPORT.md](PROJECT_REPORT.md) for the consolidated data/model results
and [cleanup details](docs/CLEANUP_REPORT.md) for preserved historical dependencies.
The original commands below remain supported. The latest user screenshot shows
0.77029, rank 364; its submitted filename was not explicitly confirmed, so the
candidate's public-score attribution remains unconfirmed.

Recommended: `output/submission_high_upside.csv`
SHA-256: `15d050aa8709ae4e2d338b013c03216d4b3f3279348a3faca71080c17e44baed`

A new higher-upside candidate passed every declared local gate. Its public score is unknown.

Use Python 3.12 and the project `.venv`. Exact modeling packages are pinned in
`improvements/high_upside/requirements-high-upside.txt`. The wrapper selects one
OpenMP runtime on this Mac without disabling duplicate-runtime safety checks.
No extra data or pretrained weights are required. Retain the supplied `input`
directory; it and the venv are excluded from the new archive.
Training after the accelerator amendment requires the local MPS GPU to be exposed
to the process; saved-model inference runs on CPU. The first three CPU pilots are
reused as explicitly recorded historical evidence, with their original signatures.

Prediction-only replay:

```sh
.venv/bin/python improvements/high_upside/h_launch.py reproduce
```

For the retained historical reference, the original exact saved-model command
also remains available:

```sh
.venv/bin/python improvements/round3/bagging.py reproduce
```

Full higher-upside phase order (matching caches are reused):

```sh
.venv/bin/python improvements/high_upside/h_launch.py preflight
.venv/bin/python improvements/high_upside/h_launch.py screen
.venv/bin/python improvements/high_upside/h_launch.py primary_cv
.venv/bin/python improvements/high_upside/h_launch.py select
.venv/bin/python improvements/high_upside/h_launch.py confirmation
.venv/bin/python improvements/high_upside/h_launch.py averaging
.venv/bin/python improvements/high_upside/h_launch.py final
.venv/bin/python improvements/high_upside/h_launch.py reproduce
```

Do not run all historical notebooks merely to obtain the recommended CSV.
Notebooks 08/09 review the plan/results; training flags are false by default.
Selection source, weights and counts cannot be changed after confirmation.
Read `rounds/round5/reports/HIGH_UPSIDE_EXPERIMENT_LOG.md` for exact settings, adaptive decisions and
negative results. The earlier journals retain previous work.

`improvements/high_upside/artifacts/model_package_manifest.json` contains archive
member SHA-256s. The new ZIP was verified against them and its CRC. Earlier ZIPs,
kernel/cache directories and raw logs are excluded. All present protected earlier
files must match their recorded hashes; excluded older ZIPs may be absent after
unpacking. Supplied inputs are still needed for inference.
