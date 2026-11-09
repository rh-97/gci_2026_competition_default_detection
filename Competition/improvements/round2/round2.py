"""Second-pass local-data-only experiments; first-pass files are immutable inputs.

All selection uses the original development rows. The previously evaluated audit
is historical, not a fresh independent test. Public feedback is recorded only.
"""
from pathlib import Path
import os, sys
os.environ.setdefault('OMP_NUM_THREADS','4')
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import experiment as old
import argparse, hashlib, inspect, json, time, traceback, threading
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, log_loss
from sklearn.model_selection import StratifiedKFold
from catboost import CatBoostClassifier
from xgboost import XGBClassifier
import lightgbm as lgb

ROOT=old.ROOT
ART=HERE/'artifacts'; MODELS=HERE/'models'
for p in [ART,MODELS,ART/'screen',ART/'cv',ART/'errors']: p.mkdir(parents=True,exist_ok=True)
SEED=old.SEED
LOCK=threading.Lock()

def dump(path,value):
    path=Path(path); temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)))
    temp.replace(path)

def read(path): return json.loads(Path(path).read_text())

def event(kind,**kwargs):
    row={'time_utc':datetime.now(timezone.utc).isoformat(),'event':kind,**kwargs}
    with LOCK:
        with (ART/'events.jsonl').open('a') as f: f.write(json.dumps(row,default=str)+'\n')

def load():
    # Read the frozen split, never rewrite the first-pass split artifact.
    train=pd.read_csv(ROOT/'input/train.csv'); test=pd.read_csv(ROOT/'input/test.csv')
    split=np.load(old.ART/'splits.npz')
    return train,test,train.TARGET.to_numpy(),{k:split[k] for k in split.files}

