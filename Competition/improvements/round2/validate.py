"""Comparable development CV, ensemble selection and fixed-iteration seed check."""
import argparse, hashlib, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import round2 as r
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

def screen_rows():
    return [r.read(p) for p in sorted((r.ART/'screen').glob('*.json')) if r.read(p)['status']=='complete']

def choose_candidates():
    rows=screen_rows(); chosen=[]
    cats=sorted([a for a in rows if a['spec']['kind']=='cat' and a['name']!='r2_cat_baseline'],key=lambda a:-a['auc'])
    chosen+=cats[:2]
    feature_trials=[a for a in cats if a['spec']['features'] in ['risk','finance','missing','combined']]
    if feature_trials and feature_trials[0] not in chosen and feature_trials[0]['auc']>=.7474925822989676:
        chosen.append(feature_trials[0])
    native=next((a for a in cats if a['name']=='r2_cat_native_missing'),None)
    if native is not None and native not in chosen and native['auc']>.7484925822989676:
        chosen.append(native)
    for kind in ['xgb','lgb']:
        group=sorted([a for a in rows if a['spec']['kind']==kind],key=lambda a:-a['auc'])
        if group: chosen.append(group[0])
    plan=[a['spec'] for a in chosen]
    r.dump(r.ART/'cv_plan.json',plan)
    return plan

def cv_one(spec,train,y,dev,seed=r.SEED+2,fixed=None,directory=None):
    directory=directory or r.ART/'cv'
    directory.mkdir(parents=True,exist_ok=True)
    path=directory/(spec['name']+'.json'); sig=r.implementation_hash()
    if path.exists():
        record=r.read(path)
        if record['spec']==spec and record['implementation_hash']==sig and record['fold_seed']==seed and record.get('fixed_iterations')==fixed:
            return record
    x=r.features(train,spec['features'])
    if 'columns' in spec: x=x[spec['columns']]
    folds=list(StratifiedKFold(5,shuffle=True,random_state=seed).split(dev,y[dev]))
    start=time.time(); r.event('cv_start',name=spec['name'],fold_seed=seed,fixed_iterations=fixed,directory=str(directory))
    fold_dir=directory/spec['name']; fold_dir.mkdir(parents=True,exist_ok=True)
    def one(item):
        k,(a,b)=item; f=fold_dir/f'fold{k}.json'; pred_file=fold_dir/f'fold{k}.npy'
        if f.exists() and pred_file.exists():
            rec=r.read(f)
            if rec['spec']==spec and rec['implementation_hash']==sig and rec['fold_seed']==seed and rec.get('fixed_iterations')==fixed:
                return k,b,np.load(pred_file),rec['iterations'],rec['auc'],rec['seconds']
        t=time.time()
        if fixed is None:
            model,enc,p,it=r.fit(spec,x,y,dev[a],dev[b],seed=r.SEED+k if seed==r.SEED+2 else seed+100+k)
        # Fixed-iteration validation does not pass the validation targets to fit.
        if fixed is not None:
            model,enc,_,it=r.fit(spec,x,y,dev[a],fixed=fixed,seed=seed+100+k)
            p=model.predict_proba(enc.transform(x.iloc[dev[b]]))[:,1]
        score=roc_auc_score(y[dev[b]],p); seconds=time.time()-t
        np.save(pred_file,p)
        resolved=model.get_all_params() if spec['kind']=='cat' else model.get_params()
        if fixed is None:
            curve=model.get_evals_result() if spec['kind']=='cat' else (model.evals_result() if spec['kind']=='xgb' else model.evals_result_)
            r.dump(fold_dir/f'fold{k}_learning_curve.json',curve)
        r.dump(f,dict(spec=spec,implementation_hash=sig,fold_seed=seed,fixed_iterations=fixed,iterations=it,auc=score,seconds=seconds,resolved_parameters=resolved))
        r.event('cv_fold_finish',name=spec['name'],fold_seed=seed,fold=k,auc=score,iterations=it,seconds=seconds)
        print('CV',spec['name'],seed,k,round(score,7),it,flush=True)
        return k,b,p,it,score,seconds
    oof=np.zeros(len(dev)); scores=[None]*5; trees=[None]*5; times=[None]*5
    with ThreadPoolExecutor(max_workers=2) as pool:
        for k,b,p,it,score,seconds in pool.map(one,enumerate(folds)):
            oof[b]=p; scores[k]=score; trees[k]=it; times[k]=seconds
    np.save(directory/(spec['name']+'_oof.npy'),oof)
    record=dict(name=spec['name'],spec=spec,implementation_hash=sig,fold_seed=seed,fixed_iterations=fixed,
        auc=roc_auc_score(y[dev],oof),fold_auc=scores,iterations=trees,fold_seconds=times,seconds=time.time()-start,
        note='Development selection estimate; not an independent untouched-test result.')
    r.dump(path,record); r.event('cv_finish',name=spec['name'],auc=record['auc'],fold_seed=seed)
    print('CV COMPLETE',spec['name'],record['auc'],flush=True)
    return record

