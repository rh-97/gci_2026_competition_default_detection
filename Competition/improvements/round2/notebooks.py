"""Generate two new notebooks without touching any existing notebook."""
from pathlib import Path
import nbformat as nbf
import round2 as r

def md(s): return nbf.v4.new_markdown_cell(s.strip())
def code(s): return nbf.v4.new_code_cell(s.strip())
def save(name,cells):
    path=r.ROOT/name
    if path.exists(): raise FileExistsError('Preserve existing notebooks; choose a new filename: '+str(path))
    for i,cell in enumerate(cells):
        if cell.cell_type=='code': compile(cell.source,f'{name}:cell{i}','exec')
    nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Competition local venv','language':'python','name':'competition-local'},'language_info':{'name':'python','version':'3.12.15'}})
    nbf.write(nb,path)

setup='''
from pathlib import Path
import sys,json,numpy as np,pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display,Markdown,Code
ROOT=Path.cwd() if (Path.cwd()/'input/train.csv').exists() else Path.cwd()/'Competition'
assert (ROOT/'input/train.csv').exists()
assert Path(sys.prefix).resolve()==(ROOT/'.venv').resolve(), 'Use the project local venv.'
sys.path.insert(0,str(ROOT/'improvements/round2'))
import round2 as r
ART=r.ART
plt.rcParams.update({'figure.dpi':110,'axes.spines.top':False,'axes.spines.right':False})
print('Python:',sys.executable)
print('Known first-pass public score:',r.read(ART/'public_score.json')['public_roc_auc'])
'''

