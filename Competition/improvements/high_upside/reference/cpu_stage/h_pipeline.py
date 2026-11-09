"""Bounded structural pilots, frozen validation, final training and exact replay."""
from pathlib import Path
import argparse,hashlib,json,time,traceback,itertools,sys
from datetime import datetime,timezone
from importlib.metadata import version
import joblib
import numpy as np
import pandas as pd
from scipy.special import expit,logit
from sklearn.metrics import roc_auc_score
import h_models as m
from h_features import t,frame
import r4_final as old

HERE=Path(__file__).resolve().parent;ART=HERE/'artifacts';MODELS=HERE/'models';MODELS.mkdir(exist_ok=True)
PRIMARY=t.SEED+2;SECONDARY=t.SEED+301;THIRD=t.SEED+1101;CONFIRM=t.SEED+3101
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def event(kind,**kwargs):
    with (ART/'model_events.jsonl').open('a') as f:f.write(json.dumps(dict(time_utc=datetime.now(timezone.utc).isoformat(),event=kind,**kwargs),default=str)+'\n')
def package_versions():return {p:version(p) for p in ['numpy','pandas','scikit-learn','catboost','lightgbm','torch','tabm','rtdl_num_embeddings','joblib']}
IDENTITY=dict(sources=m.SOURCE_HASHES,dependencies=t.SIGNATURE,packages=package_versions(),plan_sha256=sha(HERE/'MODELING_PLAN.md'))
SIGNATURE=hashlib.sha256(json.dumps(IDENTITY,sort_keys=True).encode()).hexdigest()

def candidates():
    common=dict(kind='tabm',architecture='tabm-mini',dropout=.1,learning_rate=.002,weight_decay=.0003,max_epochs=140,patience=20,max_seconds=1500)
    out=[dict(**common,name='hu_tabm_raw_piecewise',features='raw',embedding='piecewise',hypothesis='Numerical embeddings and joint shared-weight ensembling on supplied raw predictors.'),
        dict(**common,name='hu_tabm_signed_piecewise',features='signed',embedding='piecewise',hypothesis='Same neural recipe with the successful tree representation.'),
        dict(**common,name='hu_tabm_signed_periodic',features='signed',embedding='periodic',hypothesis='Periodic numerical embeddings can expose different smooth thresholds and interactions.')]
    out.append({**common,'name':'hu_tabm_regularized','features':'signed','embedding':'piecewise','architecture':'tabm','dropout':.25,'learning_rate':.001,
        'weight_decay':.003,'max_epochs':180,'hypothesis':'A full TabM recipe with stronger regularization tests a different generalization tradeoff; several settings change jointly.'})
    for learned,why in [('score_reconstruction','Use observed external scores as auxiliary supervised targets, with nested OOF reconstructions and residuals.'),
        ('interaction_risk','Use regularized OOF borrower/loan/score interaction risks to expose nonlinear population structure.')]:
        out.append(dict(name='hu_cat_'+learned,kind='cat',features='signed',learned=learned,params=dict(depth=5,l2_leaf_reg=8,random_strength=.5),max_iterations=4500,patience=200,hypothesis=why))
    return out

