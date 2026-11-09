"""Explain recorded primary blend results without fitting or changing weights."""
import pandas as pd
import round2 as r
from validate import pool_records

def main():
    candidates=r.read(r.ART/'blend_candidates.json');pool=pool_records();lead='r2_cat_term_proxies'
    rows=[]
    for component in pool:
        name=component['name']
        if name==lead:continue
        options=[a for a in candidates if len(a['names'])==2 and set(a['names'])=={lead,name}]
        if not options:continue
        best=max(options,key=lambda a:a['auc'])
        rows.append(dict(component=name,individual_auc=component['auc'],best_recorded_pair_auc=best['auc'],
            lead_weight=best['weights'][best['names'].index(lead)],component_weight=best['weights'][best['names'].index(name)]))
    rows.sort(key=lambda a:-a['best_recorded_pair_auc'])
    r.dump(r.ART/'complementarity_summary.json',{'lead':lead,'scope':'Recorded primary development weight grid only; no new fitting or secondary-seed search',
        'interpretation':'A higher individual AUC does not guarantee a better mixture; differences can also reflect calibration and correlated errors. These scores do not isolate a causal mechanism.','comparisons':rows})
    pd.DataFrame(rows).to_csv(r.ART/'complementarity_summary.csv',index=False)
    print(pd.DataFrame(rows).to_string(index=False))

if __name__=='__main__':main()
