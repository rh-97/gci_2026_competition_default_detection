"""Check a specific uncovered primary-grid mixture; never use secondary labels."""
import numpy as np
from sklearn.metrics import roc_auc_score
import round2 as r
from validate import pool_records

def main():
    _,_,y,split=r.load();target=y[split['development']];pool=pool_records()
    names=['r2_cat_term_proxies','lgb_tune_15','r2_xgb_finance']
    ps=[np.load(r.ROOT/next(a['prediction_path'] for a in pool if a['name']==n)) for n in names]
    primary=r.read(r.ART/'provisional_selection.json');rows=[]
    for cat_weight in [.5,2/3,.75,.8,.9]:
        weights=[cat_weight,(1-cat_weight)/2,(1-cat_weight)/2]
        p=sum(w*a for w,a in zip(weights,ps))
        rows.append(dict(names=names,weights=weights,auc=roc_auc_score(target,p)))
    best=max(rows,key=lambda a:a['auc'])
    result=dict(hypothesis='The two helper algorithms have nearly identical best pair AUCs; split their existing total weight while holding the lead CatBoost weight fixed.',
        selection_scope='Primary development predictions only; no secondary labels or new fitting',comparisons=rows,
        current_primary_auc=primary['auc'],best=best,increment=best['auc']-primary['auc'],
        further_validation_warranted=best['auc']>primary['auc']+.00015,
        note='This probe does not silently replace the frozen validated candidate. Reopen only for a material primary gain and record a new validation decision.')
    r.dump(r.ART/'balanced_helper_probe.json',result);r.event('balanced_helper_probe',increment=result['increment'],reopen=result['further_validation_warranted'])
    print(result,flush=True)

if __name__=='__main__':main()
