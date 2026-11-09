"""Execute the prospectively recorded quantization follow-up after initial screens."""
from concurrent.futures import ThreadPoolExecutor
import round3 as t

def main():
    initial=t.read(t.ART/'candidate_plan.json');by={a['name']:a for a in t.screen_rows()}
    assert all(s['name']in by for s in initial),'Complete initial screening first.'
    base=dict(depth=5,l2_leaf_reg=8,random_strength=.5)
    def spec(name,why,changes,mode='proxy',**extra):
        return dict(name='r3_cat_'+name,kind='cat',features=mode,params={**base,**changes},
            hypothesis=why,max_iterations=4500,patience=200,source='improvements/round3/followup.py',**extra)
    train,test,y,split=t.load()
    columns=list(t.features(train.iloc[:3],'proxy').columns)
    loan=[c for c in columns if c=='CREDIT_TERM' or c.startswith(('ASSUMED_PERIOD_RATE_','TERM_MULTIPLE_'))]
    score=[c for c in columns if c.startswith('EXT_')]
    overrides=lambda selected:[str(columns.index(c))+':border_count=512' for c in selected]
    signed_columns=list(t.features(train.iloc[:3],'signed').columns)
    ignore=lambda suffix:[i for i,c in enumerate(signed_columns) if c.endswith(suffix)]
    specs=[spec('borders1024','Follow up the positive 512-border result: test whether finer quantization continues to help.',dict(border_count=1024)),
        spec('depth4_b512','Combine independently promising shallower trees and finer quantization on the proxy representation.',dict(depth=4,l2_leaf_reg=5,border_count=512)),
        spec('native_b512','Test the interaction between native missing bins and finer quantization.',dict(border_count=512),missing='native'),
        spec('loan_b512','Isolate higher resolution for credit term and loan proxies; test whether they explain the global border-count gain.',dict(per_float_feature_quantization=overrides(loan))),
        spec('scores_b512','Isolate higher resolution for external scores as an alternative explanation for the global border-count gain.',dict(per_float_feature_quantization=overrides(score))),
        spec('signed_only','Decompose the positive joint term representation: keep signed residual additions and ignore rounded category additions.',dict(ignored_features=ignore('_CATEGORY')),mode='signed'),
        spec('term_categories','Decompose the positive joint term representation: keep rounded category additions and ignore signed residual additions.',dict(ignored_features=ignore('_SIGNED')),mode='signed')]
    eligible=[a for a in by.values() if a['status']=='complete' and a['name']in ['r3_cat_signed','r3_cat_rates','r3_cat_crosses','r3_cat_engineered_proxy']
        and a['auc']>by['r3_cat_baseline']['auc'] and a['best_blend']['auc']-a['reference_auc']>=.0001]
    if eligible:
        best=max(eligible,key=lambda a:a['best_blend']['auc'])
        specs.append(spec('feature_b512','Combine the eligible best new feature block ('+best['name']+') with finer quantization under the recorded rule.',
            dict(border_count=512),mode=best['spec']['features']))
    path=t.ART/'followup_plan.json'
    if path.exists():assert t.read(path)==specs
    else:t.dump(path,specs);t.event('followup_plan_frozen',specs=specs,plan='FOLLOWUP_PLAN.md')
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda s:t.screen_one(s,train,y,split),specs))
    t.event('followup_complete',count=len(specs))

if __name__=='__main__':main()
