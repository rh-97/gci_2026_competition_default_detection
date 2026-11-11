"""Paths, data loading, metrics and a small prediction cache shared by the notebooks."""
from pathlib import Path
import hashlib
import json
import time

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, log_loss

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
WORK = ROOT / 'work'            # regenerated caches (git-ignored)
OUTPUTS = ROOT / 'outputs'      # submission and result summaries (tracked)
SEED = 2026
SENTINEL_DAYS = 365243          # DAYS_EMPLOYED placeholder used for pensioners/unemployed

for folder in (WORK, WORK / 'preds', OUTPUTS):
    folder.mkdir(parents=True, exist_ok=True)


def load_raw():
    """Supplied train/test tables, unchanged."""
    return pd.read_csv(DATA / 'train.csv'), pd.read_csv(DATA / 'test.csv')


def load_features():
    """Feature table written by notebook 02: train rows first, then test rows."""
    frame = pd.read_parquet(WORK / 'features.parquet')
    sets = json.loads((WORK / 'feature_sets.json').read_text())
    train = frame[frame.IS_TEST == 0].reset_index(drop=True)
    test = frame[frame.IS_TEST == 1].reset_index(drop=True)
    return train, test, sets


def auc(y, p):
    return float(roc_auc_score(y, p))


def summary(y, p):
    return dict(auc=auc(y, p), log_loss=float(log_loss(y, np.clip(p, 1e-7, 1 - 1e-7))))


def config_hash(config):
    return hashlib.sha256(json.dumps(config, sort_keys=True, default=str).encode()).hexdigest()[:12]


def save_preds(name, oof, test, info):
    np.savez(WORK / 'preds' / f'{name}.npz', oof=oof, test=test)
    (WORK / 'preds' / f'{name}.json').write_text(json.dumps(info, indent=2, default=float))


def load_preds(name):
    arrays = np.load(WORK / 'preds' / f'{name}.npz')
    info = json.loads((WORK / 'preds' / f'{name}.json').read_text())
    return arrays['oof'], arrays['test'], info


def cached_info(name):
    path = WORK / 'preds' / f'{name}.json'
    return json.loads(path.read_text()) if path.exists() else None


class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.seconds = time.time() - self.start