def preflight():
    specs=candidates();path=ART/'model_candidate_plan.json'
    if path.exists():assert t.read(path)==specs
    else:t.dump(path,specs);event('pilot_plan_frozen',count=len(specs),signature=SIGNATURE)
    train,test,y,split=t.load();tiny=train.iloc[:300].copy();perturbed=tiny.copy();perturbed.SK_ID_CURR=-1;perturbed.TARGET=1-perturbed.TARGET
    for mode in ['raw','signed']:
        pd.testing.assert_frame_equal(frame(tiny,mode),frame(perturbed,mode));assert list(frame(tiny,mode))==list(frame(test.iloc[:50],mode))
    tr=split['inner_fit'][:1200];va=split['inner_valid'][:400]
    spec={**specs[0],'name':'software_preflight','max_epochs':2,'patience':2}
    bundle,p,count,curve=m.fit(spec,train,y,tr,va,seed=t.SEED+77)
    joblib.dump(bundle,MODELS/'software_preflight.joblib');again=joblib.load(MODELS/'software_preflight.joblib').predict(train.iloc[va]);assert np.array_equal(p,again)
    batch=bundle.predict(train.iloc[va[:13]]);singles=np.r_[tuple(bundle.predict(train.iloc[[i]]) for i in va[:13])]
    assert np.max(np.abs(batch-singles))<1e-6
    x=frame(train.iloc[va[:1]],spec['features']).copy();cat=bundle.encoder.cats[0];x[cat]='__UNSEEN_SOFTWARE_CHECK__'
    _,encoded=bundle.encoder.transform(x);assert encoded[0,0]==0
    # Both feature blocks must fit without targets from validation and preserve row order.
    from h_features import builder
    transforms={}
    for kind in ['score_reconstruction','interaction_risk']:
        b=builder(kind);a=b.fit_transform(train.iloc[tr].reset_index(drop=True),y[tr],t.SEED);z=b.transform(train.iloc[va])
        assert list(a)==list(z) and len(a)==len(tr) and len(z)==len(va)
        pd.testing.assert_frame_equal(b.transform(train.iloc[va[:10]]).reset_index(drop=True),pd.concat([b.transform(train.iloc[[i]]) for i in va[:10]],ignore_index=True).reset_index(drop=True))
        transforms[kind]=b.quality
    ps=old_bank(test.iloc[:100]);original=pd.read_csv(t.ROOT/'output/submission_round3_bagged.csv').TARGET.to_numpy()[:100]
    difference=float(np.max(np.abs(ps-original)));assert difference<1e-14
    result=dict(passed=True,signature=SIGNATURE,feature_target_id_independence=True,train_test_schema=True,neural_saved_model_replay_exact=True,
        neural_batch_max_difference=float(np.max(np.abs(batch-singles))),unknown_category_reserved=True,learned_transform_batch_invariance=True,
        auxiliary_software_probe=transforms,prior_75_model_replay_max_difference=difference,python=sys.executable,
        note='Tiny two-epoch neural fit and small auxiliary fits are software checks, not competitive trial results.')
    t.dump(ART/'model_preflight.json',result);print('PREFLIGHT',result,flush=True)

def blend(recipe,ps):
    if recipe['method']=='probability':return sum(w*ps[n] for n,w in zip(recipe['names'],recipe['weights']))
    return expit(sum(w*logit(np.clip(ps[n],1e-7,1-1e-7)) for n,w in zip(recipe['names'],recipe['weights'])))

def screen():
    specs=candidates();path=ART/'model_candidate_plan.json'
    if path.exists():assert t.read(path)==specs
    else:t.dump(path,specs);t.dump(ART/'model_environment.json',dict(identity=IDENTITY,signature=SIGNATURE,python=sys.executable,device='cpu',threads=4));event('pilot_plan_frozen',count=len(specs),signature=SIGNATURE)
    train,test,y,split=t.load();tr=split['inner_fit'];va=split['inner_valid'];base=t.reference_prediction(t.component_predictions('screen'));ba=roc_auc_score(y[va],base)
    folder=ART/'pilots';folder.mkdir(exist_ok=True)
    for spec in specs:
        name=spec['name'];file=folder/(name+'.json')
        if file.exists() and t.read(file).get('signature')==SIGNATURE and t.read(file)['status']=='complete':continue
        event('pilot_start',spec=spec);start=time.time();rows=[]
        try:
            def progress(row):rows.append(row);t.dump(folder/(name+'_progress.json'),rows)
            bundle,p,count,curve=m.fit(spec,train,y,tr,va,seed=t.SEED,progress=progress)
            blends=[dict(new_weight=w,auc=float(roc_auc_score(y[va],(1-w)*base+w*p))) for w in [.1,.25,.5,.75,1.]]
            record=dict(name=name,spec=spec,signature=SIGNATURE,status='complete',**t.metrics(y[va],p),count=count,seconds=time.time()-start,
                reference_auc=float(ba),blends=blends,best_blend=max(blends,key=lambda a:a['auc']),diagnostics=bundle.diagnostics,
                correlation=float(np.corrcoef(base,p)[0,1]))
            np.save(folder/(name+'.npy'),p);t.dump(folder/(name+'_curve.json'),curve);joblib.dump(bundle,MODELS/(name+'_pilot.joblib'))
        except Exception as exc:
            (folder/(name+'_error.txt')).write_text(traceback.format_exc());record=dict(name=name,spec=spec,signature=SIGNATURE,status='failed',error=str(exc),seconds=time.time()-start)
        t.dump(file,record);event('pilot_complete',name=name,status=record['status'],auc=record.get('auc'),seconds=record['seconds']);print('PILOT',record,flush=True)

