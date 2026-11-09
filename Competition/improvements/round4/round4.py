"""Immutable round-four fitting core. Earlier passes are read-only dependencies."""
from pathlib import Path
import os,sys
os.environ.setdefault('OMP_NUM_THREADS','4')
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'round3'))
import round3 as prev
sys.path.insert(0,str(HERE))
import argparse,hashlib,importlib.util,json,time,traceback,threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import numpy as np
import pandas as pd
from scipy.special import expit,logit
from sklearn.model_selection import StratifiedKFold

ROOT=prev.ROOT;ART=HERE/'artifacts';MODELS=HERE/'models';SEED=prev.SEED
for directory in [ART,MODELS,ART/'screen',ART/'cv',ART/'confirmation',ART/'fraction']:
    directory.mkdir(parents=True,exist_ok=True)
SOURCE_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
LOCK=threading.Lock()
dump=prev.dump;read=prev.read;load=prev.load;metrics=prev.metrics

def dependency(name,filename):
    spec=importlib.util.spec_from_file_location(name,filename)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

V3=dependency('_r4_readonly_r3_validation',prev.HERE/'validate.py')
REFERENCE=read(prev.ART/'selection.json')
PUBLIC=read(prev.ART/'round3_public_result.json')
_preserved=read(HERE/'reference/preserved_hashes.json')
_environment=read(ART/'environment.json')
_identity=dict(engine_sha256=SOURCE_SHA,previous_implementation=prev.implementation_hash(),
    data={k:v for k,v in _preserved.items() if k.startswith('input/') or k.endswith('/splits.npz')},
    packages=_environment['packages'])
SIGNATURE=hashlib.sha256(json.dumps(_identity,sort_keys=True).encode()).hexdigest()

def assert_core():
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==SOURCE_SHA,'Core source changed while loaded; stop and audit before fitting.'

def event(kind,**kwargs):
    with LOCK:
        with (ART/'events.jsonl').open('a') as f:
            f.write(json.dumps(dict(time_utc=datetime.now(timezone.utc).isoformat(),event=kind,**kwargs),default=str)+'\n')

def features(df,mode='final55'):
    x=prev.features(df,'signed')
    if mode in ['period3','period24','period3_24','all_terms']:
        periods=[3] if mode=='period3' else [24] if mode=='period24' else [3,24]
        for n in periods:
            z=x.CREDIT_TERM/n
            x[f'TERM_MULTIPLE_{n}_SIGNED']=z-np.rint(z)
            x[f'TERM_ROUND_{n}_CATEGORY']=np.rint(z).astype('Int64').astype(str)
    if mode in ['goods_ratio','goods_structure','all_terms']:
        x['GOODS_TERM']=x.AMT_GOODS_PRICE/x.AMT_ANNUITY.replace(0,np.nan)
    if mode in ['goods_structure','all_terms']:
        for n in [6,12]:
            z=x.GOODS_TERM/n
            x[f'GOODS_TERM_MULTIPLE_{n}_SIGNED']=z-np.rint(z)
            x[f'GOODS_TERM_MULTIPLE_{n}_DISTANCE']=(z-np.rint(z)).abs()
            x[f'GOODS_TERM_ROUND_{n}_CATEGORY']=np.rint(z).astype('Int64').astype(str)
    return x.replace([np.inf,-np.inf],np.nan)

def build_features(df,spec,origin='round4'):
    if origin=='round2':x=prev.r.features(df,spec['features'])
    elif origin=='round3':x=prev.features(df,spec['features'])
    else:x=features(df,spec['features'])
    if 'columns'in spec:x=x[spec['columns']]
    return x

def fit(spec,x,y,tr,va=None,fixed=None,seed=SEED):
    assert_core()
    result=prev.fit(spec,x,y,tr,va=va,fixed=fixed,seed=seed)
    assert_core();return result

def model_seed(fold_seed,parent,offset=0,full=False):
    if full:
        base={SEED+3:SEED+100,SEED+302:SEED+500,SEED+602:SEED+900}[fold_seed]
    else:base=SEED if fold_seed==SEED+2 else fold_seed+100
    return int(base+parent+offset)

def folds(target,seed,nested10=False):
    outer=list(StratifiedKFold(5,shuffle=True,random_state=seed).split(np.zeros(len(target)),target))
    if not nested10:return [(a,b,k) for k,(a,b) in enumerate(outer)]
    result=[];allrows=np.arange(len(target))
    for parent,(a,b) in enumerate(outer):
        inner=StratifiedKFold(2,shuffle=True,random_state=seed+700+parent)
        for _,half in inner.split(b,target[b]):
            val=b[half];mask=np.ones(len(target),dtype=bool);mask[val]=False
            result.append((allrows[mask],val,parent))
    return result

