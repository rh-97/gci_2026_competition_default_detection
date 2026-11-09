"""Create only new third-pass notebooks; do not rewrite an existing notebook."""
import textwrap
import nbformat as n
import round3 as t

def md(s):return n.v4.new_markdown_cell(textwrap.dedent(s).strip())
def code(s):
    source=textwrap.dedent(s).strip();compile(source,'<notebook>','exec');return n.v4.new_code_cell(source)

SETUP='''
from pathlib import Path
import sys, json
ROOT=Path.cwd()
if not (ROOT/'input').exists():
    ROOT=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'input/train.csv').exists())
assert Path(sys.prefix).resolve()==(ROOT/'.venv').resolve(), 'Use the project local venv'
sys.path.insert(0,str(ROOT/'improvements/round3'))
import round3 as t
import validate as v
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
ART=t.ART
print('Python:',sys.executable)
print('Third-pass implementation:',t.implementation_hash())
'''

def build05():
    cells=[md('''
    # Third pass: hypotheses, matched comparisons and negative results

    The previous pass achieved a screenshot-reported public score of **0.76756**,
    rank **568**. File attribution follows the conversation; the screenshot does
    not show a filename. This notebook reviews a new, prospectively planned pass
    using only supplied rows. The public score does not select experiments.

    The main question is whether tuning **after** finding better features improves
    the result. New features and other model families follow the recorded plan.
    Full details and exact per-trial configurations: `ROUND3_EXPERIMENT_LOG.md`.
    Existing notebooks are unchanged.
    '''),code(SETUP),code('''
    display(Markdown((t.HERE/'PLAN.md').read_text()))
    display(Markdown((t.HERE/'FOLLOWUP_PLAN.md').read_text()))
    display(Markdown((t.HERE/'BAGGING_PLAN.md').read_text()))
    display(pd.Series(t.read(ART/'public_feedback.json')))
    '''),md('''
    ## Feature definitions and constraints

    The reference representation contains the previous compact predictors plus
    three hypothetical rate transforms and two term-distance transforms. New
    blocks isolate signed term residuals/coarse categories, extra assumed periods,
    explicit categorical crosses, or the larger original representation.

    None recovers a real loan schedule or interest rate. Rates solve the assumed
    annuity equation for a declared period count. Signed distances retain the
    direction relative to a rounded multiple. All are functions of supplied row
    values. Group aggregates, neural quantiles and category vocabularies fit only
    training rows. IDs and targets are excluded.
    '''),code('''
    train,test,y,split=t.load()
    counts=[dict(representation=m,columns=t.features(train.iloc[:10],m).shape[1])
            for m in ['proxy','signed','rates','crosses','engineered_proxy']]
    display(pd.DataFrame(counts))
    print('Training rows:',len(train),'test rows:',len(test),'positive rate:',y.mean())
    display(pd.Series(t.read(ART/'preflight.json')))
    '''),md('''
    ## Every screen, including failures

    Scores below use the repeatedly explored inner split. The baseline is the
    **complete current mixture**, not only its lead CatBoost component. A weaker
    individual model can still be useful when its errors differ. Screening
    complementarity must survive five-fold validation and frozen confirmation.
    '''),code('''
    rows=t.screen_rows()
    complete=[a for a in rows if a['status']=='complete']
    frame=pd.DataFrame([dict(name=a['name'],kind=a['spec']['kind'],auc=a.get('auc'),
        blend_auc=a.get('best_blend',{}).get('auc'),
        blend_gain=a.get('best_blend',{}).get('auc',np.nan)-a.get('reference_auc',np.nan),
        iterations=a.get('iterations'),seconds=a.get('seconds'),status=a['status']) for a in rows])
    display(frame.sort_values('blend_auc',ascending=False))
    control=next(a for a in complete if a['name']=='r3_cat_baseline')
    assert control['baseline_max_difference']==0
    print('Control maximum prediction difference:',control['baseline_max_difference'])
    '''),code('''
    plot=frame[frame.status=='complete'].sort_values('blend_gain')
    fig,ax=plt.subplots(figsize=(10,max(5,len(plot)*.31)))
    ax.barh(plot.name,plot.blend_gain,color=np.where(plot.blend_gain>=.0001,'#326788','#bd7952'))
    ax.axvline(.0001,color='gray',linestyle='--',label='Promotion threshold')
    ax.set_xlabel('Best screened blend AUC gain over the complete round-two mixture')
    ax.legend();fig.tight_layout();plt.show()
    '''),code('''
    neural=[a for a in complete if a['spec']['kind']=='mlp']
    if neural:
        fig,ax=plt.subplots(figsize=(9,4))
        for a in neural:
            curve=t.read(ART/'screen'/(a['name']+'_curve.json'))
            ax.plot([b['epoch'] for b in curve],[b['validation_auc'] for b in curve],label=a['name'])
        ax.set(xlabel='Training epoch',ylabel='Inner validation AUC',title='Scratch-trained neural models')
        ax.legend();fig.tight_layout();plt.show()
    '''),md('''
    ## Current-model slices and blend-only diagnostics

    Slice differences are exploratory. Sparse categories have unstable estimates;
    a lower slice AUC alone does not justify a specialist model. The percentile
    transform is a ranking score rather than a calibrated default probability.
    '''),code('''
    display(pd.read_csv(ART/'current_model_slice_diagnostic.csv'))
    display(pd.DataFrame(t.read(ART/'early_blend_diagnostic.json')))
    if (ART/'stacking_probe.json').exists():
        probe=t.read(ART/'stacking_probe.json')
        display(pd.DataFrame([dict(name=a['spec']['name'],auc=a['auc'],best_blend_gain=a['gain']) for a in probe['results']]))
        print(probe['caveat'])
        print('Warrants fully nested follow-up:',probe['warrants_nested_followup'])
    display(pd.Series(t.read(ART/'promotion.json')))
    '''),md('''
    ## Exact trial record and interpretation

    Interpretations distinguish observed effects from proposed mechanisms. A
    negative result does not establish universal ineffectiveness. Operational
    incidents and corrections are retained in the journal.
    '''),code('''
    ledger=t.read(ART/'experiment_ledger.json')
    for a in ledger:
        display(Markdown('### '+a['name']+'\\n\\n'+a['spec']['hypothesis']+'\\n\\n'+a['interpretation']))
        display(a['spec'])
    '''),md('''
    ## Re-run experiments deliberately

    Results and predictions above are saved evidence. Training is opt-in because
    the full run can take substantial CPU time. Cached configurations are reused
    only when their implementation signature and exact specification match.
    '''),code('''
    RUN_SCREENING=False
    if RUN_SCREENING:
        t.screen()
    ''')]
    return cells

