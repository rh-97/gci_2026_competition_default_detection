"""Conditional paired bootstrap on frozen predictions; never used for selection."""
from pathlib import Path
import sys
import numpy as np
from scipy.special import expit,logit
from sklearn.metrics import roc_auc_score
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'round4'))
import round4 as t
ART=Path(__file__).resolve().parent/'artifacts'
def interval(target,base,p,seed):
    if np.array_equal(base,p):return dict(gain=0.,ci95=[0.,0.],replicates=0,reason='Identical frozen predictions.')
    rng=np.random.default_rng(seed);pos=np.flatnonzero(target==1);neg=np.flatnonzero(target==0);values=[]
    for _ in range(400):
        ix=np.r_[rng.choice(pos,len(pos),replace=True),rng.choice(neg,len(neg),replace=True)]
        values.append(roc_auc_score(target[ix],p[ix])-roc_auc_score(target[ix],base[ix]))
    return dict(gain=float(roc_auc_score(target,p)-roc_auc_score(target,base)),ci95=np.quantile(values,[.025,.975]).tolist(),replicates=400)
def main():
    train,test,y,split=t.load();target=y[split['development']];choice=t.read(ART/'model_selection.json')
    ps={'round3_reference':t.reference_prediction(t.component_predictions('primary'))}
    for row in t.read(ART/'model_promotion.json')['chosen']:ps[row['name']]=np.load(ART/'primary_cv'/(row['name']+'_oof.npy'))
    def prediction(recipe):
        if recipe['method']=='probability':return sum(w*ps[n] for n,w in zip(recipe['names'],recipe['weights']))
        return expit(sum(w*logit(np.clip(ps[n],1e-7,1-1e-7)) for n,w in zip(recipe['names'],recipe['weights'])))
    result=dict(primary_frozen=interval(target,ps['round3_reference'],prediction(choice),t.SEED+5901),
        caveat='Paired stratified row resampling conditions on fitted OOF predictions. It omits fitting and search uncertainty; not a search-adjusted significance test or an independent test. Does not alter any gate or prediction.')
    if not choice['primary_gate_passed'] and choice['best_attempt']['names']!=['round3_reference']:
        result['primary_best_attempt_selection_diagnostic']=interval(target,ps['round3_reference'],prediction(choice['best_attempt']),t.SEED+5902)
    for label,bfile,pfile in [('confirmation',ART/'new_confirmation/reference_oof.npy',ART/'new_confirmation/candidate_oof.npy'),
        ('three_seed',ART/'model_reference_three_seed_oof.npy',ART/'model_candidate_three_seed_oof.npy')]:
        if bfile.exists() and pfile.exists():result[label]=interval(target,np.load(bfile),np.load(pfile),t.SEED+5903)
    t.dump(ART/'model_conditional_uncertainty.json',result);print(result,flush=True)
if __name__=='__main__':main()