def reference_families():
    rows=[]
    for a in V3.families():rows.append({**a,'origin':'round2'})
    rows += [dict(name=a['name'],spec=a['spec'],iterations=a['iterations'],origin='round3') for a in REFERENCE['new_families']]
    return rows

def component_predictions(stage='primary'):
    if stage=='screen':
        result={}
        for row in reference_families():
            name=row['name']
            if row['origin']=='round3':path=prev.ART/'screen'/(name+'.npy')
            else:
                path=prev.r.ART/'screen'/(name+'.npy')
                if not path.exists():path=prev.r.old.ART/(name+'_inner.npy')
            result[name]=np.load(path)
        return result
    if stage=='primary':result=V3.current_primary_components();directory=prev.ART/'cv'
    elif stage=='secondary':result=V3.current_secondary_components();directory=prev.ART/'secondary'
    elif stage=='third':
        return {a['name']:np.load(prev.ART/'confirmation'/(a['name']+'_oof.npy')) for a in reference_families()}
    else:raise ValueError(stage)
    for row in REFERENCE['new_families']:result[row['name']]=np.load(directory/(row['name']+'_oof.npy'))
    return result

def reference_prediction(components):
    old=V3.add_reference(components)
    return V3.recipe_prediction(REFERENCE,old,dict(np.load(prev.ART/'primary_cdf_references.npz')))

def with_reference(components):
    out=dict(components);out['round3_reference']=reference_prediction(out);return out

def three_seed_components():
    values=[component_predictions(s) for s in ['primary','secondary','third']]
    return {n:np.mean([p[n] for p in values],axis=0) for n in values[0]}

def reference_weights():
    old={a['name']:a['weight'] for a in V3.families()};weights={}
    for name,w in zip(REFERENCE['names'],REFERENCE['weights']):
        parts=old.items() if name=='round2_reference' else [(name,1.)]
        for n,v in parts:weights[n]=weights.get(n,0)+w*v
    return weights

def recipe_prediction(recipe,ps,cdfs=None):
    names=recipe['names'];weights=recipe['weights'];method=recipe['method']
    if method=='probability':return sum(w*ps[n] for n,w in zip(names,weights))
    if method=='log_odds':return expit(sum(w*logit(np.clip(ps[n],1e-7,1-1e-7)) for n,w in zip(names,weights)))
    if method=='percentile':
        return sum(w*(np.searchsorted(cdfs[n],ps[n],side='right')+.5)/(len(cdfs[n])+1) for n,w in zip(names,weights))
    raise ValueError(method)

def candidates():
    base=dict(depth=5,l2_leaf_reg=8,random_strength=.5)
    def cat(name,why,changes=None,mode='final55',stage='A',**extra):
        return dict(name='r4_cat_'+name,kind='cat',features=mode,stage=stage,params={**base,**(changes or {})},
            hypothesis=why,max_iterations=6000 if name=='slow' else 4500,patience=250 if name=='slow' else 200,**extra)
    specs=[cat('control','Reproduce the exact round-three 55-column default model before trusting any new comparison.'),
        cat('control512','Reproduce the exact round-three 55-column 512-border model.',dict(border_count=512))]
    for depth in [4,6,7]:specs.append(cat(f'depth{depth}','Change depth on the successful 55-column representation while holding shrinkage fixed.',dict(depth=depth)))
    for strength in [2,24,64]:specs.append(cat(f'l2_{strength}','Retune leaf shrinkage after the signed/category representation changed.',dict(l2_leaf_reg=strength)))
    specs += [cat('slow','Test smaller boosting steps on the final representation.',dict(learning_rate=.025)),
        cat('fast','Test larger boosting steps on the final representation.',dict(learning_rate=.075))]
    for value in [0.,2.]:specs.append(cat('random'+str(int(value)),'Retune split-score noise on the final representation.',dict(random_strength=value)))
    for count in [128,1024]:specs.append(cat(f'borders{count}','Test the bias/variance tradeoff of coarser or finer quantization on all 55 columns.',dict(border_count=count)))
    specs += [cat('rsm075','Test column sampling with the added term features.',dict(rsm=.75)),
        cat('ctr2','Test less complex categorical combinations after adding term categories.',dict(max_ctr_complexity=2)),
        cat('native','Retest native missing bins with the final signed/category features.',missing='native'),
        cat('groups','Test training-fold-only frequencies and group-relative predictors with the final features.',groups=True),
        cat('onehot16','Test explicit splits for the added low-cardinality term categories.',dict(one_hot_max_size=16)),
        cat('depthwise','Test asymmetric growth with a minimum leaf size as one combined recipe.',dict(grow_policy='Depthwise',min_data_in_leaf=100))]
    for parent,label in [('r3_lgb_proxy','lgb55'),('r3_lgb_proxy_smooth','lgb55_smooth'),('r3_xgb_proxy','xgb55')]:
        original=read(prev.ART/'screen'/(parent+'.json'))['spec']
        specs.append(dict(name='r4_'+label,kind=original['kind'],features='final55',stage='A',params=original['params'],groups=original.get('groups',False),
            hypothesis='Test the final signed/category representation in the earlier alternative-family recipe ('+parent+').'))
    for mode,why in [('period3','Test a finer ratio-rounding scale as a separate representation ablation.'),
        ('period24','Test a coarser ratio-rounding scale as a separate representation ablation.'),
        ('period3_24','Test whether finer and coarser added scales complement each other.'),
        ('goods_ratio','Test goods-price/annuity as a different supplied-amount ratio without extra categorical structure.'),
        ('goods_structure','Test signed residuals and coarse categories of goods-price/annuity.'),
        ('all_terms','Test the joint added-scale and goods-ratio block rather than assuming its parts add up.')]:
        specs.append(cat(mode,why,mode=mode,stage='B'))
    assert len([s for s in specs if s['stage']=='A'])==23 and len(specs)==29
    return specs