def pilot_rows():return [t.read(ART/'pilots'/(s['name']+'.json')) for s in candidates()]

def promotion():
    rows=pilot_rows();chosen=[]
    for kind in ['tabm','cat']:
        eligible=[a for a in rows if a['status']=='complete' and a['spec']['kind']==kind and a['best_blend']['auc']-a['reference_auc']>=.0003]
        eligible=[a for a in eligible if not (a['spec']['kind']=='tabm' and a['diagnostics']['stop_reason']=='time cap' and a['diagnostics']['epochs_completed']<15 and a['best_blend']['auc']-a['reference_auc']<.002)]
        if eligible:
            best=max(eligible,key=lambda a:a['best_blend']['auc']);chosen.append(dict(name=best['name'],spec=best['spec'],origin='high_upside'))
    plan=dict(chosen=chosen,threshold=.0003,decisions=[dict(name=a['name'],status=a['status'],promoted=a['name']in [b['name'] for b in chosen],
        gain=a['best_blend']['auc']-a['reference_auc'] if a['status']=='complete' else None) for a in rows])
    path=ART/'model_promotion.json'
    if path.exists():assert t.read(path)==plan
    else:t.dump(path,plan);event('promotion_frozen',**plan)
    print('PROMOTED',chosen,flush=True);return chosen

def cv_one(row,train,y,dev,seed=PRIMARY,fixed=None,directory=None):
    folder=directory or ART/'primary_cv';folder.mkdir(exist_ok=True);name=row['name'];path=folder/(name+'.json')
    origin=row.get('origin','high_upside');signature=dict(engine=SIGNATURE,spec=row['spec'],origin=origin,seed=seed,fixed=fixed)
    if path.exists() and t.read(path).get('signature')==signature:return t.read(path)
    work=folder/name;work.mkdir(exist_ok=True);oof=np.zeros(len(dev));counts=[];scores=[];times=[];start=time.time()
    x=t.build_features(train,row['spec'],origin) if origin!='high_upside' else None
    for k,(a,b,parent) in enumerate(t.folds(y[dev],seed)):
        meta=work/f'fold{k}.json';file=work/f'fold{k}.npy'
        if meta.exists() and file.exists() and t.read(meta).get('signature')==signature:rec=t.read(meta);p=np.load(file)
        else:
            event('cv_fold_start',name=name,seed=seed,fold=k,fixed=fixed);began=time.time();modelseed=t.model_seed(seed,parent)
            if origin=='high_upside':
                def progress(record):t.dump(work/f'fold{k}_progress.json',record)
                bundle,p,count,curve=m.fit(row['spec'],train,y,dev[a],dev[b] if fixed is None else None,fixed=fixed,seed=modelseed,progress=progress)
                if fixed is not None:p=bundle.predict(train.iloc[dev[b]])
                diagnostics=bundle.diagnostics
            else:
                model,encoder,p,count=t.fit(row['spec'],x,y,dev[a],dev[b] if fixed is None else None,fixed=fixed,seed=modelseed)
                if fixed is not None:p=model.predict_proba(encoder.transform(x.iloc[dev[b]]))[:,1]
                curve=None;diagnostics={}
            np.save(file,p);rec=dict(signature=signature,count=count,auc=float(roc_auc_score(y[dev[b]],p)),seconds=time.time()-began,diagnostics=diagnostics)
            t.dump(meta,rec)
            if curve is not None:t.dump(work/f'fold{k}_curve.json',curve)
            event('cv_fold_finish',name=name,seed=seed,fold=k,auc=rec['auc'],count=count,seconds=rec['seconds'])
        oof[b]=p;counts.append(rec['count']);scores.append(rec['auc']);times.append(rec['seconds']);print('CV',name,seed,k,rec['auc'],rec['count'],flush=True)
    np.save(folder/(name+'_oof.npy'),oof);result=dict(name=name,spec=row['spec'],origin=origin,signature=signature,**t.metrics(y[dev],oof),
        counts=counts,fold_auc=scores,fold_seconds=times,seconds=time.time()-start)
    t.dump(path,result);event('cv_complete',name=name,seed=seed,auc=result['auc']);return result

