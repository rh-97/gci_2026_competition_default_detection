"""Shared round-four CV, including paired five/nested-ten folds."""
import time,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import round4 as t

PRIMARY=t.SEED+2;SECONDARY=t.SEED+301;THIRD=t.SEED+1101;CONFIRM=t.SEED+2101
CV_SOURCE_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

def cv_one(row,train,y,dev,seed=PRIMARY,fixed=None,directory=None):
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==CV_SOURCE_SHA,'CV source changed while loaded.'
    directory=directory or t.ART/'cv';directory.mkdir(parents=True,exist_ok=True)
    spec=row['spec'];name=row['name'];origin=row.get('origin','round4')
    fixed=spec.get('fixed_cv_iterations',fixed)
    nested=spec.get('fold_scheme')=='nested10';offset=spec.get('model_seed_offset',0)
    signature=dict(spec=spec,origin=origin,engine_signature=t.SIGNATURE,cv_source_sha256=CV_SOURCE_SHA,fold_seed=seed,fixed_iterations=fixed)
    file=directory/(name+'.json')
    if file.exists() and t.read(file).get('signature')==signature:return t.read(file)
    x=t.build_features(train,spec,origin);folds=t.folds(y[dev],seed,nested)
    folder=directory/name;folder.mkdir(exist_ok=True);began=time.time()
    t.event('cv_start',name=name,fold_seed=seed,folds=len(folds),fixed_iterations=fixed)
    def one(item):
        k,(a,b,parent)=item;meta=folder/f'fold{k}.json';pred=folder/f'fold{k}.npy'
        if meta.exists() and pred.exists() and t.read(meta).get('signature')==signature:
            rec=t.read(meta);return k,b,np.load(pred),rec
        start=time.time();modelseed=t.model_seed(seed,parent,offset)
        if fixed is None:model,enc,p,it=t.fit(spec,x,y,dev[a],dev[b],seed=modelseed)
        else:
            model,enc,_,it=t.fit(spec,x,y,dev[a],fixed=fixed,seed=modelseed)
            p=model.predict_proba(enc.transform(x.iloc[dev[b]]))[:,1]
        np.save(pred,p)
        rec=dict(signature=signature,iterations=it,auc=t.metrics(y[dev[b]],p)['auc'],seconds=time.time()-start,
            training_rows=len(a),validation_rows=len(b),parent=parent,model_seed=modelseed,
            resolved_parameters=model.get_all_params() if spec['kind']=='cat' else model.get_params())
        if fixed is None:
            curve=model.get_evals_result() if spec['kind']=='cat' else (model.evals_result() if spec['kind']=='xgb' else model.evals_result_)
            t.dump(folder/f'fold{k}_curve.json',curve)
        t.dump(meta,rec);t.event('cv_fold_finish',name=name,seed=seed,fold=k,parent=parent,auc=rec['auc'],iterations=it,seconds=rec['seconds'])
        print('CV',name,seed,k,round(rec['auc'],7),it,flush=True)
        return k,b,p,rec
    oof=np.zeros(len(dev));records=[None]*len(folds)
    with ThreadPoolExecutor(max_workers=2) as pool:
        for k,b,p,rec in pool.map(one,enumerate(folds)):oof[b]=p;records[k]=rec
    np.save(directory/(name+'_oof.npy'),oof)
    result=dict(name=name,spec=spec,origin=origin,signature=signature,**t.metrics(y[dev],oof),
        iterations=[a['iterations'] for a in records],fold_auc=[a['auc'] for a in records],
        fold_seconds=[a['seconds'] for a in records],seconds=time.time()-began,folds=len(folds),
        training_rows=[a['training_rows'] for a in records],validation_rows=[a['validation_rows'] for a in records])
    t.dump(file,result);t.event('cv_complete',name=name,seed=seed,auc=result['auc'],seconds=result['seconds'])
    print('CV COMPLETE',name,result['auc'],flush=True);return result

def fold_gains(target,seed,base,candidate):
    return [float(t.metrics(target[b],candidate[b])['auc']-t.metrics(target[b],base[b])['auc']) for a,b,parent in t.folds(target,seed)]

def promote():
    specs=t.read(t.ART/'candidate_plan.json')
    if (t.ART/'followup_plan.json').exists():specs+=t.read(t.ART/'followup_plan.json')
    rows=t.screen_rows();assert len(rows)==len(specs),'Finish all planned screens first.'
    complete=[a for a in rows if a['status']=='complete' and a['name']not in ['r4_cat_control','r4_cat_control512']]
    chosen=[]
    groups=[('parameter_cat',lambda a:a['spec']['kind']=='cat' and a['spec']['features']=='final55',.0001),
        ('feature_cat',lambda a:a['spec']['kind']=='cat' and a['spec']['features']!='final55',.0001),
        ('remaining_cat',lambda a:a['spec']['kind']=='cat',.00015),
        ('other_tree',lambda a:a['spec']['kind']!='cat',.00015)]
    decisions=[]
    for group,belongs,threshold in groups:
        eligible=[a for a in complete if belongs(a) and a['best_blend']['auc']-a['reference_auc']>=threshold and a['name']not in [c['name'] for c in chosen]]
        if eligible:
            best=max(eligible,key=lambda a:a['best_blend']['auc']);chosen.append(best);decisions.append(dict(slot=group,name=best['name'],threshold=threshold))
    plan=dict(chosen=[dict(name=a['name'],spec=a['spec'],origin='round4') for a in chosen],slots=decisions,
        all_decisions=[dict(name=a['name'],promoted=a['name']in [b['name'] for b in chosen],screen_gain=a['best_blend']['auc']-a['reference_auc']) for a in complete])
    p=t.ART/'promotion.json'
    if p.exists():assert t.read(p)==plan
    else:t.dump(p,plan);t.event('promotion_frozen',names=[a['name'] for a in chosen])
    print('PROMOTED',[a['name'] for a in chosen],flush=True);return plan['chosen']

def main():
    chosen=promote();train,test,y,split=t.load()
    for row in chosen:cv_one(row,train,y,split['development'])

if __name__=='__main__':main()
