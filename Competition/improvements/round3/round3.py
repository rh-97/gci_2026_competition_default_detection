"""Third-pass experiments. Prior passes are immutable, read-only dependencies."""
from pathlib import Path
import os,sys
os.environ.setdefault('OMP_NUM_THREADS','4')
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'round2'))
import round2 as r
sys.path.insert(0,str(HERE))
import argparse,copy,hashlib,inspect,json,time,traceback,threading
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder,QuantileTransformer
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score,average_precision_score,log_loss,brier_score_loss
from threadpoolctl import threadpool_limits

ROOT=r.ROOT;ART=HERE/'artifacts';MODELS=HERE/'models';SEED=r.SEED
LOCK=threading.Lock()
dump=r.dump;read=r.read;load=r.load

def event(kind,**kwargs):
    with LOCK:
        with (ART/'events.jsonl').open('a') as f:
            f.write(json.dumps(dict(time_utc=datetime.now(timezone.utc).isoformat(),event=kind,**kwargs),default=str)+'\n')

def features(df,mode='proxy'):
    finance=r.features(df,'finance')
    lean=list(r.features(df.iloc[:1],'lean').columns)
    proxy=[c for c in finance if c.startswith(('ASSUMED_PERIOD_RATE_','TERM_MULTIPLE_'))]
    x=finance[lean+proxy].copy()
    if mode=='engineered_proxy':
        x=r.old.features(df,'engineered')
        for c in proxy: x[c]=finance[c]
    if mode=='signed':
        for n in [6,12]:
            z=x.CREDIT_TERM/n
            x[f'TERM_MULTIPLE_{n}_SIGNED']=z-np.rint(z)
            x[f'TERM_ROUND_{n}_CATEGORY']=np.rint(z).astype('Int64').astype(str)
    if mode=='rates':
        payment=(x.AMT_ANNUITY/x.AMT_CREDIT.replace(0,np.nan)).to_numpy()
        for n in [12,18,48,72,84]:
            low=np.zeros(len(x));high=np.ones(len(x))
            valid=np.isfinite(payment)&(payment>=1/n)&(payment<1)
            for _ in range(28):
                mid=(low+high)/2;factor=mid/(-np.expm1(-n*np.log1p(mid)))
                take=factor<payment;low=np.where(take,mid,low);high=np.where(take,high,mid)
            x[f'ASSUMED_PERIOD_RATE_{n}']=np.where(valid,(low+high)/2,np.nan)
    if mode=='crosses':
        for a,b in [('CODE_GENDER','NAME_EDUCATION_TYPE'),('OCCUPATION_TYPE','NAME_INCOME_TYPE'),('NAME_CONTRACT_TYPE','NAME_HOUSING_TYPE')]:
            x[a+'__'+b]=x[a].astype(str)+'|'+x[b].astype(str)
        x['AGE_BAND_5']=((-x.DAYS_BIRTH/365.25)//5).astype('Int64').astype(str)
    return x.replace([np.inf,-np.inf],np.nan)

class NeuralEncoder:
    def fit(self,x):
        self.columns=list(x.columns)
        self.cats=list(x.select_dtypes(include=['object','str']).columns)
        self.nums=[c for c in x if c not in self.cats]
        self.transformer=ColumnTransformer([
            ('numeric',make_pipeline(SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True),
                QuantileTransformer(n_quantiles=256,output_distribution='normal',random_state=SEED)),self.nums),
            ('categorical',OneHotEncoder(handle_unknown='ignore',sparse_output=False,dtype=np.float32),self.cats)])
        self.transformer.fit(x[self.columns]);return self
    def transform(self,x): return self.transformer.transform(x[self.columns]).astype('float32')

def fit(spec,x,y,tr,va=None,fixed=None,seed=SEED):
    if spec['kind']!='mlp': return r.fit(spec,x,y,tr,va,fixed,seed)
    enc=NeuralEncoder().fit(x.iloc[tr]);a=enc.transform(x.iloc[tr]);b=enc.transform(x.iloc[va]) if va is not None else None
    model=MLPClassifier(hidden_layer_sizes=tuple(spec['params']['hidden_layer_sizes']),
        alpha=spec['params']['alpha'],learning_rate_init=.001,batch_size=1024,activation='relu',
        solver='adam',max_iter=1,random_state=seed,shuffle=True)
    best=None;best_auc=-np.inf;best_epoch=0;curve=[]
    maximum=fixed or spec.get('max_iterations',80)
    with threadpool_limits(limits=4):
        for epoch in range(1,maximum+1):
            model.partial_fit(a,y[tr],classes=np.array([0,1]))
            if b is not None:
                p=model.predict_proba(b)[:,1];auc=roc_auc_score(y[va],p)
                curve.append(dict(epoch=epoch,validation_auc=auc,training_loss=float(model.loss_)))
                if auc>best_auc+1e-6:
                    best_auc=auc;best_epoch=epoch;best=copy.deepcopy(model)
                if epoch-best_epoch>=spec.get('patience',12): break
    if b is not None: model=best;iteration=best_epoch
    else: iteration=maximum
    model.round3_learning_curve_=curve
    p=model.predict_proba(b)[:,1] if b is not None else None
    return model,enc,p,int(iteration)

