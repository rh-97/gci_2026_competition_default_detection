"""Precompute two frozen neural folds while the main runner fits CPU references."""
from pathlib import Path
import os,time,json,hashlib
import numpy as np
from sklearn.metrics import roc_auc_score
import h_pipeline as h
import h_accel

def parent_neural_started(name):
    return any(a.get('event')=='cv_fold_start' and a.get('name')==name and a.get('seed')==h.CONFIRM
        for a in [json.loads(s) for s in (h.ART/'model_events.jsonl').read_text().splitlines()])

def main():
    h.check_freeze();choice=h.t.read(h.ART/'model_selection.json')
    selected=[a for a in choice['new_families'] if a['spec']['kind']=='tabm']
    if not selected:return
    row=selected[0];name=row['name'];spec=row['spec'];fixed=row['fixed_count'];train,test,y,split=h.t.load();dev=split['development']
    folder=h.ART/'new_confirmation'/name;folder.mkdir(parents=True,exist_ok=True);staging=h.ART/'parallel_confirmation';staging.mkdir(exist_ok=True)
    sig=dict(engine=h.SIGNATURE,spec=spec,origin='high_upside',seed=h.CONFIRM,fixed=fixed);done=[]
    for k,(a,b,parent) in enumerate(h.t.folds(y[dev],h.CONFIRM)):
        if k>=2 or parent_neural_started(name):break
        meta=folder/f'fold{k}.json';pred=folder/f'fold{k}.npy'
        if meta.exists() and pred.exists():continue
        h.check_freeze();start=time.time();h.event('parallel_frozen_confirmation_start',name=name,seed=h.CONFIRM,fold=k)
        bundle,_,count,curve=h_accel.fit(spec,train,y,dev[a],fixed=fixed,seed=h.t.model_seed(h.CONFIRM,parent))
        p=bundle.predict(train.iloc[dev[b]])
        rec=dict(signature=sig,count=count,auc=float(roc_auc_score(y[dev[b]],p)),seconds=time.time()-start,diagnostics=bundle.diagnostics,
            dispatcher_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),dispatch_note='Scheduling only; same frozen fitter/indices/seed/count. CPU reference fits ran concurrently.')
        temporary=staging/f'fold{k}.npy';np.save(temporary,p);temporarymeta=staging/f'fold{k}.json';h.t.dump(temporarymeta,rec)
        # If the parent has reached this family, leave its cache entirely to it.
        if not parent_neural_started(name) and not meta.exists():
            os.replace(temporary,pred);os.replace(temporarymeta,meta);done.append(k)
            h.event('parallel_frozen_confirmation_cached',name=name,seed=h.CONFIRM,fold=k,auc=rec['auc'],count=count)
            print('PRECOMPUTED',name,k,rec['auc'],count,flush=True)
        else:
            h.event('parallel_confirmation_result_not_published',name=name,fold=k,reason='Parent reached this family; avoid interfering with its cache.')
            break
    h.t.dump(h.ART/'parallel_confirmation_dispatch.json',dict(folds_cached=done,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        frozen_selection_sha256=h.sha(h.ART/'model_selection.json'),settings_changed=False,validation_early_stopping=False))
if __name__=='__main__':main()
