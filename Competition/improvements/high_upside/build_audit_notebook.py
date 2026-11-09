"""Create a new audit notebook, refusing to change any existing notebook."""
from pathlib import Path
import textwrap
import nbformat as n
ROOT=Path(__file__).resolve().parents[2]
def md(s):return n.v4.new_markdown_cell(textwrap.dedent(s).strip())
def code(s):
    s=textwrap.dedent(s).strip();compile(s,'<notebook>','exec');return n.v4.new_code_cell(s)
def main():
    cells=[md('''
    # Opportunity audit for a substantial improvement

    Current user-confirmed public AUC: **0.76824**. The user reports top-ten scores
    displayed as 1 and top-twenty scores above 0.8, with uncertain methods/data
    provenance. This motivates a competitive target, not a claim that 0.8 is
    achievable from the allowed inputs. This notebook analyzes saved predictions;
    no new model is fitted and no prediction is adjusted.

    All nine pre-existing notebooks remain unchanged. The incremental round-four
    search was stopped after seven completed screens at the user's priority change.
    '''),code('''
    from pathlib import Path
    import sys,json,hashlib
    import numpy as np,pandas as pd
    import matplotlib.pyplot as plt
    from IPython.display import display,Markdown
    ROOT=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'input/train.csv').exists())
    assert Path(sys.prefix).resolve()==(ROOT/'.venv').resolve()
    HERE=ROOT/'improvements/high_upside';ART=HERE/'artifacts'
    summary=json.loads((ART/'audit_summary.json').read_text())
    assert hashlib.sha256((HERE/'opportunity_audit.py').read_bytes()).hexdigest()==summary['source_sha256']
    print('Python:',sys.executable)
    display(summary)
    display(Markdown((HERE/'OPPORTUNITY_AUDIT_PLAN.md').read_text()))
    '''),md('''
    ## Where ranking errors occur

    AUC is the fraction of positive-negative pairs ordered correctly, with half
    credit for ties. Each matrix cell below contributes a fraction of **all**
    positive-negative pairs to `1 - AUC`. Rows identify the positive applicant's
    group; columns identify the negative applicant's group. Cells sum exactly to
    the reference's global loss. Diagonal cells describe errors within groups.
    Off-diagonal cells describe cross-group errors.

    These are error attributions, not achievable improvements. Correcting every
    selected pair independently may not correspond to any consistent score order.
    '''),code('''
    cells=pd.read_csv(ART/'pair_loss_cells.csv',dtype={'positive_group':str,'negative_group':str})
    slices=pd.read_csv(ART/'group_slices.csv',dtype={'value':str})
    components=pd.read_csv(ART/'within_between_loss.csv')
    for name,frame in cells.groupby('group'):
        assert abs(frame.global_auc_loss.sum()-summary['global_pair_loss'])<1e-12,name
    display(components)
    display(slices[slices.group=='EXT_missing_count'])
    display(slices[slices.group=='NAME_CONTRACT_TYPE'])
    '''),code('''
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    group='EXT_missing_count'
    matrix=cells[cells.group==group].pivot(index='positive_group',columns='negative_group',values='global_auc_loss')
    im=axes[0].imshow(matrix.to_numpy(),cmap='YlOrRd',vmin=0)
    for i in range(len(matrix)):
        for j in range(len(matrix.columns)):
            axes[0].text(j,i,f'{matrix.iloc[i,j]:.4f}',ha='center',va='center',fontsize=10,color='white' if matrix.iloc[i,j]>.5*matrix.to_numpy().max() else 'black')
    axes[0].set(xticks=range(len(matrix.columns)),xticklabels=matrix.columns,yticks=range(len(matrix)),yticklabels=matrix.index,
        xlabel='Missing scores: negative applicant',ylabel='Missing scores: positive applicant',title='Contribution to global 1 - AUC')
    fig.colorbar(im,ax=axes[0],fraction=.046)
    frame=slices[slices.group==group].sort_values('value');xx=np.arange(len(frame))
    axes[1].bar(xx-.18,frame.positives/frame.positives.sum(),.36,label='Share of positive applicants')
    axes[1].bar(xx+.18,frame.positive_share_of_total_loss,.36,label='Share of ranking loss, by positives')
    axes[1].set(xticks=xx,xticklabels=frame.value,xlabel='Number of missing external scores',ylabel='Fraction',title='Size versus error contribution')
    axes[1].legend(fontsize=8);fig.tight_layout();fig.savefig(ART/'external_score_pair_loss.png',dpi=140);plt.show()
    '''),md('''
    ## Interpretation without a subgroup selection trap

    The two-missing-score group has lower within-group AUC, but its share of
    positive-centered global ranking loss is below its share of positive cases.
    Its weaker within-group AUC alone does not establish that a specialist is the
    best use of compute. Most cash-loan errors occur within a large population;
    this is not evidence of a single small broken segment. Large groups' mean
    calibration residuals are small. A global calibration adjustment is unlikely
    to explain a large ranking jump.
    '''),code('''
    display(slices[(~slices['sparse'])&(slices.group.isin(['NAME_INCOME_TYPE','NAME_EDUCATION_TYPE','age_band']))])
    display(pd.Series(summary['saved_capacity_diagnostic']))
    '''),md('''
    ## Capacity and generalization

    One saved CatBoost model has about 0.814 AUC on a deterministic sample of its
    own training rows and 0.765 on its held-out rows. The in-sample number is
    optimistic and is not a submission-quality estimate. This illustrates a
    generalization gap, not the dataset's maximum attainable AUC. It gives little
    justification for merely increasing depth without a better representation,
    inductive bias or regularization strategy.

    ## Next hypotheses

    Prioritize a scratch-trained TabM model with numerical embeddings and explicit
    missingness; compare raw and the successful engineered representations. Test
    selected fold-safe learned borrower/profile interactions alongside the same
    reference tree learner, with a small declared pilot budget. Missing-score
    reconstruction must first show out-of-fold auxiliary predictive quality and
    downstream benefit; observed-score masking may not represent true missingness.
    Specialists/retrieval and nested stacking remain conditional on measurable
    signal and error complementarity. No larger seed bank is justified yet.

    A substantial branch targets at least 0.002 OOF improvement before expensive
    expansion. This is a compute-allocation target, not a promised score. All
    confirmation remains on previously explored labels and must be labeled so.
    '''),code('''
    protected=json.loads((ROOT/'improvements/round4/reference/preserved_hashes.json').read_text());checked=0
    for name,want in protected.items():
        path=ROOT/name
        if path.exists():
            assert hashlib.sha256(path.read_bytes()).hexdigest()==want,name
            checked+=1
    print('Unchanged protected files present:',checked)
    display(Markdown((ROOT/'HIGH_UPSIDE_PLAN.md').read_text()))
    '''),code('''
    RUN_AUDIT=False
    if RUN_AUDIT:
        sys.path.insert(0,str(HERE))
        import opportunity_audit
        opportunity_audit.run()
    ''')]
    path=ROOT/'07_signal_opportunity_audit.ipynb';assert not path.exists(),'Refuse to modify an existing notebook'
    nb=n.v4.new_notebook(cells=cells,metadata=dict(kernelspec=dict(display_name='Competition local venv',language='python',name='competition-local'),language_info=dict(name='python',version='3.12')))
    n.validate(nb);n.write(nb,path);print('Created',path)
if __name__=='__main__':main()
