"""Build the complete experiment ledger from retained artifacts and live records."""
from pathlib import Path
import json, hashlib
from datetime import datetime,timezone
import numpy as np
import pandas as pd
import round2 as r

def first_pass_rows():
    out=[]
    files=['screen_results.json','supplement_results.json','refine_results.json','feature_selection_results.json','cat_refine_results.json']
    raw=[(f,row) for f in files for row in r.old.load_json(f)]
    by={row['name']:row for _,row in raw}
    cvs={row['name']:row for row in r.old.load_json('cv_results.json')}
    for filename,row in raw:
        name=row['name']; spec=row.get('spec',{})
        kind=spec.get('kind','rf' if name=='tutorial_rf' else 'logistic')
        mode=spec.get('features','tutorial_five' if kind=='rf' else 'extended')
        hypothesis='Test whether this model configuration improves discrimination on the development split.'
        reference='lgb_engineered'
        interpretation='Several settings change together; the result does not isolate a single causal mechanism.'
        if name=='tutorial_rf':
            hypothesis='Establish a fair, split-safe version of the supplied five-feature tutorial baseline.'
            reference=name; interpretation='A reference point, not a serious attempt to use all available information.'
        elif kind=='logistic':
            reference='logistic_0.1'; hypothesis='A regularized linear classifier may generalize well or diversify boosted models.'
            interpretation='Linear effects may be insufficient for nonlinear score and payment interactions; this is an explanation, not a proven mechanism.'
        elif kind=='spline':
            reference='spline_0.1'; hypothesis='Quantile transforms and smooth univariate splines may recover nonlinear signal with less tree variance.'
            interpretation='Smooth additive effects remain weaker than the tree models; cross-feature interactions are one plausible missing component.'
        elif kind=='hgb':
            reference='hgb_20'; hypothesis='Native-categorical histogram gradient boosting offers a separate implementation and leaf-complexity tradeoff.'
            interpretation='This family was competitive enough to validate, but did not match CatBoost or tuned LightGBM.'
        elif kind=='cat':
            reference='cat_depth5'; hypothesis='Native categorical learning and a different boosting implementation may outperform the LightGBM family.'
            if mode=='lean':
                reference='cat_lean' if name!='cat_lean' else 'cat_depth5'
                hypothesis='A compact set of strong financial/score features may reduce distracting split opportunities.'
                interpretation='The compact depth-5 representation won development CV; deeper trees did not help overall. The feature explanation is plausible, not causal proof.'
            elif mode=='raw':
                hypothesis='Test whether CatBoost can learn sufficient relationships from the original columns without derived ratios.'
                interpretation='Lower AUC supports retaining derived financial and score features for this model.'
            else:
                hypothesis+=' Compare depths 4–7 and leaf regularization to control capacity.'
                interpretation='Depth and regularization were changed jointly, so the depth effect is not perfectly isolated.'
        elif name=='lgb_raw':
            reference='tutorial_rf'; hypothesis='Using all original predictors and histogram boosting should improve on the five-feature RF.'
            interpretation='Algorithm and feature count change jointly; the next raw/engineered comparison is the controlled feature ablation.'
        elif name=='lgb_engineered':
            reference='lgb_raw'; hypothesis='Loan/income ratios, age/employment ratios and external-score summaries may simplify useful interactions.'
            interpretation='Same-settings five-fold CV confirms a gain from 0.749947 to 0.756102, supporting this feature family.'
        elif name in ['lgb_extended','lgb_grouped']:
            hypothesis='Additional categorical crosses, log features, age bands and optional group summaries may expose further structure.'
            interpretation='The broader representation screened worse; added split opportunities or sparse category combinations may introduce noise.'
        elif name.startswith('lgb_tune'):
            hypothesis='Tune leaf size, minimum child size, row/column sampling, regularization, histogram resolution and group summaries.'
            interpretation='This is a joint hyperparameter search; do not attribute its AUC change to one parameter. Trials 12 and 15 generalized best among the advanced candidates.'
        elif name.startswith('lgb_top'):
            reference='lgb_tune_15'; hypothesis='Remove weaker original/derived columns using development-only gain rankings.'
            interpretation='Pruning failed to improve the tuned reference; correlated weak features can still help an ensemble of trees.'
        elif name.startswith('lgb_weight'):
            hypothesis='Increasing positive-class weight may prioritize minority-class ranking.'
            interpretation='Class weighting did not beat the best unweighted candidates; it can also shift probability calibration. Imbalance alone is not evidence weighting will help AUC.'
        elif name.startswith('lgb_small'):
            hypothesis='Shallower trees with strong regularization may improve generalization.'
        elif name in ['lgb_lean','lgb_scores']:
            hypothesis='A compact feature subset may remove redundant interactions and reduce variance.'
            interpretation='These LightGBM variants did not beat its engineered feature set; feature selection is model dependent.'
        elif name=='lgb_engineered_groups':
            hypothesis='Fold-fitted category frequencies and group-relative financial/score values may normalize peer groups.'
        ref=by[reference]['auc']
        cv=cvs.get(name)
        out.append(dict(phase='pass1',name=name,status='complete',kind=kind,features=mode,
            hypothesis=hypothesis,rationale_origin='Retrospective reconstruction from retained source, not a contemporaneous preregistration',
            auc=row['auc'],reference=reference,reference_auc=ref,delta=row['auc']-ref,
            iterations=row.get('iterations'),seconds=row.get('seconds'),params=spec.get('params',{'C':float(name.split('_')[-1])} if kind=='logistic' else {}),
            spec=spec,cv_auc=cv['auc'] if cv else None,cv_fold_auc=cv['fold_auc'] if cv else None,
            cv_iterations=cv['iterations'] if cv else None,interpretation=interpretation,
            decision='Advanced to five-fold development CV' if cv else 'Not advanced individually; retained as a screening/ablation result',
            source='improvements/'+{'screen_results.json':'experiment.py','supplement_results.json':'supplement.py','refine_results.json':'refine.py',
            'feature_selection_results.json':'select_features.py','cat_refine_results.json':'refine_cat.py'}[filename],
            artifact='improvements/artifacts/'+filename))
    return out

