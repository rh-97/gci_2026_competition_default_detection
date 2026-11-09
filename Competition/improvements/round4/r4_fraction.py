"""Paired training-fraction experiment and conservative model-count controls."""
import numpy as np
import round4 as t
import r4_cv as cv

NAME='r4_cat_signed_tenfold'

def specs():
    original=next(a for a in t.REFERENCE['new_families'] if a['name']=='r3_cat_signed')
    spec={**original['spec'],'name':NAME,'stage':'fraction','fold_scheme':'nested10','fixed_cv_iterations':original['fixed_iterations'],
        'hypothesis':'Use paired nested-ten folds at fixed capacity to train each model on 90% of development rows.'}
    control0={**original['spec'],'name':'r4_fraction_control0','stage':'fraction','fixed_cv_iterations':original['fixed_iterations'],
        'hypothesis':'Fixed-capacity five-fold control, paired to ten-fold parent groups.'}
    control1={**control0,'name':'r4_fraction_control1','model_seed_offset':50000,
        'hypothesis':'Second five-fold model seed on the same groups; two repeats match ten-fold inference model count.'}
    return dict(name=NAME,spec=spec,origin='round3'),dict(name=control0['name'],spec=control0,origin='round3'),dict(name=control1['name'],spec=control1,origin='round3')

def replace_component(ps,p):
    result=dict(ps);result['r3_cat_signed']=p;return t.reference_prediction(result)

def feasibility():
    path=t.ART/'fraction_feasibility.json'
    if path.exists():print(t.read(path));return t.read(path)
    train,test,y,split=t.load();dev=split['development'];target=y[dev];ten,control0,control1=specs()
    plan=dict(candidate=ten,control0=control0,control1=control1,rules='PLAN.md Stage C; fixed before any fraction fit.')
    t.dump(t.ART/'fraction_plan.json',plan);t.event('fraction_plan_recorded',**plan)
    directory=t.ART/'fraction/primary'
    cv.cv_one(control0,train,y,dev,fixed=1312,directory=directory)
    candidate=cv.cv_one(ten,train,y,dev,fixed=1312,directory=t.ART/'fraction/candidate_primary')
    p5=np.load(directory/(control0['name']+'_oof.npy'));p10=np.load(t.ART/'fraction/candidate_primary'/(NAME+'_oof.npy'))
    ps=t.component_predictions('primary');base=t.reference_prediction(ps)
    ref5=replace_component(ps,p5);new=replace_component(ps,p10)
    first=dict(family_five_auc=t.metrics(target,p5)['auc'],family_ten_auc=t.metrics(target,p10)['auc'],
        family_gain=t.metrics(target,p10)['auc']-t.metrics(target,p5)['auc'],
        recipe_five_auc=t.metrics(target,ref5)['auc'],recipe_ten_auc=t.metrics(target,new)['auc'],
        recipe_gain=t.metrics(target,new)['auc']-t.metrics(target,ref5)['auc'])
    report=dict(first_comparison=first,promoted=False,rule='Require family gain >=0.00020 and recipe gain >=0.00010 before the equal-model-count control.',
        caution='Different training fractions and fold arrangements; label sets are previously explored. No validation early stopping. Model-count control is conservative because it averages two OOF predictions versus one.')
    if first['family_gain']>=.0002 and first['recipe_gain']>=.0001:
        cv.cv_one(control1,train,y,dev,fixed=1312,directory=directory)
        p52=np.load(directory/(control1['name']+'_oof.npy'));budget=(p5+p52)/2
        old=replace_component(ps,budget);gain=t.metrics(target,new)['auc']-t.metrics(target,old)['auc']
        gains=cv.fold_gains(target,cv.PRIMARY,old,new)
        report['budget_comparison']=dict(five_two_repeat_family_auc=t.metrics(target,budget)['auc'],ten_one_repeat_family_auc=t.metrics(target,p10)['auc'],
            five_two_repeat_recipe_auc=t.metrics(target,old)['auc'],ten_recipe_auc=t.metrics(target,new)['auc'],recipe_gain=gain,
            parent_group_gains=gains,final_model_counts=dict(five_control=10,ten_candidate=10))
        report['promoted']=bool(gain>=.0001 and sum(a>0 for a in gains)>=4)
    if report['promoted']:
        t.dump(t.ART/'cv'/(NAME+'.json'),candidate);np.save(t.ART/'cv'/(NAME+'_oof.npy'),p10)
    t.dump(path,report);t.event('fraction_feasibility_complete',**report);print('FRACTION',report,flush=True)
    return report

def expanded_budget_check(new_predictions):
    """Only if tenfold entered the frozen recipe; no search over its capacity."""
    choice=t.read(t.ART/'selection.json')
    if NAME not in choice['names'] or not any(n==NAME and w>0 for n,w in zip(choice['names'],choice['weights'])):
        return dict(required=False,passed=True,reason='Ten-fold family not selected.')
    train,test,y,split=t.load();dev=split['development'];target=y[dev];ten,c0,c1=specs();five=[]
    for label,seed in [('primary',cv.PRIMARY),('secondary',cv.SECONDARY),('third',cv.THIRD)]:
        directory=t.ART/'fraction'/label
        reused=None
        if label!='primary' and t.read(t.ART/'environment.json')['packages']==t.read(t.prev.ART/'environment.json')['packages']:
            olddir=t.prev.ART/('secondary' if label=='secondary' else 'confirmation')
            old=t.read(olddir/'r3_cat_signed.json')
            if old['signature']['fold_seed']==seed and old['signature']['fixed_iterations']==1312 and old['spec']['params']==c0['spec']['params'] and old['spec']['features']=='signed':
                reused=olddir/'r3_cat_signed_oof.npy'
                t.event('fraction_control_reused',seed=seed,source=str(reused.relative_to(t.ROOT)),reason='Identical data, 55-column transform, fixed capacity, parent-fold partition, paired model seeds, parameters and package versions.')
        if reused is None:
            cv.cv_one(c0,train,y,dev,seed=seed,fixed=1312,directory=directory)
            reused=directory/(c0['name']+'_oof.npy')
        cv.cv_one(c1,train,y,dev,seed=seed,fixed=1312,directory=directory)
        five += [np.load(reused),np.load(directory/(c1['name']+'_oof.npy'))]
    controls=np.mean(five,axis=0);ps=t.three_seed_components()
    old=replace_component(ps,controls);candidate=replace_component(ps,new_predictions[NAME])
    gain=t.metrics(target,candidate)['auc']-t.metrics(target,old)['auc']
    result=dict(required=True,passed=bool(gain>=.0001),five_six_repeat_recipe_auc=t.metrics(target,old)['auc'],
        ten_three_repeat_recipe_auc=t.metrics(target,candidate)['auc'],gain=gain,
        final_model_count_per_tested_family=dict(five_control=30,ten_candidate=30),
        caveat='Five-fold control averages six OOF values per row; ten-fold averages three. This favors the control in validation noise reduction.')
    t.dump(t.ART/'fraction_budget_check.json',result);return result

if __name__=='__main__':feasibility()
