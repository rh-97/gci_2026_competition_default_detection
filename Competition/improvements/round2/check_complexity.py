"""Apply only the prospectively recorded frozen-pair simplification rule."""
import shutil
import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
import round2 as r
from validate import pool_records

def main():
    plan_file=r.ART/'complexity_check_plan.json'
    if not plan_file.exists():
        r.dump(r.ART/'complexity_check_results.json',{'action':'No prospective simplification plan; retain original decision.'});return
    for source,destination in [('provisional_selection.json','primary_original_winner.json'),('stability_results.json','stability_original_winner.json'),('selection.json','selection_before_complexity_check.json')]:
        if not (r.ART/destination).exists():shutil.copy2(r.ART/source,r.ART/destination)
    plan=r.read(plan_file);primary=r.read(r.ART/'primary_original_winner.json');original=r.read(r.ART/'stability_original_winner.json')
    assert primary['names']==plan['original_primary_names'] and primary['weights']==plan['original_primary_weights']
    train,test,y,split=r.load();dev=split['development'];target=y[dev];pool=pool_records()
    pair=plan['frozen_pair'];old=r.old.load_json('selection.json')
    def prediction(names,weights,secondary=False):
        arrays=[]
        for n in names:
            row=next(a for a in pool if a['name']==n)
            arrays.append(np.load(r.ART/'stability'/(n+'_oof.npy')) if secondary else np.load(r.ROOT/row['prediction_path']))
        return sum(w*p for w,p in zip(weights,arrays))
    b0=prediction(old['names'],old['weights']);b1=prediction(old['names'],old['weights'],True)
    p0=prediction(pair['names'],pair['weights']);p1=prediction(pair['names'],pair['weights'],True)
    f1=prediction(primary['names'],primary['weights'],True)
    pair_auc0=roc_auc_score(target,p0);pair_auc1=roc_auc_score(target,p1)
    base_auc0=roc_auc_score(target,b0);base_auc1=roc_auc_score(target,b1)
    fold_seed=r.SEED+301
    folds=list(StratifiedKFold(5,shuffle=True,random_state=fold_seed).split(dev,target))
    gains=[roc_auc_score(target[b],p1[b])-roc_auc_score(target[b],b1[b]) for a,b in folds]
    increment=roc_auc_score(target,f1)-pair_auc1
    eligible=pair_auc0-base_auc0>=.0002 and pair_auc1>base_auc1 and sum(g>0 for g in gains)>=3
    simplify=increment<=0 and eligible
    result=dict(rule=plan['rule'],prospective_guard=plan['prospective_guard'],pair=pair,
        full_secondary_auc=roc_auc_score(target,f1),pair_secondary_auc=pair_auc1,third_model_secondary_increment=increment,
        pair_primary_gain=pair_auc0-base_auc0,pair_secondary_gain=pair_auc1-base_auc1,pair_secondary_fold_gain=gains,
        pair_passes_original_gates=eligible,simplified=simplify,weights_retuned=False,
        caveat='Two predeclared frozen recipes are compared on reused development folds; this is model selection, not a fresh independent test.')
    if simplify:
        newprimary={**primary,**pair,'models':[next(a for a in pool if a['name']==n) for n in pair['names']],
            'baseline_auc':base_auc0,'development_delta':pair_auc0-base_auc0,
            'status':'frozen pair retained under prospective simplification rule'}
        firstfolds=list(StratifiedKFold(5,shuffle=True,random_state=r.SEED+2).split(dev,target))
        newprimary['fold_gain']=[roc_auc_score(target[b],p0[b])-roc_auc_score(target[b],b0[b]) for a,b in firstfolds]
        rng=np.random.default_rng(r.SEED+700);pos=np.flatnonzero(target==1);neg=np.flatnonzero(target==0);boot=[]
        for _ in range(600):
            ii=np.r_[rng.choice(pos,len(pos),True),rng.choice(neg,len(neg),True)]
            boot.append(roc_auc_score(target[ii],p0[ii])-roc_auc_score(target[ii],b0[ii]))
        newprimary['conditional_gain_ci95']=np.quantile(boot,[.025,.975]).tolist()
        averaged_base=roc_auc_score(target,(b0+b1)/2);averaged_pair=roc_auc_score(target,(p0+p1)/2)
        report={**original,'candidate_auc':pair_auc1,'delta':pair_auc1-base_auc1,'fold_gain':gains,
            'recommend_new_submission':True,'simplified_from_original_primary':True,
            'two_seed_diagnostic':{'baseline_primary_auc':base_auc0,'baseline_secondary_auc':base_auc1,'baseline_averaged_auc':averaged_base,
                'candidate_primary_auc':pair_auc0,'candidate_secondary_auc':pair_auc1,'candidate_averaged_auc':averaged_pair,
                'caveat':'Development averaging diagnostic; primary uses early stopping, secondary uses fixed trees. Not an independent test.'},
            'recommend_two_seed_bagging':averaged_base>max(base_auc0,base_auc1)+.00015 and averaged_pair>max(pair_auc0,pair_auc1)+.00015}
        selected={**newprimary,'status':'selected after stability check','stability':report,'complexity_decision':result}
        r.dump(r.ART/'provisional_selection.json',newprimary);r.dump(r.ART/'stability_results.json',report);r.dump(r.ART/'selection.json',selected)
    r.dump(r.ART/'complexity_check_results.json',result);r.event('complexity_check_complete',simplified=simplify,third_increment=increment)
    print('COMPLEXITY',result,flush=True)

if __name__=='__main__':main()
