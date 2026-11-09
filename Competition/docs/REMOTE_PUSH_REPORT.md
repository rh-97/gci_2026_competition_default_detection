# Remote publication and large-file cleanup

Prepared on 10 November 2026 for `origin`, <https://github.com/rh-97/gci_competition_2026>.

The GitHub push was blocked by generated reproduction ZIPs in older commits. Deleting a file from the current folder does not remove its earlier Git objects. Installing Git LFS also does not convert earlier commits. The existing LFS rules covered only `.psd` and `.mp4`, and no files were actually stored as LFS pointers.

We used the requested alternative: exclude the generated ZIPs from the histories being published. Supplied train/test data, saved models and encoders, experiment results, notebooks, code, reports and the latest submission remain included. No notebook contents, model fitting code or predictions were changed.

## What was excluded

| Generated archive | Original bytes |
| --- | ---: |
| `Competition/output/competition_high_upside_reproduction.zip` | 285,647,605 |
| `Competition/output/competition_improved_reproduction.zip` | 41,688,283 |
| `Competition/output/competition_round2_reproduction.zip` | 146,375,355 |
| `Competition/output/competition_round3_reproduction.zip` | 212,230,170 |

All four packages were excluded, including the smaller first package, because the project already retains their source and inference artifacts. Adding them to LFS would duplicate large generated deliveries and require LFS storage/download capacity. The existing PSD/MP4 LFS rules were preserved.

The largest remaining Git blob is `Competition/input/train.csv`, **44,260,698 bytes**. The branch-history scan found **zero ZIP blobs and zero blobs at or above 100 MiB**. The new ignore rule prevents accidental ZIP additions.

## Full local recovery

Before rewriting anything, a full Git bundle was created and verified:

- Bundle: `.git/local-backups/before-zip-history-cleanup.bundle`
- Size: **576,551,718 bytes**
- Local backup refs: `refs/local-backup/pre-remote-cleanup/…`
- Local original-head record: `.git/local-backups/before-zip-history-cleanup.json`

The backup includes the original branch heads and the older pinned snapshot used for output recovery. Original archive blobs and SHA-256 records are retained locally. No garbage collection or pruning was run. These backup refs and the bundle are not intended for the remote; **do not push with `--mirror`**.

The repository stays in its existing parent folder. No second persistent project repository was created. The temporary clone used for validation was outside the workspace.

## Branch histories

Only the three local branch histories were rewritten. Their file trees were compared with the corresponding original heads: differences were restricted to the four ZIP paths and `.gitignore`. The current branch then received the recovery documentation and verifier updates described below.

| Branch | Before ZIP filtering | Immediately after ZIP filtering |
| --- | --- | --- |
| `snapshot/pre-cleanup-2026-11-09` | `04e7a5ad906017a7bfe5b3336549b6bbc1aaaff7` | `4ac92c23e019c4847d99c6b2d79c0bd9108b01b1` |
| `cleanup/project-organization` | `34210f8e42234d84fa103ab8be4054eb57b4a2b9` | `67e5f6f6ecc701e54b95977714723fa43bd8ba76` |
| `organize/round-folders` | `5f619c57e2a78581286aba9adba4f5b215078824` | `ec831c939e0a91686265d009e47dccac597a8760` |

The current branch advances beyond the last hash when these documentation and verification changes are committed. Historical experiment reports retain their original audit IDs; those original commits belong to the local backup history. Machine-readable details are in [REMOTE_HISTORY_CLEANUP.json](REMOTE_HISTORY_CLEANUP.json).

## Recovery and verification changes

[output_archive.json](output_archive.json) now points CSV recovery at the published snapshot commit. It distinguishes `published_snapshot` CSVs from `local_backup_only` ZIPs, retaining original sizes, Git blob IDs and SHA-256s for both. [OUTPUTS.md](OUTPUTS.md) explains both recovery paths.

The verifier still requires the protected input data, source files, notebooks, CSVs, frozen modeling selections and all inference artifacts. If an excluded historical ZIP is available locally, its real blob is hashed and checked. In a remote clone, an unavailable generated ZIP is listed explicitly and is not counted as verified. Other missing files remain errors; stored checksums alone are never treated as successful file verification.

Validation used the existing `Competition/.venv`:

- Original repository: **231 protected files verified**, including the retained local historical ZIP objects; **180 inference files checked**.
- Fresh `--no-local` single-branch clone: all four excluded ZIP objects were confirmed absent; the pending verifier/documentation changes were copied into this clone for testing. **228 protected files verified**, with the three protected historical ZIPs explicitly reported unavailable; **180 inference files checked**.
- A negative check temporarily removed the clone's `train.csv`. Verification failed as required; the clone's file was restored afterward.
- The latest submission checksum remains `15d050aa8709ae4e2d338b013c03216d4b3f3279348a3faca71080c17e44baed`.
- Saved modeling-source/selection freezes and executed-notebook checks passed. No retraining was performed.

See [REMOTE_CLONE_VERIFICATION.json](REMOTE_CLONE_VERIFICATION.json) for the clean-clone check. The original repository's `model_verification.json` records its local check; rerunning the command in a remote clone produces the narrower, explicit ZIP-availability result.

## Publication scope

The remote had no branches or tags immediately before publication, so an ordinary push can create the three branches without force. Only `cleanup/project-organization`, `organize/round-folders` and `snapshot/pre-cleanup-2026-11-09` are publication targets; local archive, backup and filter-branch recovery refs are excluded.
