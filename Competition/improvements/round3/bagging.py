"""Prospective three-seed diagnostic and gated extension of the frozen bank."""
import argparse,hashlib,time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import joblib
from sklearn.model_selection import StratifiedKFold
from catboost import CatBoostClassifier
from xgboost import XGBClassifier
import lightgbm as lgb
import round3 as t
import validate as v
import finalize as f

def preferred_result():
    path=t.ART/'bagging_final_results.json'
    if path.exists() and t.read(path).get('accepted'):return t.read(path)
    return t.read(t.ART/'final_results.json')

def probe():
    recorded=t.read(t.ART/'bagging_plan_record.json')
    for name,want in recorded['hashes'].items():assert hashlib.sha256((t.HERE/name).read_bytes()).hexdigest()==want,name
    path=t.ART/'bagging_probe.json'
    if path.exists():print(t.read(path));return
    final=t.read(t.ART/'final_results.json')
    if not final['accepted']:
        t.dump(path,dict(passed=False,reason='Original third-pass gates failed; do not expand the seed bank.'));return
    train,test,y,split=t.load();dev=split['development'];choice=t.read(t.ART/'selection.json')
    primary,_=v.primary_pool();secondary=v.current_secondary_components()
    for row in choice['new_families']:secondary[row['name']]=np.load(t.ART/'secondary'/(row['name']+'_oof.npy'))
    secondary=v.add_reference(secondary)
    third={a['name']:np.load(t.ART/'confirmation'/(a['name']+'_oof.npy')) for a in v.families()+choice['new_families']}
    third=v.add_reference(third)
    two={n:(primary[n]+secondary[n])/2 for n in secondary}
    three={n:(primary[n]+secondary[n]+third[n])/3 for n in secondary}
    cdfs=dict(np.load(t.ART/'primary_cdf_references.npz'))
    b2=two['round2_reference'];b3=three['round2_reference']
    p2=v.recipe_prediction(choice,two,cdfs);p3=v.recipe_prediction(choice,three,cdfs)
    bm2=t.metrics(y[dev],b2);bm3=t.metrics(y[dev],b3);pm2=t.metrics(y[dev],p2);pm3=t.metrics(y[dev],p3)
    bg=v.fold_gains(y,dev,v.PRIMARY,b2,b3);pg=v.fold_gains(y,dev,v.PRIMARY,p2,p3)
    passed=(bm3['auc']-bm2['auc']>=.0002 and pm3['auc']-pm2['auc']>=.0002 and
        pm3['auc']-bm3['auc']>=.0002 and sum(a>0 for a in bg)>=4 and sum(a>0 for a in pg)>=4)
    result=dict(passed=bool(passed),reference_two_seed=bm2,reference_three_seed=bm3,
        candidate_two_seed=pm2,candidate_three_seed=pm3,reference_increment=bm3['auc']-bm2['auc'],
        candidate_increment=pm3['auc']-pm2['auc'],recipe_gain_at_three_seeds=pm3['auc']-bm3['auc'],
        reference_fold_increments=bg,candidate_fold_increments=pg,
        note='Conditional development averaging diagnostic. No weights, transforms or seed subsets were retuned.')
    np.save(t.ART/'candidate_three_seed_oof.npy',p3);t.dump(path,result)
    t.event('three_seed_probe_finish',**result);print(result,flush=True)

def fit_third(row,train,y):
    origin=row.get('origin','round3');spec=row['spec']
    if origin=='round2':
        x=t.r.features(train,spec['features'])
        if 'columns'in spec:x=x[spec['columns']]
        fitting=t.r.fit
    else:x=t.features(train,spec['features']);fitting=t.fit
    iteration=int(np.median(row['iterations']));fold_seed=t.SEED+602
    folds=list(StratifiedKFold(5,shuffle=True,random_state=fold_seed).split(x,y))
    directory=t.ART/'bagging_final_folds';directory.mkdir(exist_ok=True)
    def one(item):
        k,(a,b)=item;prefix=row['name']+f'_s2_fold{k}'
        suffix={'cat':'.cbm','xgb':'.ubj','lgb':'.txt','mlp':'.joblib'}[spec['kind']]
        file=t.MODELS/(prefix+suffix);encoder=t.MODELS/(prefix+'_encoder.joblib')
        meta=directory/(prefix+'.json');pred=directory/(prefix+'.npy');model_seed=t.SEED+900+k
        signature=dict(spec=spec,origin=origin,iteration=iteration,fold_seed=fold_seed,model_seed=model_seed,implementation_hash=t.implementation_hash())
        instance=dict(fold=k,model=str(file.relative_to(t.ROOT)),encoder=str(encoder.relative_to(t.ROOT)))
        if all(p.exists() for p in [file,encoder,meta,pred]) and t.read(meta)['signature']==signature:
            return k,b,np.load(pred),instance
        began=time.time();model,enc,_,_=fitting(spec,x,y,a,fixed=iteration,seed=model_seed)
        p=model.predict_proba(enc.transform(x.iloc[b]))[:,1]
        if spec['kind']in ['cat','xgb']:model.save_model(str(file))
        elif spec['kind']=='lgb':model.booster_.save_model(str(file))
        else:joblib.dump(model,file)
        joblib.dump(enc.__dict__,encoder);np.save(pred,p)
        t.dump(meta,dict(signature=signature,seconds=time.time()-began,auc=t.metrics(y[b],p)['auc']))
        print('THIRD FINAL',row['name'],k,flush=True);return k,b,p,instance
    oof=np.zeros(len(train));instances=[]
    if spec['kind']=='mlp':results=map(one,enumerate(folds))
    else:
        pool=ThreadPoolExecutor(max_workers=2);results=pool.map(one,enumerate(folds))
    try:
        for k,b,p,instance in results:oof[b]=p;instances.append(instance)
    finally:
        if spec['kind']!='mlp':pool.shutdown()
    np.save(t.ART/(row['name']+'_s2_full_oof.npy'),oof)
    return dict(name=row['name'],spec=spec,origin=origin,instances=instances),oof

