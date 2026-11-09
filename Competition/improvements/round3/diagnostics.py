"""Conditional paired uncertainty for frozen predictions; no selection or fitting."""
import numpy as np
from sklearn.metrics import roc_auc_score
import round3 as t
import validate as v

def interval(target,reference,candidate,seed):
    rng=np.random.default_rng(seed);pos=np.flatnonzero(target==1);neg=np.flatnonzero(target==0);gains=[]
    for _ in range(400):
        ix=np.r_[rng.choice(pos,len(pos),True),rng.choice(neg,len(neg),True)]
        gains.append(roc_auc_score(target[ix],candidate[ix])-roc_auc_score(target[ix],reference[ix]))
    return dict(gain=float(roc_auc_score(target,candidate)-roc_auc_score(target,reference)),
        conditional_gain_ci95=np.quantile(gains,[.025,.975]).tolist(),bootstrap_replicates=400,
        caveat='Paired row resampling conditions on fitted OOF predictions. It excludes fitting and selection uncertainty; this is not a search-adjusted significance test.')

def main():
    train,test,y,split=t.load();target=y[split['development']];selection=t.read(t.ART/'selection.json')
    ps,_=v.primary_pool();cdfs=dict(np.load(t.ART/'primary_cdf_references.npz'))
    results=dict(primary=interval(target,ps['round2_reference'],v.recipe_prediction(selection,ps,cdfs),t.SEED+901))
    for name,basefile,candidatefile in [('confirmation',t.ART/'confirmation/reference_oof.npy',t.ART/'confirmation/candidate_oof.npy'),
        ('two_seed',t.ART/'reference_two_seed_oof.npy',t.ART/'candidate_two_seed_oof.npy')]:
        if basefile.exists() and candidatefile.exists():results[name]=interval(target,np.load(basefile),np.load(candidatefile),t.SEED+902)
    t.dump(t.ART/'conditional_uncertainty.json',results)
    print(results,flush=True)

if __name__=='__main__':main()
