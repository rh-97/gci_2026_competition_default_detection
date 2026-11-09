"""Local-data-only Home Credit experiments. Run with ../.venv/bin/python.

Selection: inner development split -> development CV -> one untouched audit.
No ID features, target-derived input features, resampling, or external data.
"""
from pathlib import Path
import os
os.environ.setdefault('OMP_NUM_THREADS', '4')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '4')
import argparse, hashlib, json, time, warnings
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import roc_auc_score, average_precision_score, log_loss, brier_score_loss
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.preprocessing import QuantileTransformer, SplineTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
import lightgbm as lgb
from catboost import CatBoostClassifier
import optuna

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT/'improvements/artifacts'
MODELS = ROOT/'improvements/models'
for directory in [ART,MODELS,ROOT/'output']:
    directory.mkdir(parents=True,exist_ok=True)
SEED = 20261108
warnings.filterwarnings('ignore', category=FutureWarning)

def save_json(name, obj):
    (ART/name).write_text(json.dumps(obj, indent=2, default=lambda x: x.item() if isinstance(x, np.generic) else str(x)))

def load_json(name):
    return json.loads((ART/name).read_text())

def fold_map(function, folds, kind):
    """Two native CatBoost fits use the eight CPUs; results stay in fold order."""
    if kind=='cat':
        with ThreadPoolExecutor(max_workers=2) as executor:
            yield from executor.map(function,enumerate(folds))
    else:
        yield from map(function,enumerate(folds))

def load():
    train = pd.read_csv(ROOT/'input/train.csv')
    test = pd.read_csv(ROOT/'input/test.csv')
    y = train.TARGET.to_numpy()
    idx = np.arange(len(y))
    dev, audit = train_test_split(idx, test_size=.2, stratify=y, random_state=SEED)
    fit, valid = train_test_split(dev, test_size=.25, stratify=y[dev], random_state=SEED+1)
    np.savez(ART/'splits.npz', development=dev, audit=audit, inner_fit=fit, inner_valid=valid)
    return train, test, y, dev, audit, fit, valid

