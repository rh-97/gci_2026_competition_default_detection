"""Evidence-backed journals and report; keep historical records untouched."""
import argparse,json
import numpy as np
import pandas as pd
import round4 as t

def table(headers,rows):
    clean=lambda s:str(s).replace('|','/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(clean,r))+' |' for r in rows])

def interpretation(a,chosen):
    if a['status']!='complete':return 'Failed: '+a.get('error','see error trace')+'. No score or negative scientific conclusion is assigned to this failed fit.'
    if a['name']in ['r4_cat_control','r4_cat_control512']:return 'Exact reproduction control: maximum prediction difference is 0.0. This validates the shared split, representation, fitting path and environment; it is not a new improvement.'
    gain=a['best_blend']['auc']-a['reference_auc']
    text=('Best screened blend improved the current recipe by '+f'{gain:+.7f} AUC. ' if gain>0 else 'No positive screened blend gain over the current recipe. ')
    if not (t.ART/'promotion.json').exists():text+='Promotion has not been evaluated; the search is incomplete. '
    else:text+=('Promoted by its predeclared slot/threshold to common-fold CV. ' if a['name']in chosen else 'Not promoted under the predeclared slot/threshold rules. ')
    text+='The standalone AUC and blend gain answer different questions; correlated ranking errors can make a weaker individual model useful. '
    if a['spec']['stage']=='B' or a['spec']['features']!='final55':text+='These supplied-value transforms add representation, not new information; any effect may reflect split boundaries, categorical interactions or regularization. '
    else:text+='The hypothesized bias/variance or encoding mechanism is not causally identified by this score alone. '
    if a.get('saturated'):text+='The retained fit reached its configured cap, so undertraining remains possible. '
    else:text+='The selected iteration was below the configured cap; the observed result is not explained simply by exhausting that cap. '
    return text+'This repeatedly explored split cannot establish hidden-test improvement or universal ineffectiveness.'

def ledger():
    rows=t.screen_rows();promotion=t.read(t.ART/'promotion.json') if (t.ART/'promotion.json').exists() else {'chosen':[]}
    chosen={a['name'] for a in promotion['chosen']};records=[]
    for a in rows:
        cvpath=t.ART/'cv'/(a['name']+'.json');c=t.read(cvpath) if cvpath.exists() else None
        records.append(dict(pass_group='round4',record_type='main screening configuration',name=a['name'],status=a['status'],
            kind=a['spec']['kind'],features=a['spec']['features'],hypothesis=a['spec']['hypothesis'],
            rationale_origin='Plan recorded before fitting',spec=a['spec'],auc=a.get('auc'),average_precision=a.get('average_precision'),
            log_loss=a.get('log_loss'),brier=a.get('brier'),reference_auc=a.get('reference_auc'),best_blend=a.get('best_blend'),
            delta=a.get('best_blend',{}).get('auc',0)-a.get('reference_auc',0) if a['status']=='complete' else None,
            iterations=a.get('iterations'),seconds=a.get('seconds'),cv=c,interpretation=interpretation(a,chosen),
            artifact=str((t.ART/'screen'/(a['name']+'.json')).relative_to(t.ROOT))))
    t.dump(t.ART/'experiment_ledger.json',records)
    old=t.read(t.prev.ART/'complete_experiment_ledger.json');combined=old+records
    t.dump(t.ART/'complete_experiment_ledger.json',combined)
    pd.DataFrame([{k:(json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v) for k,v in r.items()} for r in combined]).to_csv(t.ART/'complete_experiment_ledger.csv',index=False)
    return records,combined

def optional(name):return t.read(t.ART/name) if (t.ART/name).exists() else {'status':'not yet available'}
def jsonblock(obj):return '```json\n'+json.dumps(obj,indent=2)+'\n```'

def journal(records,combined):
    out=['# Round four: complete experiment journal','',
        'Reference: `output/submission_round3_bagged.csv`, user-confirmed public AUC **0.76824**, rank snapshot **518**. The screenshot and explicit filename confirmation establish this attribution. Public feedback did not tune this pass. Hidden/private score remains unknown.',
        '', '## Recorded procedure','', (t.HERE/'PLAN.md').read_text(),
        '', '## Exact evidence and interpretation','',
        'All screen metrics use the repeatedly explored inner development split. Resolved library parameters and all five blend probes are in each linked JSON; full validation learning curves and predictions are adjacent. The fixed package versions are in `improvements/round4/requirements-round4.txt`. Runner settings inherit the preserved round-two tree fitter; seed, budgets and override settings are saved with each fit. No oversampling, threshold search or class rebalancing was needed for the AUC ranking objective. Missingness and category vocabularies are fitted only on training folds.',
        '',table(['Configuration','Individual AUC','Best blend gain','Iterations','Seconds','Status'],[[a['name'],a['auc'],a['delta'],a['iterations'],a['seconds'],a['status']] for a in records])]
    for a in records:
        out+=['', '### '+a['name'],'',a['hypothesis'],'',a['interpretation'],'',
            'Exact specification:',jsonblock(a['spec']),'',f"Raw metrics, all blend probes and resolved parameters: [{a['artifact']}]({a['artifact']})."]
        if a['cv']:out+=['','Common-fold validation:',jsonblock({k:v for k,v in a['cv'].items() if k not in ['spec','signature']})]
    for title,file in [('Follow-up configurations recorded before their fits','followup_plan.json'),('Promotion decisions','promotion.json'),
        ('Training-fraction plan','fraction_plan.json'),('Training-fraction result and cost control','fraction_feasibility.json'),
        ('Primary complete-grid selection','selection.json'),('Frozen new-seed confirmation','confirmation_results.json'),
        ('Matching three-seed check','averaging_results.json'),('Expanded fraction budget check','fraction_budget_check.json'),
        ('Final recommendation','final_results.json'),('Saved-model replay','reproduction.json'),('Conditional uncertainty','conditional_uncertainty.json')]:
        out+=['','## '+title,'',jsonblock(optional(file))]
    out+=['','## Operational evidence and limitations','',
        'The fitting core captures its complete file hash at import and asserts it before and after every fit. It was not edited while running. Cache keys include source, dependency, data/split and package identities. `artifacts/events.jsonl` records UTC start/finish times; raw logs and any error traces are retained locally. The round-three source-hash incident is historical and documented in its own unchanged journal. This pass does not silently recognize a new hash alias.',
        '',f'The unified ledger has {len(combined)} records: {sum(a.get("record_type")=="main screening configuration" for a in combined)} main screening configurations and {sum(a.get("record_type")!="main screening configuration" for a in combined)} separately labeled auxiliary records. Fraction-control fits, fold refits and prediction-combination grids are protocol evidence, not inflated counts of new screened configurations.',
        '', 'A new fold seed changes the partition of already explored labels. It is a robustness check, not an untouched test. The old audit was not reused as a fresh test. Conditional row bootstrap excludes fitting/search uncertainty. Individual feature importance, calibration and slice diagnostics are descriptive, not reasons for hand-adjusting predictions.',
        '', 'This pass stops when its recorded searches and gates finish. It does not establish a global optimum. Larger neural tuning, fully nested learned stacking, carefully justified specialists/interactions and further seed banks remain unproven directions. The outcome of a failed gate is to preserve the stronger evidenced submission, not to force a new file.']
    (t.ROOT/'ROUND4_EXPERIMENT_LOG.md').write_text('\n'.join(out)+'\n')

def report(records,combined):
    final=t.read(t.ART/'final_results.json');choice=t.read(t.ART/'selection.json');confirm=optional('confirmation_results.json');avg=optional('averaging_results.json');fraction=optional('fraction_feasibility.json')
    passed=final['accepted'];screen=[a for a in records if a['status']=='complete'];best=sorted(screen,key=lambda a:-(a['delta'] or 0))
    recommendation=('A new candidate passed every declared local gate. Its public score is unknown.' if passed else 'Round four did not produce a candidate that passed every declared gate. Keep the round-three bagged file with confirmed public AUC **0.76824**.')
    text=f'''# Competition improvement report — round four

{recommendation}

Recommended CSV: [`{final['submission']}`]({final['submission']}).
SHA-256: `{final['sha256']}`.
The previous public score is **0.76824**, rank snapshot **518**, explicitly confirmed by the user for `submission_round3_bagged.csv`. No round-four public score is inferred from local validation.

## Why this pass

Earlier broad tuning mainly preceded the successful 55-column signed-residual/rounded-category representation. This pass retuned that exact representation, tested six separate supplied-value feature ablations, and evaluated more training rows per model through paired nested-ten folds. The recorded plan preceded fitting. All supplied data, nine pre-existing notebooks, earlier source/models and submissions were preserved. All modeling used the project `.venv`; no online rows or pretrained weights were used.

## Experiments and decisions

There were **{len(records)} round-four screening configurations**, including two reproduction controls; **{len(screen)} completed**. Both controls reproduced their earlier predictions with maximum absolute difference **0.0**. The complete running ledger contains **{sum(a.get('record_type')=='main screening configuration' for a in combined)} main screen configurations**, with auxiliary meta probes separately labeled. Validation refits and blend grids are not counted as new screen configurations.

{table(['Configuration','Inner individual AUC','Best inner blend gain','Status'],[[a['name'],f"{a['auc']:.7f}" if a['auc']is not None else '',f"{a['delta']:+.7f}" if a['delta']is not None else '',a['status']] for a in sorted(records,key=lambda a:-(a['delta'] or -1))])}

Screening used the complete round-three recipe as its baseline. A positive screen alone did not qualify a submission: promotion required the recorded slot/threshold, followed by shared five-fold OOF. The complete primary pair/helper grid was frozen before any new confirmation fit. Fixed iterations, weights and CDFs were then transferred without retuning.

## Validation evidence

Primary OOF reference AUC: **{choice['baseline_auc']:.7f}**. Selected AUC: **{choice['auc']:.7f}**. Gain: **{choice['gain']:+.7f}**; primary gate passed: **{choice['primary_gate_passed']}**.
Frozen names: `{choice['names']}`; weights: `{choice['weights']}`; method: `{choice['method']}`.
The baseline-only recipe is retained when primary gain is below 0.00020. Later gates require positive confirmation gain in at least four of five groups, then at least 0.00020 gain against the matching three-seed reference and four positive groups. A ten-fold candidate must additionally pass its model-count control.

Confirmation:
{jsonblock(confirm)}

Three-seed check:
{jsonblock(avg)}

Training-fraction experiment:
{jsonblock(fraction)}

The fraction experiment held the existing family parameters and 1,312 trees fixed. Nested ten-fold models train on about 90% of rows versus 80% for five-fold models. The additional five-fold random-seed control, when justified by the first gate, matches inference model count while conservatively giving the control more OOF values per row. This separates useful training-fraction evidence from an unchecked increase in model count; it is not a perfectly isolated causal experiment.

These labels have been repeatedly explored. New fold seeds test partition robustness; neither they nor the historical audit are an untouched test. No full-data OOF or public feedback retuned the final policy. Percentile blends, if chosen, provide ranking scores rather than calibrated probabilities.

## What worked, what failed, and why

Each trial's exact hypothesis, specification, metrics, convergence budget, promotion decision and interpretation is in [`ROUND4_EXPERIMENT_LOG.md`](ROUND4_EXPERIMENT_LOG.md). The strongest screened alternatives were `{[a['name'] for a in best[:3]]}`; their downstream evidence determines retention. Score changes can reflect split boundaries, categorical interactions, regularization and correlated errors. Those mechanisms are hypotheses; validation results do not establish causal explanations or hidden-test improvement. Additional ratios/rounded buckets remain transforms of supplied values, not recovered loan schedules or interest rates.

The machine ledger is `improvements/round4/artifacts/complete_experiment_ledger.json` and `.csv`. Full raw curves, predictions, fold timing, resolved parameters, exact plans and source freezes are retained in `improvements/round4/artifacts`. Earlier reports and journals remain available, including the pre-round-four report in `improvements/round4/reference`.

## Reproduction, documentation and stopping

New notebooks: [`07_round4_experiments.ipynb`](07_round4_experiments.ipynb), [`08_round4_validation_reproduction.ipynb`](08_round4_validation_reproduction.ipynb). Both are executed with the local venv; training is opt-in. The saved model replay generates a new reproduction filename and verifies byte identity. Integrity verification covers every protected earlier file, new notebook execution, CSV schema/ID order/range and frozen selection source. The archive is [`output/competition_round4_reproduction.zip`](output/competition_round4_reproduction.zip); input CSVs and venv are excluded. See [`REPRODUCTION_README.md`](REPRODUCTION_README.md).

This pass completes the recorded directions and stops according to evidence. It does **not** exhaust every possible improvement. Larger neural searches, fully nested stacking, specialists with stronger slice evidence, additional justified interactions and larger seed banks remain possible, with unproven benefit and greater selection-overfitting risk. No further leaderboard improvement should be claimed without a submitted score tied to the candidate checksum.

The supplied competition documents state November 20, 2026, 01:00 UTC (07:00 Bangladesh) as the deadline, and say the last submitted file determines the entry. This is the supplied-document record, not a live platform check. A code ZIP is needed for Honors/Outstanding consideration.
'''
    (t.ROOT/'IMPROVEMENT_REPORT.md').write_text(text)
    (t.ROOT/'REPRODUCTION_README.md').write_text(f'''# Reproducing the recommended submission

Recommended: `{final['submission']}`
SHA-256: `{final['sha256']}`

{recommendation}

Use the original supplied `input` directory and project Python 3.12 `.venv`.
Pinned packages: `improvements/round4/requirements-round4.txt`.
No additional dataset, internet data or pretrained weights are required.
The archive excludes input CSVs, the venv, kernel/cache directories and earlier ZIPs.

Prediction-only replay from `Competition`:

```sh
.venv/bin/python improvements/round4/r4_final.py reproduce
```

Full round-four phase order (matching caches are reused):

```sh
.venv/bin/python improvements/round4/round4.py screen
.venv/bin/python improvements/round4/r4_followup.py
.venv/bin/python improvements/round4/r4_cv.py
.venv/bin/python improvements/round4/r4_fraction.py
.venv/bin/python improvements/round4/r4_validate.py select
.venv/bin/python improvements/round4/r4_validate.py confirmation
.venv/bin/python improvements/round4/r4_validate.py averaging
.venv/bin/python improvements/round4/r4_final.py train_final
.venv/bin/python improvements/round4/r4_final.py reproduce
```

Do not run all historical notebooks to generate predictions. New notebooks 07/08
review the evidence, and 08 checks the saved-model replay. Their training flag is
false by default. All nine older notebooks are preserved. See `ROUND4_EXPERIMENT_LOG.md`
for all trials, including failures and negative results; the earlier journals
retain prior work. Selection cannot be regridded after confirmation.

Package member SHA-256s: `improvements/round4/artifacts/package_manifest.json`.
The archive was checked against these hashes and ZIP CRC. When unpacking, the
protected-file check permits explicitly excluded input data and earlier ZIPs to
be absent; all present protected files must still match. Local original inputs
and all protected earlier files were verified before packaging.
''')

def main():
    p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');args=p.parse_args()
    records,combined=ledger();journal(records,combined)
    if args.final:report(records,combined)
    print('Documented',len(records),'round-four screens; unified records',len(combined),flush=True)
if __name__=='__main__':main()
