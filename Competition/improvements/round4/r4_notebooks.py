"""Create only new notebooks 07/08; all earlier notebooks remain immutable."""
import textwrap
import nbformat as n
import round4 as t
def md(s):return n.v4.new_markdown_cell(textwrap.dedent(s).strip())
def code(s):
    s=textwrap.dedent(s).strip();compile(s,'<notebook>','exec');return n.v4.new_code_cell(s)
SETUP='''
from pathlib import Path
import sys, json, hashlib
ROOT=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'input/train.csv').exists())
assert Path(sys.prefix).resolve()==(ROOT/'.venv').resolve(),'Use project local venv'
sys.path.insert(0,str(ROOT/'improvements/round4'))
import round4 as t
import r4_cv as cv
import r4_validate as v
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
ART=t.ART
print('Python:',sys.executable)
print('Engine signature:',t.SIGNATURE)
print('Reference public AUC:',t.PUBLIC)
'''

def experiments():
    return [md('''
    # Round four: retuning the successful representation

    The user confirmed public AUC **0.76824**, rank snapshot **518**, for
    `submission_round3_bagged.csv`. This pass asks whether the final 55-column
    representation benefits from fresh tuning, separate ratio/rounding features,
    or more training rows per model. Public feedback does not tune this search.
    All supplied rows and the project venv are used. No online data/pretrained
    weights are used. All nine older notebooks are preserved.
    '''),code(SETUP),code('''
    display(Markdown((t.HERE/'PLAN.md').read_text()))
    display(pd.Series(t.read(ART/'preflight.json')))
    train,test,y,split=t.load()
    display(pd.DataFrame([dict(mode=m,columns=t.features(train.iloc[:10],m).shape[1])
        for m in ['final55','period3','period24','period3_24','goods_ratio','goods_structure','all_terms']]))
    print('Train/test rows:',len(train),len(test),'positive fraction:',y.mean())
    '''),md('''
    ## Representations and validation discipline

    The reference adds signed residuals and rounded categories of credit/annuity
    ratios to the earlier compact loan-proxy frame. New ablations use ratio
    scales 3 and 24 and goods-price/annuity structure. These are functions of
    supplied values, not recovered interest rates or payment schedules.
    Every transform is row-local; learned imputation, vocabularies and any group
    aggregates use only training-fold rows. ID and target are excluded.

    Screens reuse the explored inner split and compare against the complete
    reference mixture. These scores select hypotheses; they are not independent
    confirmation of hidden-test improvement.
    '''),code('''
    rows=t.screen_rows()
    frame=pd.DataFrame([dict(name=a['name'],kind=a['spec']['kind'],features=a['spec']['features'],
        auc=a.get('auc'),blend_gain=a.get('best_blend',{}).get('auc',np.nan)-a.get('reference_auc',np.nan),
        iterations=a.get('iterations'),seconds=a.get('seconds'),status=a['status']) for a in rows])
    display(frame.sort_values('blend_gain',ascending=False))
    for name in ['r4_cat_control','r4_cat_control512']:
        row=next(a for a in rows if a['name']==name)
        assert row['control_max_difference']==0
        print(name,'exact reproduction:',row['control_max_difference'])
    '''),code('''
    plot=frame[frame.status=='complete'].sort_values('blend_gain')
    fig,ax=plt.subplots(figsize=(11,max(6,len(plot)*.28)))
    ax.barh(plot.name,plot.blend_gain,color=np.where(plot.blend_gain>=.0001,'#256d89','#b77b59'))
    ax.axvline(0,color='gray',linewidth=.8);ax.axvline(.0001,color='gray',linestyle='--')
    ax.set_xlabel('Best inner blend AUC gain over the complete round-three reference')
    fig.tight_layout();fig.savefig(ART/'screen_gains.png',dpi=140);plt.show()
    '''),md('''
    ## Conditional combinations and promotion

    The exact follow-up specifications were generated and recorded before their
    fits, under at most three positive-component combinations. Promotion uses
    separate parameter, feature, remaining-CatBoost and alternative-tree slots,
    with the recorded minimum gains. No exact control is promoted as a new model.
    '''),code('''
    display(t.read(ART/'followup_plan.json'))
    display(t.read(ART/'promotion.json'))
    records=t.read(ART/'experiment_ledger.json')
    for a in records:
        display(Markdown('### '+a['name']+'\\n\\n'+a['hypothesis']+'\\n\\n'+a['interpretation']))
        display(a['spec'])
    '''),md('''
    ## Training fraction at fixed model capacity

    Ten folds are formed by splitting each original five-fold validation group
    into two stratified halves. This changes training fraction from about 80%
    to 90% while pairing parent-group model seeds. Tree count is fixed at 1,312;
    validation labels are not passed for early stopping. If the first gain gate
    passes, a second five-fold model seed matches the ten-fold inference count.
    Its two OOF values per row favor variance reduction in the control. This is
    conservative end-to-end evidence, not a perfect causal isolation of row count.
    '''),code('''
    display(t.read(ART/'fraction_plan.json'))
    fraction=t.read(ART/'fraction_feasibility.json')
    display(pd.Series(fraction))
    rows=[]
    for directory in [ART/'fraction/primary',ART/'fraction/candidate_primary']:
        for file in directory.glob('*.json'):
            a=t.read(file)
            rows.append(dict(name=a['name'],folds=a['folds'],auc=a['auc'],
                train_rows=a['training_rows'],iterations=a['iterations'],seconds=a['seconds']))
    display(pd.DataFrame(rows))
    '''),md('''
    ## Rerun deliberately

    All tables use retained evidence. Training is disabled by default. Matching
    exact source/data/package/specification signatures reuse caches. Full detail,
    including negative results, is in `ROUND4_EXPERIMENT_LOG.md`.
    '''),code('''
    RUN_SCREENING=False
    if RUN_SCREENING:
        import r4_followup
        t.screen();r4_followup.main()
    ''')]