def cv():
    # A positive adaptive ablation must be decomposed before picking finalists.
    if (r.ART/'screen/r2_cat_term_proxies.json').exists():
        import proxy_followup
        proxy_followup.main()
    train,test,y,split=r.load(); plan=choose_candidates()
    for spec in plan: cv_one(spec,train,y,split['development'])

def pool_records():
    oldrows=r.old.load_json('cv_results.json'); pool=[]
    for name in ['cat_lean','lgb_tune_15']:
        row=next(a for a in oldrows if a['name']==name)
        pool.append(dict(name=name,spec=row['spec'],auc=row['auc'],iterations=row['iterations'],origin='pass1',
            prediction_path=str((r.old.ART/(name+'_oof.npy')).relative_to(r.ROOT))))
    for path in sorted((r.ART/'cv').glob('*.json')):
        row=r.read(path); pool.append(dict(name=row['name'],spec=row['spec'],auc=row['auc'],iterations=row['iterations'],origin='pass2',
            prediction_path=str((r.ART/'cv'/(row['name']+'_oof.npy')).relative_to(r.ROOT))))
    return pool

def select():
    train,test,y,split=r.load(); target=y[split['development']]
    # The native-missing control is prespecified even when a staged CV run
    # began before this representation-ablation amendment was recorded.
    native_file=r.ART/'screen/r2_cat_native_missing.json'
    if native_file.exists():
        native=r.read(native_file)
        if native['status']=='complete' and native['auc']>.7484925822989676:
            cv_one(native['spec'],train,y,split['development'])
            cvplan=r.read(r.ART/'cv_plan.json')
            if not any(s['name']==native['name'] for s in cvplan):
                cvplan.append(native['spec']);r.dump(r.ART/'cv_plan.json',cvplan)
    pool=pool_records()
    ps={row['name']:np.load(r.ROOT/row['prediction_path']) for row in pool}
    oldsel=r.old.load_json('selection.json')
    ref=sum(w*ps[n] for n,w in zip(oldsel['names'],oldsel['weights']))
    base_auc=roc_auc_score(target,ref); candidates=[]
    def add(names,weights,method):
        p=sum(w*ps[n] for n,w in zip(names,weights))
        candidates.append(dict(names=names,weights=weights,auc=roc_auc_score(target,p),method=method))
    add(oldsel['names'],oldsel['weights'],'public-scored fallback')
    for row in pool: add([row['name']],[1.],'single model')
    for i,a in enumerate(pool):
        for b in pool[i+1:]:
            for w in [.1,.25,1/3,.5,2/3,.75,.9]: add([a['name'],b['name']],[w,1-w],'coarse two-model blend')
    for row in pool:
        if row['origin']=='pass1': continue
        for keep in [.25,.5,.75,.9]:
            add(oldsel['names']+[row['name']],[keep*w for w in oldsel['weights']]+[1-keep],
                'retain frozen public model plus a new candidate')
    pairs=[a for a in candidates if len(a['names'])==2]
    best_pair=max(pairs,key=lambda a:a['auc'])
    for row in pool:
        if row['name'] in best_pair['names']: continue
        for keep in [.5,.75,.9]:
            add(best_pair['names']+[row['name']],[keep*w for w in best_pair['weights']]+[1-keep],
                'retain best primary pair plus a complementary model')
    candidates.sort(key=lambda a:-a['auc'])
    r.dump(r.ART/'blend_candidates.json',candidates)
    best=candidates[0]
    # New submission must earn an improvement over a known public-scored file.
    if best['auc']<base_auc+.0002:
        best=next(a for a in candidates if a['method']=='public-scored fallback')
    best={**best,'baseline_auc':base_auc,'development_delta':best['auc']-base_auc,
          'models':[next(row for row in pool if row['name']==n) for n in best['names']],
          'status':'provisional: requires fixed-iteration second-seed check',
          'selection_scope':'Original development rows only. Historical audit and public labels never tune weights.'}
    p=sum(w*ps[n] for n,w in zip(best['names'],best['weights']))
    folds=list(StratifiedKFold(5,shuffle=True,random_state=r.SEED+2).split(target,target))
    best['fold_gain']=[roc_auc_score(target[b],p[b])-roc_auc_score(target[b],ref[b]) for a,b in folds]
    # Paired resampling is conditional on fitted OOF predictions; not training uncertainty.
    rng=np.random.default_rng(r.SEED+700); pos=np.flatnonzero(target==1); neg=np.flatnonzero(target==0)
    gain=[]
    for _ in range(600):
        idx=np.r_[rng.choice(pos,len(pos),True),rng.choice(neg,len(neg),True)]
        gain.append(roc_auc_score(target[idx],p[idx])-roc_auc_score(target[idx],ref[idx]))
    best['conditional_gain_ci95']=np.quantile(gain,[.025,.975]).tolist()
    r.dump(r.ART/'provisional_selection.json',best)
    plan_file=r.ART/'complexity_check_plan.json'
    pair=max([a for a in candidates if len(a['names'])==2],key=lambda a:a['auc'])
    if len(best['names'])==3 and best['auc']-pair['auc']<.00015 and set(pair['names']).issubset(best['names']) and not plan_file.exists():
        new_names=[m['name'] for m in best['models'] if m['origin']=='pass2']
        started=any(any((r.ART/'stability'/n).glob('fold*.json')) for n in new_names)
        if not started:
            r.dump(plan_file,dict(original_primary_names=best['names'],original_primary_weights=best['weights'],
                original_primary_auc=best['auc'],frozen_pair=pair,primary_increment_third=best['auc']-pair['auc'],
                rule='Drop the third model only if its incremental second-seed AUC is nonpositive and this frozen pair passes the existing primary/secondary gates. No secondary weight search.',
                prospective_guard='No new-candidate second-seed fold result existed when recorded.'))
    print('PROVISIONAL',best['names'],best['weights'],best['auc'],'gain',best['development_delta'],flush=True)

