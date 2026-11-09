"""Pre-recorded follow-ups to the observed finance gain and resolved defaults."""
import time,traceback
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from sklearn.metrics import roc_auc_score,average_precision_score,log_loss
import round2 as r

def plan(train):
    rows=[r.read(p) for p in (r.ART/'screen').glob('*.json')]
    initial=r.read(r.ART/'candidate_plan.json')
    assert all(any(a['name']==s['name'] for a in rows) for s in initial),'Complete the initial screen first.'
    base=dict(depth=5,l2_leaf_reg=8,random_strength=.5)
    lean=list(r.features(train.iloc[:3],'lean').columns)
    finance=list(r.features(train.iloc[:3],'finance').columns)
    proxies=[c for c in finance if c.startswith(('ASSUMED_PERIOD_RATE_','TERM_MULTIPLE_'))]
    burden=[c for c in finance if c not in lean+proxies]
    source='improvements/round2/adaptive.py'
    def cat(name,hypothesis,**kwargs):
        return dict(name=name,kind='cat',features='finance',params=base.copy(),source=source,hypothesis=hypothesis,**kwargs)
    specs=[
        cat('r2_cat_burden','Isolate the payment-burden and household-amount block from the hypothetical rate/term proxies.',columns=lean+burden),
        cat('r2_cat_term_proxies','Isolate the redundant nonlinear rate/term representations; test whether quantization alone explains the finance gain.',columns=lean+proxies),
        cat('r2_cat_finance_native','Test whether native missing bins and financial features provide complementary gains.',missing='native')]
    parameter_ids=['r2_cat_slow','r2_cat_strong_l2','r2_cat_weak_l2','r2_cat_onehot10','r2_cat_onehot64','r2_cat_borders512','r2_cat_rsm075','r2_cat_ordered']
    best=max([a for a in rows if a['name'] in parameter_ids and a['status']=='complete'],key=lambda a:a['auc'])
    specs.append(dict(name='r2_cat_finance_tuned',kind='cat',features='finance',params=best['spec']['params'],source=source,
        max_iterations=best['spec'].get('max_iterations',4500),
        hypothesis=f"Combine the finance representation with the best screened alternative CatBoost parameter recipe ({best['name']}); this tests interaction rather than assuming additive gains."))
    for complexity in [1,2]:
        specs.append(dict(name=f'r2_cat_ctr{complexity}',kind='cat',features='lean',source=source,
            params={**base,'max_ctr_complexity':complexity},hypothesis='The saved baseline resolves max_ctr_complexity=4. Restricting categorical-combination complexity may reduce variance.'))
    specs.append(dict(name='r2_cat_bayesian_rsm075',kind='cat',features='lean',source=source,
        params={**base,'rsm':.75,'bootstrap_type':'Bayesian','bagging_temperature':1.},
        hypothesis='Explicitly switch bootstrap from the resolved MVS default to Bayesian; compare against the column-sampling trial whose bootstrap remained MVS.'))
    xb=max([a for a in rows if a['spec']['kind']=='xgb' and a['status']=='complete'],key=lambda a:a['auc'])
    specs.append(dict(name='r2_xgb_finance',kind='xgb',features='finance',params=xb['spec']['params'],source=source,
        hypothesis='Check whether the financial representation also helps the best screened XGBoost recipe.'))
    lb=next(a for a in r.old.load_json('cv_results.json') if a['name']=='lgb_tune_15')
    specs.append(dict(name='r2_lgb_finance',kind='lgb',features='finance',params=lb['spec']['params'],groups=True,source=source,
        hypothesis='Check whether the finance representation improves the known complementary LightGBM configuration.'))
    r.dump(r.ART/'adaptive_plan.json',specs)
    r.event('adaptive_plan_written',trigger='finance +0.0005898 inner AUC; resolved bootstrap MVS and CTR complexity 4',specs=specs)
    return specs

def screen_one(spec,train,y,split):
    file=r.ART/'screen'/(spec['name']+'.json')
    if file.exists():
        cached=r.read(file)
        if cached['status']=='complete' and cached['spec']==spec and cached['implementation_hash']==r.implementation_hash():
            r.event('adaptive_screen_cache_reused',name=spec['name'])
            return cached
    t=time.time();r.event('adaptive_screen_start',name=spec['name'],spec=spec)
    row=dict(name=spec['name'],spec=spec,implementation_hash=r.implementation_hash(),seed=r.SEED,
        split='original inner_fit/inner_valid, development only',feature_selection_rule='spec.columns if present; otherwise complete named representation')
    try:
        x=r.features(train,spec['features'])
        if 'columns' in spec: x=x[spec['columns']]
        model,enc,p,it=r.fit(spec,x,y,split['inner_fit'],split['inner_valid'])
        reference=np.load(r.old.ART/'cat_lean_inner.npy'); target=y[split['inner_valid']]
        resolved=model.get_all_params() if spec['kind']=='cat' else model.get_params()
        curve=model.get_evals_result() if spec['kind']=='cat' else (model.evals_result() if spec['kind']=='xgb' else model.evals_result_)
        curve_dir=r.ART/'curves'/spec['name'];curve_dir.mkdir(parents=True,exist_ok=True)
        r.dump(curve_dir/'screen_learning_curve.json',curve)
        row.update(status='complete',auc=roc_auc_score(target,p),average_precision=average_precision_score(target,p),log_loss=log_loss(target,p),
            iterations=it,features=x.shape[1],seconds=time.time()-t,auc_delta_vs_pass1_cat=roc_auc_score(target,p)-roc_auc_score(target,reference),
            prediction_correlation=float(np.corrcoef(p,reference)[0,1]),maximum_prediction_difference=float(np.max(np.abs(p-reference))),
            saturated=it>=spec.get('max_iterations',4500)-5,resolved_parameters=resolved)
        np.save(r.ART/'screen'/(spec['name']+'.npy'),p)
    except Exception as exc:
        (r.ART/'errors'/(spec['name']+'.txt')).write_text(traceback.format_exc())
        row.update(status='failed',error=str(exc),seconds=time.time()-t)
    r.dump(file,row);r.event('adaptive_screen_finish',name=spec['name'],status=row['status'],auc=row.get('auc'))
    print({k:v for k,v in row.items() if k not in ['spec','resolved_parameters','implementation_hash']},flush=True)
    return row

def main():
    train,test,y,split=r.load(); specs=plan(train)
    with ThreadPoolExecutor(max_workers=2) as pool: list(pool.map(lambda s:screen_one(s,train,y,split),specs))
    r.event('adaptive_screen_complete',candidates=len(specs))

if __name__=='__main__': main()
