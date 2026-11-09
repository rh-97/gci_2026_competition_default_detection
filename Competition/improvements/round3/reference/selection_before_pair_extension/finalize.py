"""Train only a gated third-pass choice; retain the existing CSV on a failed gate."""
import argparse,hashlib,importlib.util,time
from concurrent.futures import ThreadPoolExecutor
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from catboost import CatBoostClassifier
from xgboost import XGBClassifier
import lightgbm as lgb
import round3 as t
import validate as v

def old_finalizer():
    spec=importlib.util.spec_from_file_location('_round2_finalizer',t.r.HERE/'finalize.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def baseline_bank(test):
    manifest=t.read(t.r.ART/'model_manifest.json');old=old_finalizer();predictions={};oofs={}
    for family in manifest['families']:
        one={**family,'weight':1.}
        predictions[family['name']]=old.predict_manifest(dict(families=[one]),test)
        values=[]
        for seed in family['seeds']:
            number=seed['seed_number'];file=t.r.ART/(family['name']+f'_s{number}_full_oof.npy')
            if not file.exists():file=t.r.old.ART/(family['name']+'_full_oof.npy')
            values.append(np.load(file))
        oofs[family['name']]=np.mean(values,axis=0)
    return v.add_reference(predictions),v.add_reference(oofs)

def fit_seed(row,seed_number,train,y):
    spec=row['spec'];x=t.features(train,spec['features']);iteration=row['fixed_iterations']
    fold_seed=t.SEED+3 if seed_number==0 else t.SEED+302
    folds=list(StratifiedKFold(5,shuffle=True,random_state=fold_seed).split(x,y))
    directory=t.ART/'final_folds';directory.mkdir(exist_ok=True)
    def one(item):
        k,(a,b)=item;prefix=f"{row['name']}_s{seed_number}_fold{k}"
        suffix={'cat':'.cbm','xgb':'.ubj','lgb':'.txt','mlp':'.joblib'}[spec['kind']]
        file=t.MODELS/(prefix+suffix);encoder=t.MODELS/(prefix+'_encoder.joblib')
        meta=directory/(prefix+'.json');prediction=directory/(prefix+'.npy')
        model_seed=t.SEED+(100 if seed_number==0 else 500)+k
        signature=dict(spec=spec,iterations=iteration,fold_seed=fold_seed,model_seed=model_seed,implementation_hash=t.implementation_hash())
        instance=dict(fold=k,model=str(file.relative_to(t.ROOT)),encoder=str(encoder.relative_to(t.ROOT)))
        if all(p.exists() for p in [file,encoder,meta,prediction]) and t.read(meta)['signature']==signature:
            return k,b,np.load(prediction),instance
        began=time.time();t.event('final_fit_start',name=row['name'],seed_number=seed_number,fold=k)
        model,enc,_,_=t.fit(spec,x,y,a,fixed=iteration,seed=model_seed)
        p=model.predict_proba(enc.transform(x.iloc[b]))[:,1]
        if spec['kind']in ['cat','xgb']:model.save_model(str(file))
        elif spec['kind']=='lgb':model.booster_.save_model(str(file))
        else:joblib.dump(model,file)
        joblib.dump(enc.__dict__,encoder);np.save(prediction,p)
        t.dump(meta,dict(signature=signature,auc=t.metrics(y[b],p)['auc'],seconds=time.time()-began))
        t.event('final_fit_finish',name=row['name'],seed_number=seed_number,fold=k,seconds=time.time()-began)
        print('FINAL',row['name'],seed_number,k,flush=True)
        return k,b,p,instance
    oof=np.zeros(len(train));instances=[]
    if spec['kind']=='mlp':results=map(one,enumerate(folds))
    else:
        pool=ThreadPoolExecutor(max_workers=2);results=pool.map(one,enumerate(folds))
    try:
        for k,b,p,instance in results:oof[b]=p;instances.append(instance)
    finally:
        if spec['kind']!='mlp':pool.shutdown()
    np.save(t.ART/(row['name']+f'_s{seed_number}_full_oof.npy'),oof)
    return instances,oof

def predict_new(family,test):
    x=t.features(test,family['spec']['features']);kind=family['spec']['kind'];prediction=np.zeros(len(test))
    for seed in family['seeds']:
        for item in seed['instances']:
            enc=t.NeuralEncoder() if kind=='mlp' else t.r.Encoder()
            enc.__dict__.update(joblib.load(t.ROOT/item['encoder']));z=enc.transform(x);path=t.ROOT/item['model']
            if kind=='cat':model=CatBoostClassifier();model.load_model(str(path));p=model.predict_proba(z,thread_count=4)[:,1]
            elif kind=='xgb':model=XGBClassifier(enable_categorical=True,n_jobs=4);model.load_model(str(path));p=model.predict_proba(z)[:,1]
            elif kind=='lgb':model=lgb.Booster(model_file=str(path));p=model.predict(z,num_threads=4)
            else:model=joblib.load(path);p=model.predict_proba(z)[:,1]
            prediction+=p/(len(family['seeds'])*len(seed['instances']))
    return prediction

def write_csv(p,name):
    sub=pd.read_csv(t.ROOT/'input/sample_submission.csv');test=pd.read_csv(t.ROOT/'input/test.csv')
    assert len(p)==len(sub)==61500 and sub.SK_ID_CURR.equals(test.SK_ID_CURR)
    assert np.isfinite(p).all() and ((p>=0)&(p<=1)).all()
    sub['TARGET']=p;path=t.ROOT/'output'/name;sub.to_csv(path,index=False)
    return path,hashlib.sha256(path.read_bytes()).hexdigest()

def train_final():
    choice=t.read(t.ART/'selection.json');freeze=t.read(t.ART/'selection_freeze.json')
    assert hashlib.sha256((t.ART/'selection.json').read_bytes()).hexdigest()==freeze['selection_sha256']
    assert freeze['implementation_hash']==t.implementation_hash()
    accepted=t.read(t.ART/'confirmation_results.json')['passed'] and t.read(t.ART/'averaging_results.json')['passed']
    if not accepted:
        old=t.ROOT/'output/submission_round2.csv'
        result=dict(accepted=False,submission='output/submission_round2.csv',sha256=hashlib.sha256(old.read_bytes()).hexdigest(),
            recommendation='Retain the round-two CSV. No third-pass recipe passed every declared gate.',
            public_score=.76756,public_score_attribution='Inferred from conversation; screenshot does not identify filename.',
            new_submission_created=False)
        t.dump(t.ART/'final_results.json',result);print(result,flush=True);return
    train,test,y,split=t.load();ps,oofs=baseline_bank(test);manifest=dict(recipe=choice,new_families=[],baseline_manifest='improvements/round2/artifacts/model_manifest.json')
    for row in choice['new_families']:
        seeds=[];oo=[]
        for number in range(2):
            instances,oof=fit_seed(row,number,train,y);seeds.append(dict(seed_number=number,instances=instances));oo.append(oof)
        family=dict(name=row['name'],spec=row['spec'],seeds=seeds)
        manifest['new_families'].append(family);oofs[row['name']]=np.mean(oo,axis=0);ps[row['name']]=predict_new(family,test)
    t.dump(t.ART/'model_manifest.json',manifest)
    cdfs=dict(np.load(t.ART/'primary_cdf_references.npz'))
    p=v.recipe_prediction(choice,ps,cdfs);oof=v.recipe_prediction(choice,oofs,cdfs)
    path,sha=write_csv(p,'submission_round3.csv');np.save(t.ART/'final_full_oof.npy',oof)
    result=dict(accepted=True,new_submission_created=True,submission=str(path.relative_to(t.ROOT)),sha256=sha,rows=len(p),
        full_oof=t.metrics(y,oof),full_oof_independent=False,public_score=None,
        recommendation='Locally validated third-pass candidate; upload to measure its public score.',
        probability_min=float(p.min()),probability_max=float(p.max()),probability_mean=float(p.mean()),
        new_saved_models=sum(len(s['instances']) for f in manifest['new_families'] for s in f['seeds']),
        baseline_saved_models=30,inference_method=choice['method'])
    t.dump(t.ART/'final_results.json',result);print('SUBMISSION',result,flush=True)

def reproduce():
    result=t.read(t.ART/'final_results.json')
    if not result['accepted']:
        path=t.ROOT/result['submission'];assert hashlib.sha256(path.read_bytes()).hexdigest()==result['sha256']
        print('Fallback CSV remains byte-identical:',path);return
    manifest=t.read(t.ART/'model_manifest.json');test=pd.read_csv(t.ROOT/'input/test.csv');ps,_=baseline_bank(test)
    for family in manifest['new_families']:ps[family['name']]=predict_new(family,test)
    p=v.recipe_prediction(manifest['recipe'],ps,dict(np.load(t.ART/'primary_cdf_references.npz')))
    path,sha=write_csv(p,'submission_round3_reproduced.csv');assert sha==result['sha256'],(sha,result['sha256'])
    print('Byte-identical saved-model reproduction:',path)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['train_final','reproduce']);args=parser.parse_args()
    globals()[args.phase]()