def stability():
    train,test,y,split=r.load(); dev=split['development']; chosen=r.read(r.ART/'provisional_selection.json')
    pool=pool_records(); names=list(dict.fromkeys(['cat_lean','lgb_tune_15']+chosen['names']))
    directory=r.ART/'stability'; ps={}; rows=[]
    for name in names:
        row=next(a for a in pool if a['name']==name); spec=row['spec'].copy()
        # Old specs use the original defaults; make those budgets explicit.
        if row['origin']=='pass1': spec={**spec,'max_iterations':3000 if spec['kind']=='cat' else 3500,'patience':150}
        result=cv_one(spec,train,y,dev,seed=r.SEED+301,fixed=int(np.median(row['iterations'])),directory=directory)
        ps[name]=np.load(directory/(name+'_oof.npy')); rows.append(result)
    oldsel=r.old.load_json('selection.json')
    bp=sum(w*ps[n] for n,w in zip(oldsel['names'],oldsel['weights']))
    cp=sum(w*ps[n] for n,w in zip(chosen['names'],chosen['weights']))
    folds=list(StratifiedKFold(5,shuffle=True,random_state=r.SEED+301).split(dev,y[dev]))
    gains=[roc_auc_score(y[dev[b]],cp[b])-roc_auc_score(y[dev[b]],bp[b]) for a,b in folds]
    report=dict(baseline_auc=roc_auc_score(y[dev],bp),candidate_auc=roc_auc_score(y[dev],cp),fold_gain=gains,
        fold_seed=r.SEED+301,early_stopping_on_validation=False,weights_retuned=False,
        caveat='A robustness check on development data, not a new independent test; the same development labels were used earlier in selection.')
    report['delta']=report['candidate_auc']-report['baseline_auc']
    report['recommend_new_submission']=chosen['development_delta']>=.0002 and report['delta']>0 and sum(g>0 for g in gains)>=3
    first={row['name']:np.load(r.ROOT/row['prediction_path']) for row in pool if row['name'] in names}
    bp1=sum(w*first[n] for n,w in zip(oldsel['names'],oldsel['weights']))
    cp1=sum(w*first[n] for n,w in zip(chosen['names'],chosen['weights']))
    averaged_base=roc_auc_score(y[dev],(bp1+bp)/2)
    averaged_candidate=roc_auc_score(y[dev],(cp1+cp)/2)
    report['two_seed_diagnostic']={'baseline_primary_auc':roc_auc_score(y[dev],bp1),
        'baseline_secondary_auc':report['baseline_auc'],'baseline_averaged_auc':averaged_base,
        'candidate_primary_auc':roc_auc_score(y[dev],cp1),'candidate_secondary_auc':report['candidate_auc'],
        'candidate_averaged_auc':averaged_candidate,
        'caveat':'Conditional development diagnostic, not independent evidence. The primary seed uses validation early stopping; the secondary seed uses fixed iterations.'}
    report['recommend_two_seed_bagging']=(averaged_base>max(report['baseline_auc'],roc_auc_score(y[dev],bp1))+.00015 and
        averaged_candidate>max(report['candidate_auc'],roc_auc_score(y[dev],cp1))+.00015)
    r.dump(r.ART/'stability_results.json',report)
    final={**chosen,'status':'selected after stability check' if report['recommend_new_submission'] else 'fallback: stability did not confirm gain',
           'stability':report}
    if not report['recommend_new_submission']:
        final.update(names=oldsel['names'],weights=oldsel['weights'],models=[next(a for a in pool if a['name']==n) for n in oldsel['names']])
    r.dump(r.ART/'selection.json',final)
    print('STABILITY',report,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('phase',choices=['cv','select','stability']); args=parser.parse_args()
    globals()[args.phase]()
