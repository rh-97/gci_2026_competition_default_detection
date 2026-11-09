"""Create new explanatory notebooks; never touch supplied notebooks."""
from pathlib import Path
import json
import nbformat as nbf

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
def md(s): return nbf.v4.new_markdown_cell(s.strip())
def code(s): return nbf.v4.new_code_cell(s.strip())
def write(name,cells):
    if name=='01_competition_data_audit.ipynb' and (ROOT/name).exists(): return
    nb=nbf.v4.new_notebook(cells=cells)
    nb.metadata['kernelspec']={'display_name':'Competition local venv','language':'python','name':'competition-local'}
    nb.metadata['language_info']={'name':'python','version':'3.12.15'}
    nbf.write(nb,ROOT/name)

setup='''
from pathlib import Path
import sys, json, numpy as np, pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
ROOT = Path.cwd() if (Path.cwd()/'input/train.csv').exists() else Path.cwd()/'Competition'
assert (ROOT/'input/train.csv').exists(), 'Run from the Competition directory or its parent.'
assert Path(sys.prefix).resolve() == (ROOT/'.venv').resolve(), 'Select the project local venv kernel.'
ART=ROOT/'improvements/artifacts'
plt.rcParams.update({'figure.dpi':110,'axes.spines.top':False,'axes.spines.right':False})
train=pd.read_csv(ROOT/'input/train.csv'); test=pd.read_csv(ROOT/'input/test.csv')
print('Python:',sys.executable)
'''