def implementation_hash():
    source=''.join(inspect.getsource(f) for f in [features,NeuralEncoder,fit])
    return hashlib.sha256((source+r.implementation_hash()).encode()).hexdigest()

def signature_matches(recorded,canonical):
    if recorded==canonical:return True
    path=HERE/'reference/signature_alias_proof.json'
    if not path.exists():return False
    proof=read(path)
    if proof['aliases'].get(recorded)!=canonical:return False
    import ast
    cores=[]
    for name,want in proof['source_files'].items():
        source=(HERE/name).read_bytes()
        if hashlib.sha256(source).hexdigest()!=want:return False
        tree=ast.parse(source)
        core='\n'.join(ast.dump(node,include_attributes=False) for node in tree.body
            if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in proof['core_functions'])
        if hashlib.sha256(core.encode()).hexdigest()!=proof['core_ast_sha256']:return False
        cores.append(core)
    return len(cores)==2 and cores[0]==cores[1]

def candidates():
    base=dict(depth=5,l2_leaf_reg=8,random_strength=.5)
    def cat(name,why,changes=None,mode='proxy',**extra):
        return dict(name='r3_cat_'+name,kind='cat',features=mode,params={**base,**(changes or {})},
            hypothesis=why,max_iterations=4500,patience=200,**extra)
    specs=[cat('baseline','Exact control: recover the round-two proxy-only screen before evaluating new settings.')]
    for name,changes,why in [
        ('depth4',dict(depth=4,l2_leaf_reg=5),'Shallower trees may regularize the successful proxy representation differently.'),
        ('depth6',dict(depth=6,l2_leaf_reg=12),'More interactions may become useful with the proxy representation.'),
        ('depth7',dict(depth=7,l2_leaf_reg=20),'Test a further increase in interaction capacity with stronger shrinkage.'),
        ('slow',dict(learning_rate=.025),'Smaller boosting steps may improve the proxy model rather than the old representation.'),
        ('l2_30',dict(l2_leaf_reg=30),'Test stronger shrinkage with the winning feature block.'),
        ('borders512',dict(border_count=512),'Finer quantization may preserve loan-proxy and score thresholds.'),
        ('weight2',dict(scale_pos_weight=2.),'A moderately weighted objective may learn different useful ranking errors.'),
        ('depthwise',dict(depth=6,grow_policy='Depthwise',min_data_in_leaf=150),'Asymmetric trees may model conditional loan/score effects efficiently.')]:
        specs.append(cat(name,why,changes))
    specs += [cat('groups','Training-fold-only frequencies and group-relative financial quantities may complement the compact proxy model.',groups=True),
        cat('median','Median imputation may improve upon a sentinel or native missing split.',missing='median')]
    for mode,why in [('signed','Signed term residuals and rounded categories may retain structure lost by absolute distances.'),
        ('rates','Additional assumed-period transforms may expose useful numeric thresholds; these do not recover true rates.'),
        ('crosses','Explicit categorical interactions and age bands may complement native categorical combinations.'),
        ('engineered_proxy','The proxy block may improve the larger financial/score representation rather than just the compact one.')]:
        specs.append(cat(mode,why,mode=mode))
    oldlgb=next(a for a in r.old.load_json('cv_results.json') if a['name']=='lgb_tune_15')['spec']
    specs.append(dict(name='r3_lgb_proxy',kind='lgb',features='proxy',groups=True,params=oldlgb['params'],
        hypothesis='Use the exact compact successful proxy block in the known complementary LightGBM recipe.'))
    specs.append(dict(name='r3_lgb_proxy_smooth',kind='lgb',features='proxy',groups=True,
        params={**oldlgb['params'],'cat_smooth':100.,'cat_l2':30.,'min_child_samples':150,'num_leaves':16},
        hypothesis='Stronger categorical/leaf smoothing may work differently on the compact proxy representation.'))
    xb=read(r.ART/'screen/r2_xgb_finance.json')['spec']['params']
    specs.append(dict(name='r3_xgb_proxy',kind='xgb',features='proxy',params=xb,
        hypothesis='Remove the finance burden block that hurt CatBoost and test XGBoost on the successful compact proxy representation.'))
    for label,hidden,alpha in [('small',[64,32],.1),('wide',[128,64],1.)]:
        specs.append(dict(name='r3_mlp_'+label,kind='mlp',features='proxy',max_iterations=80,patience=12,
            params=dict(hidden_layer_sizes=hidden,alpha=alpha),hypothesis='A quantile-normalized neural model trained from scratch may contribute smooth complementary errors; fit preprocessing only on training rows.'))
    return specs

