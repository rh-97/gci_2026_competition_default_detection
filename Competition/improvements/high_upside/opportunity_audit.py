"""Decompose existing OOF ranking loss; train no models and change no predictions."""
from pathlib import Path
import sys,json,hashlib
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent/'round4'))
import round4 as t
import r4_final as saved
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
ART=HERE/'artifacts';ART.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def losses(pos,neg):
    """Unnormalized reversed-pair count, counting score ties as half errors."""
    if not len(pos) or not len(neg):return 0.
    neg=np.sort(neg);left=np.searchsorted(neg,pos,side='left');right=np.searchsorted(neg,pos,side='right')
    return float(np.sum(len(neg)-right+.5*(right-left)))

def run():
    assert Path(sys.prefix).resolve()==(t.ROOT/'.venv').resolve()
    train,test,y,split=t.load();dev=split['development'];yy=y[dev]
    p=t.reference_prediction(t.three_seed_components());data=train.iloc[dev].reset_index(drop=True)
    npair=int((yy==1).sum())*int((yy==0).sum());global_auc=roc_auc_score(yy,p)
    assert abs(losses(p[yy==1],p[yy==0])/npair-(1-global_auc))<1e-12
    groups={c:data[c].fillna('<missing>').astype(str) for c in ['NAME_CONTRACT_TYPE','NAME_INCOME_TYPE','NAME_EDUCATION_TYPE','CODE_GENDER']}
    ext=['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3']
    groups['EXT_missing_count']=data[ext].isna().sum(axis=1).astype(str)
    groups['EXT_missing_pattern']=data[ext].isna().astype(int).astype(str).agg(''.join,axis=1)
    groups['age_band']=pd.cut(-data.DAYS_BIRTH/365.25,[0,30,40,50,60,100],include_lowest=True).astype(str)
    cells=[];slices=[];summaries=[]
    for name,series in groups.items():
        labels=sorted(series.unique());matrix={}
        for a in labels:
            pos=p[(yy==1)&np.asarray(series==a)]
            for b in labels:
                neg=p[(yy==0)&np.asarray(series==b)];loss=losses(pos,neg)/npair;matrix[a,b]=loss
                cells.append(dict(group=name,positive_group=a,negative_group=b,positive_rows=len(pos),negative_rows=len(neg),
                    global_pair_weight=len(pos)*len(neg)/npair,global_auc_loss=loss,
                    cell_pair_auc=1-loss*npair/(len(pos)*len(neg)) if len(pos)*len(neg) else None))
        assert abs(sum(matrix.values())-(1-global_auc))<1e-12
        within=sum(matrix[a,a] for a in labels)
        summaries.append(dict(group=name,within_auc_loss=within,between_auc_loss=1-global_auc-within,
            within_share_of_loss=within/(1-global_auc),groups=len(labels)))
        for a in labels:
            mask=np.asarray(series==a);target=yy[mask];pred=p[mask]
            posloss=sum(matrix[a,b] for b in labels);negloss=sum(matrix[b,a] for b in labels)
            slices.append(dict(group=name,value=a,rows=int(mask.sum()),positives=int(target.sum()),negatives=int((target==0).sum()),
                positive_rate=float(target.mean()),mean_prediction=float(pred.mean()),calibration_residual=float(target.mean()-pred.mean()),
                auc=float(roc_auc_score(target,pred)) if len(np.unique(target))==2 else None,
                within_auc_loss=matrix[a,a],positive_centered_auc_loss=posloss,negative_centered_auc_loss=negloss,
                loss_involving_group=posloss+negloss-matrix[a,a],positive_share_of_total_loss=posloss/(1-global_auc),
                sparse=bool(target.sum()<100 or (target==0).sum()<100)))
    pd.DataFrame(cells).to_csv(ART/'pair_loss_cells.csv',index=False)
    pd.DataFrame(slices).to_csv(ART/'group_slices.csv',index=False)
    pd.DataFrame(summaries).to_csv(ART/'within_between_loss.csv',index=False)
    # Assess one already-saved model's generalization gap; no fitting.
    family=saved.previous_bank()['r3_cat_signed'];instance=family['seeds'][0]['instances'][0]
    tr,va,parent=t.folds(y,t.SEED+3)[0];rng=np.random.default_rng(t.SEED+5101);sample=rng.choice(tr,min(20000,len(tr)),replace=False)
    single={**family,'seeds':[dict(seed_number=0,instances=[instance])]}
    own=saved.predict_family(single,train.iloc[sample]);held=np.load(t.prev.ART/'final_folds/r3_cat_signed_s0_fold0.npy')
    assert len(held)==len(va)
    capacity=dict(model=instance['model'],own_training_sample_rows=len(sample),heldout_rows=len(va),
        own_training_sample_auc=float(roc_auc_score(y[sample],own)),heldout_auc=float(roc_auc_score(y[va],held)),
        caution='One saved model and a sampled training subset. In-sample performance is optimistic, not validation; this cannot identify the attainable AUC ceiling.')
    result=dict(reference='Frozen round-three three-seed development OOF recipe',auc=float(global_auc),rows=len(dev),
        positives=int(yy.sum()),positive_negative_pairs=npair,global_pair_loss=float(1-global_auc),
        data_sha256=sha(t.ROOT/'input/train.csv'),split_sha256=sha(t.prev.r.old.ART/'splits.npz'),
        prediction_sha256=hashlib.sha256(p.tobytes()).hexdigest(),source_sha256=sha(__file__),
        saved_capacity_diagnostic=capacity,no_models_fitted=True,predictions_changed=False,
        caveat='Exploratory attribution on repeatedly explored development labels. Pair-loss contributions are descriptive and not achievable gains or instructions to manually change predictions.')
    t.dump(ART/'audit_summary.json',result)
    print(json.dumps(result,indent=2),flush=True)
    for group in ['EXT_missing_count','NAME_CONTRACT_TYPE','NAME_INCOME_TYPE']:
        print(pd.DataFrame(slices).query('group==@group')[['value','rows','positives','auc','calibration_residual','positive_share_of_total_loss','within_auc_loss']].to_string(index=False),flush=True)
    return result

if __name__=='__main__':run()
