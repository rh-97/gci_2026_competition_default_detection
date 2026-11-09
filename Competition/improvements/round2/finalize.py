"""Fit the frozen second-pass choice and reproduce predictions from saved models."""
import argparse,hashlib,time
from concurrent.futures import ThreadPoolExecutor
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score,average_precision_score,log_loss
from catboost import CatBoostClassifier
from xgboost import XGBClassifier
import lightgbm as lgb
import round2 as r

def old_instances(row):
    suffix='.cbm' if row['spec']['kind']=='cat' else '.txt'
    return [dict(fold=k,model=str((r.old.MODELS/(row['name']+f'_fold{k}'+suffix)).relative_to(r.ROOT)),
        encoder=str((r.old.MODELS/(row['name']+f'_fold{k}_encoder.joblib')).relative_to(r.ROOT)),encoder_type='pass1') for k in range(5)]

def fit_seed(row,seed_number,train,y):
    spec=row['spec'];x=r.features(train,spec['features'])
    if 'columns'in spec: x=x[spec['columns']]
    iteration=int(np.median(row['iterations']))
    fold_seed=r.SEED+3 if seed_number==0 else r.SEED+302
    folds=list(StratifiedKFold(5,shuffle=True,random_state=fold_seed).split(x,y))
    directory=r.ART/'final_folds';directory.mkdir(exist_ok=True)
    def one(item):
        k,(a,b)=item;prefix=f"{row['name']}_s{seed_number}_fold{k}"
        suffix={'cat':'.cbm','xgb':'.ubj','lgb':'.txt'}[spec['kind']]
        model_file=r.MODELS/(prefix+suffix);encoder_file=r.MODELS/(prefix+'_encoder.joblib')
        meta_file=directory/(prefix+'.json');pred_file=directory/(prefix+'.npy')
        model_seed=r.SEED+(100 if seed_number==0 else 500)+k
        signature=dict(spec=spec,iteration=iteration,fold_seed=fold_seed,model_seed=model_seed,implementation_hash=r.implementation_hash())
        instance=dict(fold=k,model=str(model_file.relative_to(r.ROOT)),encoder=str(encoder_file.relative_to(r.ROOT)),encoder_type='pass2')
        if all(p.exists() for p in [model_file,encoder_file,meta_file,pred_file]) and r.read(meta_file)['signature']==signature:
            return k,b,np.load(pred_file),instance
        t=time.time();r.event('final_fit_start',name=row['name'],seed_number=seed_number,fold=k)
        model,enc,_,_=r.fit(spec,x,y,a,fixed=iteration,seed=model_seed)
        p=model.predict_proba(enc.transform(x.iloc[b]))[:,1]
        if spec['kind']=='cat': model.save_model(str(model_file))
        elif spec['kind']=='xgb': model.save_model(str(model_file))
        else: model.booster_.save_model(str(model_file))
        joblib.dump(enc.__dict__,encoder_file);np.save(pred_file,p)
        r.dump(meta_file,dict(signature=signature,auc=roc_auc_score(y[b],p),seconds=time.time()-t))
        r.event('final_fit_finish',name=row['name'],seed_number=seed_number,fold=k,auc=roc_auc_score(y[b],p))
        print('FINAL',row['name'],seed_number,k,round(roc_auc_score(y[b],p),7),flush=True)
        return k,b,p,instance
    oof=np.zeros(len(train));instances=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for k,b,p,instance in pool.map(one,enumerate(folds)): oof[b]=p;instances.append(instance)
    np.save(r.ART/(row['name']+f'_s{seed_number}_full_oof.npy'),oof)
    return instances,oof

def predict_manifest(manifest,test):
    prediction=np.zeros(len(test))
    for family in manifest['families']:
        x=r.features(test,family['spec']['features']);family_prediction=np.zeros(len(test))
        for seed in family['seeds']:
            seed_prediction=np.zeros(len(test))
            for item in seed['instances']:
                enc=r.old.Encoder() if item['encoder_type']=='pass1' else r.Encoder()
                enc.__dict__.update(joblib.load(r.ROOT/item['encoder']))
                z=enc.transform(x);kind=family['spec']['kind'];file=r.ROOT/item['model']
                if kind=='cat':
                    model=CatBoostClassifier();model.load_model(str(file));p=model.predict_proba(z)[:,1]
                elif kind=='xgb':
                    model=XGBClassifier(enable_categorical=True,n_jobs=4);model.load_model(str(file));p=model.predict_proba(z)[:,1]
                else:
                    model=lgb.Booster(model_file=str(file));p=model.predict(z,num_threads=4)
                seed_prediction+=p/5
            family_prediction+=seed_prediction/len(family['seeds'])
        prediction+=family['weight']*family_prediction
    return prediction

