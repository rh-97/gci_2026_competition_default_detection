# Method and software attribution

The TabM model is imported from the authors' official `tabm` package, version
0.0.3, rather than claimed as a new architecture. Reference:
[Yandex Research, TabM](https://github.com/yandex-research/tabm), the official
implementation of *TabM: Advancing Tabular Deep Learning With Parameter-Efficient
Ensembling* (ICLR 2025). The repository declares Apache-2.0 licensing. Its guidance
informs independent member-loss optimization and probability averaging.

Numerical embedding layers and quantile-bin computation come from
`rtdl_num_embeddings` 0.0.12, the package used by the official TabM implementation.
Training/autograd use PyTorch 2.15.0. Installed license and project metadata are
preserved in `artifacts/software_attribution.json`; exact versions and software
download provenance are in `requirements-high-upside.txt` and
`artifacts/pip_install_report.json`.

Project-specific training loops, encoders, learned-feature construction, validation
orchestration, audits, reporting and inference wrapper are in the new `h_*.py`
files. Their hypotheses and exact procedures are recorded in `MODELING_PLAN.md`.
Existing project tree models/features are reused with their previous source and
artifact records intact.

No dataset or trained checkpoint from the method repositories was downloaded or
used. All model weights in these pilots start from local random initialization,
and training uses only the supplied rows. Method references establish provenance
and API usage, not an expected competition score.
