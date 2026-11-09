"""Cross-fitted meta-learning feasibility screen, explicitly not fully nested."""
import time
import numpy as np
import pandas as pd
from scipy.special import logit
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold
from threadpoolctl import threadpool_limits
import round3 as t
import validate as v

def main():
    path=t.ART/'stacking_probe.json'
    if path.exists():print(t.read(path));return
    train,test,y,split=t.load();dev=split['development'];target=y[dev]
    ps=v.current_primary_components();reference=t.baseline_predictions('primary')
    x=pd.DataFrame({n:logit(np.clip(p,1e-7,1-1e-7)) for n,p in ps.items()})
    raw=train.iloc[dev].reset_index(drop=True)
    x['EXT_MISSING_COUNT']=raw[['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3']].isna().sum(axis=1).astype(str)
    x['CONTRACT']=raw.NAME_CONTRACT_TYPE.astype(str)
    x['AGE_BAND']=pd.cut(-raw.DAYS_BIRTH/365.25,[0,30,40,50,60,100]).astype(str)
    specs=[dict(name='logits_c01',C=.1,groups=False),dict(name='logits_c1',C=1.,groups=False),dict(name='logits_groups_c01',C=.1,groups=True)]
    t.dump(t.ART/'stacking_probe_specs.json',specs);t.event('stacking_probe_start',specs=specs,plan='STACKING_PROBE_PLAN.md')
    results=[];folds=list(StratifiedKFold(5,shuffle=True,random_state=t.SEED+701).split(x,target))
    with threadpool_limits(limits=1):
        for spec in specs:
            start=time.time();oof=np.zeros(len(dev));coefs=[]
            for a,b in folds:
                transform=ColumnTransformer([('logits','passthrough',list(ps))]+
                    ([('groups',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['EXT_MISSING_COUNT','CONTRACT','AGE_BAND'])] if spec['groups'] else []))
                model=make_pipeline(transform,LogisticRegression(C=spec['C'],max_iter=1000))
                model.fit(x.iloc[a],target[a]);oof[b]=model.predict_proba(x.iloc[b])[:,1]
                coefs.append(dict(features=model[0].get_feature_names_out().tolist(),weights=model[1].coef_[0].tolist(),intercept=float(model[1].intercept_[0])))
            blends=[dict(new_weight=w,**t.metrics(target,(1-w)*reference+w*oof)) for w in [.1,.25,.5,.75,1.]]
            best=max(blends,key=lambda a:a['auc']);np.save(t.ART/(spec['name']+'_meta_oof.npy'),oof)
            result=dict(spec=spec,**t.metrics(target,oof),seconds=time.time()-start,fold_coefficients=coefs,
                blends=blends,best_blend=best,gain=best['auc']-t.metrics(target,reference)['auc'])
            results.append(result);print(spec['name'],result['auc'],'best blend gain',result['gain'],flush=True)
    best=max(results,key=lambda a:a['gain'])
    report=dict(reference_auc=t.metrics(target,reference)['auc'],results=results,
        warrants_nested_followup=bool(best['gain']>=.0002),best_gain=best['gain'],
        caveat='Meta folds hold out their own meta targets, but precomputed base OOF features are not fully nested. Screening evidence only; never deploy from this probe.')
    t.dump(path,report);t.event('stacking_probe_finish',best_gain=best['gain'],warrants_nested_followup=report['warrants_nested_followup'])

if __name__=='__main__':main()