def screen_one(spec,train,y,split):
    assert_core();path=ART/'screen'/(spec['name']+'.json')
    if path.exists():
        row=read(path)
        if row.get('signature')==SIGNATURE and row['spec']==spec and row['status']=='complete':return row
    began=time.time();event('screen_start',spec=spec)
    row=dict(name=spec['name'],spec=spec,signature=SIGNATURE,seed=SEED,split='Original inner development split; repeatedly explored selection data.')
    try:
        x=features(train,spec['features']);a=split['inner_fit'];b=split['inner_valid']
        model,enc,p,it=fit(spec,x,y,a,b)
        reference=reference_prediction(component_predictions('screen'));baseline=metrics(y[b],reference)['auc']
        blends=[dict(new_weight=w,auc=metrics(y[b],(1-w)*reference+w*p)['auc']) for w in [.1,.25,.5,.75,1.]]
        curve=model.get_evals_result() if spec['kind']=='cat' else (model.evals_result() if spec['kind']=='xgb' else model.evals_result_)
        dump(ART/'screen'/(spec['name']+'_curve.json'),curve);np.save(ART/'screen'/(spec['name']+'.npy'),p)
        row.update(status='complete',**metrics(y[b],p),iterations=it,features=x.shape[1],seconds=time.time()-began,
            reference_auc=baseline,best_blend=max(blends,key=lambda a:a['auc']),blends=blends,
            saturated=it>=spec.get('max_iterations',4500)-5,
            resolved_parameters=model.get_all_params() if spec['kind']=='cat' else model.get_params())
        if spec['name']in ['r4_cat_control','r4_cat_control512']:
            parent='r3_cat_signed' if spec['name']=='r4_cat_control' else 'r3_cat_feature_b512'
            row['control_max_difference']=float(np.max(np.abs(p-np.load(prev.ART/'screen'/(parent+'.npy')))))
            assert row['control_max_difference']==0.,'Exact reference control failed.'
    except Exception as exc:
        (ART/'screen'/(spec['name']+'_error.txt')).write_text(traceback.format_exc())
        row.update(status='failed',error=str(exc),seconds=time.time()-began)
    dump(path,row);event('screen_finish',name=spec['name'],status=row['status'],auc=row.get('auc'),seconds=row['seconds'])
    print({k:v for k,v in row.items() if k in ['name','status','auc','iterations','seconds','best_blend','control_max_difference','error']},flush=True)
    return row

def screen_rows():return [read(p) for p in sorted((ART/'screen').glob('*.json')) if not p.name.endswith('_curve.json')]

def screen():
    assert_core();train,test,y,split=load();specs=candidates();plan=ART/'candidate_plan.json'
    if plan.exists():assert read(plan)==specs
    else:dump(plan,specs);event('initial_plan_frozen',configurations=len(specs),signature=SIGNATURE,engine_sha256=SOURCE_SHA)
    for spec in specs[:2]:
        control=screen_one(spec,train,y,split)
        assert control['status']=='complete' and control['control_max_difference']==0
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda s:screen_one(s,train,y,split),specs[2:]))
    event('initial_screen_complete',configurations=len(specs))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['screen']);a=p.parse_args();globals()[a.phase]()