def primary_cv():
    chosen=promotion();train,test,y,split=t.load()
    for row in chosen:cv_one(row,train,y,split['development'])

def primary_pool():
    ps={'round3_reference':t.reference_prediction(t.component_predictions('primary'))};rows=[]
    for s in t.read(ART/'model_promotion.json')['chosen']:
        a=t.read(ART/'primary_cv'/(s['name']+'.json'));rows.append(a);ps[s['name']]=np.load(ART/'primary_cv'/(s['name']+'_oof.npy'))
    return ps,rows

def fold_gains(target,seed,base,p):return [float(roc_auc_score(target[b],p[b])-roc_auc_score(target[b],base[b])) for a,b,parent in t.folds(target,seed)]

def check_freeze():
    frozen=t.read(ART/'model_selection_freeze.json');assert frozen['engine']==SIGNATURE
    for name,want in frozen['hashes'].items():assert sha(HERE/name)==want,name

def select():
    if (ART/'model_selection_freeze.json').exists():check_freeze();return
    train,test,y,split=t.load();target=y[split['development']];ps,rows=primary_pool();base=ps['round3_reference'];ba=roc_auc_score(target,base);grid=[]
    def add(names,weights,method):
        rec=dict(names=names,weights=weights,method=method);grid.append({**rec,'auc':float(roc_auc_score(target,blend(rec,ps)))})
    add(['round3_reference'],[1.],'probability');names=list(ps)
    for a,b in itertools.combinations(names,2):
        for w in [.1,.25,1/3,.5,2/3,.75,.9]:
            for method in ['probability','log_odds']:add([a,b],[w,1-w],method)
    if len(rows)==2:
        for keep in [.25,.5,.75]:
            for share in [.25,.5,.75]:
                for method in ['probability','log_odds']:add(['round3_reference',rows[0]['name'],rows[1]['name']],[keep,(1-keep)*share,(1-keep)*(1-share)],method)
    grid.sort(key=lambda a:-a['auc']);t.dump(ART/'model_blend_grid.json',grid);best=grid[0];passed=best['auc']-ba>=.0003
    if not passed:best=next(a for a in grid if a['names']==['round3_reference'])
    choice={**best,'baseline_auc':float(ba),'gain':float(best['auc']-ba),'primary_gate_passed':bool(passed),'substantial_gain':bool(best['auc']-ba>=.002),
        'fold_gains':fold_gains(target,PRIMARY,base,blend(best,ps)),'new_families':[dict(name=a['name'],spec=a['spec'],origin='high_upside',counts=a['counts'],fixed_count=int(np.median(a['counts']))) for a in rows if a['name']in best['names']],
        'confirmation_seed':CONFIRM,'grid_size':len(grid),'best_attempt':grid[0]}
    t.dump(ART/'model_selection.json',choice)
    files=['h_models.py','h_features.py','h_pipeline.py','h_launch.py','MODELING_PLAN.md','artifacts/model_candidate_plan.json','artifacts/model_promotion.json','artifacts/model_selection.json']
    t.dump(ART/'model_selection_freeze.json',dict(engine=SIGNATURE,hashes={name:sha(HERE/name) for name in files}));event('selection_frozen',**choice);print('SELECTED',choice,flush=True)

def confirmation():
    check_freeze();choice=t.read(ART/'model_selection.json');path=ART/'model_confirmation.json'
    if path.exists():return
    if not choice['primary_gate_passed']:t.dump(path,dict(passed=False,reason='Primary gain below 0.00030.'));return
    train,test,y,split=t.load();dev=split['development'];ps={};folder=ART/'new_confirmation'
    # Existing tree families can run two folds at a time via the immutable R4 CV helper.
    import r4_cv
    for row in t.reference_families():
        r4_cv.cv_one(row,train,y,dev,seed=CONFIRM,fixed=int(np.median(row['iterations'])),directory=folder)
        ps[row['name']]=np.load(folder/(row['name']+'_oof.npy'))
    reference=t.reference_prediction(ps);ps={'round3_reference':reference}
    for row in choice['new_families']:
        cv_one(row,train,y,dev,seed=CONFIRM,fixed=row['fixed_count'],directory=folder);ps[row['name']]=np.load(folder/(row['name']+'_oof.npy'))
    candidate=blend(choice,ps);target=y[dev];gain=roc_auc_score(target,candidate)-roc_auc_score(target,reference);gains=fold_gains(target,CONFIRM,reference,candidate)
    result=dict(baseline=t.metrics(target,reference),candidate=t.metrics(target,candidate),gain=float(gain),fold_gains=gains,positive_folds=sum(a>0 for a in gains),
        passed=bool(gain>0 and sum(a>0 for a in gains)>=4),weights_retuned=False,validation_early_stopping=False,
        caveat='Fresh partition of repeatedly explored labels; not an untouched test.')
    np.save(folder/'candidate_oof.npy',candidate);np.save(folder/'reference_oof.npy',reference);t.dump(path,result);event('confirmation_complete',**result);print('CONFIRMATION',result,flush=True)