def features(df,mode='lean'):
    if mode in ['lean','engineered','raw']: return old.features(df,mode)
    x=old.features(df,'lean')
    def ratio(a,b): return a/b.replace(0,np.nan)
    if mode in ['risk','combined']:
        ext=x[['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3']]
        logit=np.log(ext.clip(.0001,.9999)/(1-ext.clip(.0001,.9999)))
        x['EXT_LOGIT_MEAN']=logit.mean(axis=1)
        x['EXT_LOGIT_STD']=logit.std(axis=1)
        x['EXT_GEOMETRIC']=np.exp(np.log(ext.where(ext>0)).mean(axis=1))
        x['EXT_HARMONIC']=ext.notna().sum(axis=1)/(1/ext.where(ext>0)).sum(axis=1,min_count=1)
        weights=np.array([1.,2.,3.])
        x['EXT_WEIGHTED']=(ext*weights).sum(axis=1,min_count=1)/(ext.notna()*weights).sum(axis=1).replace(0,np.nan)
        x['EXT_CONSERVATIVE']=x.EXT_MEAN-x.EXT_STD.fillna(0)
        x['AGE_EXT_INTERACTION']=(-x.DAYS_BIRTH/365.25)*x.EXT_MEAN
        x['TERM_EXT_INTERACTION']=x.CREDIT_TERM*x.EXT_MEAN
    if mode in ['finance','combined']:
        # Hypothetical payment-period transforms, not reconstructed true rates.
        p=ratio(x.AMT_ANNUITY,x.AMT_CREDIT).to_numpy()
        for n in [24,36,60]:
            low=np.zeros(len(x)); high=np.ones(len(x))
            valid=np.isfinite(p)&(p>=1/n)&(p<1.)
            for _ in range(28):
                middle=(low+high)/2
                factor=middle/(-np.expm1(-n*np.log1p(middle)))
                choose=factor<p
                low=np.where(choose,middle,low); high=np.where(choose,high,middle)
            x[f'ASSUMED_PERIOD_RATE_{n}']=np.where(valid,(low+high)/2,np.nan)
        x['TERM_MULTIPLE_6_DISTANCE']=(x.CREDIT_TERM/6-np.rint(x.CREDIT_TERM/6)).abs()
        x['TERM_MULTIPLE_12_DISTANCE']=(x.CREDIT_TERM/12-np.rint(x.CREDIT_TERM/12)).abs()
        x['INCOME_MINUS_12_ANNUITIES']=x.AMT_INCOME_TOTAL-12*x.AMT_ANNUITY
        x['MARGIN_PER_PERSON']=ratio(x.INCOME_MINUS_12_ANNUITIES,x.CNT_FAM_MEMBERS)
        adults=x.CNT_FAM_MEMBERS-x.CNT_CHILDREN
        x['INCOME_PER_ADULT']=ratio(x.AMT_INCOME_TOTAL,adults)
        x['CREDIT_PER_ADULT']=ratio(x.AMT_CREDIT,adults)
        x['GOODS_OVER_INCOME']=ratio(x.AMT_GOODS_PRICE,x.AMT_INCOME_TOTAL)
        x['CREDIT_COST_AMOUNT']=x.AMT_CREDIT-x.AMT_GOODS_PRICE
    if mode in ['missing','combined']:
        cols=['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3','OWN_CAR_AGE','AMT_REQ_CREDIT_BUREAU_YEAR','DAYS_EMPLOYED']
        for c in cols: x[c+'_IS_MISSING']=x[c].isna().astype('int8')
        bits=x[['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3']].isna().astype(int)
        x['EXT_MISSING_PATTERN']=(bits.to_numpy()*[1,2,4]).sum(axis=1).astype(str)
        x['ORGANIZATION_FAMILY']=x.ORGANIZATION_TYPE.str.replace(r':.*','',regex=True)
        x['AGE_BAND_5']=((-x.DAYS_BIRTH/365.25)//5).astype('Int64').astype(str).fillna('__MISSING__')
    return x.replace([np.inf,-np.inf],np.nan)

class Encoder(old.Encoder):
    def __init__(self,kind='cat',groups=False,missing='sentinel'):
        super().__init__(kind,groups); self.missing=missing
    def fit(self,x):
        super().fit(x)
        self.medians=x.select_dtypes(include='number').median()
        return self
    def transform(self,x):
        if self.kind!='cat': return super().transform(x)
        z=x[self.columns].copy()
        for (c,v),m in self.maps.items():
            a=z[c].map(m).astype(float)
            if v=='frequency': z[c+'_FREQ']=a
            else: z[c+'_'+v+'_REL']=z[v]/a.replace(0,np.nan)
        for c in self.cats: z[c]=z[c].astype(str)
        nums=z.columns.difference(self.cats)
        if self.missing=='sentinel': z[nums]=z[nums].fillna(-999)
        elif self.missing=='median': z[nums]=z[nums].fillna(self.medians)
        z[nums]=z[nums].astype('float32')
        return z.replace([np.inf,-np.inf],np.nan)

def implementation_hash():
    text=''.join(inspect.getsource(f) for f in [features,Encoder,fit,old.features,old.Encoder])
    return hashlib.sha256(text.encode()).hexdigest()

def fit(spec,x,y,tr,va=None,fixed=None,seed=SEED):
    enc=Encoder(spec['kind'],spec.get('groups',False),spec.get('missing','sentinel')).fit(x.iloc[tr])
    a=enc.transform(x.iloc[tr]); b=enc.transform(x.iloc[va]) if va is not None else None
    p=spec['params'].copy(); maximum=spec.get('max_iterations',4500); patience=spec.get('patience',200)
    if spec['kind']=='cat':
        model=CatBoostClassifier(iterations=fixed or maximum,learning_rate=p.pop('learning_rate',.045),loss_function='Logloss',
            eval_metric='AUC',thread_count=4,random_seed=seed,allow_writing_files=False,verbose=False,**p)
        model.fit(a,y[tr],cat_features=enc.cats,eval_set=(b,y[va]) if b is not None else None,
                  early_stopping_rounds=patience if b is not None else None)
        it=model.tree_count_
    elif spec['kind']=='xgb':
        model=XGBClassifier(n_estimators=fixed or maximum,learning_rate=p.pop('learning_rate',.035),tree_method='hist',device='cpu',
            objective='binary:logistic',eval_metric='auc',enable_categorical=True,n_jobs=4,random_state=seed,
            early_stopping_rounds=patience if b is not None else None,**p)
        model.fit(a,y[tr],eval_set=[(b,y[va])] if b is not None else None,verbose=False)
        it=model.best_iteration+1 if b is not None else model.n_estimators
    else:
        model=lgb.LGBMClassifier(n_estimators=fixed or maximum,learning_rate=p.pop('learning_rate',.035),objective='binary',metric='auc',
            n_jobs=4,random_state=seed,deterministic=True,force_col_wise=True,verbosity=-1,**p)
        kwargs={} if b is None else dict(eval_set=[(b,y[va])],callbacks=[lgb.early_stopping(patience,verbose=False)])
        model.fit(a,y[tr],**kwargs); it=model.best_iteration_ or model.n_estimators
    pred=model.predict_proba(b)[:,1] if b is not None else None
    return model,enc,pred,int(it)

def candidates():
    base={'depth':5,'l2_leaf_reg':8,'random_strength':.5}
    def cat(name,feature,hypothesis,changes=None,**extra):
        return dict(name=name,kind='cat',features=feature,params={**base,**(changes or {})},hypothesis=hypothesis,**extra)
    specs=[cat('r2_cat_baseline','lean','Reproduce the first-pass compact CatBoost to verify implementation equivalence.',max_iterations=3000,patience=150)]
    for mode,why in [
        ('risk','Smooth score summaries and score/age/term interactions may help shallow trees model risk.'),
        ('finance','Payment burden, per-adult amounts and hypothetical payment-period rates may expose financial structure.'),
        ('missing','Joint missing-score patterns and coarse organization groups may expose data-collection segments.'),
        ('combined','The three targeted feature families may be complementary; their combination may also add noise.')]:
        specs.append(cat('r2_cat_'+mode,mode,why))
    for name,changes,why in [
        ('slow',{'learning_rate':.025},'Smaller boosting steps may improve the bias/variance tradeoff.'),
        ('strong_l2',{'l2_leaf_reg':30,'random_strength':1.},'Stronger leaf shrinkage may reduce overfitting in sparse categorical groups.'),
        ('weak_l2',{'l2_leaf_reg':2,'random_strength':.1},'Less shrinkage may recover useful signal suppressed by the first-pass settings.'),
        ('onehot10',{'one_hot_max_size':10},'One-hot splits for low-cardinality categories may outperform ordered target statistics.'),
        ('onehot64',{'one_hot_max_size':64},'One-hot splits for every raw category may avoid noisy target statistics, at the cost of expressiveness.'),
        ('borders512',{'border_count':512},'Finer numeric quantization may preserve useful external-score and loan-term thresholds.'),
        ('rsm075',{'rsm':.75,'bagging_temperature':1.},'Column sampling and Bayesian bootstrap may diversify trees and improve generalization.'),
        ('ordered',{'boosting_type':'Ordered','learning_rate':.06},'Ordered boosting may reduce prediction shift from fitting residuals on the training rows.')]:
        specs.append(cat('r2_cat_'+name,'lean',why,changes,max_iterations=3500 if name=='ordered' else 5000))
    specs.append(cat('r2_cat_native_missing','lean','Native numeric missing bins may handle absence differently from the -999 sentinel.',missing='native'))
    xbase=dict(max_depth=4,min_child_weight=30,reg_lambda=20.,reg_alpha=1.,subsample=.85,colsample_bytree=.85,max_bin=256)
    for depth in [3,4,5]:
        specs.append(dict(name=f'r2_xgb_d{depth}',kind='xgb',features='engineered',params={**xbase,'max_depth':depth},
            hypothesis='A separate histogram-boosting implementation may improve individual AUC or add complementary ensemble errors.'))
    specs.append(dict(name='r2_xgb_lean',kind='xgb',features='lean',params=xbase,
        hypothesis='The compact representation may also reduce noise for XGBoost.'))
    lbase=dict(num_leaves=16,min_child_samples=150,colsample_bytree=.8,subsample=.9,subsample_freq=1,reg_lambda=10.,reg_alpha=1.,max_bin=255)
    specs.append(dict(name='r2_lgb_smooth_cats',kind='lgb',features='engineered',groups=True,
        params={**lbase,'cat_smooth':100.,'cat_l2':30.},hypothesis='Stronger categorical smoothing may improve group-relative LightGBM generalization.'))
    specs.append(dict(name='r2_lgb_linear',kind='lgb',features='lean',max_iterations=1500,patience=100,
        params={**lbase,'linear_tree':True,'linear_lambda':10.,'max_bin':127},hypothesis='Linear models inside leaves may model smooth financial relationships more efficiently than constant leaves.'))
    return specs

def screen_one(spec,train,y,split):
    path=ART/'screen'/(spec['name']+'.json'); sig=implementation_hash()
    if path.exists():
        previous=read(path)
        if previous.get('implementation_hash')==sig and previous.get('spec')==spec and previous['status']=='complete': return previous
    start=time.time(); event('screen_start',name=spec['name'],spec=spec)
    row=dict(name=spec['name'],spec=spec,implementation_hash=sig,seed=SEED,split='original inner_fit/inner_valid, development only')
    try:
        x=features(train,spec['features']); tr=split['inner_fit']; va=split['inner_valid']
        model,enc,p,it=fit(spec,x,y,tr,va)
        score=roc_auc_score(y[va],p)
        np.save(ART/'screen'/(spec['name']+'.npy'),p)
        baseline=np.load(old.ART/'cat_lean_inner.npy')
        row.update(status='complete',auc=score,average_precision=average_precision_score(y[va],p),log_loss=log_loss(y[va],p),
            iterations=it,features=x.shape[1],seconds=time.time()-start,auc_delta_vs_pass1_cat=score-roc_auc_score(y[va],baseline),
            prediction_correlation=float(np.corrcoef(p,baseline)[0,1]),maximum_prediction_difference=float(np.max(np.abs(p-baseline))),
            saturated=it>=spec.get('max_iterations',4500)-5)
    except Exception as exc:
        error=traceback.format_exc(); (ART/'errors'/(spec['name']+'.txt')).write_text(error)
        row.update(status='failed',error=str(exc),seconds=time.time()-start)
    dump(path,row); event('screen_finish',**{k:v for k,v in row.items() if k!='spec'})
    print({k:v for k,v in row.items() if k not in ['spec','implementation_hash']},flush=True)
    return row

def screen():
    train,test,y,split=load(); specs=candidates(); dump(ART/'candidate_plan.json',specs)
    # Verify the baseline first; run the other CPU fits two at a time (8 cores).
    first=screen_one(specs[0],train,y,split)
    if first['status']!='complete' or first['maximum_prediction_difference']>1e-10:
        raise RuntimeError('Baseline equivalence failed; investigate before trusting new comparisons.')
    # Cheap alternative-family probes first, followed by the CatBoost experiments.
    ordered=[s for s in specs[1:] if s['kind']!='cat']+[s for s in specs[1:] if s['kind']=='cat']
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda spec:screen_one(spec,train,y,split),ordered))
    event('screen_complete',candidates=len(specs))

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('phase',choices=['screen']); args=parser.parse_args()
    globals()[args.phase]()
