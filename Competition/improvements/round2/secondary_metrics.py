"""Retrospective metric audit of saved screens; never refit or tune a model."""
import numpy as np
from sklearn.metrics import roc_auc_score,average_precision_score,log_loss,brier_score_loss
from scipy.special import expit,logit
import round2 as r

def main():
    _,_,y,s=r.load();target=y[s['inner_valid']];records=[]
    files=['screen_results.json','supplement_results.json','refine_results.json','feature_selection_results.json','cat_refine_results.json']
    inputs=[]
    for file in files:
        for row in r.old.load_json(file):
            name=row['name'];array=r.old.ART/('baseline_inner.npy' if name=='tutorial_rf' else name+'_inner.npy')
            inputs.append(('pass1',row,array))
    for file in sorted((r.ART/'screen').glob('*.json')):
        row=r.read(file)
        if row['status']=='complete':inputs.append(('pass2',row,r.ART/'screen'/(row['name']+'.npy')))
    for phase,row,file in inputs:
        if not file.exists():continue
        p=np.load(file);assert len(p)==len(target) and np.isfinite(p).all()
        auc=roc_auc_score(target,p);assert abs(auc-row['auc'])<1e-10,(row['name'],auc,row['auc'])
        records.append(dict(phase=phase,name=row['name'],roc_auc=auc,average_precision=average_precision_score(target,p),
            log_loss=log_loss(target,p),brier_score=brier_score_loss(target,p),prediction_source=str(file.relative_to(r.ROOT))))
    r.dump(r.ART/'secondary_metric_audit.json',{'provenance':'Retrospective recomputation from retained prediction arrays, no fitting and no selection changes',
        'target_scope':'Original inner validation rows, all inside development','rows':len(target),'records':records})
    r.event('retrospective_metric_audit',records=len(records),fitting_performed=False)
    a=np.load(r.old.ART/'cat_depth4_oof.npy');b=np.load(r.old.ART/'lgb_tune_12_oof.npy');dev_target=y[s['development']]
    comparisons=[]
    for weight in [.5,2/3,.75]:
        comparisons.append(dict(cat_weight=weight,probability_auc=roc_auc_score(dev_target,weight*a+(1-weight)*b),
            log_odds_auc=roc_auc_score(dev_target,expit(weight*logit(a)+(1-weight)*logit(b)))))
    r.dump(r.ART/'first_pass_log_odds_diagnostic.json',dict(origin='Retrospective recomputation of earlier first-pass exploratory comparisons; no fitting or new selection',
        models=['cat_depth4','lgb_tune_12'],split='original development OOF',comparisons=comparisons,
        decision='Probability averaging beat log-odds averaging at every tested weight for this pair; not a universal claim.'))
    print('Audited saved predictions:',len(records),'ROC-AUC values match original records.')

if __name__=='__main__':main()
