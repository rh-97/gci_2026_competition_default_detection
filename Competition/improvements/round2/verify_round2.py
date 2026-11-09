"""Verify immutable inputs, mathematical features and final reproduction."""
import argparse,hashlib
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
import nbformat
import round2 as r

def verify(final=False):
    preserved=r.read(r.HERE/'reference/preserved_file_hashes.json')
    for name,expected in preserved.items():
        assert hashlib.sha256((r.ROOT/name).read_bytes()).hexdigest()==expected,name+' changed'
    train,test,y,split=r.load()
    assert set(split['development']).isdisjoint(split['audit'])
    assert set(split['inner_fit']).isdisjoint(split['inner_valid'])
    assert set(split['inner_fit'])|set(split['inner_valid'])==set(split['development'])
    assert set(split['development'])|set(split['audit'])==set(range(len(train)))
    assert list(train.drop(columns='TARGET').columns)==list(test.columns)
    assert not set(train.SK_ID_CURR)&set(test.SK_ID_CURR)
    a=train.iloc[:100].copy();changed=a.copy();changed.TARGET=1-changed.TARGET;changed.SK_ID_CURR+=10000000
    for mode in ['raw','lean','engineered','risk','finance','missing','combined']:
        x=r.features(a,mode)
        assert 'SK_ID_CURR'not in x and 'TARGET'not in x
        assert_frame_equal(x,r.features(changed,mode))
        assert_frame_equal(x.iloc[[0]],r.features(a.iloc[[0]],mode))
        assert list(r.features(test.iloc[:3],mode).columns)==list(x.columns)
    # The geometric/harmonic definitions use strictly positive observed scores.
    for c in ['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3']:
        assert train[c].dropna().gt(0).all() and test[c].dropna().gt(0).all(),c
    x=r.features(a,'finance')
    payment=(x.AMT_ANNUITY/x.AMT_CREDIT).to_numpy()
    for n in [24,36,60]:
        rates=x[f'ASSUMED_PERIOD_RATE_{n}'].to_numpy();valid=np.isfinite(rates)
        reconstructed=rates[valid]/(-np.expm1(-n*np.log1p(rates[valid])))
        assert np.max(np.abs(reconstructed-payment[valid]))<1e-7
    native=r.Encoder('cat',missing='native').fit(x)
    z=native.transform(x)
    assert z.EXT_SOURCE_1.isna().equals(x.EXT_SOURCE_1.isna())
    unseen=x.iloc[[0]].copy();unseen['ORGANIZATION_TYPE']='__UNSEEN_FOR_CHECK__'
    assert native.transform(unseen).ORGANIZATION_TYPE.iloc[0]=='__UNSEEN_FOR_CHECK__'
    numeric=r.Encoder('xgb').fit(x)
    assert numeric.transform(unseen).ORGANIZATION_TYPE.isna().all()
    checks=dict(preserved_files=len(preserved),all_preserved_hashes_match=True,splits_disjoint=True,
        features_ignore_ID_and_TARGET=True,row_batch_invariance=True,train_test_feature_schema_matches=True,
        hypothetical_rate_formula_verified=True,observed_scores_strictly_positive=True,unseen_categories_handled=True,
        numeric_native_missing_preserved=True,final=final)
    if final:
        frozen=r.read(r.ART/'selection_freeze.json')
        assert frozen['selection_sha256']==hashlib.sha256((r.ART/'selection.json').read_bytes()).hexdigest()
        assert frozen['implementation_hash']==r.implementation_hash()
        result=r.read(r.ART/'final_results.json');csv=r.ROOT/result['submission']
        assert hashlib.sha256(csv.read_bytes()).hexdigest()==result['sha256']
        assert csv.read_bytes()==(r.ROOT/'output/submission_round2_reproduced.csv').read_bytes()
        sub=pd.read_csv(csv);sample=pd.read_csv(r.ROOT/'input/sample_submission.csv')
        assert sub.columns.tolist()==['SK_ID_CURR','TARGET'] and len(sub)==61500
        assert sub.SK_ID_CURR.equals(sample.SK_ID_CURR) and sub.SK_ID_CURR.is_unique
        assert np.isfinite(sub.TARGET).all() and sub.TARGET.between(0,1).all()
        manifest=r.read(r.ART/'model_manifest.json')
        assert np.isclose(sum(f['weight'] for f in manifest['families']),1.)
        for f in manifest['families']:
            assert f['weight']>=0
            for seed in f['seeds']:
                assert len(seed['instances'])==5
                for item in seed['instances']:
                    assert (r.ROOT/item['model']).exists() and (r.ROOT/item['encoder']).exists()
        for name in ['03_round2_experiment_journal.ipynb','04_round2_validation_and_submission.ipynb']:
            nb=nbformat.read(r.ROOT/name,as_version=4);nbformat.validate(nb)
            for cell in nb.cells:
                if cell.cell_type=='code':
                    assert cell.execution_count is not None,(name,'unexecuted code')
                    assert all(o.output_type!='error' for o in cell.outputs),(name,'execution error')
        checks.update(selection_unchanged_after_freeze=True,submission_format_valid=True,
            saved_model_reproduction_byte_identical=True,new_notebooks_fully_executed=True)
    r.dump(r.ART/'verification.json',checks);print(checks)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');a=p.parse_args();verify(a.final)
