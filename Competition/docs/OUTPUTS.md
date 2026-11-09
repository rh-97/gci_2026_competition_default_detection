# Output files and recovery

Only `output/submission_high_upside.csv` is kept in the working tree. Thirteen older CSV/replay/ZIP files (700,947,463 bytes) were removed after their exact Git blob identity and SHA-256 were recorded in [output_archive.json](output_archive.json). No data, model weights or preprocessing files were removed.

The latest CSV is reproducible byte for byte:

```sh
# From the repository root:
Competition/.venv/bin/python Competition/project.py reproduce
```

The command checks the replay and removes its temporary duplicate CSV. Older ZIPs are historical packages: recover them from the full local backup rather than expecting today's report/code state to generate the same ZIP bytes. They were excluded from all published branch histories to allow the GitHub push. Supplied input data and saved model files remain included.

Restore an individual CSV from the published snapshot, from the repository root (in a single-branch clone, first fetch `snapshot/pre-cleanup-2026-11-09`):

```sh
git restore --source=snapshot/pre-cleanup-2026-11-09 -- Competition/output/submission_round3_bagged.csv
```

Restore the historical CSVs when an older notebook requires them:

```sh
git restore --source=snapshot/pre-cleanup-2026-11-09 -- Competition/output
```

Restoring a tracked historical file stages it for addition to the current branch. `git show snapshot/pre-cleanup-2026-11-09:Competition/output/FILENAME > /tmp/FILENAME` extracts a CSV without changing the branch. Archived files are ignored if restored as untracked files.

The original repository retains the full pre-rewrite history in `.git/local-backups/before-zip-history-cleanup.bundle` (576,551,718 bytes, verified with `git bundle verify`). Local backup refs also retain the original branch heads. For example, extract a ZIP locally with:

```sh
git show refs/local-backup/pre-remote-cleanup/snapshot/pre-cleanup-2026-11-09:Competition/output/competition_high_upside_reproduction.zip > /tmp/competition_high_upside_reproduction.zip
```

These refs and the bundle are **local only**. A remote clone cannot recover those exact ZIP bytes unless the backup is supplied separately. The latest submission is reproducible from the models included in the remote repository. Keep the backup if the exact historical ZIPs matter; do not use `git push --mirror`, which would publish the old oversized history too.

The verifier checks available archived protected outputs against their Git blobs and recorded SHA-256s. In a remote clone, excluded historical ZIPs are explicitly listed as unavailable and are not counted as verified. Data, sources, notebooks, CSVs and all saved inference files remain mandatory checks.

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

Historical end-to-end notebook-generation and packaging scripts can assume the original root-level notebook layout. Use the local backup snapshot in a separate temporary worktree when recreating those historical deliveries. The current `project.py status`, `verify`, `reproduce` and `report` commands support the new layout. Existing notebook source and outputs have not been rewritten. See [the history cleanup report](REMOTE_PUSH_REPORT.md) for old/new commit mappings and push scope.