def build06():
    return [md('''
    # Third pass: validation, frozen decisions and reproduction

    The reference is the entire previous recipe. This notebook reviews common-fold
    OOF selection, the frozen new-fold-seed test, and a fair comparison against the
    current two-seed model bank. A new partition is a robustness check on previously
    explored labels, not an untouched test. A failed gate keeps the previous CSV.
    '''),code(SETUP),code('''
    selection=t.read(ART/'selection.json')
    display(pd.Series(selection))
    rows=[t.read(p) for p in sorted((ART/'cv').glob('*.json'))]
    display(pd.DataFrame([dict(model=a['name'],auc=a['auc'],fold_sd=np.std(a['fold_auc'],ddof=1),
                              median_iterations=int(np.median(a['iterations']))) for a in rows]))
    display(pd.Series(t.read(ART/'blend_methods.json')))
    if (ART/'winner_complementarity.json').exists():display(pd.Series(t.read(ART/'winner_complementarity.json')))
    '''),code('''
    fig,ax=plt.subplots(figsize=(9,4))
    drawn=False
    for family in selection['new_families']:
        path=ART/'cv'/family['name']/'fold0_curve.json'
        if not path.exists():continue
        curve=t.read(path)
        if isinstance(curve,dict) and 'AUC' in curve.get('validation',{}):
            values=curve['validation']['AUC']
            ax.plot(np.arange(1,len(values)+1),values,label=family['name'])
            ax.axvline(family['iterations'][0],color='gray',linewidth=.7,alpha=.5)
            drawn=True
    if drawn:
        ax.set(xlabel='Boosting iteration',ylabel='Validation AUC',title='Primary fold 1: selection learning curves')
        ax.legend();fig.tight_layout();plt.show()
    else:plt.close(fig)
    '''),md('''
    ## Frozen confirmation and fair seed averaging

    The candidate recipe, weights, CDF references and iteration counts are fixed
    before confirmation. Confirmation never passes validation labels to model
    fitting. Any accepted final bank must also beat the existing two-seed bank;
    otherwise a one-seed improvement could disappear through averaging.
    '''),code('''
    confirm=t.read(ART/'confirmation_results.json')
    average=t.read(ART/'averaging_results.json')
    display(pd.Series(confirm));display(pd.Series(average))
    if (ART/'bagging_probe.json').exists():display(pd.Series(t.read(ART/'bagging_probe.json')))
    if 'fold_gains' in confirm:
        fig,ax=plt.subplots(figsize=(9,4))
        xx=np.arange(1,6)
        ax.bar(xx-.18,selection['fold_gains'],.36,label='Primary selection folds')
        ax.bar(xx+.18,confirm['fold_gains'],.36,label='New seed, fixed iterations')
        ax.axhline(0,color='gray',linewidth=.8)
        ax.set(xlabel='Fold within each seed',ylabel='AUC gain over the round-two reference')
        ax.legend();fig.tight_layout();plt.show()
    '''),md('''
    ## Final result and saved-model inference

    Full-data OOF scores, if a candidate passed, are diagnostics after selection.
    They do not change the chosen weights. The public score of a new CSV remains
    unknown. Reproduction below loads saved models or verifies the retained CSV.
    '''),code('''
    import finalize
    import bagging
    result=bagging.preferred_result()
    display(pd.Series(result))
    bagging.reproduce()
    sub=pd.read_csv(ROOT/result['submission'])
    assert len(sub)==61500 and list(sub)==['SK_ID_CURR','TARGET']
    assert sub.SK_ID_CURR.equals(pd.read_csv(ROOT/'input/sample_submission.csv').SK_ID_CURR)
    display(sub.head())
    '''),code('''
    if (ART/'importance_summary.json').exists():
        info=t.read(ART/'importance_summary.json')
        print(info['note'])
        for family in info['families']:
            frame=pd.read_csv(ROOT/family['file']).head(15).sort_values('mean_importance_pct')
            fig,ax=plt.subplots(figsize=(9,5))
            ax.barh(frame.feature,frame.mean_importance_pct)
            ax.set(xlabel='Mean within-model normalized importance (%)',title=family['name']+' / '+family['measure'])
            fig.tight_layout();plt.show()
    '''),code('''
    import hashlib
    manifest=t.read(t.HERE/'reference/preserved_hashes.json')
    for name,want in manifest.items():
        path=ROOT/name
        if path.exists():assert hashlib.sha256(path.read_bytes()).hexdigest()==want,name
    print('Existing notebooks and all present protected artifacts are unchanged.')
    print('CSV SHA-256:',hashlib.sha256((ROOT/result['submission']).read_bytes()).hexdigest())
    '''),md('''
    ## Deliberate full reproduction

    Use `.venv/bin/python` from the Competition directory. The phase order is:
    `round3.py screen`, `followup.py`, `stacking_probe.py`, `validate.py cv`, `validate.py select`,
    `validate.py confirmation`, `validate.py averaging`,
    `finalize.py train_final`, `finalize.py reproduce`, then the prospective
    `bagging.py probe`, `bagging.py train`, `bagging.py reproduce` check.
    The plan and complete journal describe any recorded follow-ups. Input CSVs
    and the venv are excluded from the code archive; retain the supplied data.
    '''),code('''
    RUN_VALIDATION_AND_TRAINING=False
    if RUN_VALIDATION_AND_TRAINING:
        v.cv();v.select();v.confirmation();v.averaging()
        finalize.train_final();finalize.reproduce()
        bagging.probe();bagging.train();bagging.reproduce()
    ''')]

def main():
    for name,cells in [('05_round3_hypotheses_and_experiments.ipynb',build05()),('06_round3_validation_and_reproduction.ipynb',build06())]:
        path=t.ROOT/name
        assert not path.exists(),'Refuse to change an existing notebook: '+name
        nb=n.v4.new_notebook(cells=cells,metadata=dict(kernelspec=dict(display_name='Competition local venv',language='python',name='competition-local'),language_info=dict(name='python',version='3.12')))
        n.validate(nb);n.write(nb,path);print('Created',name)

if __name__=='__main__':main()