def second_pass_rows():
    out=[]
    planned=r.read(r.ART/'candidate_plan.json') if (r.ART/'candidate_plan.json').exists() else r.candidates()
    if (r.ART/'adaptive_plan.json').exists(): planned+=r.read(r.ART/'adaptive_plan.json')
    if (r.ART/'budget_control_plan.json').exists(): planned.append(r.read(r.ART/'budget_control_plan.json'))
    if (r.ART/'proxy_followup_plan.json').exists(): planned+=r.read(r.ART/'proxy_followup_plan.json')
    planned=list({s['name']:s for s in planned}.values())
    reference=next(row for row in r.old.load_json('refine_results.json') if row['name']=='cat_lean')['auc']
    for spec in planned:
        file=r.ART/'screen'/(spec['name']+'.json')
        row=r.read(file) if file.exists() else dict(name=spec['name'],spec=spec,status='pending')
        complete=row['status']=='complete'
        explanation='Pending: no performance claim.'
        if complete:
            delta=row['auc']-reference
            explanation=('Improved on the first-pass compact CatBoost on this one split; it still needs CV confirmation.' if delta>0 else
                         'Did not improve on the first-pass compact CatBoost on this split; this does not establish universal inferiority.')
            if spec['kind']!='cat': explanation+=' Different algorithms may still help a blend through complementary errors.'
            if row.get('saturated'): explanation+=' The best iteration approached the training cap, so the iteration budget may limit this result.'
        elif row['status']=='failed': explanation='Execution failed; no model-quality conclusion is justified. See the preserved traceback.'
        if spec['name']=='r2_cat_rsm075':
            explanation+=' A parameter preflight resolved bootstrap_type=MVS despite bagging_temperature=1; this is not evidence for a Bayesian-bootstrap effect. The explicit Bayesian follow-up tests that separately.'
        cvfile=r.ART/'cv'/(spec['name']+'.json'); cv=r.read(cvfile) if cvfile.exists() else None
        out.append(dict(phase='pass2',name=spec['name'],status=row['status'],kind=spec['kind'],features=spec['features'],
            hypothesis=spec['hypothesis'],rationale_origin='Written in the candidate plan before this trial started',
            auc=row.get('auc'),reference='pass1_cat_lean_inner',reference_auc=reference,
            delta=row.get('auc_delta_vs_pass1_cat'),iterations=row.get('iterations'),seconds=row.get('seconds'),params=spec['params'],spec=spec,
            implementation_hash=row.get('implementation_hash'),cv_auc=cv.get('auc') if cv else None,
            cv_fold_auc=cv.get('fold_auc') if cv else None,cv_iterations=cv.get('iterations') if cv else None,
            interpretation=explanation,error=row.get('error'),decision='CV complete' if cv else 'Screening only / pending selection',
            source=spec.get('source','improvements/round2/round2.py'),artifact=str(file.relative_to(r.ROOT))))
    # Adaptive candidates are also retained if written after the initial plan.
    known={row['name'] for row in out}
    for file in sorted((r.ART/'screen').glob('*.json')):
        if file.stem in known: continue
        row=r.read(file); spec=row['spec']
        out.append(dict(phase='pass2',name=spec['name'],status=row['status'],kind=spec['kind'],features=spec['features'],
            hypothesis=spec['hypothesis'],rationale_origin='Adaptive follow-up; rationale recorded before execution',
            auc=row.get('auc'),reference='pass1_cat_lean_inner',reference_auc=reference,delta=row.get('auc_delta_vs_pass1_cat'),
            iterations=row.get('iterations'),seconds=row.get('seconds'),params=spec['params'],spec=spec,
            interpretation='Adaptive follow-up; compare its stored development results and CV before drawing a conclusion.',
            decision='Adaptive experiment',source='improvements/round2/round2.py',artifact=str(file.relative_to(r.ROOT))))
    return out

