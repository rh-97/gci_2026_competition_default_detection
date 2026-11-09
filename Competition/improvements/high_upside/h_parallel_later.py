"""Schedule frozen CPU challenger folds alongside later GPU work, after gates pass."""
from pathlib import Path
import argparse,hashlib,json,os,time
import joblib
import numpy as np
from sklearn.metrics import roc_auc_score
import h_pipeline as h
import h_accel
SOURCE_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

def check():
    h.check_freeze();assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==SOURCE_SHA

def parent_started(name,seed,final):
    kind='final_fit_start' if final else 'cv_fold_start'
    for line in (h.ART/'model_events.jsonl').read_text().splitlines():
        try:a=json.loads(line)
        except json.JSONDecodeError:continue
        if a.get('event')==kind and a.get('name')==name and a.get('seed')==seed:return True
    return False

def main(mode):
    check();gate='model_averaging.json' if mode=='final' else 'model_confirmation.json'
    assert h.t.read(h.ART/gate)['passed'],'Do not spend compute beyond a failed/pending gate.'
    choice=h.t.read(h.ART/'model_selection.json');rows=[a for a in choice['new_families'] if a['spec']['kind']=='cat']
    train,test,y,split=h.t.load();staging=h.ART/('parallel_'+mode+'_staging');staging.mkdir(exist_ok=True)
    completed=[]
    if mode=='final':jobs=[('s'+str(k),seed,k) for k,seed in enumerate([h.t.SEED+3,h.t.SEED+302,h.t.SEED+602])]
    else:jobs=[('model_secondary',h.SECONDARY,None),('model_third',h.THIRD,None)]
    for row in rows:
        name=row['name'];spec=row['spec'];fixed=row['fixed_count']
        for label,seed,number in jobs:
            indices=np.arange(len(y)) if mode=='final' else split['development']
            target=y[indices];folder=h.ART/'model_final_folds' if mode=='final' else h.ART/label/name;folder.mkdir(parents=True,exist_ok=True)
            signature_base=dict(engine=h.SIGNATURE,spec=spec,fixed=fixed)
            for k,(a,b,parent) in enumerate(h.t.folds(target,seed)):
                if parent_started(name,seed,mode=='final'):break
                check();modelseed=h.t.model_seed(seed,parent,full=mode=='final')
                if mode=='final':
                    prefix=name+f'_s{number}_f{k}';signature={**signature_base,'fold_seed':seed,'model_seed':modelseed}
                    modelpath=h.MODELS/(prefix+'.joblib');meta=folder/(prefix+'.json');predpath=folder/(prefix+'.npy');curvepath=folder/(prefix+'_curve.json')
                    exists=all(p.exists() for p in [modelpath,meta,predpath])
                else:
                    prefix=name+'_'+label+f'_f{k}';signature={**signature_base,'origin':'high_upside','seed':seed}
                    meta=folder/f'fold{k}.json';predpath=folder/f'fold{k}.npy';curvepath=folder/f'fold{k}_curve.json';modelpath=None
                    exists=meta.exists() and predpath.exists()
                if exists and h.t.read(meta).get('signature')==signature:continue
                start=time.time();h.event('parallel_'+mode+'_fold_start',name=name,seed=seed,fold=k)
                bundle,_,count,curve=h_accel.fit(spec,train,y,indices[a],fixed=fixed,seed=modelseed)
                p=bundle.predict(train.iloc[indices[b]])
                rec=dict(signature=signature,count=count,auc=float(roc_auc_score(y[indices[b]],p)),seconds=time.time()-start,
                    diagnostics=bundle.diagnostics,dispatcher_sha256=SOURCE_SHA,dispatch_note='Only scheduling differs from the frozen main fit; gate passed before dispatch.')
                temp_pred=staging/(prefix+'.npy');np.save(temp_pred,p);temp_meta=staging/(prefix+'.json');h.t.dump(temp_meta,rec)
                temp_curve=staging/(prefix+'_curve.json');h.t.dump(temp_curve,curve)
                temp_model=staging/(prefix+'.joblib')
                if mode=='final':joblib.dump(bundle,temp_model)
                check()
                if not parent_started(name,seed,mode=='final') and not meta.exists():
                    if mode=='final':os.replace(temp_model,modelpath)
                    os.replace(temp_pred,predpath);os.replace(temp_curve,curvepath);os.replace(temp_meta,meta)
                    completed.append(dict(name=name,seed=seed,fold=k,auc=rec['auc'],count=count))
                    h.event('parallel_'+mode+'_fold_cached',**completed[-1]);print('CACHED',mode,completed[-1],flush=True)
                else:
                    h.event('parallel_'+mode+'_not_published',name=name,seed=seed,fold=k,reason='Parent reached family; leave its cache alone.');break
    h.t.dump(h.ART/('parallel_'+mode+'_dispatch.json'),dict(completed=completed,source_sha256=SOURCE_SHA,selection_sha256=h.sha(h.ART/'model_selection.json'),
        gate=gate,settings_changed=False,validation_early_stopping=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['averaging','final']);a=p.parse_args();main(a.mode)
