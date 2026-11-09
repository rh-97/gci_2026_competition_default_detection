"""Final development-only checks: compact features, shallow trees, class weighting."""
import time
import numpy as np
from sklearn.metrics import roc_auc_score
import experiment as e

train,test,y,dev,audit,tr,va=e.load()
specs=[]; rows=[]
base=dict(num_leaves=16,max_depth=-1,min_child_samples=200,colsample_bytree=1.,subsample=.9,subsample_freq=1,reg_lambda=20.,reg_alpha=1.,max_bin=127)
for mode in ['lean','scores']:
    specs.append(dict(name='lgb_'+mode,kind='lgb',features=mode,params=base))
for leaves in [8,12]:
    p={**base,'num_leaves':leaves,'max_bin':255}
    specs.append(dict(name=f'lgb_small_{leaves}',kind='lgb',features='engineered',params=p))
for weight in [2.,5.]:
    specs.append(dict(name=f'lgb_weight_{weight}',kind='lgb',features='engineered',params={**base,'scale_pos_weight':weight}))
for mode in ['raw','lean']:
    specs.append(dict(name='cat_'+mode,kind='cat',features=mode,params=dict(depth=5,l2_leaf_reg=8,random_strength=.5)))
for spec in specs:
    start=time.time(); x=e.features(train,spec['features'])
    model,enc,p,it=e.fit_model(spec,x,y,tr,va)
    row=dict(name=spec['name'],auc=roc_auc_score(y[va],p),iterations=it,seconds=time.time()-start,spec=spec)
    rows.append(row); np.save(e.ART/(row['name']+'_inner.npy'),p)
    e.save_json('refine_results.json',rows)
    print({k:v for k,v in row.items() if k!='spec'},flush=True)