def averaging():
    check_freeze();choice=t.read(ART/'model_selection.json');path=ART/'model_averaging.json'
    if path.exists():return
    if not t.read(ART/'model_confirmation.json')['passed']:t.dump(path,dict(passed=False,reason='Earlier gate failed.'));return
    train,test,y,split=t.load();dev=split['development'];primary,rows=primary_pool();values=[primary]
    for stage,seed in [('secondary',SECONDARY),('third',THIRD)]:
        folder=ART/('model_'+stage);ps={'round3_reference':t.reference_prediction(t.component_predictions(stage))}
        for row in choice['new_families']:
            cv_one(row,train,y,dev,seed=seed,fixed=row['fixed_count'],directory=folder);ps[row['name']]=np.load(folder/(row['name']+'_oof.npy'))
        values.append(ps)
    ps={n:np.mean([p[n] for p in values],axis=0) for n in values[1]};candidate=blend(choice,ps);base=ps['round3_reference'];target=y[dev]
    gain=roc_auc_score(target,candidate)-roc_auc_score(target,base);gains=fold_gains(target,PRIMARY,base,candidate)
    result=dict(baseline=t.metrics(target,base),candidate=t.metrics(target,candidate),gain=float(gain),fold_gains=gains,
        passed=bool(gain>=.0003 and sum(a>0 for a in gains)>=4),substantial_gain=bool(gain>=.002),weights_retuned=False,
        caveat='Matching three-seed development comparison. Selection and fitting uncertainty are not removed.')
    np.save(ART/'model_candidate_three_seed_oof.npy',candidate);np.save(ART/'model_reference_three_seed_oof.npy',base)
    t.dump(path,result);event('averaging_complete',**result);print('AVERAGING',result,flush=True)

def fit_final_seed(row,number,train,y):
    folder=ART/'model_final_folds';folder.mkdir(exist_ok=True);seed=[t.SEED+3,t.SEED+302,t.SEED+602][number];oof=np.zeros(len(y));instances=[]
    for k,(a,b,parent) in enumerate(t.folds(y,seed)):
        prefix=row['name']+f'_s{number}_f{k}';modelpath=MODELS/(prefix+'.joblib');meta=folder/(prefix+'.json');predpath=folder/(prefix+'.npy')
        sig=dict(engine=SIGNATURE,spec=row['spec'],fixed=row['fixed_count'],fold_seed=seed,model_seed=t.model_seed(seed,parent,full=True))
        if all(p.exists() for p in [modelpath,meta,predpath]) and t.read(meta)['signature']==sig:p=np.load(predpath)
        else:
            start=time.time();event('final_fit_start',name=row['name'],seed=seed,fold=k)
            bundle,_,count,curve=m.fit(row['spec'],train,y,a,fixed=row['fixed_count'],seed=sig['model_seed']);p=bundle.predict(train.iloc[b]);joblib.dump(bundle,modelpath);np.save(predpath,p)
            t.dump(meta,dict(signature=sig,count=count,seconds=time.time()-start,auc=float(roc_auc_score(y[b],p)),diagnostics=bundle.diagnostics))
            event('final_fit_complete',name=row['name'],seed=seed,fold=k,seconds=time.time()-start)
        oof[b]=p;instances.append(dict(fold=k,model=str(modelpath.relative_to(t.ROOT))));print('FINAL',row['name'],number,k,flush=True)
    np.save(ART/(row['name']+f'_s{number}_full_oof.npy'),oof);return dict(seed_number=number,instances=instances),oof