write('01_competition_data_audit.ipynb',[
md('''# Competition and data audit

GCI Global 2026 Home Credit Default Risk. Predict the probability of payment difficulties (`TARGET=1`). The supplied README specifies ROC-AUC, submission columns `SK_ID_CURR,TARGET`, and that the **last submitted file** determines the final entry. Its stated deadline is November 20 at 01:00 UTC (07:00 Bangladesh time). These are the local instructions, not a live verification of the competition platform.

Only the supplied CSVs and local column dictionary are used. No external data, hand-labeling, or online reference code. The original notebooks remain unchanged. The local tutorial is the reference for the five-feature baseline; the new modeling code is written for this project.

The validation plan reserves 20% for an untouched audit. Tuning uses only the remaining development data. Fitted transformations, categorical vocabularies and optional group medians are learned inside each training split. Customer IDs are excluded from models.'''),
code(setup),
code('''
display(pd.DataFrame({'rows':[len(train),len(test)],'columns':[train.shape[1],test.shape[1]]},index=['train','test']))
display(pd.read_excel(ROOT/'HomeCredit_columns_description.xlsx'))
target=train.TARGET.value_counts().sort_index().to_frame('count')
target['percent']=100*target['count']/len(train)
display(target)
assert set(train.TARGET.unique())=={0,1}
assert train.SK_ID_CURR.is_unique and test.SK_ID_CURR.is_unique
assert not set(train.SK_ID_CURR)&set(test.SK_ID_CURR)
assert list(train.drop(columns='TARGET').columns)==list(test.columns)
print('Feature duplicates:',train.drop(columns=['SK_ID_CURR','TARGET']).duplicated().sum())
display(train.isna().mean().sort_values(ascending=False).rename('missing_fraction').head(15))
'''),
code('''
fig,axes=plt.subplots(1,3,figsize=(14,3.5),layout='constrained')
target['count'].plot.bar(ax=axes[0],color=['#35678e','#d97652'],rot=0,title='Target imbalance')
train.isna().mean().sort_values().tail(10).plot.barh(ax=axes[1],title='Missing data')
for value,label in [(0,'No payment difficulties'),(1,'Payment difficulties')]:
    train.loc[train.TARGET.eq(value),'EXT_SOURCE_2'].plot.hist(bins=40,density=True,alpha=.5,ax=axes[2],label=label)
axes[2].legend(fontsize=7); axes[2].set_title('External score 2 by target')
axes[2].set_ylabel('Density')
plt.show()
'''),
md('''## Missingness and special values

`DAYS_EMPLOYED=365243` is a sentinel, not a thousand years of employment. Replace it with missing and add an indicator. Preserve informative missingness rather than dropping most rows or imputing all customers identically. The missing car age is retained; no assumption is made that missing age means the client owns no car.

An 8% positive class makes accuracy misleading: predicting zero for every row scores roughly 92% accuracy. Optimize ROC-AUC using probabilities. Average precision and probability calibration metrics are secondary diagnostics. Do not balance the audit or test distributions, and do not apply SMOTE before splitting.'''),
code('''
print('Employment sentinel train/test:',train.DAYS_EMPLOYED.eq(365243).mean(),test.DAYS_EMPLOYED.eq(365243).mean())
display(train.groupby(pd.qcut(train.SK_ID_CURR,10),observed=True).TARGET.agg(['size','mean']))
print('Train ID range:',train.SK_ID_CURR.min(),train.SK_ID_CURR.max())
print('Test ID range:',test.SK_ID_CURR.min(),test.SK_ID_CURR.max())
'''),
md('''## Train/test shift

Compare feature missingness, numerical distributions, categorical proportions, and a classifier that tries to distinguish train from test. Exclude the sequential ID: its artificial non-overlap would trivially reveal the source. A near-0.5 adversarial AUC supports random stratified validation but cannot prove the absence of hidden or target shift. Large samples can give small p-values for negligible differences, so inspect effect sizes.'''),
code('''
from scipy.stats import ks_2samp
numeric=train.select_dtypes(include='number').columns.difference(['SK_ID_CURR','TARGET'])
shift=[]
for c in numeric:
    a=train[c].dropna(); b=test[c].dropna()
    ks=ks_2samp(a,b)
    shift.append({'feature':c,'KS_statistic':ks.statistic,'train_missing':train[c].isna().mean(),'test_missing':test[c].isna().mean()})
shift=pd.DataFrame(shift).sort_values('KS_statistic',ascending=False)
display(shift.head(12)); shift.to_csv(ART/'numeric_shift.csv',index=False)
cat_shift=[]
for c in train.select_dtypes(include=['object','str']).columns:
    a=train[c].fillna('__MISSING__').value_counts(normalize=True)
    b=test[c].fillna('__MISSING__').value_counts(normalize=True)
    idx=a.index.union(b.index)
    cat_shift.append({'feature':c,'total_variation_distance':.5*(a.reindex(idx,fill_value=0)-b.reindex(idx,fill_value=0)).abs().sum(),'unseen_test_categories':len(set(b.index)-set(a.index))})
display(pd.DataFrame(cat_shift).sort_values('total_variation_distance',ascending=False))
'''),
code('''
import sys
sys.path.insert(0,str(ROOT/'improvements'))
from experiment import features, Encoder, SEED
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from lightgbm import LGBMClassifier
both=pd.concat([train.drop(columns='TARGET'),test],ignore_index=True)
source=np.r_[np.zeros(len(train),dtype=int),np.ones(len(test),dtype=int)]
x=features(both,'raw')
a,b=train_test_split(np.arange(len(source)),test_size=.25,stratify=source,random_state=SEED)
enc=Encoder().fit(x.iloc[a])
adversary=LGBMClassifier(n_estimators=150,num_leaves=15,min_child_samples=200,learning_rate=.05,verbosity=-1,n_jobs=2,random_state=SEED)
adversary.fit(enc.transform(x.iloc[a]),source[a])
adversarial_auc=roc_auc_score(source[b],adversary.predict_proba(enc.transform(x.iloc[b]))[:,1])
print('Train-versus-test adversarial AUC:',round(adversarial_auc,6))
(ART/'data_audit.json').write_text(json.dumps({'adversarial_auc':adversarial_auc,'train_rows':len(train),'test_rows':len(test),'positive_rate':train.TARGET.mean()},indent=2))
'''),
md('''## Modeling decisions

Use all 32 customer features, retain missing values for trees, add financial and lifetime ratios and external-score summaries, and compare against unengineered data. Try regularized LightGBM, native-categorical CatBoost, and logistic regression. Optional category frequencies and group medians are fitted separately inside each split. Neither test rows nor validation targets are used to fit those transformations.

Tune on development data, verify finalists with five-fold stratified CV, choose a simple blend only if it improves pooled out-of-fold AUC, then evaluate the frozen choice once on the untouched audit. Final five-fold models use all labeled data and fixed iteration counts chosen during development. This reduces randomness and retains every labeled row for learning in four folds. Keep the independent audit as the primary estimate; final full-data OOF predictions are a diagnostic because their development labels already influenced selection.''')])

