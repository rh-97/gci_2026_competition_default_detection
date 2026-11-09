"""Descriptive error slices and conditional uncertainty, never selection inputs."""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
import round4 as t
import r4_validate as v

def interval(target,base,candidate,seed):
    if np.array_equal(base,candidate):return dict(gain=0.,conditional_ci95=[0.,0.],replicates=0,reason='Identical frozen predictions.')
    rng=np.random.default_rng(seed);pos=np.flatnonzero(target==1);neg=np.flatnonzero(target==0);gains=[]
    for _ in range(400):
        ix=np.r_[rng.choice(pos,len(pos),replace=True),rng.choice(neg,len(neg),replace=True)]
        gains.append(roc_auc_score(target[ix],candidate[ix])-roc_auc_score(target[ix],base[ix]))
    return dict(gain=float(roc_auc_score(target,candidate)-roc_auc_score(target,base)),conditional_ci95=np.quantile(gains,[.025,.975]).tolist(),replicates=400)

def main():
    v.check_freeze();train,test,y,split=t.load();dev=split['development'];target=y[dev];ps,rows=v.primary_pool()
    recipe=t.read(t.ART/'selection.json');base=ps['round3_reference'];candidate=t.recipe_prediction(recipe,ps,dict(np.load(t.ART/'primary_cdf_references.npz')))
    result=dict(caveat='Paired stratified row resampling conditions on fitted predictions and excludes fitting/search uncertainty. This is not search-adjusted inference or an untouched test.',
        primary_frozen=interval(target,base,candidate,t.SEED+4901))
    for label,basepath,candpath in [('confirmation',t.ART/'confirmation/reference_oof.npy',t.ART/'confirmation/candidate_oof.npy'),
        ('three_seed',t.ART/'reference_three_seed_oof.npy',t.ART/'candidate_three_seed_oof.npy')]:
        if basepath.exists() and candpath.exists():result[label]=interval(target,np.load(basepath),np.load(candpath),t.SEED+4902)
    t.dump(t.ART/'conditional_uncertainty.json',result)
    final=t.read(t.ART/'final_results.json');reference=t.reference_prediction(t.three_seed_components())
    p=np.load(t.ART/'candidate_three_seed_oof.npy') if final['accepted'] else reference
    data=train.iloc[dev].reset_index(drop=True);grouping={}
    for column in ['NAME_CONTRACT_TYPE','NAME_INCOME_TYPE','CODE_GENDER']:
        grouping[column]=data[column].fillna('<missing>').astype(str)
    grouping['EXT_SOURCE_missing']=data[['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3']].isna().sum(axis=1).astype(str)
    grouping['age_band']=pd.cut(-data.DAYS_BIRTH/365.25,[0,30,40,50,60,100],include_lowest=True).astype(str)
    grouping['prediction_decile']=pd.qcut(p,10,duplicates='drop').astype(str)
    records=[]
    for group,series in grouping.items():
        for value in sorted(series.unique()):
            mask=np.asarray(series==value);n=int(mask.sum());yy=target[mask];pp=p[mask]
            if not n:continue
            metrics=t.metrics(yy,pp) if len(np.unique(yy))==2 else dict(auc=None,average_precision=None,log_loss=None,brier=float(np.mean((yy-pp)**2)))
            records.append(dict(group=group,value=value,rows=n,positives=int(yy.sum()),positive_rate=float(yy.mean()),mean_prediction=float(pp.mean()),
                calibration_residual=float(yy.mean()-pp.mean()),**metrics))
    pd.DataFrame(records).to_csv(t.ART/'error_analysis.csv',index=False)
    t.dump(t.ART/'diagnostic_policy.json',dict(predictions='Accepted frozen three-seed OOF' if final['accepted'] else 'Unchanged round-three three-seed development OOF',
        decisions_changed=False,note='Exploratory slice and decile calibration metrics. Sparse groups are unstable. No specialists, manual adjustments, threshold or weights are selected from these diagnostics.'))
    print('Diagnostics complete:',result,flush=True)
if __name__=='__main__':main()
