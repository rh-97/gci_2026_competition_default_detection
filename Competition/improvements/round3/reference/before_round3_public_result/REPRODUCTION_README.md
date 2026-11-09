# Reproducing the recommended submission

Recommended file: `output/submission_round3_bagged.csv`

SHA-256: `7d933ea1e9bffea4e3bf034a81a8ece315655dcebdeb9408682d159d60bbfb02`

Read `IMPROVEMENT_REPORT.md` for results and limitations, and
`ROUND3_EXPERIMENT_LOG.md` for every third-pass trial. Previous experiments are
retained in `EXPERIMENT_LOG.md`. Only notebooks 05 and 06 were created this pass;
all earlier notebooks are preserved for reference.

Use the project Python 3.12 `.venv`. Exact installed dependencies are recorded
in `improvements/round3/requirements-round3.txt`. The archive excludes the venv,
supplied input CSVs and previous ZIPs. Place the originally supplied `input`
directory beside this file. No extra dataset or pretrained weights are required.

From this directory, prediction-only replay is:

```sh
.venv/bin/python improvements/round3/bagging.py reproduce
```

Notebook 06 is the executed review/inference entry point. Its training flag is
false by default. Do not run all historical notebooks merely to generate the
recommended CSV: the saved model bank already supports inference. Full training
phase commands and cache rules are in the improvement report.

`improvements/round3/artifacts/package_manifest.json` contains SHA-256 hashes
for the packaged files. Archive creation checked each member and ZIP CRC.