def fmt(value,digits=6): return '—' if value is None else f'{value:.{digits}f}'

def enrich(rows):
    by={a['name']:a for a in rows}
    metrics={}
    if (r.ART/'secondary_metric_audit.json').exists():metrics={a['name']:a for a in r.read(r.ART/'secondary_metric_audit.json')['records']}
    final_selection=r.read(r.ART/'selection.json') if (r.ART/'selection.json').exists() else None
    provisional=r.read(r.ART/'provisional_selection.json') if (r.ART/'provisional_selection.json').exists() else None
    parents={'r2_cat_budget_control':'r2_cat_baseline','r2_cat_finance_native':'r2_cat_finance',
        'r2_cat_finance_tuned':'r2_cat_finance','r2_cat_burden':'r2_cat_finance','r2_cat_term_proxies':'r2_cat_finance',
        'r2_cat_proxies_native':'r2_cat_term_proxies','r2_cat_proxies_rsm075':'r2_cat_term_proxies',
        'r2_cat_rates_only':'r2_cat_term_proxies','r2_cat_distances_only':'r2_cat_term_proxies',
        'r2_cat_bayesian_rsm075':'r2_cat_rsm075','r2_xgb_d3':'r2_xgb_d4','r2_xgb_d5':'r2_xgb_d4',
        'r2_xgb_lean':'r2_xgb_d4','r2_xgb_finance':'r2_xgb_d3','r2_lgb_finance':'lgb_tune_15'}
    for a in rows:
        if a['name']in metrics:
            for key in ['average_precision','log_loss','brier_score']:a[key]=metrics[a['name']][key]
            a['secondary_metric_provenance']='Retrospectively recomputed from saved predictions, not a new fitting run'
        parent=parents.get(a['name'],a['reference'])
        if a['phase']=='pass2' and a['kind']=='cat' and a['name'] not in parents and a['name']!='r2_cat_baseline': parent='r2_cat_budget_control'
        reference=by.get(parent)
        a['parent_reference']=parent
        a['parent_auc']=reference.get('auc') if reference else None
        a['parent_delta']=a['auc']-a['parent_auc'] if a.get('auc') is not None and a['parent_auc'] is not None else None
        spec=a.get('spec') or {};kind=a['kind'];new=a['phase']=='pass2'
        if kind=='cat':
            recipe=dict(iterations=spec.get('max_iterations',4500 if new else 3000),learning_rate=.045,loss_function='Logloss',eval_metric='AUC',
                thread_count=4,random_seed=r.SEED,allow_writing_files=False,patience=spec.get('patience',200 if new else 150),
                numeric_missing=spec.get('missing','sentinel (-999)'))
        elif kind=='lgb':
            recipe=dict(n_estimators=spec.get('max_iterations',4500 if new else 3500),learning_rate=.035,objective='binary',
                n_jobs=4,random_state=r.SEED,deterministic=True,force_col_wise=True,patience=spec.get('patience',200 if new else 150))
        elif kind=='xgb':
            recipe=dict(n_estimators=spec.get('max_iterations',4500),learning_rate=.035,tree_method='hist',device='cpu',
                objective='binary:logistic',eval_metric='auc',enable_categorical=True,n_jobs=4,random_state=r.SEED,patience=spec.get('patience',200))
        elif kind=='rf': recipe=dict(n_estimators=100,max_depth=10,random_state=0,n_jobs=4)
        elif kind=='hgb': recipe=dict(max_iter=1800,learning_rate=.05,scoring='roc_auc',validation_fraction=.15,n_iter_no_change=50,random_state=r.SEED)
        elif kind=='spline': recipe=dict(imputer='training median + missing indicators',quantiles=100,quantile_distribution='uniform',spline_knots=5,spline_degree=3,spline_knot_positions='uniform',include_bias=False,max_iter=700,solver='lbfgs')
        else: recipe=dict(imputer='training median + missing indicators',scaler='StandardScaler',categorical='OneHotEncoder(ignore unknown)',max_iter=1000,solver='lbfgs')
        recipe.update(a['params']);a['runner_settings']=recipe
        a['parameter_note']='Runner-controlled settings; remaining library defaults follow pinned dependencies. Resolved parameters are retained in adaptive screen/CV fold artifacts where available.'
        if a['name']=='r2_cat_rsm075': a['implementation_note']='Bagging-temperature preflight resolved MVS; treat this as column sampling, not an established Bayesian-bootstrap effect.'
        if a['phase']=='pass1' and a['name'] in r.old.load_json('selection.json')['names']:
            a['decision']='Retained in the first-pass public-scored ensemble (confirmed public AUC 0.7654)'
        if a['phase']=='pass2' and a['status']=='complete':
            if a['name'] in ['r2_cat_baseline','r2_cat_budget_control']:
                a['decision']='Implementation/stopping-budget control; used to interpret other trials, not claimed as a new recipe'
            elif final_selection and a['name'] in final_selection['names']:
                weight=final_selection['weights'][final_selection['names'].index(a['name'])]
                a['decision']=f'Retained in the final frozen ensemble at weight {weight:.6f}'
            elif final_selection and provisional and a['name'] in provisional['names']:
                a['decision']='Primary ensemble candidate not retained after the frozen second-seed decision'
            elif provisional and a['name'] in provisional['names']:
                a['decision']='Provisionally retained by primary CV; awaiting the frozen second-seed decision'
            elif a.get('cv_auc') is not None:
                a['decision']='Validated on common folds; ensemble selection pending' if not provisional else 'Validated on common folds; not retained in the current blend'
            else:
                a['decision']='Screened but not advanced by the documented promising/diverse-family shortlist'
    return rows

