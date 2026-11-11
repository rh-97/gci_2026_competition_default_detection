"""Stratified K-fold runner: out-of-fold (OOF) predictions for train, fold-averaged predictions for test.

Each seed uses its own fold split, so averaging several seeds also averages over partitions.
`augment(tr, va, seed, fold)` may add fold-dependent columns; it only ever sees labels of the
training part `tr`, which keeps label-based features honest.
Each (run name, seed) is cached in work/preds/ and reused when the configuration is unchanged.
"""
import numpy as np
from sklearn.model_selection import StratifiedKFold

from .utils import SEED, Timer, auc, cached_info, config_hash, load_preds, save_preds

N_SPLITS = 5


def folds(y, seed):
    return list(StratifiedKFold(N_SPLITS, shuffle=True, random_state=SEED + seed).split(np.zeros(len(y)), y))


def _one_seed(name, model, X, y, X_test, seed, augment, verbose):
    oof, test, rows = np.zeros(len(y)), np.zeros(len(X_test)), []
    for k, (tr, va) in enumerate(folds(y, seed)):
        with Timer() as clock:
            Xtr, Xva, Xte = (X.iloc[tr], X.iloc[va], X_test) if augment is None else augment(tr, va, seed, k)
            p_va, p_te, info = model(Xtr, y[tr], Xva, y[va], Xte, seed=SEED + 100 * seed + k)
        oof[va] = p_va
        test += p_te / N_SPLITS
        rows.append(dict(seed=seed, fold=k, auc=auc(y[va], p_va), seconds=round(clock.seconds, 1), **info))
        if verbose:
            print(f'  {name} seed {seed} fold {k}: AUC {rows[-1]["auc"]:.5f}  {info}  ({clock.seconds:.0f}s)', flush=True)
    return oof, test, rows


def run_cv(name, model, X, y, X_test, seeds=(0,), augment=None, config=None, use_cache=True, verbose=True):
    """Run `model(Xtr, ytr, Xva, yva, Xte, seed) -> (p_va, p_te, info)` over folds and seeds.

    Returns (oof, test, info); oof/test are averaged over seeds.
    """
    config = dict(config or {}, columns=list(X.columns))
    key = config_hash(config)
    oofs, tests, rows, seed_auc, minutes = [], [], [], [], 0.
    for seed in seeds:
        part = f'{name}__s{seed}'
        cached = cached_info(part)
        if use_cache and cached and cached['key'] == key:
            oof, test, info = load_preds(part)
        else:
            with Timer() as clock:
                oof, test, fold_rows = _one_seed(name, model, X, y, X_test, seed, augment, verbose)
            info = dict(key=key, config=config, seed=seed, auc=auc(y, oof), folds=fold_rows, minutes=clock.seconds / 60)
            save_preds(part, oof, test, info)
        oofs.append(oof)
        tests.append(test)
        rows += info['folds']
        seed_auc.append(info['auc'])
        minutes += info['minutes']
    oof, test = np.mean(oofs, axis=0), np.mean(tests, axis=0)
    info = dict(name=name, config=config, seeds=list(seeds), auc=auc(y, oof), seed_auc=seed_auc, folds=rows, minutes=minutes)
    save_preds(name, oof, test, info)
    if verbose:
        print(f'{name}: OOF AUC {info["auc"]:.5f}  per seed {np.round(seed_auc, 5).tolist()}  ({minutes:.1f} min of fitting)')
    return oof, test, info


def median_iterations(info):
    """Typical best iteration across folds, used to fix the training length of final models."""
    return int(np.median([row['iterations'] for row in info['folds']]))
