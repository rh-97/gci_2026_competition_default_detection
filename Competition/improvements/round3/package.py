"""Publish the local report and a complete, hash-verified code/model archive."""
import hashlib,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import nbformat
import round3 as t
import bagging
from document import table

def report():
    choice=t.read(t.ART/'selection.json');confirmation=t.read(t.ART/'confirmation_results.json')
    average=t.read(t.ART/'averaging_results.json');final=bagging.preferred_result()
    publicpath=t.ART/'round3_public_result.json'
    public=t.read(publicpath) if publicpath.exists() else None
    if public:
        assert public['submission']==final['submission'] and public['sha256']==final['sha256'],'Public result must identify the recommended CSV.'
        assert hashlib.sha256((t.ROOT/public['submission']).read_bytes()).hexdigest()==public['sha256']
    verified=t.read(t.ART/'verification.json')
    assert verified.get('final') and verified.get('new_notebooks_fully_executed'),'Complete final verification before packaging.'
    assert verified['recommended_submission_sha256']==final['sha256'],'Verification must cover the currently recommended CSV.'
    rows=t.screen_rows();complete=[a for a in rows if a['status']=='complete'];promote=t.read(t.ART/'promotion.json')
    by={a['name']:a for a in complete}
    cvs=[t.read(p) for p in sorted((t.ART/'cv').glob('*.json'))]
    trials=table(['Experiment','Individual inner AUC','Best inner blend gain','Retained iterations','Seconds'],[
        [a['name'],f"{a['auc']:.6f}",f"{a['best_blend']['auc']-a['reference_auc']:+.6f}",a['iterations'],f"{a['seconds']:.1f}"]
        for a in sorted(complete,key=lambda a:-a['best_blend']['auc'])])
    cvtable=table(['New model','Development OOF AUC','Fold SD','Median iterations'],[
        [a['name'],f"{a['auc']:.6f}",f"{np.std(a['fold_auc'],ddof=1):.6f}",int(np.median(a['iterations']))] for a in sorted(cvs,key=lambda a:-a['auc'])])
    evaluations=[['Primary development selection',f"{choice['baseline_auc']:.6f}",f"{choice['auc']:.6f}",f"{choice['gain']:+.6f}"]]
    if 'baseline_auc'in confirmation:evaluations.append(['New fold seed; fixed iterations',f"{confirmation['baseline_auc']:.6f}",f"{confirmation['candidate_auc']:.6f}",f"{confirmation['gain']:+.6f}"])
    if 'baseline_two_seed_auc'in average:evaluations.append(['Matching two-seed bank',f"{average['baseline_two_seed_auc']:.6f}",f"{average['candidate_two_seed_auc']:.6f}",f"{average['gain']:+.6f}"])
    bagprobe=t.read(t.ART/'bagging_probe.json') if (t.ART/'bagging_probe.json').exists() else {}
    if 'reference_three_seed'in bagprobe:
        evaluations.append(['Matching three-seed diagnostic',f"{bagprobe['reference_three_seed']['auc']:.6f}",f"{bagprobe['candidate_three_seed']['auc']:.6f}",f"{bagprobe['recipe_gain_at_three_seeds']:+.6f}"])
        if final.get('seeds_per_family')==3:
            evaluations.append(['Proposed bank vs current bank (development)',f"{bagprobe['reference_two_seed']['auc']:.6f}",f"{bagprobe['candidate_three_seed']['auc']:.6f}",f"{bagprobe['candidate_three_seed']['auc']-bagprobe['reference_two_seed']['auc']:+.6f}"])
    evaluation=table(['Evaluation','Current round-two recipe','Frozen third-pass recipe','Gain'],evaluations)
    uncertainty=t.read(t.ART/'conditional_uncertainty.json') if (t.ART/'conditional_uncertainty.json').exists() else {}
    uncertaintytext=table(['Prediction comparison','Observed gain','Conditional paired 95% interval'],[
        [name,f"{a['gain']:+.6f}",'['+f"{a['conditional_gain_ci95'][0]:+.6f}, {a['conditional_gain_ci95'][1]:+.6f}"+']'] for name,a in uncertainty.items()]) if uncertainty else 'Conditional uncertainty diagnostics were not produced.'
    methods=t.read(t.ART/'early_blend_diagnostic.json')
    methodtable=table(['Method; same current families and weights','Primary OOF AUC','Previously inspected secondary OOF AUC'],[
        [a['method'],f"{a['primary_auc']:.6f}",f"{a['previous_secondary_auc']:.6f}"] for a in methods])
    probe=t.read(t.ART/'stacking_probe.json') if (t.ART/'stacking_probe.json').exists() else None
    probetext=('Three cross-fitted logistic meta-model probes were also tested. Best screened blend gain: '
        +f"{probe['best_gain']:+.6f}"+'. Fully nested follow-up warranted under its recorded rule: '+str(probe['warrants_nested_followup'])+'. '
        +'These probes are not fully nested: the base OOF features can indirectly use other meta-validation targets. They cannot justify a submission. '
        +'Exact coefficients and diagnostics are retained in `stacking_probe.json`.' if probe else 'No learned stacking probe was run.')
    refrecipe=t.read(t.r.ART/'selection.json')
    reftext=', '.join(f"{w:.3%} {name}" for name,w in zip(refrecipe['names'],refrecipe['weights']))
    flattext=''
    if choice['method']=='probability':
        flat={}
        for name,w in zip(choice['names'],choice['weights']):
            parts=zip(refrecipe['names'],refrecipe['weights']) if name=='round2_reference' else [(name,1.)]
            for part,vv in parts:flat[part]=flat.get(part,0)+w*vv
        flattext='Expanded family weights: '+', '.join(f"{w:.3%} {name}" for name,w in flat.items() if w>0)+'.'
    complexity=t.read(t.ART/'winner_complementarity.json') if (t.ART/'winner_complementarity.json').exists() else None
    complexitytext=('The primary advantage over the best recorded recipe with fewer new families was '
        +f"{complexity['primary_marginal_gain']:+.6f}"+'. That alternative uses a different prediction transform, so this is not a clean one-factor ablation. '
        +'The margin is small and does not establish a separately significant benefit for every additional family. The whole frozen recipe, not each marginal component, is subject to the deployment gates.'
        if complexity and complexity['primary_marginal_gain']is not None else '')
    if complexity and complexity.get('later_descriptive_comparisons'):
        complexitytext+=' With that simpler primary recipe held fixed, descriptive winner-minus-simpler gains were '+', '.join(
            name+' '+f"{a['difference']:+.6f}" for name,a in complexity['later_descriptive_comparisons'].items())+'. These diagnostics did not change selection.'
    bagtext=('The prospective three-seed averaging gate '+('passed' if bagprobe.get('passed') else 'did not pass')+'. '
        +('Reference increment '+f"{bagprobe['reference_increment']:+.6f}"+', candidate increment '+f"{bagprobe['candidate_increment']:+.6f}"+'. ' if 'reference_increment'in bagprobe else bagprobe.get('reason','')+' ')
        +'The rule required >=0.00020 increment for both banks, >=0.00020 recipe gain at three seeds, and positive increments in at least four of five primary row groups for both. No seed subsets or weights were searched. '
        +('The recommended CSV uses three equally weighted seeds per family; the two-seed CSV is preserved.' if final.get('seeds_per_family')==3 else 'The original two-seed decision is retained.')
        +' Plan and evidence: `BAGGING_PLAN.md`, `bagging_probe.json` and `bagging_final_results.json`.')
    stored=t.read(t.ART/'stored_helper_probe.json') if (t.ART/'stored_helper_probe.json').exists() else None
    assert not (stored and stored['warrants_new_validation_branch']),'Validate the promising stored-helper branch before packaging a final recommendation.'
    storedtext=('A late read-only check tested '+str(stored['helpers'])+' previously fitted OOF helpers against the frozen third-pass winner, using six fixed blends each. '
        +'The best helper was `'+str(stored['best_helper'])+'`, with primary gain '+f"{stored['best_gain']:+.6f}"+'. '
        +'It did not reach the predeclared 0.00020 threshold for a new validation branch. Older histogram boosting, spline, CatBoost, LightGBM and XGBoost predictions were therefore examined rather than silently discarded. '
        +'Every blend and its alignment check is retained in `stored_helper_probe.json`; the prospective late plan is `STORED_HELPER_PLAN.md`. This adaptive check is not independent evidence and did not alter the frozen recipe.' if stored else '')
    outcome=('A new third-pass recipe passed all declared gates. Its public score is unknown until submitted.' if final['accepted'] else
        'No third-pass recipe passed every declared gate. Keep the existing round-two submission; this pass does not justify replacing it.')
    if public:
        outcome=f"The submitted round-three bagged recipe achieved public AUC {public['score']:.5f}, displayed rank {public['rank']:,}."
        publicsummary=table(['Submission','Reported public AUC','Rank snapshot','Gain over previous'],[
            ['First pass','0.76540','1,094','—'],['Round two','0.76756','568','+0.00216'],
            ['Round three, bagged',f"{public['score']:.5f}",f"{public['rank']:,}",f"{public['gain_vs_round2']:+.5f}"]])
        publicsummary+='\n\nThe user explicitly confirmed submitting `output/submission_round3_bagged.csv` and supplied the leaderboard screenshot. Its local SHA-256 matches the frozen prediction file. '
        publicsummary+=f"The public-score gain is **{public['gain_vs_round2']:+.5f}** over round two and **{public['gain_vs_first_pass']:+.5f}** over the first pass. "
        publicsummary+='Ranks are snapshots. Attribution of the round-two score to its CSV follows the earlier conversation; the round-three filename is explicitly confirmed. The private/full-test score remains unknown. '
        publicsummary+='This feedback was recorded after model selection, final fitting and submission generation; it did not tune parameters or weights. Evidence is in `improvements/round3/artifacts/round3_public_result.json`. '
        publicsummary+='The observed gain supports the entire submitted recipe; it does not isolate the marginal contribution of the third seed.'
    else:
        publicsummary='''The latest user-provided leaderboard screenshot shows **0.76756**, displayed rank **568** for `hasanRocky`,
versus the earlier **0.7654**, rank **1,094**: a gain of **0.00216**. Ranks are snapshots.
Attribution to `output/submission_round2.csv` follows the conversation; the screenshot does not show a filename.
The private/full-test score remains unknown. Public feedback did not select third-pass settings or weights.'''
    if final['accepted']:
        initial=t.read(t.ART/'final_results.json')
        total=final['new_saved_models']+final['baseline_saved_models']
        created=initial['new_saved_models']+final.get('additional_third_seed_models',0)
        banktext=f"The recommended bank contains **{total} model instances**. This pass fitted {created} new instances and reused 30 existing instances. Family weights are fixed; folds and seeds are averaged equally within each family."
    else:banktext='The existing 30-instance reference bank is retained; no replacement final bank is recommended.'
    finaldetail=('Final full-data OOF metrics (diagnostic after selection): `'+json.dumps(final['full_oof'])+'`. These are not independent test scores.' if final['accepted'] else
        'No new final models or replacement CSV were produced after the failed gate.')
    if final.get('seeds_per_family')==3:
        two=t.read(t.ART/'final_results.json')
        finaldetail+=' The preserved [two-seed CSV](output/submission_round3.csv) has full-data OOF AUC '+f"{two['full_oof']['auc']:.9f}"+', versus '+f"{final['full_oof']['auc']:.9f}"+' for three seeds (difference '+f"{final['full_oof']['auc']-two['full_oof']['auc']:+.9f}"+'). '
        finaldetail+='This essentially tied diagnostic does not confirm an extra full-data AUC benefit from the third seed. AP, log loss and Brier improve slightly with three seeds. The recommendation follows the predeclared development gate; this diagnostic did not retune the policy. Both new CSVs remain available.'
    text=f'''# Competition improvement report

## Current recommendation

**{outcome}**

{publicsummary}

Recommended CSV: [`{final['submission']}`]({final['submission']}).
SHA-256: `{final['sha256']}`.

{banktext}

Executed notebooks and frozen training-result JSON files retain their pre-submission score fields. Post-submission
feedback is recorded separately so those historical records remain unchanged.

All seven notebooks present before this pass, prior-pass source, supplied CSVs and prior submissions are unchanged.
The project `.venv` was used throughout. No external rows, pretrained weights, recovered labels or pseudo-labels were used.

## Why another pass was warranted

The prior stopping statement was too strong: finishing planned experiments did not exhaust every reasonable approach.
Most earlier parameter tuning preceded discovery of the better loan-proxy representation.
This pass retunes that representation, isolates further transformations, tests compact-representation alternative learners,
and compares prediction-combination methods. The plan and promotion/gating rules were recorded before fitting.
Quantization/component follow-ups respond to initial screens; the pair-grid correction and seed-averaging check
are separately recorded amendments. These are adaptive research decisions, with their timing and evidence retained.

Plan: [`improvements/round3/PLAN.md`](improvements/round3/PLAN.md).
Full third-pass journal: [`ROUND3_EXPERIMENT_LOG.md`](ROUND3_EXPERIMENT_LOG.md).
Earlier experiment journal: [`EXPERIMENT_LOG.md`](EXPERIMENT_LOG.md).
The complete earlier report is preserved at [`improvements/round3/reference/before_round3_IMPROVEMENT_REPORT.md`](improvements/round3/reference/before_round3_IMPROVEMENT_REPORT.md).

## What was tested and how decisions were made

This pass screened **{len(rows)} configurations**: {len(complete)} completed, {len(rows)-len(complete)} failed.
The prior passes screened 91 configurations; the running screening total is **{91+len(rows)}** including controls.
Prediction-combination grids and validation refits are recorded separately, rather than inflated into the configuration count.
The combined machine ledger is `improvements/round3/artifacts/complete_experiment_ledger.json` (and `.csv`);
the three auxiliary meta-learning probes are explicitly labeled separately from the main screening configurations.

The exact previous proxy control reproduced its inner predictions with maximum absolute difference **0.0**.
All screens used the original, repeatedly explored inner split. Promotion required an inner blend gain >=0.00010 over
the **complete** current mixture, with at most two CatBoost, one other tree and one neural finalist.
Promoted: `{[a['name'] for a in promote['chosen']]}`.

Parameter tests covered depth, step size, shrinkage, numeric quantization, positive-class weighting,
asymmetric tree growth, missing-value treatment and fold-fitted group aggregates.
Feature tests isolated signed term residuals/categories, extra assumed payment periods, categorical crosses,
and the larger original feature set. Extra rate transforms and term categories are representations of supplied values;
they do not recover actual interest rates or schedules.

The scratch-trained neural models used training-fold median imputation/missing indicators, quantile normalization,
one-hot categoricals and small ReLU networks. Alternative models were evaluated for complementary errors,
not only individual AUC. Every exact configuration, metric, learning curve, resolved setting and interpretation is retained.

### Every screen

{trials}

### Common-fold validation

{cvtable}

### What worked and what did not

The joint signed-residual/rounded-category block scored **{by['r3_cat_signed']['auc']:.6f}**,
versus the proxy control **{by['r3_cat_baseline']['auc']:.6f}**. Signed residuals alone scored
**{by['r3_cat_signed_only']['auc']:.6f}** and rounded categories alone **{by['r3_cat_term_categories']['auc']:.6f}**.
The joint result is not explained by categories alone. A plausible mechanism is that coarse categorical buckets
and within-bucket residuals expose interactions to finite trees; this is an interpretation, not a causal finding
or evidence of real payment schedules.

Global 512-border quantization scored **{by['r3_cat_borders512']['auc']:.6f}**. Applying 512 borders only to
loan features scored **{by['r3_cat_loan_b512']['auc']:.6f}**, and only to score features **{by['r3_cat_scores_b512']['auc']:.6f}**.
Neither reproduced the global gain. Raising all borders to 1024 scored **{by['r3_cat_borders1024']['auc']:.6f}**;
more resolution was not uniformly better. The joint term block with 512 borders screened slightly below
the default-border version individually, and their CV ordering also favored the default-border model.
Both can still contribute because their prediction errors differ. The retained recipe is chosen by common-fold
blend performance, not by an isolated interpretation of the screen.

The compact LightGBM finalist improved its individual development score over the old LightGBM helper,
but did not enter the winning primary recipe. Individual strength and contribution to an existing ensemble
are different comparisons. The two neural recipes were much weaker and failed to improve a screened blend.
Their learning curves stopped before the epoch cap, so this run does not attribute the weak result simply
to hitting the configured maximum. It also does not rule out better neural architectures or optimization.

Depth-four/depth-seven tree recipes also changed shrinkage, and the neural recipes changed both width and
regularization; those comparisons cannot isolate a single parameter's causal effect. Exact parent comparisons,
settings, retention decisions and negative results are recorded for each trial in the journal.

### Blend methods using existing predictions

{methodtable}

This checks the method on the same family bank and weights. Probability averaging beat these two alternative
methods in the initial diagnostic. Additional recorded blend probes with new finalists are in
`improvements/round3/artifacts/blend_candidates.json`.
Percentile scores are ranking transforms, not calibrated default probabilities. Their primary OOF empirical CDFs
use predictions only and are frozen for later checks and inference.

{probetext}

{storedtext}

## Frozen decision and evidence

Chosen representation of predictions: `{choice['method']}`.
Names: `{choice['names']}`. Weights: `{choice['weights']}`.
The atomic `round2_reference` is {reftext}.
{flattext}
{complexitytext}

{evaluation}

{uncertaintytext}

Primary per-fold gains: `{choice['fold_gains']}`.
Confirmation per-fold gains: `{confirmation.get('fold_gains','Not run: primary gate failed.')}`.

The primary selection gate required >=0.00020 AUC improvement.
The new-fold-seed check used fixed iteration counts, no validation early stopping, and frozen weights/transforms;
it required positive pooled gain and at least four positive folds out of five.
The matching two-seed comparison additionally required >=0.00020 gain over the current two-seed recipe.
Earlier failing gates prevent unnecessary final fitting.

A primary-grid review added missing direct new/new and old/new family pairs before the corrected winner's
confirmation. The interrupted first confirmation was not consulted; its evidence and exact original source/freeze
are retained under `improvements/round3/reference/selection_before_pair_extension`. The corrected primary winner was frozen before
using the fresh confirmation seed `{choice['confirmation_seed']}`. These seed values are random integers, not dates.

{bagtext}

{finaldetail}

Confirmation changes the partition of previously explored labels; it is a robustness check, not an untouched test.
The historical audit is not used as a fresh test. Full-data OOF does not retune selection.
Conditional paired-bootstrap diagnostics, if present, are in `conditional_uncertainty.json`; they condition on fitted
predictions and exclude search/fitting uncertainty. They are not search-adjusted significance tests.

## Error analysis, interpretation and stopping

Exploratory two-seed OOF slices covered external-score missing count, contract, income type, age and gender.
Large slices showed small mean calibration residuals. Sparse categories were unstable; no manual prediction
adjustments or specialist models were justified by those slices alone. Raw slice metrics are retained.

The journal distinguishes observed score changes from tentative mechanisms. More complex features and models
can change quantization, interactions, calibration and correlated errors even without adding information.
A screen result does not identify which mechanism caused it, or establish performance on hidden labels.

This pass stops after its declared model/feature/combination directions and frozen gates have been assessed.
It does **not** exhaust every possible improvement. Larger neural searches, fully nested learned stacking,
specialist models, additional carefully designed interactions and larger seed banks remain possible research directions.
Their benefit is unproven; further small gains on the same repeatedly used selection labels can be misleading.
The retained evidence explains the stopping decision rather than claiming a global optimum.

## Notebooks, integrity and reproduction

- [`05_round3_hypotheses_and_experiments.ipynb`](05_round3_hypotheses_and_experiments.ipynb): hypotheses, definitions, all screens, convergence, negative results and interpretation.
- [`06_round3_validation_and_reproduction.ipynb`](06_round3_validation_and_reproduction.ipynb): frozen validation decisions, final result and saved-model replay.
- [`output/competition_round3_reproduction.zip`](output/competition_round3_reproduction.zip): source, all notebooks, required model banks, documentation, manifests and evidence.

Both new notebooks executed successfully. Feature checks cover target/ID independence, row/batch invariance,
train/test schema, hypothetical-rate equations and unseen neural categories. Protected file hashes and selection/source
freezes are checked. The recommended CSV has 61,500 finite scores in the sample ID order.
Saved-model replay is byte-identical for an accepted new CSV; a fallback is checked against its preserved checksum.
Some initial raw screening hashes reflect a source-line-offset recording error after an import-path-only edit.
The original/current core ASTs are identical and the phantom hash was exactly reproduced. Raw records are retained;
cache validation recognizes only this proven alias. Evidence and source snapshots are in
`improvements/round3/reference/signature_alias_proof.json`, with the correction documented in the journal.

From `Competition`, use the project interpreter and supplied `input` directory:

```sh
.venv/bin/python improvements/round3/round3.py screen
.venv/bin/python improvements/round3/followup.py
.venv/bin/python improvements/round3/stacking_probe.py
.venv/bin/python improvements/round3/validate.py cv
.venv/bin/python improvements/round3/validate.py select
.venv/bin/python improvements/round3/validate.py confirmation
.venv/bin/python improvements/round3/validate.py averaging
.venv/bin/python improvements/round3/finalize.py train_final
.venv/bin/python improvements/round3/finalize.py reproduce
.venv/bin/python improvements/round3/bagging.py probe
.venv/bin/python improvements/round3/bagging.py train
.venv/bin/python improvements/round3/bagging.py reproduce
.venv/bin/python improvements/round3/stored_helpers.py
.venv/bin/python improvements/round3/complementarity.py
.venv/bin/python improvements/round3/diagnostics.py
.venv/bin/python improvements/round3/importance.py
.venv/bin/python improvements/round3/document.py
.venv/bin/python improvements/round3/execute_notebook.py 05_round3_hypotheses_and_experiments.ipynb
.venv/bin/python improvements/round3/execute_notebook.py 06_round3_validation_and_reproduction.ipynb
.venv/bin/python improvements/round3/verify.py --final
.venv/bin/python improvements/round3/document.py
.venv/bin/python improvements/round3/package.py
```

Full reproduction reuses matching cached evidence; delete only third-pass cache artifacts to deliberately refit.
The source also references the preserved earlier-pass artifacts included in the archive.
The archive excludes input CSVs, the venv, kernel/cache directories and earlier ZIPs. Retain the originally supplied data.
Exact installed software versions are in `improvements/round3/requirements-round3.txt`.

The supplied README/tutorial gives a deadline of **November 20, 2026, 01:00 UTC (07:00 Bangladesh)** and says the
**last submitted file** determines the final entry; this is a local-document statement, not a live platform check.
A code ZIP is required for Honors/Outstanding consideration. Upload only the intended CSV and record its actual
public score against its checksum before claiming a further leaderboard improvement.
'''
    (t.ROOT/'IMPROVEMENT_REPORT.md').write_text(text)
    replay=('improvements/round3/bagging.py' if final['accepted'] else 'improvements/round2/finalize.py')
    (t.ROOT/'REPRODUCTION_README.md').write_text(f'''# Reproducing the recommended submission

Recommended file: `{final['submission']}`

SHA-256: `{final['sha256']}`

{('Confirmed public AUC: '+f"{public['score']:.5f}"+'; rank snapshot: '+str(public['rank'])+'. See `improvements/round3/artifacts/round3_public_result.json` for the user-confirmed submission record.') if public else 'Public score has not yet been recorded.'}

Read `IMPROVEMENT_REPORT.md` for results and limitations, and
`ROUND3_EXPERIMENT_LOG.md` for every third-pass trial. Previous experiments are
retained in `EXPERIMENT_LOG.md`. Only notebooks 05 and 06 were created this pass;
all earlier notebooks are preserved for reference.
The executed notebook outputs and frozen training summaries predate public-score feedback;
the updated score is recorded separately in the report and public-result JSON.

Use the project Python 3.12 `.venv`. Exact installed dependencies are recorded
in `improvements/round3/requirements-round3.txt`. The archive excludes the venv,
supplied input CSVs and previous ZIPs. Place the originally supplied `input`
directory beside this file. No extra dataset or pretrained weights are required.

From this directory, prediction-only replay is:

```sh
.venv/bin/python {replay} reproduce
```

Notebook 06 is the executed review/inference entry point. Its training flag is
false by default. Do not run all historical notebooks merely to generate the
recommended CSV: the saved model bank already supports inference. Full training
phase commands and cache rules are in the improvement report.

`improvements/round3/artifacts/package_manifest.json` contains SHA-256 hashes
for the packaged files. Archive creation checked each member and ZIP CRC.
''')