def predict_third(family,test):
    spec=family['spec'];kind=spec['kind']
    x=t.r.features(test,spec['features']) if family['origin']=='round2' else t.features(test,spec['features'])
    p=np.zeros(len(test))
    for item in family['instances']:
        enc=t.NeuralEncoder() if kind=='mlp' else t.r.Encoder()
        enc.__dict__.update(joblib.load(t.ROOT/item['encoder']));z=enc.transform(x);file=t.ROOT/item['model']
        if kind=='cat':m=CatBoostClassifier();m.load_model(str(file));q=m.predict_proba(z,thread_count=4)[:,1]
        elif kind=='xgb':m=XGBClassifier(enable_categorical=True,n_jobs=4);m.load_model(str(file));q=m.predict_proba(z)[:,1]
        elif kind=='lgb':m=lgb.Booster(model_file=str(file));q=m.predict(z,num_threads=4)
        else:m=joblib.load(file);q=m.predict_proba(z)[:,1]
        p+=q/len(family['instances'])
    return p

def two_seed_bank(train,test):
    ps,oo=f.baseline_bank(test);manifest=t.read(t.ART/'model_manifest.json')
    for family in manifest['new_families']:
        ps[family['name']]=f.predict_new(family,test)
        oo[family['name']]=np.mean([np.load(t.ART/(family['name']+f'_s{s}_full_oof.npy')) for s in [0,1]],axis=0)
    return ps,oo

def train():
    probe_result=t.read(t.ART/'bagging_probe.json')
    if not probe_result['passed']:
        t.dump(t.ART/'bagging_final_results.json',dict(accepted=False,reason='Three-seed gate failed; keep the original two-seed decision.'));return
    choice=t.read(t.ART/'selection.json')
    protected={name:hashlib.sha256((t.HERE/name).read_bytes()).hexdigest() for name in
        ['bagging.py','BAGGING_PLAN.md','artifacts/bagging_probe.json','artifacts/selection.json','artifacts/model_manifest.json']}
    freeze=t.ART/'bagging_freeze.json'
    if freeze.exists():assert t.read(freeze)==protected
    else:t.dump(freeze,protected);t.event('three_seed_final_policy_frozen',source_hashes=protected)
    train_data,test,y,split=t.load();ps,oo=two_seed_bank(train_data,test);manifest=dict(recipe=choice,families=[])
    for row in v.families()+choice['new_families']:
        family,oof=fit_third(row,train_data,y);manifest['families'].append(family)
        name=row['name'];ps[name]=(2*ps[name]+predict_third(family,test))/3;oo[name]=(2*oo[name]+oof)/3
    ps=v.add_reference(ps);oo=v.add_reference(oo);t.dump(t.ART/'bagging_model_manifest.json',manifest)
    cdfs=dict(np.load(t.ART/'primary_cdf_references.npz'));p=v.recipe_prediction(choice,ps,cdfs);oof=v.recipe_prediction(choice,oo,cdfs)
    path,sha=f.write_csv(p,'submission_round3_bagged.csv');np.save(t.ART/'bagged_final_full_oof.npy',oof)
    result={**t.read(t.ART/'final_results.json'),'submission':str(path.relative_to(t.ROOT)),'sha256':sha,
        'full_oof':t.metrics(y,oof),'seeds_per_family':3,'additional_third_seed_models':5*len(manifest['families']),
        'new_saved_models':15*len(choice['new_families']),'baseline_saved_models':45,
        'recommendation':'Third-pass recipe plus prospectively validated three-seed averaging; public score unknown until uploaded.',
        'probability_min':float(p.min()),'probability_max':float(p.max()),'probability_mean':float(p.mean())}
    t.dump(t.ART/'bagging_final_results.json',result);print('BAGGED SUBMISSION',result,flush=True)

def reproduce():
    path=t.ART/'bagging_final_results.json'
    if not path.exists() or not t.read(path).get('accepted'):return f.reproduce()
    for name,want in t.read(t.ART/'bagging_freeze.json').items():assert hashlib.sha256((t.HERE/name).read_bytes()).hexdigest()==want,name
    train_data,test,y,split=t.load();ps,_=two_seed_bank(train_data,test)
    manifest=t.read(t.ART/'bagging_model_manifest.json')
    for family in manifest['families']:
        name=family['name'];ps[name]=(2*ps[name]+predict_third(family,test))/3
    ps=v.add_reference(ps);p=v.recipe_prediction(manifest['recipe'],ps,dict(np.load(t.ART/'primary_cdf_references.npz')))
    result=t.read(path);csv,sha=f.write_csv(p,'submission_round3_bagged_reproduced.csv');assert sha==result['sha256']
    print('Three-seed byte-identical reproduction:',csv,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['probe','train','reproduce']);a=parser.parse_args();globals()[a.phase]()
