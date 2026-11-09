"""Create a new results notebook after the frozen modeling pipeline completes."""
from pathlib import Path
import textwrap
import nbformat as n
ROOT=Path(__file__).resolve().parents[2]
def md(s):return n.v4.new_markdown_cell(textwrap.dedent(s).strip())
def code(s):
    s=textwrap.dedent(s).strip();compile(s,'<notebook>','exec');return n.v4.new_code_cell(s)
def main():
    path=ROOT/'09_high_upside_results_reproduction.ipynb';assert not path.exists(),'Refuse to rewrite an existing notebook'
    assert (ROOT/'improvements/high_upside/artifacts/model_final_results.json').exists()
    cells=[md('''
    # Higher-upside models: results, decisions and reproduction

    This notebook reviews six structural pilots: four scratch TabM recipes and
    two learned-feature CatBoost recipes. The previous submitted file has confirmed
    public AUC **0.76824**. The target **0.8+** is aspirational; another entrant's
    score does not establish what these allowed inputs can achieve. No external
    data, recovered labels or pretrained weights are used.

    All ten notebooks that preceded this modeling phase are unchanged. Notebook
    08 recorded the procedure before these pilots. All trial evidence, including
    failures and negative results, is retained.
    '''),code('''
    from pathlib import Path
    import sys,json,hashlib,subprocess
    import numpy as np,pandas as pd
    import matplotlib.pyplot as plt
    from IPython.display import display,Markdown
    ROOT=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'input/train.csv').exists())
    assert Path(sys.prefix).resolve()==(ROOT/'.venv').resolve()
    HERE=ROOT/'improvements/high_upside';ART=HERE/'artifacts'
    read=lambda p:json.loads(p.read_text())
    records=read(ART/'model_experiment_ledger.json')
    final=read(ART/'model_final_results.json')
    print('Python:',sys.executable)
    display(pd.Series(final))
    display(Markdown((HERE/'MODELING_PLAN.md').read_text()))
    display(Markdown((HERE/'ACCELERATOR_AMENDMENT.md').read_text()))
    display(Markdown((HERE/'COMPLEXITY_POLICY.md').read_text()))
    display(read(ART/'model_preflight.json'))
    '''),md('''
    ## Standalone strength and ensemble contribution

    Every pilot uses the same explored inner split and the complete reference
    mixture. Its five blend probes are saved, including pure new-model weight 1.
    A weaker standalone model can contribute complementary ranking errors. A
    small screen gain still needs common-fold CV and fixed-weight confirmation.
    Software probes do not count as competitive configurations.
    '''),code('''
    rows=pd.DataFrame([dict(name=a['name'],kind=a['kind'],auc=a['auc'],blend_gain=a['delta'],
        retained_count=a['count'],seconds=a['seconds'],status=a['status'],promoted=a['promoted']) for a in records])
    display(rows.sort_values('blend_gain',ascending=False))
    valid=rows[rows.status=='complete'].sort_values('blend_gain')
    if len(valid):
        fig,ax=plt.subplots(figsize=(11,4.5));ax.barh(valid['name'],valid['blend_gain'])
        ax.axvline(0,color='gray',linewidth=.8);ax.axvline(.0003,color='#b56336',linestyle='--',label='Screen promotion threshold')
        ax.set_xlabel('Best screened blend AUC gain over the complete reference')
        ax.legend();fig.tight_layout();fig.savefig(ART/'model_screen_gains.png',dpi=140);plt.show()
    '''),code('''
    fig,ax=plt.subplots(figsize=(10,5));drawn=False
    for a in records:
        if a['kind']!='tabm' or a['status']!='complete':continue
        curve=read(ART/'pilots'/(a['name']+'_curve.json'))
        ax.plot([r['epoch'] for r in curve],[r['validation_auc'] for r in curve],label=a['name'])
        drawn=True
    if drawn:
        reference=next(a['reference_auc'] for a in records if a['status']=='complete')
        ax.axhline(reference,color='black',linestyle='--',label='Complete reference, inner split')
        ax.set(xlabel='Completed epoch',ylabel='Inner validation AUC',title='Scratch neural learning curves')
        ax.legend(fontsize=8);fig.tight_layout();fig.savefig(ART/'model_neural_curves.png',dpi=140);plt.show()
    else:plt.close(fig)
    '''),md('''
    ## Why each experiment was retained or rejected

    Auxiliary reconstruction R2 is evaluated on observed external scores; it does
    not measure ranking gains or guarantee quality on genuinely missing scores.
    Interaction-risk maps use inner OOF targets for training features and full
    outer-training maps for validation/test features. Each outer validation label
    is excluded from every transformation and fit. Time-capped neural fits are
    explicitly distinguished from converged negative results.
    '''),code('''
    for a in records:
        display(Markdown('### '+a['name']+'\\n\\n'+a['hypothesis']+'\\n\\n'+a['interpretation']))
        display(a['spec']);display(a['diagnostics'])
        if a['cv']:display({k:v for k,v in a['cv'].items() if k not in ['spec','signature']})
    display(read(ART/'model_promotion.json'))
    '''),md('''
    ## Frozen selection, confirmation and matching seed count

    The pair/helper grid, selection source, weights and median epochs/trees were
    fixed before new confirmation fits. Confirmation uses fixed counts and no
    validation early stopping. Matching three-seed validation averages each
    family before the frozen combination method. These are robustness checks on
    previously explored labels, not untouched independent tests. Failed gates
    stop deployment and retain the current submission.
    '''),code('''
    freeze=read(ART/'model_selection_freeze.json')
    for name,want in freeze['hashes'].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==want,name
    choice=read(ART/'model_selection.json');confirm=read(ART/'model_confirmation.json');average=read(ART/'model_averaging.json')
    display(pd.Series(choice));display(pd.Series(confirm));display(pd.Series(average))
    display(pd.DataFrame(read(ART/'model_blend_grid.json')).head(15))
    if 'fold_gains'in confirm:
        fig,ax=plt.subplots(figsize=(9,4));xx=np.arange(1,6)
        ax.bar(xx-.18,choice['fold_gains'],.36,label='Primary selection')
        ax.bar(xx+.18,confirm['fold_gains'],.36,label='New partition, fixed count')
        ax.axhline(0,color='gray',linewidth=.8);ax.set(xlabel='Group within each partition',ylabel='AUC gain over the complete reference')
        ax.legend();fig.tight_layout();fig.savefig(ART/'model_fold_gains.png',dpi=140);plt.show()
    '''),md('''
    ## Recommended CSV and saved-model replay

    A newly accepted file is replayed below through the same project-venv CLI
    that sets one OpenMP runtime. No duplicate-runtime checks are disabled. A
    retained reference is checked against its preserved checksum and prior exact
    replay evidence. A model's own training AUC and this notebook's local scores
    are not public scores. Full-data OOF never retunes the chosen recipe.
    '''),code('''
    if final['accepted']:
        subprocess.run([sys.executable,str(HERE/'h_launch.py'),'reproduce'],check=True,cwd=ROOT)
    replay=read(ART/'model_reproduction.json');assert replay['byte_identical']
    path=ROOT/final['submission'];assert hashlib.sha256(path.read_bytes()).hexdigest()==final['sha256']==replay['sha256']
    sub=pd.read_csv(path);sample=pd.read_csv(ROOT/'input/sample_submission.csv');test=pd.read_csv(ROOT/'input/test.csv')
    assert list(sub)==['SK_ID_CURR','TARGET'] and len(sub)==61500
    assert sub.SK_ID_CURR.equals(sample.SK_ID_CURR) and sub.SK_ID_CURR.equals(test.SK_ID_CURR)
    assert sub.SK_ID_CURR.is_unique and np.isfinite(sub.TARGET).all() and sub.TARGET.between(0,1).all()
    print('Recommended CSV:',final['submission']);display(replay);display(sub.head())
    protected=read(HERE/'reference/modeling_preserved_hashes.json');checked=0
    for name,want in protected.items():
        path=ROOT/name
        if path.exists():
            assert hashlib.sha256(path.read_bytes()).hexdigest()==want,name
            checked+=1
    print('Unchanged protected files present:',checked)
    '''),md('''
    ## Deliberate rerun

    Saved evidence is displayed by default. Training below is opt-in and matching
    exact signatures reuse caches. The current journal describes all negatives,
    operations and limitations. The next research direction must earn its cost;
    finishing these recipes does not prove all possible improvements exhausted.
    '''),code('''
    RUN_MODEL_PIPELINE=False
    if RUN_MODEL_PIPELINE:
        subprocess.run([sys.executable,str(HERE/'h_launch.py'),'run'],check=True,cwd=ROOT)
    display(Markdown((ROOT/'HIGH_UPSIDE_EXPERIMENT_LOG.md').read_text()))
    ''')]
    nb=n.v4.new_notebook(cells=cells,metadata=dict(kernelspec=dict(display_name='Competition local venv',language='python',name='competition-local'),language_info=dict(name='python',version='3.12')))
    n.validate(nb);n.write(nb,path);print('Created',path)
if __name__=='__main__':main()
