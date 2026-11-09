"""Primary-only complete grid, immutable choice, then independent fold partitions."""
import argparse,hashlib,itertools
from pathlib import Path
import numpy as np
import round4 as t
import r4_cv as cv

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def check_freeze():
    frozen=t.read(t.ART/'selection_freeze.json')
    for name,want in frozen['hashes'].items():assert sha(t.HERE/name)==want,name
    assert frozen['engine_signature']==t.SIGNATURE

def primary_pool():
    ps=t.with_reference(t.component_predictions('primary'));rows=[]
    for p in sorted((t.ART/'cv').glob('*.json')):
        a=t.read(p);assert a['signature']['engine_signature']==t.SIGNATURE
        rows.append(a);ps[a['name']]=np.load(p.with_name(a['name']+'_oof.npy'))
    return ps,rows

def select():
    if (t.ART/'selection_freeze.json').exists():check_freeze();return t.read(t.ART/'selection.json')
    train,test,y,split=t.load();target=y[split['development']];ps,rows=primary_pool()
    cdfs={n:np.sort(p) for n,p in ps.items()};np.savez(t.ART/'primary_cdf_references.npz',**cdfs)
    base=ps['round3_reference'];auc=t.metrics(target,base)['auc'];trials=[]
    new=[a['name'] for a in rows];old=[a['name'] for a in t.reference_families()];methods=['probability','log_odds','percentile']
    def add(names,weights,method,reason):
        recipe=dict(names=names,weights=weights,method=method)
        trials.append({**recipe,'auc':t.metrics(target,t.recipe_prediction(recipe,ps,cdfs))['auc'],'reason':reason})
    add(['round3_reference'],[1.],'probability','Unchanged round-three reference.')
    for method in methods[1:]:add(old,list(t.reference_weights().values()),method,'Reference weights with a different combination transform.')
    # Complete old/new, reference/new and new/new pairs, before confirmation.
    for a,b in itertools.combinations(old+['round3_reference']+new,2):
        if a not in new and b not in new:continue
        for w in [.1,.25,1/3,.5,2/3,.75,.9]:
            for method in methods:add([a,b],[w,1-w],method,'Direct pair, including composite reference.')
    for a,b in itertools.combinations(new,2):
        for keep in [.25,.5,.75]:
            for share in [.25,.5,.75]:
                for method in methods:add(['round3_reference',a,b],[keep,(1-keep)*share,(1-keep)*(1-share)],method,'Reference plus two helpers; unequal helper shares included.')
    trials.sort(key=lambda a:-a['auc']);t.dump(t.ART/'blend_candidates.json',trials)
    best=trials[0];passed=best['auc']-auc>=.0002
    if not passed:best=next(a for a in trials if a['names']==['round3_reference'])
    required=[a for a in rows if a['name']in best['names']]
    choice={**best,'baseline_auc':auc,'gain':best['auc']-auc,'primary_gate_passed':bool(passed),
        'fold_gains':cv.fold_gains(target,cv.PRIMARY,base,t.recipe_prediction(best,ps,cdfs)),
        'new_families':[dict(name=a['name'],spec=a['spec'],origin=a['origin'],iterations=a['iterations'],fixed_iterations=int(np.median(a['iterations']))) for a in required],
        'confirmation_seed':cv.CONFIRM,'grid_size':len(trials),'no_public_score_tuning':True}
    t.dump(t.ART/'selection.json',choice)
    names=['round4.py','r4_cv.py','r4_followup.py','r4_fraction.py','r4_validate.py','r4_final.py','r4_exact_reference.py','run_round4.py','PLAN.md',
        'artifacts/candidate_plan.json','artifacts/followup_plan.json','artifacts/promotion.json','artifacts/fraction_plan.json',
        'artifacts/fraction_feasibility.json','artifacts/selection.json','artifacts/primary_cdf_references.npz']
    t.dump(t.ART/'selection_freeze.json',dict(engine_signature=t.SIGNATURE,hashes={n:sha(t.HERE/n) for n in names if (t.HERE/n).exists()}))
    t.event('selection_frozen',**choice);print('SELECTED',choice,flush=True);return choice

