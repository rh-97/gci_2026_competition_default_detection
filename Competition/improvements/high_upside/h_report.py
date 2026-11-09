"""Report all structural experiments without importing the neural runtime."""
from pathlib import Path
import sys,json,argparse,re
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'round4'))
import round4 as t
HERE=Path(__file__).resolve().parent;ART=HERE/'artifacts'
def table(headers,rows):
    clean=lambda v:str(v).replace('|','/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(clean,r))+' |' for r in rows])
def block(obj):return '```json\n'+json.dumps(obj,indent=2)+'\n```'
def optional(name):return t.read(ART/name) if (ART/name).exists() else {'status':'not yet available'}

def ledger():
    plan=t.read(ART/'model_candidate_plan.json');promotion=optional('model_promotion.json');chosen={a['name'] for a in promotion.get('chosen',[])};records=[]
    for spec in plan:
        p=ART/'pilots'/(spec['name']+'.json')
        if not p.exists():continue
        a=t.read(p);cvfile=ART/'primary_cv'/(spec['name']+'.json');cv=t.read(cvfile) if cvfile.exists() else None
        gain=a['best_blend']['auc']-a['reference_auc'] if a['status']=='complete' else None
        if a['status']=='failed':text='Software/fit failure: '+a['error']+'. No scientific negative conclusion is inferred from a failed fit.'
        else:
            text=f"Standalone inner AUC {a['auc']:.7f}; best blend gain {gain:+.7f} against the complete current reference. "
            if (ART/'model_promotion.json').exists():text+='Promoted to common-fold CV. ' if a['name']in chosen else 'Did not advance under the recorded promotion rule. '
            else:text+='Promotion is pending completion of the six pilots. '
            if spec['kind']=='tabm':
                d=a['diagnostics'];text+=f"Retained epoch {a['count']} of {d['epochs_completed']} completed; stopping reason: {d['stop_reason']}. "
                text+='This tests this embedding/shared-ensemble recipe, not all neural architectures. A time-truncated fit cannot rule out useful convergence. '
            elif spec['learned']=='score_reconstruction':text+='Auxiliary score R2 measures reconstruction on observed rows, not default ranking or quality on genuinely missing scores. Downstream validation determines usefulness. '
            else:text+='Inner OOF risk maps prevent direct own-target encoding; their extra supervised representation can still add noise, selection bias or redundant signal already available to CatBoost. '
            text+='Mechanisms are hypotheses, not causal findings. Repeatedly explored selection labels cannot establish hidden-test improvement.'
        records.append(dict(pass_group='higher_upside',record_type='main screening configuration',name=a['name'],status=a['status'],kind=spec['kind'],features=spec['features'],
            hypothesis=spec['hypothesis'],spec=spec,auc=a.get('auc'),average_precision=a.get('average_precision'),log_loss=a.get('log_loss'),brier=a.get('brier'),
            reference_auc=a.get('reference_auc'),best_blend=a.get('best_blend'),delta=gain,count=a.get('count'),seconds=a['seconds'],diagnostics=a.get('diagnostics'),
            promoted=a['name']in chosen,cv=cv,fit_signature=a.get('signature'),recorded_backend=a.get('diagnostics',{}).get('device','cpu'),
            interpretation=text,artifact=str(p.relative_to(t.ROOT))))
    t.dump(ART/'model_experiment_ledger.json',records);combined=t.read(t.HERE/'artifacts/complete_experiment_ledger.json')+records
    t.dump(ART/'model_complete_experiment_ledger.json',combined)
    pd.DataFrame([{k:json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in combined]).to_csv(ART/'model_complete_experiment_ledger.csv',index=False)
    return records,combined

def journal(records):
    prior=(HERE/'reference/before_modeling/HIGH_UPSIDE_EXPERIMENT_LOG.md').read_text().replace('## Next experiment status','## Status when the opportunity audit concluded')
    text=[prior,'','## Model-stage recorded plan','',(HERE/'MODELING_PLAN.md').read_text(),'','## Prospective local-GPU amendment','',
        (HERE/'ACCELERATOR_AMENDMENT.md').read_text(),'','## Budget-aware selection before freeze','',
        (HERE/'COMPLEXITY_POLICY.md').read_text(),'','## Every pilot','',
        table(['Pilot','Status','Individual inner AUC','Best blend gain','Retained count','Seconds'],[[a['name'],a['status'],a['auc'],a['delta'],a['count'],round(a['seconds'],1)] for a in records])]
    for a in records:
        text+=['','### '+a['name'],'',a['hypothesis'],'',a['interpretation'],'',block(a['spec']),'',
            f"Raw metrics/all five weights: [{a['artifact']}]({a['artifact']}). Full curves and predictions are adjacent.",'',block(a['diagnostics'])]
        if a['cv']:text+=['','Primary common-fold CV:',block({k:v for k,v in a['cv'].items() if k not in ['spec','signature']})]
    for title,file in [('Software and leakage checks','model_preflight.json'),('Exact environment','model_environment.json'),('Promotion','model_promotion.json'),
        ('Primary frozen selection','model_selection.json'),('Confirmation','model_confirmation.json'),('Matching three-seed comparison','model_averaging.json'),
        ('Final result','model_final_results.json'),('Reproduction','model_reproduction.json'),('Conditional uncertainty','model_conditional_uncertainty.json'),
        ('Gate-aware parallel scheduling status','parallel_later_status.json'),('Matching-seed CPU dispatch','parallel_averaging_dispatch.json'),
        ('Final CPU dispatch','parallel_final_dispatch.json')]:text+=['','## '+title,'',block(optional(file))]
    text+=['','## Operations and evidence timing','',
        'PyTorch/TabM and numerical embeddings were installed into the existing project venv; the previous 17 modeling package versions remained unchanged. The pip report records software downloads only. No datasets or pretrained checkpoints were fetched. A Mac OpenMP duplicate-runtime abort occurred during the first import. Setting DYLD_LIBRARY_PATH to the venv torch/lib directory before process launch resolved it; duplicate-runtime checking was kept enabled. Tiny two-epoch and auxiliary software probes are labeled operational checks and excluded from the competitive configuration count.',
        '', 'The full source bytes of h_models.py and h_features.py are captured at import and checked during fitting. Cache identities include these, the preserved reference/data/split identity, plan and exact package versions. The six exact specs were written before the software probe and real pilots. The original CPU environment JSON was persisted after the first pilot had started; its identity matches the already-recorded CPU preflight/pilot signatures and is preserved under reference/cpu_stage. The current environment adds the separately hashed GPU implementation and prospective amendment while linking the original CPU identity. No core source was changed while fits were running; both workers were stopped before the runner was amended.',
        '', 'All validation labels are absent from fitted feature transforms, auxiliary teachers and risk maps. Validation AUC may select epochs/trees during screening and primary CV; fixed-count confirmation and final fitting do not use their validation labels for stopping. Each member of TabM is trained with its own BCE, with the mean member loss optimized; inference averages probabilities. The first three complete neural pilots ran on CPU. A local benchmark outside the sandbox then exposed a roughly three-times-faster MPS GPU. The CPU workers were stopped before primary CV; the fourth neural pilot was incomplete and its partial curve was archived. The prospective ACCELERATOR_AMENDMENT.md records this change. Completed CPU evidence keeps its original signatures and is checked by reference/cpu_stage_reuse.json; no numerical GPU-training alias is claimed. Subsequent neural training uses the separately hashed h_accel.py on MPS, and all retained predictions/saved-model inference use CPU. Exact checkpoint replay is checked, but bit-identical GPU retraining is not promised. Hyperparameters and validation gates did not change. Categorical unknowns use a reserved category. Low-cardinality numerical inputs may use one effective piecewise bin; library warnings are retained in raw logs.',
        '', 'Scheduling-only helpers precompute already-frozen neural confirmation folds on the idle GPU while the main process fits CPU references: first two folds, then the remaining three after reference fits were observed to take longer. A separate gate-aware scheduler may overlap eligible CPU challenger folds with later GPU fits, but only after confirmation/averaging pass respectively. They call the same frozen fitter with the exact same rows, seeds and counts, publish matching per-fold cache signatures, and avoid publishing if the parent reaches that family. Dispatcher source hashes and events are retained; this introduces no new configuration, data or selection. Per-fold seconds measure completed fits. Enclosing call seconds can exclude reused/precomputed work, so fold timings and event timestamps should be used to assess total work and overlap. Interrupted partial fits remain separate operational evidence.',
        '', 'Fresh partitions of previously explored labels are robustness checks. Any conditional OOF, subgroup metric, training score or full-data OOF remains descriptive after selection. Neither leaderboard observations nor training scores establish the attainable ceiling. No perfect-score provenance or misconduct is inferred. The 0.8+ target remains aspirational unless a submitted score confirms it.']
    (t.ROOT/'HIGH_UPSIDE_EXPERIMENT_LOG.md').write_text('\n'.join(text)+'\n')

def report(records,combined):
    final=t.read(ART/'model_final_results.json');choice=t.read(ART/'model_selection.json');confirm=t.read(ART/'model_confirmation.json');average=t.read(ART/'model_averaging.json')
    accepted=final['accepted'];summary=('A new higher-upside candidate passed every declared local gate. Its public score is unknown.' if accepted else 'The higher-upside pilots did not produce a recipe that passed every declared gate. The recommended submission remains the public-confirmed round-three bagged file, AUC **0.76824**.')
    complexity=dict(primary_new_predictor_bundles=0,auxiliary_reconstruction_regressors=0,neural_shared_internal_members=0,legacy_primary_models=75)
    if accepted:
        manifest=t.read(ART/'model_manifest.json');complexity['legacy_primary_models']=75 if 'round3_reference'in manifest['recipe']['names'] else 0
        for family in manifest['families']:
            n=sum(len(seed['instances']) for seed in family['seeds']);complexity['primary_new_predictor_bundles']+=n
            if family['spec'].get('learned')=='score_reconstruction':complexity['auxiliary_reconstruction_regressors']+=3*n
            if family['spec']['kind']=='tabm':complexity['neural_shared_internal_members']+=16*n
    complexity['note']='Each reconstructed-score primary bundle also contains three auxiliary regressors. TabM internal members share weights and are not separate saved fold models. new_models in the final result counts primary fold predictor bundles.'
    t.dump(ART/'model_deployment_complexity.json',complexity)
    planpath=t.ROOT/'HIGH_UPSIDE_PLAN.md';plantext=planpath.read_text()
    plantext=re.sub(r'Status:.*?priority change\.', 'Status: the six structural pilots and their applicable validation gates are complete.',plantext,count=1,flags=re.S)
    plantext=re.sub(r'The audit fitted no new model\..*?no new submission has yet been accepted\.',
        'The audit fitted no new model. The subsequent modeling phase is complete; see HIGH_UPSIDE_EXPERIMENT_LOG.md for the result. '+summary,plantext,count=1,flags=re.S)
    plantext=plantext.replace('PyTorch is not installed','PyTorch was not installed when this strategy was written; it was subsequently installed')
    planpath.write_text(plantext)
    text=f'''# Competition improvement report — higher-upside experiments

{summary}

Recommended file: [`{final['submission']}`]({final['submission']}). SHA-256: `{final['sha256']}`.
Confirmed previous public score: **0.76824**, rank snapshot **518**, explicitly attributed by the user to `submission_round3_bagged.csv`.
{('A new CSV has been created and locally reproduced; submit it to measure its public score.' if accepted else 'No new submission was created because the planned validation rules did not support replacing the current file. This is a completed experiment outcome, not a claim that every possible approach is exhausted.')}

## Goal, constraints and research change

The target is **0.8+**, requiring +0.03176 public AUC over the confirmed score. The user reports top-ten scores displayed as 1 and top-twenty scores above 0.8, with unknown data/method provenance. This is relevant competitive context, not independently verified attainability under the permitted data. The supplied README restricts this task to a subset of Home Credit data; only the supplied train/test rows were used. No online dataset, original history table, recovered labels or pretrained weights were imported. All modeling used the local venv. All ten notebooks existing before this modeling phase are preserved.

The incremental round-four sweep was stopped after seven screens at the user's priority change. Its partial evidence remains in `ROUND4_EXPERIMENT_LOG.md`; it did not produce a submission. The opportunity audit in new notebook 07 found a single-model training-sample AUC 0.8141 versus held-out 0.7652, illustrating a generalization gap. Lower AUC in a missing-score slice did not imply disproportionate global ranking-loss contribution. That motivated new model/representation families rather than another depth/seed sweep. The audit does not estimate the data ceiling.

## Six structural pilots

Four scratch TabM recipes evaluated raw/engineered inputs, piecewise-linear/periodic numerical embeddings and a regularized full TabM recipe. Two learned-feature CatBoost recipes tested fold-safe auxiliary external-score reconstructions and regularized interaction-risk encodings. All retained missingness and trained preprocessing only on their training rows. Neural loss optimizes the mean of individual member BCE losses; inference averages probabilities. Settings, timings, curves, errors, per-trial interpretations and exact software versions are retained.

After the first three CPU pilots, a local hardware probe outside the sandbox revealed a roughly three-times-faster MPS GPU. A prospective amendment moved remaining neural fits to it before any primary CV. Original CPU results and signatures remain unchanged and explicitly checked; new fits have a separately hashed implementation/backend identity. All inference stays on CPU for exact saved-weight replay. No hyperparameter or score gate changed; GPU retraining bit identity is not promised. See `improvements/high_upside/ACCELERATOR_AMENDMENT.md` and executed notebook 08b.

{table(['Pilot','Individual inner AUC','Best screened blend gain','Retained epochs/trees','Seconds','Status'],[[a['name'],f"{a['auc']:.7f}" if a['auc'] is not None else '',f"{a['delta']:+.7f}" if a['delta'] is not None else '',a['count'],f"{a['seconds']:.1f}",a['status']] for a in records])}

The inner split is repeatedly explored. It screens hypotheses; it does not establish hidden-test improvement. Promotion allows at most one neural and one learned-feature finalist, with >=0.00030 blend gain. A meaningful branch targets >=0.002 OOF gain; smaller robust gains can qualify a candidate but do not trigger a broad expansion. No new seed-bank sweep was run. The unified ledger contains {len(combined)} records, including {sum(a.get('record_type')=='main screening configuration' for a in combined)} main configurations and separately labeled auxiliary probes. Software checks and fold refits do not inflate this count.

## Frozen validation and result

Primary choice:
{block(choice)}

Fresh-fold confirmation:
{block(confirm)}

Matching three-seed check:
{block(average)}

Final result:
{block(final)}

Deployment counts, including auxiliary models inside the saved predictor bundles:
{block(complexity)}

Conditional uncertainty on frozen predictions:
{block(optional('model_conditional_uncertainty.json'))}

Any row-bootstrap intervals condition on fitted predictions and exclude fitting/search uncertainty; they are not independent or search-adjusted significance tests and do not change gates.

The complete pair/helper grid and winning recipe were frozen before confirmation. Primary and matching-three-seed eligibility require >=0.00030 gain; confirmation requires positive pooled gain and four positive groups out of five. Epoch/tree counts, weights and combination methods stay fixed. Confirmation seed {choice['confirmation_seed']} is a new partition of already explored development labels, not an untouched test. Historical audit and public scores did not tune the candidate. Final full-data OOF, if produced, is diagnostic and did not change selection.

A budget-aware selection amendment was recorded after neural CV and while tree CV was incomplete, before the full joint-grid choice and any confirmation. A second new family must add >=0.00030 primary AUC over the best one-family addition to earn the later training cost; otherwise the simpler recipe is selected. The complete unconstrained grid and both maxima remain recorded. This is an adaptive compute-allocation decision, not a significance claim. Fitting code/inputs were unchanged and completed caches were retained; only the selection controller changed while both workers were stopped. See `improvements/high_upside/COMPLEXITY_POLICY.md`.

## Documentation and reproduction

- [HIGH_UPSIDE_EXPERIMENT_LOG.md](HIGH_UPSIDE_EXPERIMENT_LOG.md): complete audit and modeling journal, why/how, failures and negative results.
- [HIGH_UPSIDE_PLAN.md](HIGH_UPSIDE_PLAN.md), and `improvements/high_upside/MODELING_PLAN.md`: strategy and exact pre-fit rules.
- [07_signal_opportunity_audit.ipynb](07_signal_opportunity_audit.ipynb): executed opportunity audit.
- [08_high_upside_modeling_plan.ipynb](08_high_upside_modeling_plan.ipynb): executed plan created before fitting.
- [08b_local_gpu_amendment.ipynb](08b_local_gpu_amendment.ipynb): prospective accelerator amendment before primary validation.
- [08c_compute_budget_policy.ipynb](08c_compute_budget_policy.ipynb): budget-aware selection rule recorded before recipe freeze.
- [09_high_upside_results_reproduction.ipynb](09_high_upside_results_reproduction.ipynb): executed results and reproduction evidence.
- `improvements/high_upside/artifacts/model_complete_experiment_ledger.json` and `.csv`: combined trial records.
- [REPRODUCTION_README.md](REPRODUCTION_README.md): local-venv inference and full phase commands.
- [output/competition_high_upside_reproduction.zip](output/competition_high_upside_reproduction.zip): new source/model/evidence archive, excluding the supplied input directory and venv.

All protected old file hashes and new notebook execution are checked. The recommended file has 61,500 finite scores in original sample/test ID order. For an accepted new candidate, saved-model replay is byte-identical on the recorded local runtime; the retained reference has its earlier exact replay evidence and unchanged checksum. Cross-platform numerical equivalence is subject to the pinned runtime/hardware. Prior reports and archives remain unchanged as historical evidence, apart from the current living report/readme; pre-modeling snapshots are under `improvements/high_upside/reference/before_modeling`.

## Stopping and remaining uncertainty

These six structural hypotheses and their declared gates were evaluated. Completing this pass does not establish a global optimum. Fully nested stacking, retrieval models, stronger auxiliary tasks and larger neural budgets remain possible directions, conditional on evidence and compute. A failure here does not prove those directions ineffective. A new architecture alone is no guarantee of a 0.03 AUC jump. The report distinguishes actual results from the 0.8 target and from other entrants' unverified methods.

The supplied competition documents give November 20, 2026, 01:00 UTC (07:00 Bangladesh) as the deadline and say the last submitted file determines the entry; this is the local-document record, not a live platform check. Code ZIP reproduction is needed for Honors/Outstanding consideration.
'''
    (t.ROOT/'IMPROVEMENT_REPORT.md').write_text(text)
    (t.ROOT/'REPRODUCTION_README.md').write_text(f'''# Reproducing the recommended submission

Recommended: `{final['submission']}`
SHA-256: `{final['sha256']}`

{summary}

Use Python 3.12 and the project `.venv`. Exact modeling packages are pinned in
`improvements/high_upside/requirements-high-upside.txt`. The wrapper selects one
OpenMP runtime on this Mac without disabling duplicate-runtime safety checks.
No extra data or pretrained weights are required. Retain the supplied `input`
directory; it and the venv are excluded from the new archive.
Training after the accelerator amendment requires the local MPS GPU to be exposed
to the process; saved-model inference runs on CPU. The first three CPU pilots are
reused as explicitly recorded historical evidence, with their original signatures.

Prediction-only replay:

```sh
.venv/bin/python improvements/high_upside/h_launch.py reproduce
```

For the retained historical reference, the original exact saved-model command
also remains available:

```sh
.venv/bin/python improvements/round3/bagging.py reproduce
```

Full higher-upside phase order (matching caches are reused):

```sh
.venv/bin/python improvements/high_upside/h_launch.py preflight
.venv/bin/python improvements/high_upside/h_launch.py screen
.venv/bin/python improvements/high_upside/h_launch.py primary_cv
.venv/bin/python improvements/high_upside/h_launch.py select
.venv/bin/python improvements/high_upside/h_launch.py confirmation
.venv/bin/python improvements/high_upside/h_launch.py averaging
.venv/bin/python improvements/high_upside/h_launch.py final
.venv/bin/python improvements/high_upside/h_launch.py reproduce
```

Do not run all historical notebooks merely to obtain the recommended CSV.
Notebooks 08/09 review the plan/results; training flags are false by default.
Selection source, weights and counts cannot be changed after confirmation.
Read `HIGH_UPSIDE_EXPERIMENT_LOG.md` for exact settings, adaptive decisions and
negative results. The earlier journals retain previous work.

`improvements/high_upside/artifacts/model_package_manifest.json` contains archive
member SHA-256s. The new ZIP was verified against them and its CRC. Earlier ZIPs,
kernel/cache directories and raw logs are excluded. All present protected earlier
files must match their recorded hashes; excluded older ZIPs may be absent after
unpacking. Supplied inputs are still needed for inference.
''')

def main():
    p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');args=p.parse_args();records,combined=ledger();journal(records)
    if args.final:report(records,combined)
    print('Documented',len(records),'structural pilots; unified records',len(combined),flush=True)
if __name__=='__main__':main()
