"""Generate only the three prospectively specified positive-component combinations."""
from concurrent.futures import ThreadPoolExecutor
import round4 as t

def main():
    rows=t.screen_rows();by={a['name']:a for a in rows};initial=t.read(t.ART/'candidate_plan.json')
    assert all(s['name']in by for s in initial),'Complete the initial 29 screens.'
    control=by['r4_cat_control']['auc'];base=dict(depth=5,l2_leaf_reg=8,random_strength=.5)
    gain=lambda a:a['best_blend']['auc']-a['reference_auc']
    good=lambda a:a['auc']>=control+.0002 or gain(a)>=.00015
    cats=[a for a in rows if a['status']=='complete' and a['spec']['kind']=='cat' and not a['name'].startswith('r4_cat_control')]
    params=[a for a in cats if a['spec']['stage']=='A' and good(a)]
    features=[a for a in cats if a['spec']['stage']=='B' and gain(a)>=.00015]
    specs=[]
    def make(name,why,param,mode='final55',**extra):
        return dict(name='r4_cat_'+name,kind='cat',features=mode,stage='follow-up',params=param,hypothesis=why,max_iterations=6000 if param.get('learning_rate')==.025 else 4500,patience=250 if param.get('learning_rate')==.025 else 200,**extra)
    feature=max(features,key=lambda a:a['best_blend']['auc']) if features else None
    param=max(params,key=lambda a:a['best_blend']['auc']) if params else None
    if feature and param:
        extras={k:param['spec'][k] for k in ['groups','missing'] if k in param['spec']}
        specs.append(make('feature_param','Combine eligible feature '+feature['name']+' with eligible parameter recipe '+param['name']+'.',param['spec']['params'],feature['spec']['features'],**extras))
    depths=[a for a in cats if a['name']in ['r4_cat_depth4','r4_cat_depth6','r4_cat_depth7'] and a['auc']>=control+.0002 and gain(a)>0]
    leaves=[a for a in cats if a['name'].startswith('r4_cat_l2_') and a['auc']>=control+.0002 and gain(a)>0]
    if depths and leaves:
        d=max(depths,key=lambda a:a['best_blend']['auc']);l=max(leaves,key=lambda a:a['best_blend']['auc'])
        specs.append(make('joint_depth_l2','Combine independently positive depth and shrinkage settings; '+d['name']+' and '+l['name']+'.',
            {**base,'depth':d['spec']['params']['depth'],'l2_leaf_reg':l['spec']['params']['l2_leaf_reg']}))
    native=by.get('r4_cat_native')
    if feature and native and native['status']=='complete' and gain(native)>=.00015:
        candidate=make('feature_native','Combine the eligible native-missing result with '+feature['name']+'.',base.copy(),feature['spec']['features'],missing='native')
        if not any(all(candidate.get(k)==s.get(k) for k in ['features','params','groups','missing']) for s in specs):specs.append(candidate)
    assert len(specs)<=3
    file=t.ART/'followup_plan.json'
    if file.exists():assert t.read(file)==specs
    else:t.dump(file,specs);t.event('followup_plan_recorded',specs=specs,control_auc=control)
    train,test,y,split=t.load()
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda s:t.screen_one(s,train,y,split),specs))
    print('Follow-up configurations:',len(specs),flush=True)

if __name__=='__main__':main()
