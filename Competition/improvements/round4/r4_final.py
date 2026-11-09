"""Saved-model inference and final fitting only after all frozen gates pass."""
import argparse,time,hashlib,subprocess,sys
from concurrent.futures import ThreadPoolExecutor
import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from xgboost import XGBClassifier
import lightgbm as lgb
import round4 as t
import r4_validate as v

def previous_bank():
    """Normalize existing 75 models to one read-only inference manifest."""
    families={}
    for a in t.read(t.prev.r.ART/'model_manifest.json')['families']:
        families[a['name']]=dict(name=a['name'],spec=a['spec'],origin='round2',seeds=a['seeds'])
    for a in t.read(t.prev.ART/'model_manifest.json')['new_families']:
        families[a['name']]={**a,'origin':'round3'}
    for a in t.read(t.prev.ART/'bagging_model_manifest.json')['families']:
        families[a['name']]['seeds']=families[a['name']]['seeds']+[dict(seed_number=2,instances=a['instances'])]
    assert sum(len(s['instances']) for f in families.values() for s in f['seeds'])==75
    return families

def predict_family(family,test):
    spec=family['spec'];x=t.build_features(test,spec,family['origin']);out=np.zeros(len(test))
    for seed in family['seeds']:
        for item in seed['instances']:
            enc=t.prev.r.Encoder();enc.__dict__.update(joblib.load(t.ROOT/item['encoder']));z=enc.transform(x);p=t.ROOT/item['model']
            if spec['kind']=='cat':m=CatBoostClassifier();m.load_model(str(p));q=m.predict_proba(z,thread_count=4)[:,1]
            elif spec['kind']=='xgb':m=XGBClassifier(enable_categorical=True,n_jobs=4);m.load_model(str(p));q=m.predict_proba(z)[:,1]
            else:m=lgb.Booster(model_file=str(p));q=m.predict(z,num_threads=4)
            out+=q/(len(family['seeds'])*len(seed['instances']))
    return out

def previous_oofs():
    out={}
    for a in t.reference_families():
        vals=[]
        for s in range(3):
            if s==2:path=t.prev.ART/(a['name']+'_s2_full_oof.npy')
            elif a['origin']=='round3':path=t.prev.ART/(a['name']+f'_s{s}_full_oof.npy')
            else:
                path=t.prev.r.ART/(a['name']+f'_s{s}_full_oof.npy')
                if not path.exists():path=t.prev.r.old.ART/(a['name']+'_full_oof.npy')
            vals.append(np.load(path))
        out[a['name']]=np.mean(vals,axis=0)
    return out

def fit_seed(row,number,train,y):
    spec=row['spec'];origin=row['origin'];x=t.build_features(train,spec,origin);fixed=row['fixed_iterations']
    seed=[t.SEED+3,t.SEED+302,t.SEED+602][number];folds=t.folds(y,seed,spec.get('fold_scheme')=='nested10')
    directory=t.ART/'final_folds';directory.mkdir(exist_ok=True)
    def one(item):
        k,(a,b,parent)=item;prefix=row['name']+f'_s{number}_fold{k}';suffix={'cat':'.cbm','lgb':'.txt','xgb':'.ubj'}[spec['kind']]
        modelpath=t.MODELS/(prefix+suffix);encpath=t.MODELS/(prefix+'_encoder.joblib');meta=directory/(prefix+'.json');predpath=directory/(prefix+'.npy')
        modelseed=t.model_seed(seed,parent,spec.get('model_seed_offset',0),full=True)
        sig=dict(engine_signature=t.SIGNATURE,final_source_sha256=v.sha(__file__),spec=spec,origin=origin,fixed_iterations=fixed,fold_seed=seed,model_seed=modelseed)
        instance=dict(fold=k,parent=parent,model=str(modelpath.relative_to(t.ROOT)),encoder=str(encpath.relative_to(t.ROOT)))
        if all(p.exists() for p in [modelpath,encpath,meta,predpath]) and t.read(meta)['signature']==sig:return b,np.load(predpath),instance
        began=time.time();t.event('final_fit_start',name=row['name'],seed=seed,fold=k)
        model,enc,_,it=t.fit(spec,x,y,a,fixed=fixed,seed=modelseed);p=model.predict_proba(enc.transform(x.iloc[b]))[:,1]
        if spec['kind']in ['cat','xgb']:model.save_model(str(modelpath))
        else:model.booster_.save_model(str(modelpath))
        joblib.dump(enc.__dict__,encpath);np.save(predpath,p)
        t.dump(meta,dict(signature=sig,iterations=it,auc=t.metrics(y[b],p)['auc'],seconds=time.time()-began,training_rows=len(a),validation_rows=len(b)))
        t.event('final_fit_finish',name=row['name'],seed=seed,fold=k,seconds=time.time()-began);print('FINAL',row['name'],number,k,flush=True)
        return b,p,instance
    oof=np.zeros(len(y));instances=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for b,p,item in pool.map(one,enumerate(folds)):oof[b]=p;instances.append(item)
    np.save(t.ART/(row['name']+f'_s{number}_full_oof.npy'),oof)
    return dict(seed_number=number,instances=instances),oof

