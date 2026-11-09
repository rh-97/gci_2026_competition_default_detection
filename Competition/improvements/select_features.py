"""Check whether removing weak/redundant columns improves development AUC."""
import time
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
import experiment as e

train,test,y,dev,audit,tr,va=e.load()
rows=e.load_json('screen_results.json')+e.load_json('supplement_results.json')+e.load_json('refine_results.json')
best=max([r for r in rows if 'spec'in r and r['spec']['kind']=='lgb'],key=lambda r:r['auc'])
spec=best['spec']; x=e.features(train,spec['features'])
model,enc,_,_=e.fit_model(spec,x,y,tr,va)
importance=pd.Series(model.booster_.feature_importance('gain'),index=model.feature_name_).sort_values(ascending=False)
importance.to_csv(e.ART/'development_feature_importance.csv')
results=[]
for n in [25,40,55,70]:
    cols=[c for c in importance.index if c in x.columns][:n]
    if len(cols)>=x.shape[1]: continue
    candidate={**spec,'name':f'lgb_top_{n}','columns':cols}
    start=time.time(); _,_,p,it=e.fit_model(candidate,x,y,tr,va)
    row=dict(name=candidate['name'],auc=roc_auc_score(y[va],p),iterations=it,seconds=time.time()-start,spec=candidate)
    results.append(row); np.save(e.ART/(row['name']+'_inner.npy'),p)
    e.save_json('feature_selection_results.json',results)
    print({k:v for k,v in row.items() if k!='spec'},flush=True)
