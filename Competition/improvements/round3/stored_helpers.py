"""Read-only late complementarity probe; never alter the frozen winner."""
import time
import numpy as np
from scipy.special import expit,logit
import round3 as t
import validate as v

def main():
    path=t.ART/'stored_helper_probe.json'
    if path.exists():print(t.read(path));return
    choice=t.read(t.ART/'selection.json');ps,_=v.primary_pool()
    cdfs=dict(np.load(t.ART/'primary_cdf_references.npz'));winner=v.recipe_prediction(choice,ps,cdfs)
    train,test,y,split=t.load();target=y[split['development']]
    baseline=t.metrics(target,winner)['auc'];assert abs(baseline-choice['auc'])<1e-12
    used=set()
    for name,w in zip(choice['names'],choice['weights']):
        if w<=0:continue
        if name=='round2_reference':used.update(a['name'] for a in v.families())
        else:used.add(name)
    pool=[]
    for row in t.r.old.load_json('cv_results.json'):
        file=t.r.old.ART/(row['name']+'_oof.npy')
        if file.exists() and row['name']not in used:pool.append(dict(row=row,path=file,origin='first pass'))
    for file in sorted((t.r.ART/'cv').glob('*.json')):
        row=t.read(file);pred=file.with_name(row['name']+'_oof.npy')
        if pred.exists() and row['name']not in used:pool.append(dict(row=row,path=pred,origin='second pass'))
    specs=[dict(name=a['row']['name'],origin=a['origin'],spec=a['row']['spec'],iterations=a['row']['iterations'],
        prediction_path=str(a['path'].relative_to(t.ROOT))) for a in pool]
    t.dump(t.ART/'stored_helper_specs.json',specs);t.event('stored_helper_probe_start',helpers=len(specs),plan='STORED_HELPER_PLAN.md')
    results=[];started=time.time()
    for item in pool:
        row=item['row'];p=np.load(item['path']);assert len(p)==len(target)
        original=t.metrics(target,p)['auc'];assert abs(original-row['auc'])<1e-12,row['name']
        blends=[]
        for weight in [.05,.1,.25]:
            for method in ['probability','log_odds']:
                q=(1-weight)*winner+weight*p if method=='probability' else expit((1-weight)*logit(np.clip(winner,1e-7,1-1e-7))+weight*logit(np.clip(p,1e-7,1-1e-7)))
                auc=t.metrics(target,q)['auc']
                blends.append(dict(helper_weight=weight,method=method,auc=auc,gain=auc-baseline))
        best=max(blends,key=lambda a:a['auc'])
        results.append(dict(name=row['name'],origin=item['origin'],helper_auc=original,best=best,blends=blends,alignment_verified=True))
        print(row['name'],best,flush=True)
    best=max(results,key=lambda a:a['best']['gain']) if results else None
    report=dict(reference='Frozen third-pass primary winner',baseline_auc=baseline,results=results,helpers=len(results),
        best_helper=best['name'] if best else None,best_gain=best['best']['gain'] if best else 0.,
        warrants_new_validation_branch=bool(best and best['best']['gain']>=.0002),seconds=time.time()-started,
        note='Late adaptive primary-only screening on stored OOF predictions. It does not alter frozen weights or independently confirm a new model.')
    t.dump(path,report);t.event('stored_helper_probe_finish',best_gain=report['best_gain'],warrants_new_validation_branch=report['warrants_new_validation_branch'])

if __name__=='__main__':main()