def predict_new(family,test):
    p=np.zeros(len(test))
    for seed in family['seeds']:
        for item in seed['instances']:p+=joblib.load(t.ROOT/item['model']).predict(test)/(len(family['seeds'])*len(seed['instances']))
    return p

def old_bank(test):
    ps={name:old.predict_family(family,test) for name,family in old.previous_bank().items()};return t.reference_prediction(ps)

def final():
    check_freeze();choice=t.read(ART/'model_selection.json');path=ART/'model_final_results.json'
    if path.exists():return
    if not (t.read(ART/'model_confirmation.json')['passed'] and t.read(ART/'model_averaging.json')['passed']):
        result=dict(accepted=False,new_submission_created=False,submission='output/submission_round3_bagged.csv',sha256=sha(t.ROOT/'output/submission_round3_bagged.csv'),public_score=.76824,
            reason='No higher-upside recipe passed every declared gate. Completed pilot/validation evidence is retained.');t.dump(path,result);print('RETAINED',result,flush=True);return
    train,test,y,split=t.load();manifest=dict(recipe=choice,families=[],reference_bank='Original 75 saved instances');ps={};oo={}
    if 'round3_reference'in choice['names']:ps['round3_reference']=old_bank(test);oo['round3_reference']=t.reference_prediction(old.previous_oofs())
    for row in choice['new_families']:
        seeds=[];oofs=[]
        for number in range(3):s,p=fit_final_seed(row,number,train,y);seeds.append(s);oofs.append(p)
        family=dict(name=row['name'],spec=row['spec'],seeds=seeds);manifest['families'].append(family);ps[row['name']]=predict_new(family,test);oo[row['name']]=np.mean(oofs,axis=0)
    p=blend(choice,ps);oof=blend(choice,oo);csv,digest=old.write_csv(p,'submission_high_upside.csv');np.save(ART/'model_final_full_oof.npy',oof);t.dump(ART/'model_manifest.json',manifest)
    result=dict(accepted=True,new_submission_created=True,submission=str(csv.relative_to(t.ROOT)),sha256=digest,public_score=None,rows=len(p),
        full_oof=t.metrics(y,oof),full_oof_independent=False,new_models=sum(len(s['instances']) for f in manifest['families'] for s in f['seeds']),
        baseline_models=75 if 'round3_reference'in choice['names'] else 0,probability_min=float(p.min()),probability_max=float(p.max()),probability_mean=float(p.mean()),
        recommendation='Passed local gates; public score unknown. The 0.8 target is not an achieved score.')
    t.dump(path,result);event('submission_created',**result);print('SUBMISSION',result,flush=True)

def reproduce():
    check_freeze();result=t.read(ART/'model_final_results.json')
    if not result['accepted']:
        assert sha(t.ROOT/result['submission'])==result['sha256'];t.dump(ART/'model_reproduction.json',dict(byte_identical=True,fallback_checksum=True,sha256=result['sha256'],
            note='Unchanged reference CSV; exact saved-model replay was established in the prior round-three artifacts.'));return
    train,test,y,split=t.load();manifest=t.read(ART/'model_manifest.json');ps={}
    if 'round3_reference'in manifest['recipe']['names']:ps['round3_reference']=old_bank(test)
    for family in manifest['families']:ps[family['name']]=predict_new(family,test)
    p=blend(manifest['recipe'],ps);path,digest=old.write_csv(p,'submission_high_upside_reproduced.csv');assert digest==result['sha256'],(digest,result['sha256'])
    t.dump(ART/'model_reproduction.json',dict(byte_identical=True,sha256=digest,path=str(path.relative_to(t.ROOT)),saved_model_replay=True));print('EXACT REPLAY',digest,flush=True)

def run():
    try:
        for name in ['screen','primary_cv','select','confirmation','averaging','final','reproduce']:
            t.dump(ART/'model_pipeline_status.json',dict(status='running',stage=name));print('STAGE',name,flush=True);globals()[name]()
        t.dump(ART/'model_pipeline_status.json',dict(status='modeling_complete',stage='Document/execute/verify result notebooks and package.'))
    except BaseException:
        t.dump(ART/'model_pipeline_status.json',dict(status='failed',traceback=traceback.format_exc()));raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['preflight','screen','primary_cv','select','confirmation','averaging','final','reproduce','run']);a=p.parse_args();globals()[a.phase]()