def write_submission(prediction,name):
    test=pd.read_csv(r.ROOT/'input/test.csv');sub=pd.read_csv(r.ROOT/'input/sample_submission.csv')
    assert sub.SK_ID_CURR.equals(test.SK_ID_CURR) and sub.SK_ID_CURR.is_unique
    assert len(prediction)==61500 and np.isfinite(prediction).all() and ((prediction>=0)&(prediction<=1)).all()
    sub['TARGET']=prediction;path=r.ROOT/'output'/name;sub.to_csv(path,index=False)
    return path,hashlib.sha256(path.read_bytes()).hexdigest()

def save_importance(manifest):
    for family in manifest['families']:
        columns=[];kind=family['spec']['kind']
        for seed in family['seeds']:
            for item in seed['instances']:
                path=r.ROOT/item['model']
                if kind=='cat':
                    model=CatBoostClassifier();model.load_model(str(path))
                    series=pd.Series(model.get_feature_importance(thread_count=4),index=model.feature_names_)
                elif kind=='xgb':
                    model=XGBClassifier(enable_categorical=True,n_jobs=4);model.load_model(str(path));booster=model.get_booster()
                    series=pd.Series(booster.get_score(importance_type='gain')).reindex(booster.feature_names,fill_value=0)
                else:
                    model=lgb.Booster(model_file=str(path))
                    series=pd.Series(model.feature_importance('gain'),index=model.feature_name())
                columns.append(series)
        matrix=pd.concat(columns,axis=1)
        table=pd.DataFrame({'mean_importance':matrix.mean(axis=1),'fold_std':matrix.std(axis=1)}).sort_values('mean_importance',ascending=False)
        table.index.name='feature';table.to_csv(r.ART/(family['name']+'_final_importance.csv'))

def train_final():
    train,test,y,split=r.load();chosen=r.read(r.ART/'selection.json')
    assert chosen['status'] in ['selected after stability check','fallback: stability did not confirm gain']
    r.dump(r.ART/'selection_freeze.json',dict(selection_sha256=hashlib.sha256((r.ART/'selection.json').read_bytes()).hexdigest(),
        implementation_hash=r.implementation_hash(),note='Frozen before full-data training or final OOF feedback.'))
    two_seeds=chosen['stability']['recommend_two_seed_bagging']
    manifest=dict(families=[],seeds_per_family=2 if two_seeds else 1,selection=chosen,
        notes='Old first-pass models are reused for their original final folds. All other encoders fit only their training fold.')
    blended_oof=np.zeros(len(train))
    for weight,row in zip(chosen['weights'],chosen['models']):
        seeds=[];family_oof=np.zeros(len(train))
        for seed_number in range(2 if two_seeds else 1):
            if seed_number==0 and row['origin']=='pass1':
                instances=old_instances(row);oof=np.load(r.old.ART/(row['name']+'_full_oof.npy'))
            else: instances,oof=fit_seed(row,seed_number,train,y)
            seeds.append(dict(seed_number=seed_number,instances=instances));family_oof+=oof/(2 if two_seeds else 1)
        manifest['families'].append(dict(name=row['name'],weight=weight,spec=row['spec'],seeds=seeds))
        blended_oof+=weight*family_oof
    r.dump(r.ART/'model_manifest.json',manifest)
    save_importance(manifest)
    prediction=predict_manifest(manifest,test)
    path,sha=write_submission(prediction,'submission_round2.csv')
    np.save(r.ART/'final_full_oof.npy',blended_oof)
    report=dict(submission=str(path.relative_to(r.ROOT)),sha256=sha,rows=len(test),
        probability_min=float(prediction.min()),probability_max=float(prediction.max()),probability_mean=float(prediction.mean()),
        models=[dict(name=a['name'],weight=a['weight'],seeds=len(a['seeds'])) for a in manifest['families']],
        full_oof_auc=roc_auc_score(y,blended_oof),full_oof_average_precision=average_precision_score(y,blended_oof),
        full_oof_log_loss=log_loss(y,blended_oof),full_oof_independent=False,
        recommended_new_recipe=chosen['stability']['recommend_new_submission'],two_seed_bagging=two_seeds,
        public_score=None,public_score_note='User must submit this new CSV; no public improvement is assumed.',
        existing_public_score=.7654,existing_public_csv='output/submission_improved.csv')
    if not report['recommended_new_recipe'] and not two_seeds:
        assert sha==r.read(r.ART/'public_score.json')['sha256'],'Unchanged recipe must reproduce the old public-scored CSV exactly.'
        report['recommendation']='Keep the known public-scored CSV; this pass did not validate an improved recipe.'
    else: report['recommendation']='A locally validated candidate; submit to obtain its actual public score.'
    r.dump(r.ART/'final_results.json',report)
    print('SUBMISSION',report,flush=True)

def reproduce():
    manifest=r.read(r.ART/'model_manifest.json');test=pd.read_csv(r.ROOT/'input/test.csv')
    pred=predict_manifest(manifest,test);path,sha=write_submission(pred,'submission_round2_reproduced.csv')
    expected=r.read(r.ART/'final_results.json')['sha256'];assert sha==expected,(sha,expected)
    print('Byte-for-byte reproduction verified:',path)
    return path

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['train_final','reproduce']);args=parser.parse_args()
    globals()[args.phase]()