def features(df, mode='engineered'):
    x = df.drop(columns=['TARGET','SK_ID_CURR'], errors='ignore').copy()
    x['DAYS_EMPLOYED'] = x.DAYS_EMPLOYED.replace(365243, np.nan).astype('float64')
    for c in x.select_dtypes(include=['object','str']).columns:
        x[c] = x[c].fillna('__MISSING__').astype(str)
    if mode == 'raw': return x
    raw_columns=list(x.columns)
    def ratio(a,b):
        return a/b.replace(0, np.nan)
    x['EMPLOYED_SENTINEL'] = df.DAYS_EMPLOYED.eq(365243).astype('int8')
    x['MISSING_COUNT'] = df.drop(columns=['TARGET','SK_ID_CURR'], errors='ignore').isna().sum(axis=1)
    amounts = ['AMT_INCOME_TOTAL','AMT_CREDIT','AMT_ANNUITY','AMT_GOODS_PRICE']
    for i,a in enumerate(amounts):
        for b in amounts[i+1:]: x[f'{a}_OVER_{b}'] = ratio(x[a],x[b])
    x['CREDIT_TERM'] = ratio(x.AMT_CREDIT,x.AMT_ANNUITY)
    x['CREDIT_GOODS_DIFF'] = x.AMT_CREDIT-x.AMT_GOODS_PRICE
    x['CREDIT_GOODS_DIFF_RATIO'] = ratio(x.CREDIT_GOODS_DIFF,x.AMT_GOODS_PRICE)
    x['INCOME_PER_PERSON'] = ratio(x.AMT_INCOME_TOTAL,x.CNT_FAM_MEMBERS)
    x['CREDIT_PER_PERSON'] = ratio(x.AMT_CREDIT,x.CNT_FAM_MEMBERS)
    x['ANNUITY_PER_PERSON'] = ratio(x.AMT_ANNUITY,x.CNT_FAM_MEMBERS)
    x['INCOME_AFTER_ANNUITY'] = x.AMT_INCOME_TOTAL-x.AMT_ANNUITY
    x['NON_CHILDREN'] = x.CNT_FAM_MEMBERS-x.CNT_CHILDREN
    x['CHILDREN_FRACTION'] = ratio(x.CNT_CHILDREN,x.CNT_FAM_MEMBERS)
    x['AGE_YEARS'] = -x.DAYS_BIRTH/365.25
    x['EMPLOYED_YEARS'] = -x.DAYS_EMPLOYED/365.25
    x['AGE_AT_EMPLOYMENT'] = x.AGE_YEARS-x.EMPLOYED_YEARS
    for c in ['DAYS_EMPLOYED','DAYS_REGISTRATION','DAYS_ID_PUBLISH','DAYS_LAST_PHONE_CHANGE']:
        x[c+'_OVER_BIRTH'] = ratio(x[c],x.DAYS_BIRTH)
    x['PHONE_OVER_EMPLOYED'] = ratio(x.DAYS_LAST_PHONE_CHANGE,x.DAYS_EMPLOYED)
    x['CAR_OVER_AGE'] = ratio(x.OWN_CAR_AGE,x.AGE_YEARS)
    ext=x[['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3']]
    for agg in ['mean','min','max','std','sum']:
        x['EXT_'+agg.upper()] = getattr(ext,agg)(axis=1)
    x['EXT_COUNT'] = ext.notna().sum(axis=1)
    x['EXT_PRODUCT'] = ext.prod(axis=1, min_count=3)
    for a,b in [(1,2),(1,3),(2,3)]:
        x[f'EXT_{a}_{b}_PRODUCT'] = x[f'EXT_SOURCE_{a}']*x[f'EXT_SOURCE_{b}']
        x[f'EXT_{a}_{b}_DIFF'] = x[f'EXT_SOURCE_{a}']-x[f'EXT_SOURCE_{b}']
    x['EXT_MEAN_OVER_AGE'] = ratio(x.EXT_MEAN,x.AGE_YEARS)
    x['EXT_MEAN_TIMES_TERM'] = x.EXT_MEAN*x.CREDIT_TERM
    req=['AMT_REQ_CREDIT_BUREAU_'+v for v in ['HOUR','MON','QRT','YEAR']]
    x['BUREAU_SUM'] = x[req].sum(axis=1,min_count=1)
    x['CONTACT_FLAGS_SUM'] = x[['FLAG_MOBIL','FLAG_EMP_PHONE','FLAG_WORK_PHONE']].sum(axis=1)
    x['EDUCATION_RANK'] = x.NAME_EDUCATION_TYPE.map({'Lower secondary':0,'Secondary / secondary special':1,'Incomplete higher':2,'Higher education':3,'Academic degree':4})
    if mode == 'extended':
        for c in amounts: x[c+'_LOG'] = np.log1p(x[c].clip(lower=0))
        for a,b in [('CODE_GENDER','NAME_EDUCATION_TYPE'),('OCCUPATION_TYPE','NAME_EDUCATION_TYPE'),('NAME_INCOME_TYPE','ORGANIZATION_TYPE'),('NAME_CONTRACT_TYPE','NAME_HOUSING_TYPE')]:
            x[a+'__'+b] = x[a]+'|'+x[b]
        x['AGE_BIN'] = (x.AGE_YEARS//5).astype('Int64').astype(str)
        x['EMPLOYED_BIN'] = (x.EMPLOYED_YEARS//3).astype('Int64').astype(str)
    if mode=='lean':
        keep=raw_columns+['EMPLOYED_SENTINEL','MISSING_COUNT','CREDIT_TERM','CREDIT_GOODS_DIFF_RATIO',
             'INCOME_PER_PERSON','AMT_INCOME_TOTAL_OVER_AMT_ANNUITY','AMT_INCOME_TOTAL_OVER_AMT_CREDIT',
             'DAYS_EMPLOYED_OVER_BIRTH','EXT_MEAN','EXT_MIN','EXT_MAX','EXT_STD','EXT_COUNT','AGE_AT_EMPLOYMENT']
        x=x[keep]
    if mode=='scores':
        x=x[raw_columns+[c for c in x if c.startswith('EXT_') and c not in raw_columns]+['EMPLOYED_SENTINEL','MISSING_COUNT']]
    for c in x.select_dtypes(include=['object','str']).columns:
        x[c] = x[c].fillna('__MISSING__').astype(str)
    return x.replace([np.inf,-np.inf],np.nan)

class Encoder:
    """Categorical vocabulary and optional unsupervised aggregates fitted per fold."""
    def __init__(self, kind='lgb', groups=False): self.kind,self.groups=kind,groups
    def fit(self,x):
        self.columns=list(x.columns)
        self.cats=list(x.select_dtypes(include=['object','str']).columns)
        self.levels={c:sorted(x[c].unique().tolist()) for c in self.cats}
        self.maps={}
        if self.groups:
            for c in ['ORGANIZATION_TYPE','OCCUPATION_TYPE','NAME_EDUCATION_TYPE','NAME_INCOME_TYPE','AGE_BIN']:
                if c not in x: continue
                self.maps[(c,'frequency')]=x[c].value_counts(normalize=True)
                for val in ['AMT_INCOME_TOTAL','AMT_CREDIT','AMT_ANNUITY','EXT_MEAN']:
                    if val not in x: continue
                    self.maps[(c,val)] = x.groupby(c, observed=True)[val].median()
        return self
    def transform(self,x):
        z=x[self.columns].copy()
        for (c,v),m in self.maps.items():
            a=z[c].map(m).astype(float)
            if v=='frequency': z[c+'_FREQ']=a
            else: z[c+'_'+v+'_REL']=z[v]/a.replace(0,np.nan)
        for c in self.cats:
            if self.kind=='cat': z[c]=z[c].astype(str)
            else: z[c]=pd.Categorical(z[c].where(z[c].isin(self.levels[c])),categories=self.levels[c])
        if self.kind=='cat':
            nums=z.columns.difference(self.cats)
            z[nums]=z[nums].fillna(-999).astype('float32')
        return z.replace([np.inf,-np.inf],np.nan)

def fit_model(spec, x, y, tr, va=None, fixed=None, seed=SEED):
    kind=spec['kind']
    if 'columns' in spec: x=x[spec['columns']]
    enc=Encoder(kind, spec.get('groups',False)).fit(x.iloc[tr])
    a=enc.transform(x.iloc[tr]); b=enc.transform(x.iloc[va]) if va is not None else None
    p=spec['params'].copy()
    if kind=='lgb':
        model=lgb.LGBMClassifier(objective='binary',n_estimators=fixed or 3500, learning_rate=.035,
                verbosity=-1,n_jobs=4,random_state=seed,deterministic=True,force_col_wise=True,**p)
        kwargs={} if b is None else dict(eval_set=[(b,y[va])],eval_metric='auc',callbacks=[lgb.early_stopping(150,first_metric_only=True,verbose=False)])
        model.fit(a,y[tr],**kwargs)
        iteration=model.best_iteration_ or model.n_estimators
    elif kind=='cat':
        model=CatBoostClassifier(iterations=fixed or 3000,learning_rate=.045,loss_function='Logloss',eval_metric='AUC',
                thread_count=4,random_seed=seed,verbose=False,allow_writing_files=False,**p)
        model.fit(a,y[tr],cat_features=enc.cats,eval_set=(b,y[va]) if b is not None else None,
                  early_stopping_rounds=150 if b is not None else None)
        iteration=model.tree_count_
    elif kind=='hgb':
        # pandas category dtype enables native categorical splits.
        model=HistGradientBoostingClassifier(max_iter=fixed or 1800,learning_rate=.05,
                scoring='roc_auc',early_stopping=fixed is None,n_iter_no_change=50,
                validation_fraction=.15,random_state=seed,**p)
        model.fit(a,y[tr]); iteration=model.n_iter_
    elif kind=='spline':
        cats=enc.cats; nums=list(a.columns.difference(cats))
        pre=ColumnTransformer([
            ('numeric',make_pipeline(SimpleImputer(strategy='median',add_indicator=True),
                QuantileTransformer(n_quantiles=100,output_distribution='uniform',random_state=seed),
                SplineTransformer(n_knots=5,degree=3,knots='uniform',include_bias=False)),nums),
            ('categorical',OneHotEncoder(handle_unknown='ignore'),cats)],sparse_threshold=1.)
        model=make_pipeline(pre,LogisticRegression(max_iter=700,solver='lbfgs',**p))
        model.fit(a,y[tr]); iteration=1
    pred=model.predict_proba(b)[:,1] if b is not None else None
    return model,enc,pred,int(iteration)

def baseline(train,y,tr,va):
    """Tutorial-equivalent RF, with preprocessing fitted only on training split."""
    cols=['NAME_CONTRACT_TYPE','AMT_INCOME_TOTAL','EXT_SOURCE_2','OWN_CAR_AGE','ORGANIZATION_TYPE']
    def prep(t,counts,mean):
        a=t[cols].copy()
        a.NAME_CONTRACT_TYPE=a.NAME_CONTRACT_TYPE.map({'Cash loans':0,'Revolving loans':1})
        a.ORGANIZATION_TYPE=a.ORGANIZATION_TYPE.map(counts).fillna(0)
        a.EXT_SOURCE_2=a.EXT_SOURCE_2.fillna(mean)
        car=(a.OWN_CAR_AGE.where(a.OWN_CAR_AGE<60)//10)
        a=a.drop(columns='OWN_CAR_AGE')
        for i in range(6): a[f'CAR_{i}']=car.eq(i).astype(int)
        return a
    counts=train.iloc[tr].ORGANIZATION_TYPE.value_counts(); mean=train.iloc[tr].EXT_SOURCE_2.mean()
    a=prep(train.iloc[tr],counts,mean); b=prep(train.iloc[va],counts,mean)
    model=RandomForestClassifier(n_estimators=100,max_depth=10,random_state=0,n_jobs=4).fit(a,y[tr])
    return model.predict_proba(b)[:,1]

def screen(trials=24):
    train,test,y,dev,audit,tr,va=load()
    print('Baseline',flush=True)
    pred=baseline(train,y,tr,va)
    records=[dict(name='tutorial_rf',auc=roc_auc_score(y[va],pred))]
    print(records[-1],flush=True)
    np.save(ART/'baseline_inner.npy',pred)
    candidates=[]
    def evaluate(spec):
        start=time.time(); x=features(train,spec['features'])
        model,enc,pred,it=fit_model(spec,x,y,tr,va)
        row=dict(name=spec['name'],auc=roc_auc_score(y[va],pred),iterations=it,seconds=time.time()-start,spec=spec)
        records.append(row); candidates.append(row)
        np.save(ART/(spec['name']+'_inner.npy'),pred)
        save_json('screen_results.json',records)
        print({k:v for k,v in row.items() if k!='spec'},flush=True)
        return row['auc']
    base=dict(num_leaves=24,max_depth=-1,min_child_samples=100,colsample_bytree=.9,subsample=.85,subsample_freq=1,reg_lambda=10,reg_alpha=.1,max_bin=127)
    for mode in ['raw','engineered','extended']:
        evaluate(dict(name='lgb_'+mode,kind='lgb',features=mode,params=base))
    evaluate(dict(name='lgb_grouped',kind='lgb',features='extended',groups=True,params=base))
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study=optuna.create_study(direction='maximize',sampler=optuna.samplers.TPESampler(seed=SEED,n_startup_trials=8))
    def objective(t):
        p=dict(num_leaves=t.suggest_int('num_leaves',12,56),min_child_samples=t.suggest_int('min_child_samples',50,350),
               colsample_bytree=t.suggest_float('colsample_bytree',.6,1),subsample=t.suggest_float('subsample',.65,1),subsample_freq=1,
               reg_lambda=t.suggest_float('reg_lambda',.1,60,log=True),reg_alpha=t.suggest_float('reg_alpha',.001,10,log=True),
               max_bin=t.suggest_categorical('max_bin',[63,127,255]),max_depth=-1)
        mode=t.suggest_categorical('features',['engineered','extended'])
        groups=t.suggest_categorical('groups',[False,True])
        return evaluate(dict(name=f'lgb_tune_{t.number:02}',kind='lgb',features=mode,groups=groups,params=p))
    study.optimize(objective,n_trials=trials)
    study.trials_dataframe().to_csv(ART/'optuna_trials.csv',index=False)
    for depth,l2 in [(4,5),(5,8),(6,8),(7,12)]:
        evaluate(dict(name=f'cat_depth{depth}',kind='cat',features='engineered',params=dict(depth=depth,l2_leaf_reg=l2,random_strength=.5)))
    # Independent linear family tests whether blending can add a different signal.
    x=features(train,'extended'); cat=list(x.select_dtypes(include=['object','str']).columns); num=list(x.columns.difference(cat))
    pre=ColumnTransformer([('numeric',make_pipeline(SimpleImputer(strategy='median',add_indicator=True),StandardScaler()),num),
                           ('category',OneHotEncoder(handle_unknown='ignore'),cat)])
    for c in [.01,.1,1.]:
        model=make_pipeline(pre,LogisticRegression(C=c,max_iter=1000,solver='lbfgs'))
        model.fit(x.iloc[tr],y[tr]); pred=model.predict_proba(x.iloc[va])[:,1]
        name=f'logistic_{c}'; np.save(ART/(name+'_inner.npy'),pred)
        records.append(dict(name=name,auc=roc_auc_score(y[va],pred)))
        print(records[-1],flush=True)
    save_json('screen_results.json',records)
    print('SCREEN COMPLETE',flush=True)

def cv(kind='all', resume=False):
    train,test,y,dev,audit,tr,va=load()
    rows=load_json('screen_results.json')
    if (ART/'supplement_results.json').exists(): rows+=load_json('supplement_results.json')
    if (ART/'refine_results.json').exists(): rows+=load_json('refine_results.json')
    if (ART/'feature_selection_results.json').exists(): rows+=load_json('feature_selection_results.json')
    if (ART/'cat_refine_results.json').exists(): rows+=load_json('cat_refine_results.json')
    lgbrows=sorted([r for r in rows if 'spec'in r and r['spec']['kind']=='lgb'],key=lambda r:-r['auc'])
    cats=sorted([r for r in rows if 'spec'in r and r['spec']['kind']=='cat'],key=lambda r:-r['auc'])
    selected=lgbrows[:3]+cats[:3]
    others=sorted([r for r in rows if 'spec' in r and r['spec']['kind'] not in ['lgb','cat']],key=lambda r:-r['auc'])
    for model_kind in sorted({r['spec']['kind'] for r in others}):
        selected.append(next(r for r in others if r['spec']['kind']==model_kind))
    # Include an unengineered ablation to validate the feature gain across folds.
    selected += [r for r in lgbrows if r['name'] in ['lgb_raw','lgb_engineered'] and r not in selected]
    if kind!='all': selected=[r for r in selected if r['spec']['kind']==kind]
    results=load_json('cv_results.json') if resume and (ART/'cv_results.json').exists() else []
    folds=list(StratifiedKFold(5,shuffle=True,random_state=SEED+2).split(dev,y[dev]))
    for row in selected:
        if any(r['name']==row['name'] and r['spec']==row['spec'] for r in results): continue
        spec=row['spec']; x=features(train,spec['features']); oof=np.zeros(len(dev)); iterations=[]; scores=[]
        def one_fold(item):
            k,(a,b)=item
            model,enc,pred,it=fit_model(spec,x,y,dev[a],dev[b],seed=SEED+k)
            return k,b,pred,it
        for k,b,pred,it in fold_map(one_fold,folds,spec['kind']):
            oof[b]=pred; iterations.append(it); scores.append(roc_auc_score(y[dev[b]],pred))
            print('CV',spec['name'],k,round(scores[-1],6),it,flush=True)
        np.save(ART/(spec['name']+'_oof.npy'),oof)
        results.append(dict(name=spec['name'],auc=roc_auc_score(y[dev],oof),fold_auc=scores,iterations=iterations,spec=spec))
        save_json('cv_results.json',results)
    # Search only simple, coarse mixtures on development OOF predictions.
    results=sorted(results,key=lambda r:-r['auc']); best=results[0]
    blendrows=[]; target=y[dev]
    for i,a in enumerate(results):
        pa=np.load(ART/(a['name']+'_oof.npy'))
        for b in results[i+1:]:
            pb=np.load(ART/(b['name']+'_oof.npy'))
            for w in [.25,1/3,.5,2/3,.75]:
                p=w*pa+(1-w)*pb
                blendrows.append(dict(names=[a['name'],b['name']],weights=[w,1-w],auc=roc_auc_score(target,p)))
    blendrows.sort(key=lambda r:-r['auc'])
    save_json('blend_candidates.json',blendrows)
    # Require a small meaningful CV gain to justify extra complexity.
    winner=blendrows[0] if blendrows and blendrows[0]['auc']>best['auc']+.00015 else dict(names=[best['name']],weights=[1.],auc=best['auc'])
    # Only a few family-diverse triples; require another incremental gain to
    # pay for the third model, rather than searching a fine weight grid.
    families={k:[r for r in results if r['spec']['kind']==k] for k in ['lgb','cat','hgb','spline']}
    triples=[]
    if families['lgb'] and families['cat']:
        first=families['lgb'][0]; second=families['cat'][0]
        for family in ['hgb','spline']:
            if families[family]: triples.append([first,second,families[family][0]])
        if len(families['lgb'])>1: triples.append([first,families['lgb'][1],second])
        if len(families['cat'])>1: triples.append([first,second,families['cat'][1]])
    if len(winner['names'])==2:
        anchor=[next(r for r in results if r['name']==n) for n in winner['names']]
        for family in families.values():
            extra=next((r for r in family if r['name'] not in winner['names']),None)
            if extra is not None: triples.append(anchor+[extra])
    triple_rows=[]
    for triple in triples:
        ps=[np.load(ART/(r['name']+'_oof.npy')) for r in triple]
        weight_sets=[[.5,.25,.25],[.25,.5,.25],[.25,.25,.5],[1/3]*3]
        if [r['name'] for r in triple[:2]]==winner['names']:
            weight_sets += [[s*winner['weights'][0],s*winner['weights'][1],1-s] for s in [.5,.75,.9]]
        for weights in weight_sets:
            pred=sum(w*p for w,p in zip(weights,ps))
            triple_rows.append(dict(names=[r['name'] for r in triple],weights=weights,auc=roc_auc_score(target,pred)))
    triple_rows.sort(key=lambda r:-r['auc']); save_json('triple_blend_candidates.json',triple_rows)
    if triple_rows and triple_rows[0]['auc']>winner['auc']+.00015: winner=triple_rows[0]
    winner['models']=[next(r for r in results if r['name']==n) for n in winner['names']]
    save_json('selection.json',winner)
    print('CV SELECTION',winner,flush=True)

def metrics(y,p):
    return dict(roc_auc=roc_auc_score(y,p),average_precision=average_precision_score(y,p),log_loss=log_loss(y,p),brier=brier_score_loss(y,p))

def audit():
    train,test,y,dev,hold,tr,va=load(); selection=load_json('selection.json')
    # Freeze selection before ever scoring the audit. No early stopping on audit.
    pred=np.zeros(len(hold)); training_pred=np.zeros(len(dev))
    save_json('selection_freeze.json',dict(sha256=hashlib.sha256((ART/'selection.json').read_bytes()).hexdigest(),
              note='Selection and iteration counts frozen before audit model fitting or scoring.'))
    for w,row in zip(selection['weights'],selection['models']):
        spec=row['spec']; x=features(train,spec['features']); it=int(np.median(row['iterations']))
        model,enc,_,_=fit_model(spec,x,y,dev,fixed=it)
        p=model.predict_proba(enc.transform(x.iloc[hold]))[:,1]
        training_pred+=w*model.predict_proba(enc.transform(x.iloc[dev]))[:,1]
        np.save(ART/(row['name']+'_audit.npy'),p); pred+=w*p
    bp=baseline(train,y,dev,hold)
    np.savez(ART/'audit_predictions.npz',indices=hold,target=y[hold],improved=pred,baseline=bp)
    rng=np.random.default_rng(SEED); pos=np.flatnonzero(y[hold]==1); neg=np.flatnonzero(y[hold]==0)
    diffs=[]; aucs=[]
    for _ in range(1500):
        ii=np.r_[rng.choice(pos,len(pos),replace=True),rng.choice(neg,len(neg),replace=True)]
        auc=roc_auc_score(y[hold][ii],pred[ii]); aucs.append(auc)
        diffs.append(auc-roc_auc_score(y[hold][ii],bp[ii]))
    report=dict(baseline=metrics(y[hold],bp),improved=metrics(y[hold],pred),development_training=metrics(y[dev],training_pred),
                auc_ci95=np.quantile(aucs,[.025,.975]).tolist(),auc_gain_ci95=np.quantile(diffs,[.025,.975]).tolist(),
                audit_rows=len(hold),selection=selection)
    save_json('audit_results.json',report)
    sub=[]
    for c in ['CODE_GENDER','NAME_CONTRACT_TYPE','NAME_INCOME_TYPE','NAME_EDUCATION_TYPE']:
        values=train.iloc[hold][c].to_numpy()
        for v in np.unique(values):
            mask=values==v
            if mask.sum()>=100 and len(np.unique(y[hold][mask]))==2:
                sub.append(dict(feature=c,group=v,rows=int(mask.sum()),defaults=int(y[hold][mask].sum()),auc=roc_auc_score(y[hold][mask],pred[mask])))
    pd.DataFrame(sub).to_csv(ART/'audit_subgroups.csv',index=False)
    print('AUDIT',report,flush=True)

def final():
    import joblib
    train,test,y,dev,audit,tr,va=load(); selection=load_json('selection.json'); allidx=np.arange(len(y))
    folds=list(StratifiedKFold(5,shuffle=True,random_state=SEED+3).split(allidx,y))
    blend=np.zeros(len(test)); oofblend=np.zeros(len(y)); stats=[]
    for w,row in zip(selection['weights'],selection['models']):
        spec=row['spec']; x=features(train,spec['features']); xt=features(test,spec['features'])
        # Match final fold training size to development-fit size. Fixed iteration
        # counts were selected without final validation labels.
        it=int(np.median(row['iterations'])); tp=np.zeros(len(test)); oof=np.zeros(len(y))
        importance=[]
        def one_final_fold(item):
            k,(a,b)=item
            model,enc,_,_=fit_model(spec,x,y,a,fixed=it,seed=SEED+100+k)
            return k,b,model,enc
        for k,b,model,enc in fold_map(one_final_fold,folds,spec['kind']):
            p=model.predict_proba(enc.transform(x.iloc[b]))[:,1]; oof[b]=p
            tp+=model.predict_proba(enc.transform(xt))[:,1]/5
            if spec['kind']=='lgb':
                model.booster_.save_model(str(MODELS/f'{row["name"]}_fold{k}.txt'))
                importance.append(pd.Series(model.booster_.feature_importance(importance_type='gain'),index=model.feature_name_))
            elif spec['kind']=='cat':
                model.save_model(str(MODELS/f'{row["name"]}_fold{k}.cbm'))
                importance.append(pd.Series(model.feature_importances_,index=model.feature_names_))
            else:
                joblib.dump(model,MODELS/f'{row["name"]}_fold{k}.joblib')
            joblib.dump(enc.__dict__,MODELS/f'{row["name"]}_fold{k}_encoder.joblib')
            print('FINAL',row['name'],k,roc_auc_score(y[b],p),flush=True)
        if importance: pd.concat(importance,axis=1).mean(axis=1).sort_values(ascending=False).rename('importance').to_csv(ART/(row['name']+'_importance.csv'))
        np.save(ART/(row['name']+'_test.npy'),tp); np.save(ART/(row['name']+'_full_oof.npy'),oof)
        blend+=w*tp; oofblend+=w*oof
        stats.append(dict(name=row['name'],iterations=it,full_oof_auc=roc_auc_score(y,oof)))
    sample=pd.read_csv(ROOT/'input/sample_submission.csv'); sub=sample.copy(); sub['TARGET']=blend
    assert list(sub.columns)==['SK_ID_CURR','TARGET'] and len(sub)==len(test)
    assert sub.SK_ID_CURR.equals(test.SK_ID_CURR) and sub.SK_ID_CURR.equals(sample.SK_ID_CURR)
    assert sub.SK_ID_CURR.is_unique and np.isfinite(blend).all() and ((blend>=0)&(blend<=1)).all()
    output=ROOT/'output/submission_improved.csv'; sub.to_csv(output,index=False)
    pd.DataFrame({'SK_ID_CURR':train.SK_ID_CURR,'TARGET':y,'prediction':oofblend}).to_csv(ART/'final_oof.csv',index=False)
    save_json('final_results.json',dict(models=stats,full_oof=metrics(y,oofblend),submission=str(output),
            rows=len(sub),prediction_min=float(blend.min()),prediction_max=float(blend.max()),prediction_mean=float(blend.mean()),
            sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
            caveat='Full-data OOF is diagnostic: development labels previously influenced model selection. Use untouched audit for an independent estimate.'))
    print('SUBMISSION',output,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('phase',choices=['screen','cv','audit','final']); parser.add_argument('--trials',type=int,default=24)
    parser.add_argument('--kind',default='all',choices=['all','lgb','cat','hgb','spline'])
    parser.add_argument('--resume',action='store_true',help='Reuse CV results only for this exact dataset and source.')
    args=parser.parse_args()
    if args.phase=='screen': screen(args.trials)
    elif args.phase=='cv': cv(args.kind,args.resume)
    else: globals()[args.phase]()