def archive():
    files=[]
    files += list(t.ROOT.glob('*.ipynb'))
    files += [t.ROOT/n for n in ['IMPROVEMENT_REPORT.md','EXPERIMENT_LOG.md','ROUND3_EXPERIMENT_LOG.md']]
    files += [p for p in t.ROOT.iterdir() if p.is_file() and p.suffix in ['.csv','.xlsx','.json','.yaml','.yml','.txt','.md'] and p not in files]
    for p in (t.ROOT/'improvements').rglob('*'):
        if not p.is_file():continue
        if any(part in ['__pycache__','.ipynb_checkpoints','catboost_info','kernels','matplotlib'] for part in p.parts):continue
        if p.suffix in ['.tmp','.log','.zip'] or p.name in ['package_manifest.json']:continue
        files.append(p)
    files += list((t.ROOT/'output').glob('*.csv'))
    files=sorted(set(files));manifest={str(p.relative_to(t.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    manifest_path=t.ART/'package_manifest.json';t.dump(manifest_path,manifest);files.append(manifest_path)
    path=t.ROOT/'output/competition_round3_reproduction.zip'
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:z.write(p,p.relative_to(t.ROOT))
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        for name,want in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==want,name
    print('Verified archive:',path,'bytes:',path.stat().st_size,'files:',len(files),flush=True)

def images():
    import base64
    for name in ['05_round3_hypotheses_and_experiments.ipynb','06_round3_validation_and_reproduction.ipynb']:
        nb=nbformat.read(t.ROOT/name,as_version=4)
        for ci,cell in enumerate(nb.cells):
            for oi,output in enumerate(cell.get('outputs',[])):
                data=output.get('data',{}).get('image/png')
                if data:(t.ART/(Path(name).stem+f'_plot_{ci}_{oi}.png')).write_bytes(base64.b64decode(data))

if __name__=='__main__':report();images();archive()
