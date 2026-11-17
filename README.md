# Home Credit default risk (GCI Global 2026)

Code that reproduces the submitted predictions. Everything about the approach (data findings, features, models,
validation, results and what did not work) is explained in the notebooks; a summary of the whole strategy is at the
end of notebook 05. The notebooks are saved with their outputs, so they can be read without running them.

## Contents

| Path | What it does |
| --- | --- |
| `notebooks/01_data_exploration.ipynb` | Explores the data |
| `notebooks/02_feature_engineering.ipynb` | Builds the label-free features and same-person pairs → `work/` |
| `notebooks/03_base_models.ipynb` | Trains the reference models |
| `notebooks/04_new_ideas.ipynb` | Screens new ideas and trains the final models |
| `notebooks/05_ensemble_and_submission.ipynb` | Blends the models and writes `outputs/submission.csv` |
| `src/` | Shared helpers: paths and caching (`utils.py`), cross-validation (`cv.py`), model wrappers (`models.py`) |

## How to run

The steps below were developed and tested on macOS (Apple silicon) with conda. Linux uses the same commands;
Windows needs different paths and a different loop, given separately. The Linux and Windows commands have not
been tested, so small adjustments may be needed on those platforms.

**1. Data.** Put the supplied files in a `data/` folder next to `notebooks/`:

```
data/train.csv
data/test.csv
data/sample_submission.csv
```

**2. Environment and run.** Requires [conda](https://docs.conda.io/) (Miniconda or Anaconda). Run the commands from
the project folder (the one containing `README.md`).

### macOS (tested) and Linux

```sh
# Environment (Python 3.12). llvm-openmp provides the OpenMP runtime that LightGBM needs on macOS.
conda create -p ./.venv python=3.12 llvm-openmp
.venv/bin/pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Run the notebooks in order
cd notebooks
export HC_DEVICE=mps   # macOS with Apple silicon only: neural network on the GPU. Leave out on Linux (CPU).
for nb in 0*.ipynb; do
  ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 "$nb"
done
```

On Linux, if conda reports that `llvm-openmp` is not available, leave it out: LightGBM then uses the system's
OpenMP library (`libgomp`), which most distributions include.

### Windows (PowerShell; not tested)

```powershell
# Environment (Python 3.12). In a conda environment on Windows, python.exe sits in .venv\ and tools in .venv\Scripts\.
conda create -p .\.venv python=3.12
.\.venv\python.exe -m pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Run the notebooks in order
cd notebooks
Get-ChildItem 0*.ipynb | Sort-Object Name | ForEach-Object {
  ..\.venv\Scripts\jupyter.exe nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 $_.Name
}
```

Use an "Anaconda PowerShell Prompt", or a PowerShell where `conda` works. `llvm-openmp` is not needed: the Windows
builds of LightGBM use the OpenMP runtime of the Microsoft Visual C++ Redistributable (install it if `import
lightgbm` fails). `HC_DEVICE` is not used on Windows; everything runs on the CPU.

**3. Result.** The submission is written to `outputs/submission.csv`. Intermediate results go to `work/`: features,
and each model's predictions per seed. A re-run only computes what is not cached yet; delete `work/` to start from
scratch.

## Notes

* **Run time.** About 9 hours on an M1 MacBook with `HC_DEVICE=mps`, mostly the neural network (9 seeds, about
  30 minutes each) and CatBoost (about 25 minutes per seed). On a CPU only (Linux, Windows, or macOS without
  `HC_DEVICE`), the neural network takes roughly twice as long.
* **Threads.** 8 CPU threads by default. To change: `export HC_THREADS=4` (macOS/Linux) or `$env:HC_THREADS = "4"`
  (Windows PowerShell), before running the notebooks.
* **Tested setup.** The macOS steps were followed exactly in a new environment on an M1 MacBook. The notebooks ran
  without errors, and the predictions matched the submitted file up to rounding (largest difference about 1e-14;
  same blend weights and scores).
* **If `import lightgbm` fails on macOS** with `Library not loaded: @rpath/libomp.dylib`, the OpenMP runtime is
  missing: run `conda install -p ./.venv llvm-openmp`.
* **If `import torch` fails on macOS** with `OMP: Error #15`, two OpenMP copies are loaded. Fix: replace
  `.venv/lib/python3.12/site-packages/torch/lib/libomp.dylib` with a symlink to `.venv/lib/libomp.dylib`.
* **Repeatability.** All seeds are fixed. CatBoost and neural-network results can differ in the 4th decimal between
  machines (x86 vs ARM, CPU vs GPU). For the submitted file, the extra CatBoost seeds (3–5) and neural-network seeds
  (3–8) were trained in separate processes with exactly the same code and settings as notebook 04 and picked up from
  its cache. A re-run therefore reproduces the submission up to such small floating-point differences.
