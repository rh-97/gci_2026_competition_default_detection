"""Artifact, leakage-boundary, notebook and submission integrity checks."""
from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd
import nbformat
from pandas.testing import assert_frame_equal
import experiment as e

def verify(final=False):
    originals=e.load_json('original_file_hashes.json')
    for name,expected in originals.items():
        assert hashlib.sha256((e.ROOT/name).read_bytes()).hexdigest()==expected, name+' changed'
    train,test,y,dev,audit,fit,valid=e.load()
    assert not set(dev)&set(audit)
    assert not set(fit)&set(valid)
    assert set(fit)|set(valid)==set(dev)
    assert set(dev)|set(audit)==set(range(len(train)))
    # Feature construction never depends on IDs, labels, or other batch rows.
    a=train.iloc[:30].copy(); changed=a.copy()
    changed['TARGET']=1-changed.TARGET; changed['SK_ID_CURR']+=10000000
    for mode in ['raw','engineered','extended','lean','scores']:
        assert_frame_equal(e.features(a,mode),e.features(changed,mode))
        assert_frame_equal(e.features(a,mode).iloc[[0]],e.features(a.iloc[[0]],mode))
    x=e.features(a,'engineered')
    enc=e.Encoder('lgb',groups=True).fit(x)
    # Unseen categories are missing for LightGBM; no fitting on validation rows.
    held=x.iloc[[0]].copy(); held['ORGANIZATION_TYPE']='NEVER_SEEN'
    transformed=enc.transform(held)
    assert transformed.ORGANIZATION_TYPE.isna().all()
    assert transformed.ORGANIZATION_TYPE_FREQ.isna().all()
    assert 'TARGET' not in transformed and 'SK_ID_CURR' not in transformed
    if final:
        frozen=e.load_json('selection_freeze.json')
        assert hashlib.sha256((e.ART/'selection.json').read_bytes()).hexdigest()==frozen['sha256']
        assert e.load_json('audit_results.json')['selection']==e.load_json('selection.json')
        a=train.drop(columns=['SK_ID_CURR','TARGET']); b=test.drop(columns='SK_ID_CURR')
        assert not a.duplicated().any() and not b.duplicated().any()
        assert not set(pd.util.hash_pandas_object(a,index=False)) & set(pd.util.hash_pandas_object(b,index=False))
        expected=e.load_json('final_results.json')
        sub=pd.read_csv(e.ROOT/'output/submission_improved.csv')
        sample=pd.read_csv(e.ROOT/'input/sample_submission.csv')
        assert sub.columns.tolist()==sample.columns.tolist()
        assert len(sub)==len(test)==61500 and sub.SK_ID_CURR.equals(sample.SK_ID_CURR)
        assert sub.SK_ID_CURR.equals(test.SK_ID_CURR) and sub.SK_ID_CURR.is_unique
        assert sub.TARGET.between(0,1).all() and np.isfinite(sub.TARGET).all()
        assert hashlib.sha256((e.ROOT/'output/submission_improved.csv').read_bytes()).hexdigest()==expected['sha256']
        assert (e.ROOT/'output/submission_improved.csv').read_bytes()==(e.ROOT/'output/submission_reproduced.csv').read_bytes()
        for name in ['01_competition_data_audit.ipynb','02_improved_models_and_submission.ipynb']:
            nb=nbformat.read(e.ROOT/name,as_version=4); nbformat.validate(nb)
            for cell in nb.cells:
                if cell.cell_type=='code':
                    assert cell.execution_count is not None, (name,'unexecuted cell')
                    assert all(o.output_type!='error' for o in cell.outputs), (name,'error output')
    result={'original_files_unchanged':True,'splits_disjoint':True,'no_ID_or_target_in_features':True,
            'row_feature_batch_invariance':True,'unseen_categories_handled':True,'final_checks':final}
    e.save_json('verification.json',result)
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    import sys
    verify('--final' in sys.argv)
