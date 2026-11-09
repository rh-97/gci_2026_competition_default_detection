"""Write the evidence report and self-contained code/model submission ZIP."""
from pathlib import Path
import hashlib, json, os, zipfile
import numpy as np
import pandas as pd
import experiment as e
os.environ.setdefault('MPLCONFIGDIR',str(e.ART/'matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

rows=[]
for f in ['screen_results.json','supplement_results.json','refine_results.json','feature_selection_results.json','cat_refine_results.json']:
    rows+=e.load_json(f)
cv=e.load_json('cv_results.json'); selection=e.load_json('selection.json')
audit=e.load_json('audit_results.json'); final=e.load_json('final_results.json')
da=e.load_json('data_audit.json')
by_name={r['name']:r for r in cv}
best_triple=e.load_json('triple_blend_candidates.json')[0]

def table(records,cols):
    header='| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'
    return header+'\n'.join('| '+' | '.join(str(row[c]) for c in cols)+' |' for row in records)

baseline=audit['baseline']['roc_auc']; improved=audit['improved']['roc_auc']
cvtable=table([{'Model':r['name'],'OOF AUC':f"{r['auc']:.6f}",'Fold SD':f"{np.std(r['fold_auc'],ddof=1):.6f}",
               'Median trees':int(np.median(r['iterations']))} for r in sorted(cv,key=lambda r:-r['auc'])],
              ['Model','OOF AUC','Fold SD','Median trees'])
top=sorted(rows,key=lambda r:-r['auc'])
screentable=table([{'Model':r['name'],'Inner AUC':f"{r['auc']:.6f}"} for r in top[:12]],['Model','Inner AUC'])
mix=', '.join(f'{w:.0%} {n}' for n,w in zip(selection['names'],selection['weights']))
fullauc=final['full_oof']['roc_auc']
txt=f'''# Competition improvement report

## Result

The frozen improved model scores **{improved:.6f} ROC-AUC** on the untouched 20% audit,
versus **{baseline:.6f}** for the tutorial-style five-feature random forest:
an absolute gain of **{improved-baseline:.6f}**. Both use the same audit rows and development training rows.
The improved AUC's conditional bootstrap 95% interval is {audit['auc_ci95'][0]:.6f}–{audit['auc_ci95'][1]:.6f};
the paired gain interval is {audit['auc_gain_ci95'][0]:.6f}–{audit['auc_gain_ci95'][1]:.6f}.
The hidden competition test score is unknown; the CSV has not been uploaded to Omnicampus.

Final model: **{mix}**, with five stratified training folds per selected model.
Development pooled OOF AUC: **{selection['auc']:.6f}**.
Full-data diagnostic OOF AUC: **{fullauc:.6f}**. Development labels influenced model selection,
so the untouched audit is the independent performance estimate.

## Competition and data

The supplied README defines binary loan payment difficulty prediction, scored by ROC-AUC.
There are 171,202 labeled rows, 61,500 test rows, 32 customer predictors, and an 8.07% positive rate.
The local instructions give a November 20, 2026 deadline at 01:00 UTC (07:00 Bangladesh time)
and say the **last submitted file** determines the final competition entry. They also require reproducible
code for Honors/Outstanding Student. These statements come from the supplied README, without live platform verification.

All dataset rows are from the supplied train/test CSVs. No external dataset, manual labels,
test-target reconstruction, hand-built target-encoded input features, or online reference code was used.
The local tutorial is credited for the five-feature baseline; new modeling code was written for this project.
Software packages were installed into the existing project `.venv`; no online data was fetched.
SHA-256 checks confirm all three original notebooks and all three input CSVs are unchanged.

The data audit found no duplicated training feature rows. Important missing columns include
`EXT_SOURCE_1` (69.5%), `OWN_CAR_AGE` (66.0%), and `EXT_SOURCE_3` (31.9%).
The employment value 365243 is a sentinel, treated as missing with an indicator.
IDs are sequential and non-overlapping between train and test, and are excluded from models.
An adversarial classifier distinguishing train from test, excluding ID, scores **{da['adversarial_auc']:.6f} AUC**.
This suggests modest feature shift; it does not rule out hidden target or subgroup shift.

## Validation and search

1. Reserve a seeded, stratified 20% audit before tuning (34,241 rows).
2. Screen candidates on a 60% fit / 20% inner-validation split of all labeled rows.
3. Compare finalists using five-fold stratified CV restricted to the 80% development portion.
4. Choose single models or coarse pairwise probability blends using development OOF predictions only.
   Blending must improve OOF AUC by at least 0.00015 to justify additional complexity.
   A small set of family-diverse triples must add a further 0.00015 to justify a third model.
5. Freeze model choice, blend weights and median tree counts; fit on development and evaluate audit once.
6. Train five final folds on all labeled rows at fixed development-selected tree counts, save each model
   and encoder, and average their test probabilities using the frozen weights.

Categorical vocabularies, imputers, scalers, quantile transforms, splines, category frequencies,
and optional group medians are fitted inside training splits. The test set never fits these transformations.
Class imbalance is handled through the scoring metric and stratification, with class weighting tested
as an explicit variant. No row resampling or thresholding is used in the submission.

**{len(rows)} screened configurations** cover the tutorial RF, raw/engineered/extended/compact feature sets,
24 seeded Optuna LightGBM trials, shallow trees, two class weights, native-categorical CatBoost depths,
three histogram gradient boosting variants, linear logistic regression, nonlinear spline logistic regression,
group-relative features, and feature pruning. {len(cv)} finalists/ablations undergo five-fold development validation.

Feature engineering includes income-to-credit and annuity ratios, credit term, credit-versus-goods-price
differences, per-family amounts, employment/age and other lifetime ratios, external-score summaries,
pairwise products and differences, missingness indicators, and fold-fitted category/group summaries.

### Five-fold development results

{cvtable}

### Best inner-screen scores

{screentable}

Inner-screen scores are used for tuning, not as independent claims of generalization. Detailed
trials, fold scores, selection configuration and prediction arrays are in `improvements/artifacts`.
The unengineered/engineered ablation uses the same base LightGBM settings so its fold comparison
isolates the feature change more fairly than comparing separately tuned models.

## Diagnostics and stopping decision

The same-settings feature ablation improves five-fold OOF AUC from
{by_name['lgb_raw']['auc']:.6f} to {by_name['lgb_engineered']['auc']:.6f}.
Compact depth-5 CatBoost scores {by_name['cat_lean']['auc']:.6f}, above the larger-feature
depth-4 version ({by_name['cat_depth4']['auc']:.6f}) and the deeper compact version
({by_name['cat_lean_depth6']['auc']:.6f}). Its strongest final-fold importance features are
external-score mean, credit-to-annuity term, external-score minimum/maximum and customer age.
The best three-model blend scores {best_triple['auc']:.6f}, only
{best_triple['auc']-selection['auc']:.6f} above the selected two-model blend, below the additional-model threshold.

The new notebooks contain missingness and distribution checks, ROC/precision-recall curves,
calibration plots, subgroup audit metrics and mean-fold feature importances. Average precision,
log loss and Brier score are recorded alongside AUC. Subgroup results are descriptive and may be noisy.

The search tested substantially different models, representations and regularization choices,
then checked whether simple blends improved five-fold OOF performance. Class weights,
categorical interactions, compact features and feature pruning were evaluated rather than assumed helpful.
After these comparisons, further small tuning gains would be difficult to distinguish from development
overfitting. The independent audit was evaluated only after selection; no post-audit tuning was performed.
This is a defensible stopping point, not proof of a global optimum or a guaranteed leaderboard result.

## Deliverables and verification

- `output/submission_improved.csv`: {final['rows']:,} rows, exact sample ID order, finite model probabilities in [0,1].
- `01_competition_data_audit.ipynb`: executed competition/data audit.
- `02_improved_models_and_submission.ipynb`: executed experiment report and exact model-based reproduction.
- `improvements/experiment.py` and companion scripts: complete reproducible training/search workflow.
- `improvements/models`: persisted fold models and training-fitted encoders.
- `improvements/requirements-modeling.txt`: portable pinned modeling dependencies.
- `output/competition_improved_reproduction.zip`: new notebooks, source, models, evidence and submission.

Submission SHA-256: `{final['sha256']}`.
The modeling notebook reloads all saved models and reproduces the submission byte-for-byte.
Both new notebooks execute successfully in the project venv. Integrity checks cover unchanged
originals, disjoint splits, feature independence from labels and IDs, row/batch invariance,
unseen categories, CSV structure and exact reproduction.

## Reproduction

Place the supplied `input` folder and column dictionary under `Competition`; neither training data nor
the venv is duplicated into the ZIP. Use the existing local venv, or recreate a Python 3.12 environment
and install `improvements/requirements-modeling.txt`. The original conda environment files are also retained.
Then run from `Competition`:

```sh
.venv/bin/python improvements/experiment.py screen --trials 24
.venv/bin/python improvements/supplement.py
.venv/bin/python improvements/refine.py
.venv/bin/python improvements/select_features.py
.venv/bin/python improvements/refine_cat.py
.venv/bin/python improvements/experiment.py cv
.venv/bin/python improvements/experiment.py audit
.venv/bin/python improvements/experiment.py final
```

For fast prediction-only reproduction, execute the second new notebook. To use the supplied kernelspec,
`improvements/execute_notebook.py` runs it in the project venv without changing global Jupyter settings.
The complete raw `pip freeze` includes conda build paths; use the portable modeling requirements for a new environment.

Upload the improved CSV to Omnicampus and check that its scoring timestamp updates. Upload the reproduction
ZIP as code evidence if required. The local test data have no labels, so local validation cannot reveal the hidden test AUC.
'''
(e.ROOT/'IMPROVEMENT_REPORT.md').write_text(txt)

# Compact visual summary, exported as a standalone artifact.
fig,axes=plt.subplots(1,2,figsize=(12,4.5),layout='constrained')
screen=[r for r in rows if r['name']!='tutorial_rf']
axes[0].plot(np.maximum.accumulate([r['auc'] for r in screen]),color='#35678e')
axes[0].set(xlabel='Screened configuration',ylabel='Best inner validation AUC',title='Development search progress')
ordered=sorted(cv,key=lambda r:r['auc'])
axes[1].barh([r['name'] for r in ordered],[r['auc'] for r in ordered],color='#35678e')
axes[1].set(xlim=(min(r['auc'] for r in cv)-.005,max(r['auc'] for r in cv)+.002),xlabel='Pooled OOF AUC',title='Five-fold development validation')
fig.savefig(e.ART/'results_summary.png',dpi=160)
plt.close(fig)

# Hash only durable deliverables, not runtime kernel/cache files.
files=[e.ROOT/n for n in ['01_competition_data_audit.ipynb','02_improved_models_and_submission.ipynb','IMPROVEMENT_REPORT.md',
       'README.ipynb','tutorial.ipynb','preprocessing.ipynb','HomeCredit_columns_description.xlsx','environment.yml','conda-explicit-osx-arm64.txt']]
for f in (e.ROOT/'improvements').rglob('*'):
    if not f.is_file(): continue
    if any(p in f.parts for p in ['__pycache__','kernels','matplotlib']): continue
    if f.suffix=='.log': continue
    if f.name=='package_manifest.json': continue
    files.append(f)
files.append(e.ROOT/'output/submission_improved.csv')
manifest={str(f.relative_to(e.ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
e.save_json('package_manifest.json',manifest)
files.append(e.ART/'package_manifest.json')
archive=e.ROOT/'output/competition_improved_reproduction.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for f in files: z.write(f,arcname=str(Path('Competition')/f.relative_to(e.ROOT)))
with zipfile.ZipFile(archive) as z: assert z.testzip() is None
print('Report:',e.ROOT/'IMPROVEMENT_REPORT.md')
print('Package:',archive,'bytes:',archive.stat().st_size)
