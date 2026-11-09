"""Controlled third-pass promotion, OOF comparison and frozen confirmation."""
import argparse,hashlib,time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.special import expit,logit
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
import round3 as t

PRIMARY=t.SEED+2
SECONDARY=t.SEED+301
CONFIRM=t.SEED+1101

def families():
    old=t.read(t.r.ART/'selection.json')
    return [dict(name=a['name'],spec=a['spec'],iterations=a['iterations'],origin='round2',weight=w)
        for a,w in zip(old['models'],old['weights'])]

def current_primary_components():
    out={}
    for a in families():
        name=a['name'];path=t.r.ART/'cv'/(name+'_oof.npy')
        if not path.exists():path=t.r.old.ART/(name+'_oof.npy')
        out[name]=np.load(path)
    return out

def current_secondary_components():
    return {a['name']:np.load(t.r.ART/'stability'/(a['name']+'_oof.npy')) for a in families()}

def add_reference(predictions):
    ps=dict(predictions)
    ps['round2_reference']=sum(a['weight']*ps[a['name']] for a in families())
    return ps

def recipe_prediction(recipe,ps,cdfs=None):
    weights=recipe['weights'];names=recipe['names'];method=recipe['method']
    if method=='probability':return sum(w*ps[n] for n,w in zip(names,weights))
    if method=='log_odds':return expit(sum(w*logit(np.clip(ps[n],1e-7,1-1e-7)) for n,w in zip(names,weights)))
    if method=='percentile':
        assert cdfs is not None
        return sum(w*(np.searchsorted(cdfs[n],ps[n],side='right')+.5)/(len(cdfs[n])+1) for n,w in zip(names,weights))
    raise ValueError(method)

def cv_one(row,train,y,dev,seed=PRIMARY,fixed=None,directory=None):
    directory=directory or t.ART/'cv';directory.mkdir(parents=True,exist_ok=True)
    spec=row['spec'];name=row['name'];origin=row.get('origin','round3')
    signature=dict(spec=spec,origin=origin,implementation_hash=t.implementation_hash(),fold_seed=seed,fixed_iterations=fixed)
    path=directory/(name+'.json')
    if path.exists() and t.read(path).get('signature')==signature:return t.read(path)
    if origin=='round2':
        x=t.r.features(train,spec['features'])
        if 'columns'in spec:x=x[spec['columns']]
        fitting=t.r.fit
    else:x=t.features(train,spec['features']);fitting=t.fit
    folds=list(StratifiedKFold(5,shuffle=True,random_state=seed).split(dev,y[dev]))
    start=time.time();t.event('cv_start',name=name,fold_seed=seed,fixed=fixed)
    fold_dir=directory/name;fold_dir.mkdir(exist_ok=True)
    def one(item):
        k,(a,b)=item;meta=fold_dir/f'fold{k}.json';file=fold_dir/f'fold{k}.npy'
        if meta.exists() and file.exists() and t.read(meta).get('signature')==signature:
            rec=t.read(meta);return k,b,np.load(file),rec['iterations'],rec['auc'],rec['seconds']
        began=time.time();model_seed=t.SEED+k if seed==PRIMARY else seed+100+k
        if fixed is None:model,enc,p,it=fitting(spec,x,y,dev[a],dev[b],seed=model_seed)
        else:
            model,enc,_,it=fitting(spec,x,y,dev[a],fixed=fixed,seed=model_seed)
            p=model.predict_proba(enc.transform(x.iloc[dev[b]]))[:,1]
        seconds=time.time()-began;score=roc_auc_score(y[dev[b]],p)
        np.save(file,p);t.dump(meta,dict(signature=signature,iterations=it,auc=score,seconds=seconds))
        if fixed is None:
            curve=model.round3_learning_curve_ if spec['kind']=='mlp' else (model.get_evals_result() if spec['kind']=='cat' else (model.evals_result() if spec['kind']=='xgb' else model.evals_result_))
            t.dump(fold_dir/f'fold{k}_curve.json',curve)
        t.event('cv_fold_finish',name=name,seed=seed,fold=k,auc=score,iterations=it,seconds=seconds)
        print('CV',name,seed,k,round(score,7),it,flush=True)
        return k,b,p,it,score,seconds
    oof=np.zeros(len(dev));scores=[None]*5;trees=[None]*5;times=[None]*5
    if spec['kind']=='mlp':results=map(one,enumerate(folds))
    else:
        pool=ThreadPoolExecutor(max_workers=2);results=pool.map(one,enumerate(folds))
    try:
        for k,b,p,it,score,seconds in results:
            oof[b]=p;scores[k]=score;trees[k]=it;times[k]=seconds
    finally:
        if spec['kind']!='mlp':pool.shutdown()
    np.save(directory/(name+'_oof.npy'),oof)
    rec=dict(name=name,spec=spec,origin=origin,signature=signature,auc=roc_auc_score(y[dev],oof),fold_auc=scores,
        iterations=trees,fold_seconds=times,seconds=time.time()-start)
    t.dump(path,rec);t.event('cv_finish',name=name,seed=seed,auc=rec['auc'])
    print('CV COMPLETE',name,rec['auc'],flush=True)
    return rec