def baseline_predictions(stage='screen'):
    selection=read(r.ART/'selection.json');out=None
    for name,w in zip(selection['names'],selection['weights']):
        if stage=='screen':
            path=r.ART/'screen'/(name+'.npy')
            if not path.exists(): path=r.old.ART/(name+'_inner.npy')
        elif stage=='primary':
            path=r.ART/'cv'/(name+'_oof.npy')
            if not path.exists(): path=r.old.ART/(name+'_oof.npy')
        else: path=r.ART/'stability'/(name+'_oof.npy')
        p=np.load(path);out=w*p if out is None else out+w*p
    return out

def metrics(y,p):
    return dict(auc=float(roc_auc_score(y,p)),average_precision=float(average_precision_score(y,p)),
        log_loss=float(log_loss(y,p)),brier=float(brier_score_loss(y,p)))

def screen_one(spec,train,y,split):
    path=ART/'screen'/(spec['name']+'.json');signature=implementation_hash()
    if path.exists():
        row=read(path)
        if signature_matches(row.get('implementation_hash'),signature) and row['spec']==spec and row['status']=='complete': return row
    started=time.time();event('screen_start',spec=spec)
    row=dict(name=spec['name'],spec=spec,implementation_hash=signature,seed=SEED,split='original inner_fit/inner_valid, development only')
    try:
        x=features(train,spec['features']);tr=split['inner_fit'];va=split['inner_valid']
        model,enc,p,it=fit(spec,x,y,tr,va)
        np.save(ART/'screen'/(spec['name']+'.npy'),p)
        reference=baseline_predictions();reference_auc=roc_auc_score(y[va],reference)
        blends=[dict(new_weight=w,auc=float(roc_auc_score(y[va],(1-w)*reference+w*p))) for w in [.1,.25,.5,.75,1.]]
        curve=model.round3_learning_curve_ if spec['kind']=='mlp' else (model.get_evals_result() if spec['kind']=='cat' else (model.evals_result() if spec['kind']=='xgb' else model.evals_result_))
        dump(ART/'screen'/(spec['name']+'_curve.json'),curve)
        row.update(status='complete',**metrics(y[va],p),iterations=it,features=x.shape[1],seconds=time.time()-started,
            reference_auc=reference_auc,individual_gain=roc_auc_score(y[va],p)-reference_auc,
            best_blend=max(blends,key=lambda a:a['auc']),blends=blends,correlation=float(np.corrcoef(reference,p)[0,1]),
            saturated=it>=spec.get('max_iterations',4500)-5,
            resolved_parameters=model.get_all_params() if spec['kind']=='cat' else model.get_params())
        if spec['name']=='r3_cat_baseline':
            previous=np.load(r.ART/'screen/r2_cat_term_proxies.npy')
            row['baseline_max_difference']=float(np.max(np.abs(p-previous)))
            assert row['baseline_max_difference']==0.,'Round-two control must be exactly reproduced.'
    except Exception as exc:
        error=traceback.format_exc();(ART/'screen'/(spec['name']+'_error.txt')).write_text(error)
        row.update(status='failed',error=str(exc),seconds=time.time()-started)
    dump(path,row);event('screen_finish',name=spec['name'],status=row['status'],auc=row.get('auc'),seconds=row['seconds'])
    print({k:v for k,v in row.items() if k in ['name','status','auc','iterations','seconds','best_blend','error','baseline_max_difference']},flush=True)
    return row

def screen_rows():
    return [read(p) for p in sorted((ART/'screen').glob('*.json')) if not p.name.endswith('_curve.json')]

def screen():
    train,test,y,split=load();specs=candidates();plan=ART/'candidate_plan.json'
    if plan.exists(): assert read(plan)==specs
    else: dump(plan,specs);event('candidate_plan_recorded',count=len(specs),implementation_hash=implementation_hash())
    control=screen_one(specs[0],train,y,split)
    assert control['status']=='complete' and control['baseline_max_difference']==0
    # Keep native thread limits local to each tree fit; two 4-thread fits use 8 CPUs.
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda s:screen_one(s,train,y,split),[s for s in specs[1:] if s['kind']!='mlp']))
    # threadpoolctl changes process-wide BLAS settings, so neural fits run alone.
    for spec in [s for s in specs if s['kind']=='mlp']: screen_one(spec,train,y,split)
    event('screen_complete',count=len(specs))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['screen']);args=parser.parse_args()
    globals()[args.phase]()
