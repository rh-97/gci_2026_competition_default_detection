"""Model wrappers with one shared signature: fit on (Xtr, ytr), predict Xva and Xte.

Each factory returns `fit_predict(Xtr, ytr, Xva, yva, Xte, seed) -> (p_va, p_te, info)`.
If `iterations` is None, the validation fold is used for early stopping (development runs);
otherwise training runs for exactly `iterations` rounds/epochs (final runs).
"""
import copy
import os
import random
import warnings

import lightgbm as lgb
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from catboost import CatBoostClassifier
from sklearn.preprocessing import QuantileTransformer

THREADS = int(os.environ.get("HC_THREADS", "8"))   # CPU threads per model


def categorical_columns(X):
    return [c for c in X.columns if X[c].dtype == object or isinstance(X[c].dtype, (pd.CategoricalDtype, pd.StringDtype))]


# ---------------------------------------------------------------- LightGBM
def lightgbm(params, iterations=None, learning_rate=0.035, max_rounds=5000, patience=150):
    def fit_predict(Xtr, ytr, Xva, yva, Xte, seed):
        cats = categorical_columns(Xtr)
        levels = {c: sorted(Xtr[c].astype(str).unique()) for c in cats}

        def encode(X):  # vocabulary from the training part only; unseen values become missing
            X = X.copy()
            for c in cats:
                X[c] = pd.Categorical(X[c].astype(str), categories=levels[c])
            return X

        model = lgb.LGBMClassifier(objective='binary', n_estimators=iterations or max_rounds, learning_rate=learning_rate,
                                   random_state=seed, n_jobs=THREADS, verbosity=-1, deterministic=True,
                                   force_col_wise=True, **params)
        a, b, c = encode(Xtr), encode(Xva), encode(Xte)
        if iterations is None:
            model.fit(a, ytr, eval_X=b, eval_y=yva, eval_metric='auc',
                      callbacks=[lgb.early_stopping(patience, first_metric_only=True, verbose=False)])
            used = model.best_iteration_
        else:
            model.fit(a, ytr)
            used = iterations
        return model.predict_proba(b)[:, 1], model.predict_proba(c)[:, 1], dict(iterations=int(used))
    return fit_predict


# ---------------------------------------------------------------- CatBoost
def catboost(params, iterations=None, learning_rate=0.045, max_rounds=5000, patience=200):
    def fit_predict(Xtr, ytr, Xva, yva, Xte, seed):
        cats = categorical_columns(Xtr)

        def encode(X):
            X = X.copy()
            for c in cats:
                X[c] = X[c].astype(str)
            return X

        model = CatBoostClassifier(iterations=iterations or max_rounds, learning_rate=learning_rate, loss_function='Logloss',
                                   eval_metric='AUC', random_seed=seed, thread_count=THREADS, verbose=False,
                                   allow_writing_files=False, **params)
        a, b, c = encode(Xtr), encode(Xva), encode(Xte)
        if iterations is None:
            model.fit(a, ytr, cat_features=cats, eval_set=(b, yva), early_stopping_rounds=patience)
            used = model.get_best_iteration() + 1
        else:
            model.fit(a, ytr, cat_features=cats)
            used = iterations
        return model.predict_proba(b)[:, 1], model.predict_proba(c)[:, 1], dict(iterations=int(used))
    return fit_predict