def promote():
    plan=t.read(t.ART/'candidate_plan.json');allrows=t.screen_rows()
    if (t.HERE/'FOLLOWUP_PLAN.md').exists():assert (t.ART/'followup_plan.json').exists(),'Execute the recorded follow-up before promotion.'
    if (t.ART/'followup_plan.json').exists():plan+=t.read(t.ART/'followup_plan.json')
    assert len(allrows)==len(plan),'Finish initial screening before promotion.'
    rows=[a for a in allrows if a['status']=='complete' and a['name']!='r3_cat_baseline']
    chosen=[]
    for group,limit in [('cat',2),('other_tree',1),('mlp',1)]:
        def belongs(a):return a['spec']['kind']in ['lgb','xgb'] if group=='other_tree' else a['spec']['kind']==group
        eligible=[a for a in rows if belongs(a) and a['best_blend']['auc']-a['reference_auc']>=.00010]
        eligible.sort(key=lambda a:-a['best_blend']['auc']);chosen+=eligible[:limit]
    report=dict(rule='At most 2 CatBoost, 1 other tree, 1 neural model; inner-blend gain >=0.00010.',
        chosen=[dict(name=a['name'],spec=a['spec'],origin='round3',screen_auc=a['auc'],screen_blend=a['best_blend']) for a in chosen],
        decisions=[dict(name=a['name'],promoted=any(a['name']==b['name'] for b in chosen),
            inner_gain=a['best_blend']['auc']-a['reference_auc']) for a in rows])
    path=t.ART/'promotion.json'
    if path.exists():assert t.read(path)==report
    else:t.dump(path,report);t.event('promotion_frozen',names=[a['name'] for a in chosen])
    print('PROMOTED',[a['name'] for a in chosen],flush=True)
    return report['chosen']

def cv():
    chosen=promote();train,test,y,split=t.load()
    for row in chosen:cv_one(row,train,y,split['development'])

def primary_pool():
    ps=add_reference(current_primary_components());rows=[]
    for file in sorted((t.ART/'cv').glob('*.json')):
        row=t.read(file);rows.append(row);ps[row['name']]=np.load(t.ART/'cv'/(row['name']+'_oof.npy'))
    return ps,rows

def fold_gains(y,dev,seed,reference,candidate):
    return [float(roc_auc_score(y[dev[b]],candidate[b])-roc_auc_score(y[dev[b]],reference[b]))
        for a,b in StratifiedKFold(5,shuffle=True,random_state=seed).split(dev,y[dev])]

