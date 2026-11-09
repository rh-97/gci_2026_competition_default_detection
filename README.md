# Home Credit competition project

The latest generated candidate is [submission_high_upside.csv](Competition/output/submission_high_upside.csv).
The user's latest leaderboard screenshot shows **0.77029**, rank snapshot **364**;
the uploaded filename was not explicitly confirmed. Matched local AUC improved
from **0.76480 to 0.76626**. These are different evaluations.

Read [the consolidated project report](Competition/PROJECT_REPORT.md) for the data,
preprocessing, model choices, failures, validation and results. The
[complete experiment catalog](Competition/docs/EXPERIMENT_CATALOG.md) covers all
135 recorded trials/probes. [Cleanup details](Competition/docs/CLEANUP_REPORT.md)
explain what was removed and why.

## Commands

Run from this repository's root, using the existing project venv:

```sh
Competition/.venv/bin/python Competition/project.py status
Competition/.venv/bin/python Competition/project.py verify
Competition/.venv/bin/python Competition/project.py reproduce
Competition/.venv/bin/python Competition/project.py report
```

`reproduce` loads saved models and recreates the candidate; it does not train.
See [REPRODUCTION_README.md](Competition/REPRODUCTION_README.md) for dependencies,
the original inference command and optional historical training commands. The
venv remains installed locally and is excluded from Git. No remote is configured.

## Layout

| Path | Purpose |
| --- | --- |
| `Competition/input/` | Supplied train, test and sample submission; preserved unchanged |
| `Competition/output/` | Candidate, earlier submissions, exact replays and reproduction ZIPs |
| `Competition/project.py` | Current status, integrity checks and prediction-only replay |
| `Competition/PROJECT_REPORT.md` | Consolidated explanation and results |
| `Competition/docs/` | Complete trial catalog and cleanup/recovery records |
| `Competition/*.ipynb` | Existing supplied and experiment notebooks; unchanged |
| `Competition/improvements/high_upside/` | Latest frozen fitter, preprocessing, models and evidence |
| `Competition/improvements/{round2,round3,round4}/` | Historical experiments and dependencies used by current models |
| `Competition/improvements/` | First-pass code, models, splits and audit evidence |

The import chain for the latest models uses earlier feature builders and encoders.
Those modules are required for saved-model loading and exact replay. They were
retained at their original paths rather than renamed or silently rewritten.

## Git recovery

- `snapshot/pre-cleanup-2026-11-09`: complete pre-cleanup recovery commit, including
  supplied data, weights, results and existing ZIPs; excludes the venv and Python
  caches under the pre-existing ignore rules.
- `cleanup/project-organization`: cleanup and consolidated documentation.

Inspect the snapshot without changing branches:

```sh
git show snapshot/pre-cleanup-2026-11-09:Competition/improvements/high_upside/finish_modeling.py
```

To restore a removed tracked file into the current branch:

```sh
git restore --source=snapshot/pre-cleanup-2026-11-09 -- path/to/file
```

The full existing reproduction ZIPs are preserved as historical deliveries.
Their enclosed reports reflect the state when packaged; the current report and
Git history include later leaderboard and cleanup updates. The competition rules
remain in the supplied [README notebook](Competition/README.ipynb).