def confirmation():
    check_freeze();choice=t.read(t.ART/'selection.json');out=t.ART/'confirmation_results.json'
    if out.exists():return t.read(out)
    if not choice['primary_gate_passed']:
        result=dict(passed=False,reason='Primary gain below 0.00020; no confirmation fits justified.');t.dump(out,result);return result
    train,test,y,split=t.load();dev=split['development'];target=y[dev];ps={};directory=t.ART/'confirmation'
    for row in t.reference_families()+choice['new_families']:
        fixed=row.get('fixed_iterations',int(np.median(row['iterations'])))
        cv.cv_one(row,train,y,dev,seed=cv.CONFIRM,fixed=fixed,directory=directory)
        ps[row['name']]=np.load(directory/(row['name']+'_oof.npy'))
    ps=t.with_reference(ps);cdfs=dict(np.load(t.ART/'primary_cdf_references.npz'))
    p=t.recipe_prediction(choice,ps,cdfs);base=ps['round3_reference'];gains=cv.fold_gains(target,cv.CONFIRM,base,p)
    gain=t.metrics(target,p)['auc']-t.metrics(target,base)['auc']
    result=dict(baseline=t.metrics(target,base),candidate=t.metrics(target,p),gain=gain,fold_gains=gains,
        positive_folds=sum(a>0 for a in gains),passed=bool(gain>0 and sum(a>0 for a in gains)>=4),
        validation_early_stopping=False,weights_retuned=False,fold_seed=cv.CONFIRM,
        caveat='Fresh partition of previously explored development labels; not an untouched independent test.')
    np.save(directory/'candidate_oof.npy',p);np.save(directory/'reference_oof.npy',base)
    t.dump(out,result);t.event('confirmation_complete',**result);print('CONFIRMATION',result,flush=True);return result

def averaging():
    check_freeze();choice=t.read(t.ART/'selection.json');out=t.ART/'averaging_results.json'
    if out.exists():return t.read(out)
    if not t.read(t.ART/'confirmation_results.json')['passed']:
        result=dict(passed=False,reason='Earlier gate failed; retain public-confirmed round-three CSV.');t.dump(out,result);return result
    train,test,y,split=t.load();dev=split['development'];target=y[dev];ps,rows=primary_pool()
    allps=[ps]
    for stage,seed in [('secondary',cv.SECONDARY),('third',cv.THIRD)]:
        values=t.component_predictions(stage);directory=t.ART/stage
        for row in choice['new_families']:
            cv.cv_one(row,train,y,dev,seed=seed,fixed=row['fixed_iterations'],directory=directory)
            values[row['name']]=np.load(directory/(row['name']+'_oof.npy'))
        allps.append(t.with_reference(values))
    used=[a['name'] for a in t.reference_families()]+[a['name'] for a in choice['new_families']]
    averaged={n:np.mean([p[n] for p in allps],axis=0) for n in used};averaged=t.with_reference(averaged)
    base=averaged['round3_reference'];p=t.recipe_prediction(choice,averaged,dict(np.load(t.ART/'primary_cdf_references.npz')))
    gain=t.metrics(target,p)['auc']-t.metrics(target,base)['auc'];gains=cv.fold_gains(target,cv.PRIMARY,base,p)
    import r4_fraction
    budget=r4_fraction.expanded_budget_check(averaged)
    result=dict(baseline=t.metrics(target,base),candidate=t.metrics(target,p),gain=gain,fold_gains=gains,
        positive_folds=sum(a>0 for a in gains),fraction_budget_check=budget,
        passed=bool(gain>=.0002 and sum(a>0 for a in gains)>=4 and budget['passed']),
        averaging='Average three matching family OOF vectors before applying the frozen blend transform.',
        weights_retuned=False,caveat='Repeatedly explored development labels; not independent validation.')
    np.save(t.ART/'candidate_three_seed_oof.npy',p);np.save(t.ART/'reference_three_seed_oof.npy',base)
    t.dump(out,result);t.event('averaging_complete',**result);print('AVERAGING',result,flush=True);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['select','confirmation','averaging']);a=p.parse_args();globals()[a.phase]()
