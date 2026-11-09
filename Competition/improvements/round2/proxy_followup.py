"""Isolate the positive term-proxy ablation before development CV selection."""
from concurrent.futures import ThreadPoolExecutor
import round2 as r
from adaptive import screen_one

def plan():
    parent=r.read(r.ART/'screen/r2_cat_term_proxies.json')['spec']
    columns=parent['columns'];base=[c for c in columns if not c.startswith(('ASSUMED_PERIOD_RATE_','TERM_MULTIPLE_'))]
    rates=[c for c in columns if c.startswith('ASSUMED_PERIOD_RATE_')]
    distances=[c for c in columns if c.startswith('TERM_MULTIPLE_')]
    def make(name,hypothesis,**changes):
        return {**parent,'name':name,'hypothesis':hypothesis,'source':'improvements/round2/proxy_followup.py',**changes}
    specs=[
        make('r2_cat_proxies_native','The proxy-only representation improved screening by 0.00146; combine it with the independently promising native missing policy.',missing='native'),
        make('r2_cat_rates_only','Separate the hypothetical positive-rate transforms from the term-rounding distances.',columns=base+rates),
        make('r2_cat_distances_only','Separate the 6/12-period term-distance transforms from hypothetical rates.',columns=base+distances),
        make('r2_cat_proxies_rsm075','Test whether the promising proxy block complements column sampling while retaining the resolved MVS bootstrap.',params={**parent['params'],'rsm':.75,'bagging_temperature':1.})]
    r.dump(r.ART/'proxy_followup_plan.json',specs)
    return specs

def main():
    train,test,y,split=r.load();specs=plan()
    r.event('proxy_followup_start',trigger='rate/term proxies +0.0014595; burden block -0.0008014',specs=specs)
    with ThreadPoolExecutor(max_workers=2) as pool: list(pool.map(lambda s:screen_one(s,train,y,split),specs))
    r.event('proxy_followup_complete',candidates=len(specs))

if __name__=='__main__':main()
