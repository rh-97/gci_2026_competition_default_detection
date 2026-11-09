# Output files and recovery

Only `output/submission_high_upside.csv` is kept in the working tree. Thirteen older CSV/replay/ZIP files (700,947,463 bytes) were removed after their exact Git blob identity and SHA-256 were recorded in [output_archive.json](output_archive.json). No data, model weights or preprocessing files were removed.

The latest CSV is reproducible byte for byte:

```sh
# From the repository root:
Competition/.venv/bin/python Competition/project.py reproduce
```

The command checks the replay and removes its temporary duplicate CSV. Older ZIPs are historical packages: restore them from Git rather than expecting today's report/code state to generate the same ZIP bytes.

Restore an individual output from the snapshot, from the repository root:

```sh
git restore --source=snapshot/pre-cleanup-2026-11-09 -- Competition/output/submission_round3_bagged.csv
```

Restore all historical outputs when an older notebook requires them:

```sh
git restore --source=snapshot/pre-cleanup-2026-11-09 -- Competition/output
```

Restoring a tracked historical file stages it for addition to the current branch. `git show snapshot/pre-cleanup-2026-11-09:Competition/output/FILENAME > /tmp/FILENAME` extracts a copy without changing the branch. Archived files are ignored if restored as untracked files. The current verifier checks archived protected outputs directly against their original Git blobs and SHA-256s rather than requiring redundant working copies.

| Archived project-relative path | Bytes |
| --- | --- |
| `output/competition_high_upside_reproduction.zip` | 285,647,605 |
| `output/competition_improved_reproduction.zip` | 41,688,283 |
| `output/competition_round2_reproduction.zip` | 146,375,355 |
| `output/competition_round3_reproduction.zip` | 212,230,170 |
| `output/submission_high_upside_reproduced.csv` | 1,667,306 |
| `output/submission_improved.csv` | 1,667,316 |
| `output/submission_reproduced.csv` | 1,667,316 |
| `output/submission_round2.csv` | 1,667,271 |
| `output/submission_round2_reproduced.csv` | 1,667,271 |
| `output/submission_round3.csv` | 1,667,271 |
| `output/submission_round3_bagged.csv` | 1,667,514 |
| `output/submission_round3_bagged_reproduced.csv` | 1,667,514 |
| `output/submission_round3_reproduced.csv` | 1,667,271 |

Historical end-to-end notebook-generation and packaging scripts can assume the original root-level notebook layout. Use the original snapshot in a separate temporary worktree when recreating those historical deliveries. The current `project.py status`, `verify`, `reproduce` and `report` commands support the new layout. Existing notebook source and outputs have not been rewritten.
