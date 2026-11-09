"""Describe the frozen winner's marginal complexity; never change selection."""
import numpy as np
import round3 as t
import validate as v

def main():
    choice=t.read(t.ART/'selection.json');grid=t.read(t.ART/'blend_candidates.json')
    count=lambda row:sum(n.startswith('r3_') and w>0 for n,w in zip(row['names'],row['weights']))
    simpler=[a for a in grid if count(a)<count(choice)]
    best=max(simpler,key=lambda a:a['auc']) if simpler else None
    ps,_=v.primary_pool();new=[n for n,w in zip(choice['names'],choice['weights']) if n.startswith('r3_') and w>0]
    result=dict(winner_names=choice['names'],winner_weights=choice['weights'],winner_auc=choice['auc'],
        best_recorded_primary_recipe_with_fewer_new_families=best,
        primary_marginal_gain=choice['auc']-best['auc'] if best else None,
        correlations=[dict(a=a,b=b,pearson=float(np.corrcoef(ps[a],ps[b])[0,1])) for i,a in enumerate(new) for b in new[i+1:]],
        note='Descriptive complexity check on a frozen primary recipe. It does not retune weights, change gates, remove a model, or establish a separately significant marginal benefit.')
    if best is not None:
        train,test,y,split=t.load();target=y[split['development']]
        cdfs=dict(np.load(t.ART/'primary_cdf_references.npz'));secondary=v.current_secondary_components()
        for row in choice['new_families']:
            path=t.ART/'secondary'/(row['name']+'_oof.npy')
            if path.exists():secondary[row['name']]=np.load(path)
        secondary=v.add_reference(secondary)
        confirmation={a['name']:np.load(t.ART/'confirmation'/(a['name']+'_oof.npy'))
            for a in v.families()+choice['new_families'] if (t.ART/'confirmation'/(a['name']+'_oof.npy')).exists()}
        if all(a['name']in confirmation for a in v.families()):confirmation=v.add_reference(confirmation)
        checks={}
        for label,pool in [('fixed_confirmation',confirmation),('secondary',secondary),
            ('two_seed_average',{n:(ps[n]+secondary[n])/2 for n in secondary if n in ps})]:
            if all(n in pool for n in set(best['names']+choice['names'])):
                a=t.metrics(target,v.recipe_prediction(choice,pool,cdfs))['auc']
                b=t.metrics(target,v.recipe_prediction(best,pool,cdfs))['auc']
                checks[label]=dict(frozen_winner_auc=a,frozen_primary_simpler_recipe_auc=b,difference=a-b)
        result['later_descriptive_comparisons']=checks
    t.dump(t.ART/'winner_complementarity.json',result);print(result)

if __name__=='__main__':main()