def build():
    save('03_round2_experiment_journal.ipynb',[
md('''# Second-pass experiment journal: hypotheses, methods and failures

The user confirmed **public ROC-AUC 0.7654** for `submission_improved.csv`, with displayed rank 1,094 in the supplied screenshot. The public entry is tied to its exact CSV checksum. This notebook documents the next optimization pass, using only the supplied rows and the local venv.

The first-pass audit is now historical. It is not a new untouched test for later choices. All new screening, feature choices and ensemble weights use the original development rows. The complete per-trial record is in `EXPERIMENT_LOG.md`, its JSON/CSV ledger and the source/event files under `improvements/round2`.

First-pass rationales were reconstructed from retained code and are labeled retrospective. Second-pass hypotheses were recorded before their runs; adaptive follow-ups state which earlier result triggered them. Possible explanations are distinguished from proven effects.'''),
code(setup),
code('''
display(pd.Series(r.read(ART/'environment.json')))
display(pd.Series(r.read(ART/'validation_plan.json')))
public=r.read(ART/'public_score.json');display(pd.Series(public))
'''),
md('''## Baseline equivalence and input integrity

The second-pass trainer must reproduce the first-pass compact CatBoost predictions before new results can be compared. Splits, target order, preprocessing and model settings must agree. Feature construction must ignore labels/IDs and produce the same row features alone or in a batch. Hypothetical rate features are checked against their defining equation. The original files and public-scored CSV are preserved.'''),
code('''
baseline=r.read(ART/'screen/r2_cat_baseline.json')
display(pd.Series({k:v for k,v in baseline.items() if k not in ['spec','implementation_hash']}))
assert baseline['maximum_prediction_difference']==0
checks=r.read(ART/'verification.json')
display(pd.Series({k:v for k,v in checks.items() if k!='final'}))
print('Final bundle verification is recorded separately after both new notebooks execute.')
'''),
md('''## Screening results: keep negative evidence

The screen uses the original 60% fit / 20% validation split. Differences are selection estimates, not final public scores. A lower individual AUC does not rule out ensemble value. The reference for displayed deltas is the first-pass compact CatBoost on these exact rows; comparisons across algorithms change more than one mechanism.'''),
code('''
ledger=r.read(ART/'complete_experiment_ledger.json')
current=[a for a in ledger if a['phase']=='pass2']
table=pd.DataFrame([{k:a.get(k) for k in ['name','status','kind','features','auc','delta','iterations','seconds','cv_auc']} for a in current])
display(table.sort_values('auc',ascending=False).reset_index(drop=True))
complete=table[table.status.eq('complete')].sort_values('delta')
fig,ax=plt.subplots(figsize=(10,max(5,.25*len(complete))),layout='constrained')
ax.barh(complete.name,complete.delta,color=np.where(complete.delta>0,'#35678e','#c77951'))
ax.axvline(0,color='black',linewidth=.8)
ax.set(xlabel='Inner validation AUC difference versus first-pass compact CatBoost',title='Every completed second-pass screen')
plt.show()
'''),
md('''## Finance ablation: what caused the apparent gain?

The finance block adds payment-burden margins and per-adult amounts, along with nonlinear transforms of credit/annuity. An ablation separates those blocks. A budget control holds features and model parameters fixed while changing the early-stopping patience/cap. Native missing values are tested separately and combined with finance.

The rate features solve a loan-annuity equation for assumed 24/36/60 payment periods. They are **representations of existing input columns**, not recovered contractual rates. The factor 12 in an income margin is an explicit hypothetical frequency transform; the local dictionary does not establish the actual schedule. Extra risk summaries and missingness categories are tested separately rather than assumed useful.'''),
code('''
ids=['r2_cat_baseline','r2_cat_budget_control','r2_cat_finance','r2_cat_burden','r2_cat_term_proxies','r2_cat_native_missing','r2_cat_finance_native','r2_cat_finance_tuned']
display(table[table.name.isin(ids)].set_index('name').reindex([n for n in ids if n in set(table.name)]))
import inspect
display(Code(inspect.getsource(r.features),language='python'))
'''),
md('''### Descriptive loan-pattern evidence

These plots use development labels only. Error bars are Wilson binomial intervals for the displayed bins, without adjustment for feature selection or confounding. Associations do not establish that a loan schedule or interest rate causes default. Train/test distribution checks concern features only.'''),
code('''
from IPython.display import Image
display(Image(filename=str(ART/'loan_structure_development.png')))
display(pd.read_csv(ART/'loan_structure_development_bins.csv'))
display(pd.Series(r.read(ART/'loan_structure_distribution_check.json')))
'''),
md('''## Resolved defaults and implementation details

The saved first-pass model resolves CatBoost bootstrap MVS, maximum categorical-combination complexity 4, 254 numeric borders, one-hot threshold 2 and Plain boosting. A small parameter preflight showed that `bagging_temperature` alone did not switch that configuration to Bayesian bootstrap. The explicit Bayesian follow-up tests the intended mechanism.

Native missing values and a -999 sentinel differ particularly for negative date-offset features: -999 can be a legitimate duration. Numeric quantization can also differ. A score change does not by itself prove which mechanism mattered. Additional categorical crosses and tighter combination limits may reduce or increase variance depending on the representation.'''),
code('''
resolved=r.read(ART/'pass1_catboost_resolved_parameters.json')
keys=['bootstrap_type','max_ctr_complexity','border_count','one_hot_max_size','boosting_type','nan_mode','rsm','learning_rate','l2_leaf_reg']
display(pd.Series({k:resolved.get(k) for k in keys}))
display(pd.Series(r.read(ART/'parameter_preflight.json')))
display(Code(inspect.getsource(r.Encoder),language='python'))
'''),
md('''## Every trial's hypothesis and interpretation

Full parameter dictionaries, source references, raw evidence paths, fold results and why a trial was retained or rejected are in the ledger. Explanations are conditional: multiple settings often change together, and one validation split can favor a noisy variant. The next notebook checks common folds and a second seed before recommending a new submission.'''),
code(r'''
for a in current:
    display(Markdown(f"### {a['name']}\n**Hypothesis:** {a['hypothesis']}\n\n**Result:** {a['status']}; AUC {a.get('auc')}; delta {a.get('delta')}; CV {a.get('cv_auc')}.\n\n**Interpretation:** {a['interpretation']}\n\n**Evidence:** `{a['artifact']}`"))
'''),
md('''## Reproduce the screen

Run from `Competition`, with the supplied input folder present:

```sh
.venv/bin/python improvements/round2/round2.py screen
.venv/bin/python improvements/round2/adaptive.py
.venv/bin/python improvements/round2/budget_control.py
.venv/bin/python improvements/round2/proxy_followup.py
.venv/bin/python improvements/round2/secondary_metrics.py
.venv/bin/python improvements/round2/proxy_eda.py
.venv/bin/python improvements/round2/document.py
```

The event journal preserves start/finish times and any failures. Completed trial records contain seeds, stopping counts, runtime, explicit parameters and implementation hashes. Adaptive trials and CV also retain learning curves and resolved parameters where available. The original notebooks and the 0.7654 submission remain unchanged.''')])

    save('04_round2_validation_and_submission.ipynb',[
md('''# Second-pass validation, model selection and submission

This notebook compares new models with the frozen public-scored first-pass model. The known public score is **0.7654**; a new candidate's public score is unknown until uploaded. It uses common development folds for selection, followed by a fixed-iteration second-seed check with frozen weights. Neither is a new independent untouched test.

The old historical audit is not reused to tune models. Final full-data OOF predictions are diagnostic because their development labels influenced selection. Every submission probability comes from saved trained models.'''),
code(setup),
md('''## Optional full validation/training rerun

Leave this switch false to inspect the completed experiment and reproduce the CSV from models. True reruns validation, selection and final fitting using the project interpreter. The screening stages in notebook 03 must have completed first. This can take substantial CPU time.'''),
code('''
RUN_VALIDATION_AND_TRAINING=False
if RUN_VALIDATION_AND_TRAINING:
    import subprocess
    for command in [['validate.py','cv'],['validate.py','select'],['validate.py','stability'],['check_complexity.py'],['finalize.py','train_final']]:
        subprocess.run([sys.executable,str(r.HERE/command[0]),*command[1:]],cwd=ROOT,check=True)
else:
    print('Using completed validation artifacts; saved-model reproduction runs below.')
'''),
md('''## Common-fold comparison

New finalists use the original five development folds, categorical vocabularies fitted only in each training fold, and validation AUC early stopping. Old CatBoost/LightGBM OOF predictions provide the exact prior benchmark. Model capacity, feature family and stopping parameters are retained in each result; individual screening winners can fail across folds.'''),
code('''
import validate
pool=validate.pool_records()
display(pd.DataFrame([{'name':a['name'],'origin':a['origin'],'development_oof_auc':a['auc'],'median_trees':int(np.median(a['iterations']))} for a in pool]).sort_values('development_oof_auc',ascending=False))
selection=r.read(ART/'selection.json');provisional=r.read(ART/'provisional_selection.json')
display(pd.DataFrame({'model':provisional['names'],'weight':provisional['weights']}))
print('Primary development AUC:',provisional['auc'],'gain:',provisional['development_delta'])
print('Conditional paired bootstrap interval:',provisional['conditional_gain_ci95'])
print('The interval conditions on fitted OOF predictions; it excludes selection/training uncertainty.')
'''),
md('''## Fixed-iteration second-seed check

Freeze weights and median tree counts from the first CV run. Refit the required model families on five different development folds without passing validation targets into training or early stopping. Compare the frozen candidate and baseline within each new fold. Require a positive pooled gain and gains in at least three folds, in addition to the primary minimum gain of 0.0002.

This is a robustness check, not an unbiased new holdout. The same development rows contributed to prior selection. A separately planned two-seed averaging diagnostic must improve over the better individual seed by more than 0.00015 for both baseline and candidate before doubling the final model bank.

A narrow complexity check was recorded before new-candidate secondary results: if the selected triple added less than 0.00015 primary AUC over its frozen best pair, drop the third model only if its incremental secondary AUC is nonpositive and the pair passes the existing gain gates. This chooses between two frozen recipes, without a secondary weight search. Original winner snapshots are retained.'''),
code('''
stability=r.read(ART/'stability_results.json')
display(pd.Series(stability))
g1=provisional['fold_gain'];g2=stability['fold_gain']
fig,ax=plt.subplots(figsize=(8,3.5),layout='constrained')
loc=np.arange(5);ax.bar(loc-.18,g1,.36,label='Primary seed (selection)');ax.bar(loc+.18,g2,.36,label='Second seed (fixed iterations)')
ax.axhline(0,color='black',linewidth=.8);ax.set(xticks=loc,xticklabels=np.arange(1,6),xlabel='Fold within each seed',ylabel='AUC gain over frozen first-pass blend')
ax.legend();plt.show()
print('Final decision:',selection['status'])
if (ART/'complexity_check_results.json').exists(): display(pd.Series(r.read(ART/'complexity_check_results.json')))
'''),
md('''## Learning-curve evidence

The first fold of one new CV model is shown without selecting a particularly favorable fold. All available fold curves are retained. These curves explain stopping behavior; their validation labels contributed to model selection.'''),
code('''
files=sorted((ART/'cv').glob('*/fold0_learning_curve.json'))
if files:
    file=files[0];curve=r.read(file)
    series=[]
    for dataset,metrics in curve.items():
        for metric,values in metrics.items():
            if metric.lower()=='auc': series.append((dataset,metric,values))
    fig,ax=plt.subplots(figsize=(8,3.5),layout='constrained')
    for dataset,metric,values in series: ax.plot(np.arange(1,len(values)+1),values,label=dataset+' '+metric)
    ax.set(xlabel='Boosting iteration',ylabel='Validation AUC',title=file.parent.name+' / fold 1')
    ax.legend();plt.show()
'''),
md('''## Final saved-model bank and exact reproduction

All final weights and iteration counts are frozen before fitting on all labeled data. The first-pass final fold models can be reused without changes. New model families and any justified second fold seed are trained separately under `improvements/round2/models`.

Each test prediction averages the saved fold probabilities in a deterministic order, then applies the frozen model weights. The following cell reloads the actual models; it does not copy a cached prediction column.'''),
code('''
final=r.read(ART/'final_results.json')
display(pd.Series(final));display(pd.DataFrame(final['models']))
from finalize import reproduce
path=reproduce()
display(pd.read_csv(path).head())
print('Expected SHA-256:',final['sha256'])
'''),
md('''### Which features did the final models use?

These are mean fold importances, with the complete tables retained as CSVs. CatBoost uses prediction-value-change importance; LightGBM and XGBoost use gain. Scales differ between algorithms and should not be compared directly. Correlated representations can share importance; the plots describe the fitted recipe, not causal financial effects.'''),
code('''
for item in final['models']:
    file=ART/(item['name']+'_final_importance.csv')
    importance=pd.read_csv(file,index_col=0)
    importance.head(20).sort_values('mean_importance').mean_importance.plot.barh(figsize=(9,6),title=item['name']+' — mean saved-model importance')
    plt.tight_layout();plt.show()
    display(importance.head(20))
'''),
md('''## Submission choice and remaining uncertainty

`output/submission_improved.csv` is the preserved file with the confirmed public score 0.7654.
`output/submission_round2.csv` is the new candidate, or an exact fallback copy if no improvement passed validation.
Read the recommendation in `final_results.json` and `IMPROVEMENT_REPORT.md` before uploading. The new public score is not known locally, and the competition's local README says the last submitted file determines the final entry.

The complete per-trial explanations, configurations, rejected ideas, runtime incidents and raw evidence are in `EXPERIMENT_LOG.md` and its machine-readable ledger. All prior notebooks remain unchanged.''')])
    print('Created new notebooks 03 and 04.')

if __name__=='__main__':build()