def select():
    if (t.ART/'selection.json').exists() and (t.ART/'selection_freeze.json').exists():
        frozen=t.read(t.ART/'selection_freeze.json')
        assert hashlib.sha256((t.ART/'selection.json').read_bytes()).hexdigest()==frozen['selection_sha256']
        for name,want in frozen.get('source_hashes',{}).items():
            assert hashlib.sha256((t.HERE/name).read_bytes()).hexdigest()==want,name
        print('Reusing frozen selection; no retuning.',flush=True);return
    train,test,y,split=t.load();dev=split['development'];target=y[dev]
    ps,rows=primary_pool();cdfs={n:np.sort(p) for n,p in ps.items()}
    np.savez(t.ART/'primary_cdf_references.npz',**cdfs)
    base=ps['round2_reference'];base_auc=roc_auc_score(target,base);candidates=[]
    def add(names,weights,method,why):
        recipe=dict(names=names,weights=weights,method=method)
        p=recipe_prediction(recipe,ps,cdfs)
        candidates.append({**recipe,'auc':float(roc_auc_score(target,p)),'why':why})
    add(['round2_reference'],[1.],'probability','Frozen current recipe, fair one-seed development comparison.')
    names=[a['name'] for a in families()];weights=[a['weight'] for a in families()]
    for method in ['log_odds','percentile']:add(names,weights,method,'Same current families/weights, change only prediction combination.')
    for row in rows:
        for w in [.1,.25,.5,.75,1.]:
            for method in ['probability','log_odds','percentile']:
                add(['round2_reference',row['name']],[1-w,w],method,'Coarse blend with the complete current recipe.')
    # A prospective primary-only amendment adds direct family replacement.
    # Anchoring every pair to the old composite can miss a stronger new pair.
    direct_names=[a['name'] for a in families()]+[a['name'] for a in rows]
    for i,a in enumerate(direct_names):
        for b in direct_names[i+1:]:
            if not (a.startswith('r3_') or b.startswith('r3_')):continue
            for w in [.1,.25,1/3,.5,2/3,.75,.9]:
                for method in ['probability','log_odds','percentile']:
                    add([a,b],[w,1-w],method,'Coarse direct old/new or new/new family pair; pair_grid_amendment.json.')
    # Only three predeclared equal-helper allocations, no continuous optimizer.
    for i,a in enumerate(rows):
        for b in rows[i+1:]:
            for keep in [.25,.5,.75]:
                add(['round2_reference',a['name'],b['name']],[keep,(1-keep)/2,(1-keep)/2],'probability','Two complementary helpers with equal new-model weights.')
    candidates.sort(key=lambda a:-a['auc']);t.dump(t.ART/'blend_candidates.json',candidates)
    t.dump(t.ART/'blend_methods.json',dict(reference_auc=base_auc,
        results=[a for a in candidates if a['why'].startswith('Same current')],
        percentile_note='Primary OOF empirical CDFs use predictions only, no target fitting. They are frozen and transferred to subsequent checks and inference. This is a ranking transform, not calibrated probability estimation. Primary score remains a selection diagnostic.'))
    best=candidates[0]
    passed=best['auc']>=base_auc+.00020
    if not passed:best=next(a for a in candidates if a['names']==['round2_reference'])
    required=[next(a for a in rows if a['name']==n) for n in best['names'] if n.startswith('r3_')]
    choice={**best,'baseline_auc':base_auc,'gain':best['auc']-base_auc,'primary_gate_passed':passed,
        'fold_gains':fold_gains(y,dev,PRIMARY,base,recipe_prediction(best,ps,cdfs)),
        'new_families':[dict(name=a['name'],spec=a['spec'],origin='round3',iterations=a['iterations'],fixed_iterations=int(np.median(a['iterations']))) for a in required],
        'confirmation_seed':CONFIRM,'status':'frozen before confirmation' if passed else 'fallback: primary gain below 0.00020'}
    t.dump(t.ART/'selection.json',choice)
    t.dump(t.ART/'selection_freeze.json',dict(selection_sha256=hashlib.sha256((t.ART/'selection.json').read_bytes()).hexdigest(),
        cdf_sha256=hashlib.sha256((t.ART/'primary_cdf_references.npz').read_bytes()).hexdigest(),implementation_hash=t.implementation_hash(),
        source_hashes={name:hashlib.sha256((t.HERE/name).read_bytes()).hexdigest() for name in ['round3.py','validate.py','finalize.py','followup.py','PLAN.md','FOLLOWUP_PLAN.md','STACKING_PROBE_PLAN.md','reference/validation_reference_hashes.json','artifacts/candidate_plan.json','artifacts/followup_plan.json','artifacts/pair_grid_amendment.json'] if (t.HERE/name).exists()}))
    print('SELECTED',choice,flush=True)