results_cells=[md('''# Improved Home Credit models: experiments and submission

This notebook explains the executed experiments and reproduces the submission from saved models. To rerun training, use the commands below with the project venv. All original notebooks are preserved; all dataset rows come from `input/train.csv` and `input/test.csv`.

The five-feature random forest baseline follows the supplied `tutorial.ipynb`, with preprocessing fitted within the split to avoid its preprocessing leakage. New model code is original to this project; no external notebook code or dataset was downloaded.'''),code(setup),
md('''## Reproduce the complete experiment

From `Competition`, run these commands in order. They perform the same seeded split, screening, five-fold development validation, one frozen audit evaluation, and final training. Repeatedly inspecting the audit and tuning against it would invalidate its independence.

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

The package versions and original-file hashes are recorded under `improvements/artifacts`. Source, notebooks, models, results and submission are included in the reproduction ZIP.'''),
code('''
# Set True to rerun the full search and training from this notebook (lengthy).
# False reuses the supplied, executed artifacts and saved models.
RUN_FULL_EXPERIMENT = False
if RUN_FULL_EXPERIMENT:
    import subprocess
    stages=[['experiment.py','screen','--trials','24'],['supplement.py'],['refine.py'],
            ['select_features.py'],['refine_cat.py'],['experiment.py','cv'],
            ['experiment.py','audit'],['experiment.py','final']]
    for stage in stages:
        subprocess.run([sys.executable,str(ROOT/'improvements'/stage[0]),*stage[1:]],cwd=ROOT,check=True)
else:
    print('Using the completed experiment; saved-model prediction is reproduced below.')
'''),
code('''
screen=json.loads((ART/'screen_results.json').read_text())
screen+=json.loads((ART/'supplement_results.json').read_text())
screen+=json.loads((ART/'refine_results.json').read_text())
screen+=json.loads((ART/'feature_selection_results.json').read_text())
screen+=json.loads((ART/'cat_refine_results.json').read_text())
table=pd.DataFrame([{k:v for k,v in row.items() if k!='spec'} for row in screen]).sort_values('auc',ascending=False)
display(table)
'''),
code('''
cv=json.loads((ART/'cv_results.json').read_text())
display(pd.DataFrame([{'model':r['name'],'pooled_oof_auc':r['auc'],'fold_mean':np.mean(r['fold_auc']),'fold_std':np.std(r['fold_auc'],ddof=1),'median_trees':int(np.median(r['iterations']))} for r in cv]).sort_values('pooled_oof_auc',ascending=False))
selection=json.loads((ART/'selection.json').read_text())
display(pd.DataFrame({'model':selection['names'],'weight':selection['weights']}))
print('Selected blend development OOF AUC:',selection['auc'])
'''),
md('''## Independent audit

The audit contains 20% of training rows, isolated before any model selection. Model choice, blend weights, categorical encoders and tree counts were frozen first. Its probabilities come from models fitted on development rows, with no audit early stopping. Paired stratified bootstrap confidence intervals quantify sampling uncertainty conditional on these fitted models; they do not capture every source of training or competition shift.'''),
code('''
audit=json.loads((ART/'audit_results.json').read_text())
display(pd.DataFrame({'Tutorial RF':audit['baseline'],'Improved model':audit['improved']}))
print('Improved AUC 95% bootstrap interval:',audit['auc_ci95'])
print('Paired AUC gain 95% bootstrap interval:',audit['auc_gain_ci95'])
print('Optimistic in-sample development diagnostics:',audit['development_training'])
'''),
code('''
from sklearn.metrics import RocCurveDisplay, PrecisionRecallDisplay
from sklearn.calibration import calibration_curve
a=np.load(ART/'audit_predictions.npz')
fig,axes=plt.subplots(1,3,figsize=(14,4),layout='constrained')
for key,label in [('baseline','Tutorial RF'),('improved','Improved')]:
    RocCurveDisplay.from_predictions(a['target'],a[key],name=label,ax=axes[0])
    PrecisionRecallDisplay.from_predictions(a['target'],a[key],name=label,ax=axes[1])
    observed,predicted=calibration_curve(a['target'],a[key],n_bins=10,strategy='quantile')
    axes[2].plot(predicted,observed,'o-',label=label)
axes[2].plot([0,.5],[0,.5],'--',color='gray'); axes[2].legend()
axes[2].set(xlabel='Predicted probability',ylabel='Observed positive fraction',title='Calibration (quantile bins)')
plt.show()
display(pd.read_csv(ART/'audit_subgroups.csv'))
'''),
md('''## Final training and feature importance

Five deterministic, stratified folds are fitted with fixed tree counts. Each row is held out from its own OOF model. Average the five test predictions within each family, then apply the frozen development blend weights. Numerical missing values are learned directly by LightGBM; CatBoost receives a numeric missing sentinel plus missing-derived features. Feature importance describes the model's use of each feature.'''),
code('''
final=json.loads((ART/'final_results.json').read_text())
display(pd.DataFrame(final['models']))
print('Diagnostic full-data OOF:',final['full_oof'])
print(final['caveat'])
for name in selection['names']:
    if not (ART/(name+'_importance.csv')).exists(): continue
    importance=pd.read_csv(ART/(name+'_importance.csv'),index_col=0).iloc[:,0]
    importance.head(20).sort_values().plot.barh(figsize=(8,6),title=name+' — mean fold importance')
    plt.tight_layout(); plt.show()
'''),
md('''## Recreate the exact submission from saved models

Run the following cell to predict the supplied test rows without retraining. It recreates the encoders, loads each saved model, averages probabilities and checks the file against the stored SHA-256 checksum. This takes longer than displaying the results above but much less time than rerunning the search.'''),
code('''
import sys, hashlib, joblib
sys.path.insert(0,str(ROOT/'improvements'))
from experiment import features, Encoder
import lightgbm as lgb
from catboost import CatBoostClassifier
prediction=np.zeros(len(test))
for weight,row in zip(selection['weights'],selection['models']):
    spec=row['spec']; xt=features(test,spec['features']); family_prediction=np.zeros(len(test))
    for fold in range(5):
        prefix=ROOT/'improvements/models'/f"{row['name']}_fold{fold}"
        encoder=Encoder(); encoder.__dict__.update(joblib.load(str(prefix)+'_encoder.joblib'))
        if spec['kind']=='lgb':
            model=lgb.Booster(model_file=str(prefix)+'.txt')
            p=model.predict(encoder.transform(xt),num_threads=4)
        elif spec['kind']=='cat':
            model=CatBoostClassifier(); model.load_model(str(prefix)+'.cbm')
            p=model.predict_proba(encoder.transform(xt))[:,1]
        else:
            model=joblib.load(str(prefix)+'.joblib')
            p=model.predict_proba(encoder.transform(xt))[:,1]
        family_prediction+=p/5
    prediction+=weight*family_prediction
submission=pd.read_csv(ROOT/'input/sample_submission.csv')
assert submission.SK_ID_CURR.equals(test.SK_ID_CURR)
assert np.isfinite(prediction).all() and ((0<=prediction)&(prediction<=1)).all()
submission['TARGET']=prediction
reproduced=ROOT/'output/submission_reproduced.csv'
submission.to_csv(reproduced,index=False)
actual=hashlib.sha256(reproduced.read_bytes()).hexdigest()
assert actual==final['sha256'], (actual,final['sha256'])
print('Exact submission reproduced:',reproduced)
display(submission.head())
'''),
md('''## Submission and limitations

Upload `output/submission_improved.csv` to Omnicampus. The local README says the final ranking uses your **last** submission. Upload the reproduction ZIP as code evidence if seeking Honors/Outstanding Student. No competition-platform submission is performed by this notebook.

The hidden test score remains unknown. Tiny CV differences may be noise. More searches can overfit development predictions, and there is no defensible way to guarantee a global optimum. The stopping decision is based on diminishing returns across model families, feature variants, regularization settings, validation folds and simple blends. Do not use the independent audit repeatedly to select additional variants.''')]
write('02_improved_models_and_submission.ipynb',results_cells)

if __name__=='__main__':
    print('Created two new notebooks.')
