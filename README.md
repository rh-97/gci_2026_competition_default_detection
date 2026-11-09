# Home Credit competition project

Start with [files grouped by round](Competition/rounds/README.md).

| Folder | Work |
| --- | --- |
| [Round 1](Competition/rounds/round1/README.md) | Supplied material, data audit and first improved models |
| [Round 2](Competition/rounds/round2/README.md) | Feature engineering and two-seed ensemble |
| [Round 3](Competition/rounds/round3/README.md) | Signed loan-term features and three-seed bagging |
| [Round 4](Competition/rounds/round4/README.md) | Stopped incremental search |
| [Round 5](Competition/rounds/round5/README.md) | Structural models, neural ensemble and score reconstruction |

Each round contains its notebooks and reports, plus relative links to its code,
saved models and raw experiment results. Links avoid duplicate copies and retain
the original checkpoint-compatible paths in `Competition/improvements/`.
There is no new Python package or algorithm refactor.

- [Consolidated data/model report](Competition/PROJECT_REPORT.md)
- [Complete 135-entry experiment catalog](Competition/docs/EXPERIMENT_CATALOG.md)
- [Latest submission CSV](Competition/output/submission_high_upside.csv)
- [Historical output recovery](Competition/docs/OUTPUTS.md)

The latest screenshot shows **0.77029**, rank snapshot **364**; the uploaded
filename was not explicitly confirmed. Matched local AUC improved **0.76480 to
0.76626**. The report distinguishes these evaluations.

## Current commands

From this repository's root, using the project-local venv:

```sh
Competition/.venv/bin/python Competition/project.py status
Competition/.venv/bin/python Competition/project.py verify
Competition/.venv/bin/python Competition/project.py reproduce
Competition/.venv/bin/python Competition/project.py report
```

Prediction replay loads saved models and keeps only the latest CSV. Older outputs
are recoverable from the snapshot branch. Existing notebook contents are unchanged;
execute with `Competition` as the kernel working directory and use its local venv.
The [reproduction guide](Competition/REPRODUCTION_README.md) gives detailed commands.

## Shared files

- `Competition/input/`: supplied train/test/sample data.
- `Competition/output/`: latest CSV only.
- `Competition/environment/`: original environment specifications; the installed
  `.venv` stays in place and is ignored by Git.
- `Competition/docs/`: overall catalog, integrity records, cleanup and recovery.
- `Competition/improvements/`: original implementation/evidence paths used by the
  saved models; navigate them through each round's links.

A few original root paths are relative compatibility links for existing notebooks
and IDE tabs. Actual notebook/report ownership is shown by the round folders and
[file location map](Competition/docs/file_locations.json).

## Git

There is one repository at this parent folder and one project `.gitignore`.
No remote is configured and nothing was pushed.

- `snapshot/pre-cleanup-2026-11-09`: original recovery snapshot (`b8d094c`).
- `cleanup/project-organization`: first cleanup (`02f8717`).
- `organize/round-folders`: current file organization.

Recover an old output from the original snapshot:

```sh
git restore --source=snapshot/pre-cleanup-2026-11-09 -- Competition/output/submission_round3_bagged.csv
```

Original supplied competition rules:
[Round 1's README notebook](Competition/rounds/round1/notebooks/README.ipynb).