# ---------------------------------------------------------------- TabM (neural network)
class NeuralEncoder:
    """Median-fill + missing flags + normal quantile transform for numbers; integer codes for categories (0 = unseen)."""

    def fit(self, X):
        self.cats = categorical_columns(X)
        self.nums = [c for c in X.columns if c not in self.cats]
        values = X[self.nums].to_numpy(dtype=float)
        self.medians = np.nan_to_num(np.nanmedian(values, axis=0))
        filled = np.where(np.isfinite(values), values, self.medians)
        self.quantiles = QuantileTransformer(n_quantiles=256, output_distribution='normal', subsample=None,
                                             random_state=0).fit(filled)
        z = np.c_[self.quantiles.transform(filled), ~np.isfinite(values)]
        self.keep = np.ptp(z, axis=0) > 0          # drop constant columns (e.g. never-missing flags)
        self.vocab = {c: {v: i + 1 for i, v in enumerate(sorted(X[c].astype(str).unique()))} for c in self.cats}
        self.cardinalities = [len(self.vocab[c]) + 1 for c in self.cats]
        return self

    def transform(self, X):
        values = X[self.nums].to_numpy(dtype=float)
        filled = np.where(np.isfinite(values), values, self.medians)
        numeric = np.c_[self.quantiles.transform(filled), ~np.isfinite(values)][:, self.keep].astype('float32')
        cats = np.column_stack([X[c].astype(str).map(self.vocab[c]).fillna(0).to_numpy(dtype='int64') for c in self.cats])
        return torch.from_numpy(numeric), torch.from_numpy(cats)


def _predict(model, numeric, cats):
    model.eval()
    out = []
    with torch.inference_mode():
        for start in range(0, len(numeric), 4096):
            logits = model(numeric[start:start + 4096], cats[start:start + 4096]).squeeze(-1)
            out.append(logits.sigmoid().mean(dim=1).numpy())   # average the k ensemble members
    return np.concatenate(out).astype(float)


def tabm(iterations=None, max_epochs=140, patience=20, schedule_epochs=140, k=16, n_blocks=2, d_block=128,
         dropout=0.1, learning_rate=0.002, weight_decay=0.0003, batch_size=1024, n_bins=48, d_embedding=8):
    """TabM-mini with piecewise-linear numeric embeddings (Gorishniy et al., 2024; packages `tabm`, `rtdl_num_embeddings`)."""
    import rtdl_num_embeddings
    import tabm as tabm_package

    def fit_predict(Xtr, ytr, Xva, yva, Xte, seed):
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.set_num_threads(THREADS)
        enc = NeuralEncoder().fit(Xtr)
        a_num, a_cat = enc.transform(Xtr)
        b_num, b_cat = enc.transform(Xva)
        c_num, c_cat = enc.transform(Xte)
        with warnings.catch_warnings():   # 0/1 flag columns get a single bin; harmless
            warnings.filterwarnings('ignore', message='.*has just two bin edges.*')
            bins = rtdl_num_embeddings.compute_bins(a_num, n_bins=n_bins)
        embedding = rtdl_num_embeddings.PiecewiseLinearEmbeddings(bins, d_embedding, activation=False, version='B')
        model = tabm_package.TabM.make(n_num_features=a_num.shape[1], cat_cardinalities=enc.cardinalities,
                                       num_embeddings=embedding, d_out=1, n_blocks=n_blocks, d_block=d_block,
                                       dropout=dropout, k=k, arch_type='tabm-mini')
        optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        schedule = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=schedule_epochs, eta_min=learning_rate * .05)
        target = torch.from_numpy(ytr.astype('float32'))
        generator = torch.Generator().manual_seed(seed)
        best, best_epoch, best_state = -np.inf, 0, None
        for epoch in range(1, (iterations or max_epochs) + 1):
            model.train()
            for batch in torch.randperm(len(target), generator=generator).split(batch_size):
                optimizer.zero_grad(set_to_none=True)
                logits = model(a_num[batch], a_cat[batch]).squeeze(-1)           # (batch, k)
                loss = F.binary_cross_entropy_with_logits(logits, target[batch, None].expand_as(logits))
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.)
                optimizer.step()
            schedule.step()
            if iterations is None:
                from sklearn.metrics import roc_auc_score
                score = roc_auc_score(yva, _predict(model, b_num, b_cat))
                if score > best + 1e-6:
                    best, best_epoch, best_state = score, epoch, copy.deepcopy(model.state_dict())
                if epoch - best_epoch >= patience:
                    break
        if iterations is None:
            model.load_state_dict(best_state)
        used = best_epoch if iterations is None else iterations
        return _predict(model, b_num, b_cat), _predict(model, c_num, c_cat), dict(iterations=int(used))
    return fit_predict
