"""Additional distinct model families and feature ablations; development only."""
import time
import numpy as np
from sklearn.metrics import roc_auc_score
import experiment as e

train,test,y,dev,audit,tr,va=e.load()
rows=[]
specs=[]
for leaves in [10,20,31]:
    specs.append(dict(name=f'hgb_{leaves}',kind='hgb',features='engineered',params=dict(max_leaf_nodes=leaves,min_samples_leaf=100,l2_regularization=15.)))
for c in [.01,.1,1.]:
    specs.append(dict(name=f'spline_{c}',kind='spline',features='engineered',params=dict(C=c)))
base=dict(num_leaves=16,max_depth=-1,min_child_samples=200,colsample_bytree=1.,subsample=.9,subsample_freq=1,reg_lambda=20,reg_alpha=1.,max_bin=127)
specs.append(dict(name='lgb_engineered_groups',kind='lgb',features='engineered',groups=True,params=base))
for spec in specs:
    start=time.time(); x=e.features(train,spec['features'])
    model,enc,p,it=e.fit_model(spec,x,y,tr,va)
    row=dict(name=spec['name'],auc=roc_auc_score(y[va],p),iterations=it,seconds=time.time()-start,spec=spec)
    rows.append(row); np.save(e.ART/(row['name']+'_inner.npy'),p)
    e.save_json('supplement_results.json',rows)
    print({k:v for k,v in row.items() if k!='spec'},flush=True)