def build():
    rows=enrich(first_pass_rows()+second_pass_rows())
    r.dump(r.ART/'complete_experiment_ledger.json',rows)
    data=[]
    for row in rows:
        flat={k:v for k,v in row.items() if k not in ['params','spec','cv_fold_auc','cv_iterations','runner_settings']}
        for k in ['params','spec','cv_fold_auc','cv_iterations']: flat[k+'_json']=json.dumps(row.get(k),sort_keys=True)
        flat['runner_settings_json']=json.dumps(row['runner_settings'],sort_keys=True)
        data.append(flat)
    pd.DataFrame(data).to_csv(r.ART/'complete_experiment_ledger.csv',index=False)
    public=r.read(r.ART/'public_score.json'); selection=r.old.load_json('selection.json')
    now=datetime.now(timezone.utc).isoformat()
    second=[x for x in rows if x['phase']=='pass2']; done=[x for x in second if x['status']=='complete']; failed=[x for x in second if x['status']=='failed']
    lines=[f'''# Complete competition experiment log

Updated automatically from retained artifacts: {now}.

This is the living record of hypotheses, implementations, results, decisions and limitations.
The JSON/CSV ledger contains every trial's complete configuration; this document provides the reasons and interpretation.
First-pass rationales are reconstructed from retained source and clearly marked as retrospective. Second-pass hypotheses are recorded before their runs.

## Confirmed competition result

The user confirmed that `output/submission_improved.csv` achieved **public ROC-AUC 0.7654**, with displayed rank **1,094** (`hasanRocky`).
This is a screenshot snapshot, not a permanent rank. The submitted file's SHA-256 is `{public['sha256']}`.
The private/full-test score is unknown. No second-pass public score is assumed or invented.

## Data, rules and reproducibility

- Only supplied `input/train.csv` and `input/test.csv` supply model rows; the supplied Excel file is a data dictionary.
- No external training data, pretrained model weights, recovered test labels, manual predictions or downloaded reference notebooks.
- Software dependencies are installed in `Competition/.venv`; software downloads do not add dataset rows.
- Preserve all existing notebooks, the first-pass CSV, original models and first-pass reproduction ZIP. New work lives under `improvements/round2` and new notebooks.
- Fixed seeds and fold indices, fold-fitted encoders and saved models make each result reviewable and reproducible.

## Validation chronology and limitations

The original partition is 60% inner fit, 20% inner validation and 20% historical audit.
The 80% development portion has five fixed stratified folds. All second-pass screening and selection remain inside that development portion.
The first-pass baseline and candidate AUCs therefore have comparable folds and row identities.

The first-pass audit was evaluated once after its selection, scoring **0.755506** versus **0.666573** for the tutorial-style RF.
Its paired bootstrap gain interval was **0.079682–0.097858**. This is a historical check. It must not be called a fresh untouched test for second-pass models.
Public feedback is one observed score for a frozen CSV, not a per-experiment tuning signal.
New development OOF gains are selection-biased estimates, so promising candidates need fold consistency and a second split-seed comparison.
Any historical-audit comparison in this pass must be labeled descriptive and performed after new selection, not used to retune.

## First-pass findings: what worked and what did not

1. All original features plus boosting substantially improved on the five-feature tutorial RF.
2. Same-settings LightGBM raw/engineered CV improved **0.749947 → 0.756102**. This is the strongest controlled evidence for the financial/score feature family.
3. Compact depth-5 CatBoost scored **0.760790** in development CV, above the larger-feature version (**0.759728**) and deeper compact version (**0.760148**).
4. Tuned LightGBM added complementary errors: the final two-thirds CatBoost / one-third LightGBM blend scored **{selection['auc']:.6f}** development OOF AUC.
5. Broad categorical crosses, feature pruning and class weighting failed to beat the best screened configurations. These were not proof that such methods never help.
6. Histogram boosting (**0.753292 CV**) and spline logistic regression (**0.748304 CV**) were weaker. The additive spline representation may miss useful interactions, but that mechanism was not isolated.
7. The best three-model blend improved development AUC by only **0.000072** over the selected pair. It was rejected by a pre-audit complexity threshold of 0.00015. That threshold is a heuristic, not a statistical significance test.
8. Gain/feature-importance pruning removed columns that may still contribute jointly; the tested top-25/40/55/70 variants did not outperform the tuned reference.

## Second-pass design

Current screen status: **{len(done)} complete, {len(failed)} failed, {len(second)-len(done)-len(failed)} pending**.

The first trial must reproduce the old compact CatBoost predictions within 1e-10 before other comparisons are trusted.
New trials test XGBoost, CatBoost regularization/quantization/categorical handling, native missing bins,
targeted feature families and two alternative LightGBM variants. The search does not assume every added feature should help.

### New feature families: how and why

- **Risk**: clipped score logits, geometric/harmonic summaries, a predefined 1:2:3 score-weighted mean, conservative mean-minus-dispersion, age×score and term×score interactions. These can simplify nonlinear relationships for shallow trees. They add representations, not new information or externally estimated risk scores.
- **Finance**: income minus 12 annuity payments, per-person margins, per-adult amounts, goods/income, credit-cost amount and distances to multiples of 6/12 in the credit/annuity ratio. The factor 12 is an explicit hypothetical payment-frequency transform; the dictionary does not establish a customer's actual payment schedule.
- **Hypothetical rates**: for assumed 24/36/60 payment periods, solve `annuity/credit = r / (1 - (1+r)^(-n))` by 28 bisection steps. Impossible positive-rate cases become missing. These are redundant nonlinear transforms of the payment ratio, not claims to have recovered actual interest rates or loan terms.
- **Missingness/structure**: individual absence indicators, an eight-state external-score absence pattern, coarse organization labels before `:` and deterministic five-year age bands. These can expose collection segments, but extra categorical states can also overfit.
- **Combined**: concatenate all targeted additions to test complementarity versus added noise.

### Comparisons and stopping rules

Screen on the original inner split, then advance promising models and diverse algorithms to common five-fold development CV.
Evaluate AUC gain, fold consistency, runtime, iteration saturation and complementary errors, not just the best single score.
Use paired OOF comparisons for descriptive uncertainty. Recheck finalists with fixed iterations on another development fold seed.
The new-recipe gate is at least +0.0002 primary OOF AUC, positive pooled second-seed gain and positive gain in at least three of five second-seed folds.
Second-seed weights are frozen. A two-seed averaging diagnostic is also planned: it must improve over the better individual seed by more than 0.00015 for both baseline and candidate before doubling the final model bank.
Freeze candidate/weights before any historical-audit description or new test prediction. Preserve the old public-scored CSV as the fallback.

## Per-trial index

| Pass | Experiment | Status | Inner AUC | Delta to stated reference | Development CV AUC |
| --- | --- | --- | --- | --- | --- |''']
    for row in rows:
        lines.append(f"| {row['phase']} | {row['name']} | {row['status']} | {fmt(row.get('auc'))} | {fmt(row.get('delta'))} | {fmt(row.get('cv_auc'))} |")
    lines.append('''
## Detailed experiment notes

Each comparison below states its reference. Cross-algorithm deltas combine representation and learner effects.
An observed difference is evidence about this configuration on this split, not proof of the suggested mechanism.
All first-pass notes are retrospective reconstructions; every second-pass candidate has a contemporaneous hypothesis in its plan/event record.
''')
    for row in rows:
        spec=row.get('spec') or {}
        lines.append(f"### {row['phase']} / {row['name']}\n\n"
            f"**Hypothesis:** {row['hypothesis']}\n\n"
            f"**How:** `{row['kind']}` on `{row['features']}` features. Source: `{row['source']}`. "
            f"Rationale origin: {row['rationale_origin']}.\n\n"
            f"**Configuration:** `{json.dumps(spec if spec else row['params'],sort_keys=True)}`\n\n"
            f"**Runner settings:** `{json.dumps(row['runner_settings'],sort_keys=True)}`. {row['parameter_note']}\n\n"
            f"**Result:** status `{row['status']}`; inner AUC {fmt(row.get('auc'))}; reference `{row['reference']}` "
            f"({fmt(row.get('reference_auc'))}); delta {fmt(row.get('delta'))}; best trees {row.get('iterations')}; runtime seconds {fmt(row.get('seconds'),2)}.\n\n"
            f"**CV:** pooled AUC {fmt(row.get('cv_auc'))}; fold AUCs `{row.get('cv_fold_auc')}`; fold tree counts `{row.get('cv_iterations')}`.\n\n"
            f"**Parent comparison:** `{row['parent_reference']}` AUC {fmt(row.get('parent_auc'))}; delta {fmt(row.get('parent_delta'))}. This clarifies within-family/component comparisons alongside the common baseline delta.\n\n"
            f"**Secondary metrics:** AP {fmt(row.get('average_precision'))}; log loss {fmt(row.get('log_loss'))}; Brier {fmt(row.get('brier_score'))}. These are retrospective saved-prediction audits where available.\n\n"
            f"**Decision / interpretation:** {row['decision']}. {row['interpretation']}\n\n"
            f"**Evidence:** `{row['artifact']}`.\n")
        if row.get('error'): lines.append(f"**Failure:** `{row['error']}`. The traceback is retained under `improvements/round2/artifacts/errors`.\n")
    lines.append('''
## Engineering incidents and fixes

These were implementation/runtime incidents, not evidence that a machine-learning hypothesis failed.

- First-pass extended categorical bins retained missing values as floating NaN inside a string column; vocabulary sorting failed on mixed types. Explicit string missing tokens fixed it before evaluation continued.
- Initial package installation failed inside the network-restricted sandbox. Approved installation into the project venv downloaded software only.
- Notebook execution initially failed because Jupyter loopback ports were restricted. Approved local execution used the project venv and a project-local kernelspec.
- A first-pass staged-CV filter temporarily reused the function argument name as a loop variable, running the spline family instead of the requested family. Renaming the variable fixed it. Singleton blend selection also needed an empty-pair guard.
- Concurrent first-pass staged CV writers could overwrite a cached spline result. The spline CV was rerun; final artifacts and notebooks passed validation. Second-pass results use separate atomic JSON files per trial and a locked event journal.
- A row/batch invariance check exposed integer versus float dtype differences when an employment sentinel was absent from a tiny batch. The employment column now explicitly uses float64; full-dataset feature values were unchanged.
- Saved encoders use dictionaries rather than pickled `__main__` classes, making notebook model reloads independent of how the training script was launched.
- The first-pass audit histogram's density-axis label was corrected, then its new notebook was re-executed. Original supplied notebooks were never changed.

Second-pass execution failures, if any, are recorded per trial above and in their traceback files. Failed runs never acquire invented AUCs.
The first-pass saved CatBoost model resolves bootstrap MVS and maximum categorical-combination complexity 4. These defaults were inspected rather than assumed.
A 300-row, five-tree parameter preflight showed that bagging_temperature alone still resolved to MVS. Its AUC was never used; the explicit Bayesian follow-up corrects the mechanism being tested.

## Evidence and reproduction map

- `improvements/artifacts`: first-pass screening, CV, blending, audit, full-data OOF, checksums and feature importances.
- `improvements/round2/artifacts/candidate_plan.json`: new hypotheses/configurations before runs.
- `improvements/round2/artifacts/events.jsonl`: UTC start/finish/failure chronology.
- `improvements/round2/artifacts/screen`: one JSON result and aligned prediction array per screen.
- `improvements/round2/artifacts/cv`: one result and aligned prediction array per new CV model.
- `improvements/round2/artifacts/complete_experiment_ledger.json` and `.csv`: complete combined machine-readable ledger.
- `improvements/round2/reference`: preserved first-pass report and immutable-file hashes.
- `improvements/round2/round2.py`: exact feature formulas, encoder behavior and candidate/training code.

Refresh this document with `.venv/bin/python improvements/round2/document.py` from `Competition`.
''')
    lines.append('\n## Final selection and robustness evidence\n')
    diagnostic=r.ART/'first_pass_log_odds_diagnostic.json'
    if diagnostic.exists():
        lines.append('### First-pass probability versus log-odds averaging\n\nThe exact earlier exploratory pair/weights were recomputed from retained OOF arrays for documentation, not newly fitted. Probability averaging was slightly better for all three tested weights. This was not proof that log-odds blending never helps.\n\n```json\n'+json.dumps(r.read(diagnostic),indent=2)+'\n```\n')
    for name,title in [('complementarity_summary.json','Individual strength versus recorded pair complementarity'),('balanced_helper_probe.json','Balanced helper-weight probe')]:
        if (r.ART/name).exists():lines.append(f'### {title}\n\n```json\n{json.dumps(r.read(r.ART/name),indent=2)}\n```\n')
    for filename,title in [('primary_original_winner.json','Original primary winner before the prospective complexity check'),
        ('complexity_check_plan.json','Prospectively recorded frozen-pair simplification rule'),('complexity_check_results.json','Frozen-pair complexity comparison'),
        ('provisional_selection.json','Primary development selection'),('stability_results.json','Fixed-iteration second-seed check'),
        ('selection.json','Final frozen choice'),('final_results.json','Generated submission and diagnostic metrics'),('verification.json','Integrity verification')]:
        path=r.ART/filename
        if path.exists():
            lines.append(f'### {title}\n\nSource: `improvements/round2/artifacts/{filename}`.\n\n```json\n{json.dumps(r.read(path),indent=2)}\n```\n')
    lines.append('''
## Interpretation limits

- A method can improve one split and fail across folds; such a result is not erased or converted into a general success claim.
- Rate-only and distance-only ablations must be compared with the joint proxy block; a joint gain does not establish a recovered real interest rate.
- First-pass metadata includes explicit settings and pinned code; resolved internal defaults were not retained for every historical screen. Those missing details are not invented.
- New adaptive screen/CV fold artifacts retain resolved parameters and learning curves where available. A small API probe is not a competition performance experiment.
- The first-pass audit and the public score are historical checks. Second-pass development, repeated-seed and full-data OOF numbers are not fresh independent test estimates.
- A new CSV's public/private performance remains unknown until the actual competition evaluates it.
''')
    (r.ROOT/'EXPERIMENT_LOG.md').write_text('\n'.join(lines))
    print('Updated EXPERIMENT_LOG.md;',len(rows),'trials in the combined ledger.')

if __name__=='__main__': build()