def confirmation():
    choice=t.read(t.ART/'selection.json')
    assert hashlib.sha256((t.ART/'selection.json').read_bytes()).hexdigest()==t.read(t.ART/'selection_freeze.json')['selection_sha256']
    if not choice['primary_gate_passed']:
        t.dump(t.ART/'confirmation_results.json',dict(passed=False,reason='Primary gate failed; no confirmation fitting justified.'));return
    train,test,y,split=t.load();dev=split['development'];ps={};directory=t.ART/'confirmation'
    for row in families()+choice['new_families']:
        fixed=int(np.median(row['iterations']));cv_one(row,train,y,dev,seed=CONFIRM,fixed=fixed,directory=directory)
        ps[row['name']]=np.load(directory/(row['name']+'_oof.npy'))
    ps=add_reference(ps);cdfs=dict(np.load(t.ART/'primary_cdf_references.npz'))
    candidate=recipe_prediction(choice,ps,cdfs);base=ps['round2_reference']
    gains=fold_gains(y,dev,CONFIRM,base,candidate);delta=roc_auc_score(y[dev],candidate)-roc_auc_score(y[dev],base)
    result=dict(baseline_auc=float(roc_auc_score(y[dev],base)),candidate_auc=float(roc_auc_score(y[dev],candidate)),gain=float(delta),
        fold_gains=gains,positive_folds=sum(a>0 for a in gains),passed=bool(delta>0 and sum(a>0 for a in gains)>=4),
        fold_seed=CONFIRM,validation_early_stopping=False,weights_retuned=False,
        caveat='A new partition of previously explored development labels, not an independent untouched test.')
    np.save(directory/'candidate_oof.npy',candidate);np.save(directory/'reference_oof.npy',base)
    t.dump(t.ART/'confirmation_results.json',result);print('CONFIRMATION',result,flush=True)

def averaging():
    choice=t.read(t.ART/'selection.json');confirm=t.read(t.ART/'confirmation_results.json')
    if not confirm['passed']:
        t.dump(t.ART/'averaging_results.json',dict(passed=False,reason='Earlier gate failed; retain round two.'));return
    train,test,y,split=t.load();dev=split['development'];primary,rows=primary_pool()
    secondary=current_secondary_components();directory=t.ART/'secondary'
    for row in choice['new_families']:
        cv_one(row,train,y,dev,seed=SECONDARY,fixed=row['fixed_iterations'],directory=directory)
        secondary[row['name']]=np.load(directory/(row['name']+'_oof.npy'))
    secondary=add_reference(secondary)
    avg={n:(primary[n]+secondary[n])/2 for n in secondary}
    cdfs=dict(np.load(t.ART/'primary_cdf_references.npz'))
    candidate=recipe_prediction(choice,avg,cdfs);base=avg['round2_reference']
    delta=roc_auc_score(y[dev],candidate)-roc_auc_score(y[dev],base)
    p1=recipe_prediction(choice,primary,cdfs);p2=recipe_prediction(choice,secondary,cdfs)
    result=dict(baseline_two_seed_auc=float(roc_auc_score(y[dev],base)),candidate_two_seed_auc=float(roc_auc_score(y[dev],candidate)),
        gain=float(delta),passed=bool(delta>=.00020),candidate_primary_auc=float(roc_auc_score(y[dev],p1)),
        candidate_secondary_auc=float(roc_auc_score(y[dev],p2)),
        secondary_gain_vs_round2=float(roc_auc_score(y[dev],p2)-roc_auc_score(y[dev],secondary['round2_reference'])),
        primary_fold_gains=fold_gains(y,dev,PRIMARY,base,candidate),
        averaging='Average matching family predictions across the two development seeds before the frozen blend transform.',
        caveat='Selection/averaging diagnostic on development rows; no new independent labels.')
    np.save(t.ART/'candidate_two_seed_oof.npy',candidate);np.save(t.ART/'reference_two_seed_oof.npy',base)
    t.dump(t.ART/'averaging_results.json',result);print('AVERAGING',result,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['cv','select','confirmation','averaging']);args=parser.parse_args()
    globals()[args.phase]()