def validation():
    return [md('''
    # Round four: frozen gates and saved-model replay

    Local selection is followed by fixed-weight confirmation on a fresh fold
    partition, then a matching three-seed comparison. These remain previously
    explored labels. No score here is an untouched or hidden-test estimate.
    Failure retains the user-confirmed 0.76824 round-three bagged file.
    '''),code(SETUP),code('''
    choice=t.read(ART/'selection.json');v.check_freeze()
    display(pd.Series(choice))
    cvs=[t.read(p) for p in sorted((ART/'cv').glob('*.json'))]
    display(pd.DataFrame([dict(name=a['name'],auc=a['auc'],folds=a['folds'],
        fold_auc=a['fold_auc'],median_iterations=int(np.median(a['iterations']))) for a in cvs]))
    grid=t.read(ART/'blend_candidates.json')
    print('Complete pre-confirmation grid size:',len(grid))
    display(pd.DataFrame(grid).head(15))
    '''),md('''
    ## Frozen confirmation and three-seed validation

    The recipe, complete pair/helper grid, source, CDFs and tree counts were
    frozen before confirmation. Each validation row's own target is excluded
    from fitting and preprocessing. Confirmation uses no validation early stop.
    At most two new families can enter a recipe. No continuous weight optimizer
    or post-confirmation grid change is allowed. A failed gate ends deployment.
    '''),code('''
    confirm=t.read(ART/'confirmation_results.json');average=t.read(ART/'averaging_results.json')
    display(pd.Series(confirm));display(pd.Series(average))
    if 'fold_gains'in confirm:
        fig,ax=plt.subplots(figsize=(9,4));xx=np.arange(1,6)
        ax.bar(xx-.18,choice['fold_gains'],.36,label='Primary selection')
        ax.bar(xx+.18,confirm['fold_gains'],.36,label='Fresh partition, fixed trees')
        ax.axhline(0,color='gray',linewidth=.8)
        ax.set(xlabel='Group within each partition',ylabel='AUC gain over round-three reference')
        ax.legend();fig.tight_layout();fig.savefig(ART/'fold_gains.png',dpi=140);plt.show()
    if (ART/'fraction_budget_check.json').exists():display(t.read(ART/'fraction_budget_check.json'))
    if (ART/'conditional_uncertainty.json').exists():display(t.read(ART/'conditional_uncertainty.json'))
    '''),code('''
    for a in choice['new_families']:
        path=ART/'cv'/a['name']/'fold0_curve.json'
        if path.exists():
            curve=t.read(path)
            values=curve.get('validation',{}).get('AUC',[])
            if values:
                fig,ax=plt.subplots(figsize=(9,4));ax.plot(np.arange(1,len(values)+1),values)
                ax.axvline(a['iterations'][0],color='gray',linestyle='--')
                ax.set(xlabel='Iteration',ylabel='Primary fold 1 AUC',title=a['name'])
                fig.tight_layout();plt.show()
    '''),md('''
    ## Final recommendation and exact reproduction

    An accepted candidate uses three full-data fold seeds and fixed capacity.
    Full-data OOF is diagnostic after selection and cannot change its recipe.
    Replay loads saved models and writes a new reproduction filename. A fallback
    uses the earlier exact inference arithmetic without changing old notebooks,
    source, model banks or submissions. Public score is tied to the confirmed
    file checksum; a new file's public score remains unknown.
    '''),code('''
    import r4_final
    result=t.read(ART/'final_results.json');display(pd.Series(result))
    replay=t.read(ART/'reproduction.json')
    path=ROOT/replay['submission']
    assert path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==result['sha256']
    assert replay['byte_identical']
    print('Saved-model replay byte-identical:',replay)
    sub=pd.read_csv(ROOT/result['submission'])
    assert list(sub)==['SK_ID_CURR','TARGET'] and len(sub)==61500
    assert sub.SK_ID_CURR.equals(pd.read_csv(ROOT/'input/sample_submission.csv').SK_ID_CURR)
    assert np.isfinite(sub.TARGET).all() and sub.TARGET.between(0,1).all()
    display(sub.head())
    '''),code('''
    protected=t.read(t.HERE/'reference/preserved_hashes.json');checked=0
    for name,want in protected.items():
        path=ROOT/name
        if path.exists():assert hashlib.sha256(path.read_bytes()).hexdigest()==want,name;checked+=1
    print('Verified protected files present:',checked)
    if (ART/'error_analysis.csv').exists():display(pd.read_csv(ART/'error_analysis.csv'))
    display(Markdown((ROOT/'IMPROVEMENT_REPORT.md').read_text()))
    '''),md('''
    ## Stopping and remaining uncertainty

    Completing this recorded pass does not exhaust every possible improvement.
    Larger scratch neural searches, fully nested stacking, justified specialists
    and additional interactions remain unproven. Repeated small gains on these
    same labels can reflect selection noise. Read the full journal before
    choosing further work, and compare any public feedback by CSV checksum.
    '''),code('''
    RUN_TRAINING=False
    if RUN_TRAINING:
        import r4_fraction
        cv.main();r4_fraction.feasibility();v.select();v.confirmation();v.averaging()
        r4_final.train_final();r4_final.reproduce()
    RUN_MODEL_REPLAY=False
    if RUN_MODEL_REPLAY:r4_final.reproduce()
    ''')]

def main():
    for name,cells in [('07_round4_experiments.ipynb',experiments()),('08_round4_validation_reproduction.ipynb',validation())]:
        path=t.ROOT/name;assert not path.exists(),'Refuse to change existing notebook '+name
        nb=n.v4.new_notebook(cells=cells,metadata=dict(kernelspec=dict(display_name='Competition local venv',language='python',name='competition-local'),language_info=dict(name='python',version='3.12')))
        n.validate(nb);n.write(nb,path);print('Created',name)
if __name__=='__main__':main()