def write_csv(p,name):
    sub=pd.read_csv(t.ROOT/'input/sample_submission.csv');test=pd.read_csv(t.ROOT/'input/test.csv')
    assert list(sub.columns)==['SK_ID_CURR','TARGET'] and sub.SK_ID_CURR.equals(test.SK_ID_CURR)
    assert len(p)==len(sub)==61500 and np.isfinite(p).all() and ((p>=0)&(p<=1)).all()
    sub.TARGET=p;path=t.ROOT/'output'/name;sub.to_csv(path,index=False);return path,v.sha(path)

def train_final():
    v.check_freeze();out=t.ART/'final_results.json'
    if out.exists():return t.read(out)
    accepted=t.read(t.ART/'confirmation_results.json')['passed'] and t.read(t.ART/'averaging_results.json')['passed']
    if not accepted:
        path=t.ROOT/'output/submission_round3_bagged.csv';result=dict(accepted=False,new_submission_created=False,
            submission=str(path.relative_to(t.ROOT)),sha256=v.sha(path),public_score=.76824,
            recommendation='Retain the public-confirmed round-three bagged submission; round four did not pass every declared gate.')
        t.dump(out,result);print('FALLBACK',result,flush=True);return result
    train,test,y,split=t.load();choice=t.read(t.ART/'selection.json');bank=previous_bank();oofs=previous_oofs();ps={}
    for row in choice['new_families']:
        seeds=[];oo=[]
        for number in range(3):s,p=fit_seed(row,number,train,y);seeds.append(s);oo.append(p)
        bank[row['name']]=dict(name=row['name'],spec=row['spec'],origin=row['origin'],seeds=seeds);oofs[row['name']]=np.mean(oo,axis=0)
    needed=set(choice['names'])-{'round3_reference'}
    if 'round3_reference'in choice['names']:needed.update(t.reference_weights())
    bank={n:bank[n] for n in sorted(needed)}
    # Reference reconstruction needs all five components only when the composite is used.
    for n,f in bank.items():ps[n]=predict_family(f,test)
    if 'round3_reference'in choice['names']:ps=t.with_reference(ps);oofs=t.with_reference(oofs)
    cdfs=dict(np.load(t.ART/'primary_cdf_references.npz'));p=t.recipe_prediction(choice,ps,cdfs);oof=t.recipe_prediction(choice,oofs,cdfs)
    manifest=dict(recipe=choice,families=list(bank.values()),engine_signature=t.SIGNATURE)
    t.dump(t.ART/'model_manifest.json',manifest);path,digest=write_csv(p,'submission_round4.csv');np.save(t.ART/'final_full_oof.npy',oof)
    result=dict(accepted=True,new_submission_created=True,submission=str(path.relative_to(t.ROOT)),sha256=digest,
        public_score=None,rows=len(p),full_oof=t.metrics(y,oof),full_oof_independent=False,
        saved_models=sum(len(s['instances']) for f in bank.values() for s in f['seeds']),
        new_saved_models=sum(len(s['instances']) for f in bank.values() if f['name'].startswith('r4_') for s in f['seeds']),
        inference_method=choice['method'],probability_min=float(p.min()),probability_max=float(p.max()),probability_mean=float(p.mean()),
        recommendation='Round-four candidate passed all local gates; public score remains unknown until submitted.')
    t.dump(out,result);t.event('final_complete',**result);print('SUBMISSION',result,flush=True);return result

def reproduce():
    v.check_freeze();result=t.read(t.ART/'final_results.json');test=pd.read_csv(t.ROOT/'input/test.csv')
    if result['accepted']:
        manifest=t.read(t.ART/'model_manifest.json');ps={f['name']:predict_family(f,test) for f in manifest['families']};choice=manifest['recipe']
        if 'round3_reference'in choice['names']:ps=t.with_reference(ps)
        p=t.recipe_prediction(choice,ps,dict(np.load(t.ART/'primary_cdf_references.npz')))
        path,digest=write_csv(p,'submission_round4_reproduced.csv');assert digest==result['sha256']
    else:
        # Isolate historical generic module names in their own process and retain
        # their exact arithmetic. Redirect only the output filename to a new file.
        subprocess.run([sys.executable,str(t.HERE/'r4_exact_reference.py')],check=True,cwd=t.prev.HERE)
        path=t.ROOT/'output/submission_round4_reference_reproduced.csv';digest=v.sha(path);assert digest==result['sha256']
    t.dump(t.ART/'reproduction.json',dict(submission=str(path.relative_to(t.ROOT)),sha256=digest,byte_identical=True,accepted=result['accepted']))
    print('REPRODUCED',path,digest,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['train_final','reproduce']);a=p.parse_args();globals()[a.phase]()
