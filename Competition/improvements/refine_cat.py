"""Follow up the promising compact CatBoost model before final selection."""
import time
import numpy as np
from sklearn.metrics import roc_auc_score
import experiment as e

train,test,y,dev,audit,tr,va=e.load(); rows=[]
for depth,l2 in [(4,5),(6,12)]:
    spec=dict(name=f'cat_lean_depth{depth}',kind='cat',features='lean',params=dict(depth=depth,l2_leaf_reg=l2,random_strength=.5))
    x=e.features(train,'lean'); start=time.time()
    _,_,p,it=e.fit_model(spec,x,y,tr,va)
    row=dict(name=spec['name'],auc=roc_auc_score(y[va],p),iterations=it,seconds=time.time()-start,spec=spec)
    rows.append(row); np.save(e.ART/(row['name']+'_inner.npy'),p)
    e.save_json('cat_refine_results.json',rows)
    print({k:v for k,v in row.items() if k!='spec'},flush=True)
