"""Verify meaningful data, feature, freeze, notebook and artifact invariants."""
import argparse,hashlib,sys
from pathlib import Path
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
import nbformat
import round3 as t

def main(final=False):
    assert Path(sys.prefix).resolve()==(t.ROOT/'.venv').resolve()
    hashes=t.read(t.HERE/'reference/preserved_hashes.json');checked=0;omitted=[]
    for name,expected in hashes.items():
        path=t.ROOT/name
        # Previous ZIPs and supplied CSVs are intentionally omitted from a code
        # archive; when present in the working project they are always checked.
        if not path.exists() and (name.startswith('input/') or name.endswith('.zip')):
            omitted.append(name);continue
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,name+' changed';checked+=1
    for name,expected in t.read(t.HERE/'reference/validation_reference_hashes.json').items():
        assert hashlib.sha256((t.ROOT/name).read_bytes()).hexdigest()==expected,name+' changed'
    train,test,y,split=t.load();a=train.iloc[:100].copy();changed=a.copy();changed.TARGET=1-changed.TARGET;changed.SK_ID_CURR+=99999999
    assert set(split['development']).isdisjoint(split['audit'])
    assert set(split['inner_fit']).isdisjoint(split['inner_valid'])
    assert set(split['inner_fit'])|set(split['inner_valid'])==set(split['development'])
    for mode in ['proxy','signed','rates','crosses','engineered_proxy']:
        x=t.features(a,mode);assert 'TARGET'not in x and 'SK_ID_CURR'not in x
        assert_frame_equal(x,t.features(changed,mode));assert_frame_equal(x.iloc[[0]],t.features(a.iloc[[0]],mode))
        assert list(x)==list(t.features(test.iloc[:3],mode))
    x=t.features(a,'rates');payment=(x.AMT_ANNUITY/x.AMT_CREDIT).to_numpy()
    for n in [12,18,24,36,48,60,72,84]:
        rates=x[f'ASSUMED_PERIOD_RATE_{n}'].to_numpy();valid=np.isfinite(rates)
        assert np.max(np.abs(rates[valid]/(-np.expm1(-n*np.log1p(rates[valid])))-payment[valid]))<1e-7
    enc=t.NeuralEncoder().fit(x);unseen=x.iloc[[0]].copy();unseen['ORGANIZATION_TYPE']='__UNSEEN_CHECK__'
    z=enc.transform(unseen);assert np.isfinite(z).all()
    for missing in ['sentinel','native','median']:
        tree_enc=t.r.Encoder('cat',groups=True,missing=missing).fit(x)
        assert_frame_equal(tree_enc.transform(x).iloc[[0]],tree_enc.transform(x.iloc[[0]]))
    neural_batch=enc.transform(x)
    np.testing.assert_allclose(neural_batch[[0]],enc.transform(x.iloc[[0]]),rtol=0,atol=0)
    checks=dict(final=final,local_venv=True,protected_files_checked=checked,protected_hashes_match=True,
        omitted_from_code_archive=omitted,splits_disjoint=True,features_ignore_target_ID=True,row_batch_invariance=True,
        train_test_schema_matches=True,hypothetical_rate_formula_verified=True,neural_unseen_categories_finite=True)
    checks['fitted_encoder_batch_invariance']=True
    for row in t.screen_rows():assert t.signature_matches(row['implementation_hash'],t.implementation_hash()),row['name']
    checks['screening_signatures_verified_with_documented_metadata_alias']=True
    if final:
        freeze=t.read(t.ART/'selection_freeze.json')
        assert hashlib.sha256((t.ART/'selection.json').read_bytes()).hexdigest()==freeze['selection_sha256']
        assert hashlib.sha256((t.ART/'primary_cdf_references.npz').read_bytes()).hexdigest()==freeze['cdf_sha256']
        assert t.implementation_hash()==freeze['implementation_hash']
        for name,want in freeze.get('source_hashes',{}).items():assert hashlib.sha256((t.HERE/name).read_bytes()).hexdigest()==want,name
        result=t.read(t.ART/'final_results.json');csv=t.ROOT/result['submission']
        checks['recommended_submission_sha256']=result['sha256']
        assert hashlib.sha256(csv.read_bytes()).hexdigest()==result['sha256']
        sub=pd.read_csv(csv);sample=pd.read_csv(t.ROOT/'input/sample_submission.csv')
        assert list(sub)==['SK_ID_CURR','TARGET'] and len(sub)==len(sample)==61500
        assert sub.SK_ID_CURR.equals(sample.SK_ID_CURR) and sub.SK_ID_CURR.is_unique
        assert np.isfinite(sub.TARGET).all() and sub.TARGET.between(0,1).all()
        if result['accepted']:
            assert csv.read_bytes()==(t.ROOT/'output/submission_round3_reproduced.csv').read_bytes()
            assert t.read(t.ART/'confirmation_results.json')['passed'] and t.read(t.ART/'averaging_results.json')['passed']
        bagpath=t.ART/'bagging_final_results.json'
        if bagpath.exists() and t.read(bagpath).get('accepted'):
            bag=t.read(bagpath);file=t.ROOT/bag['submission']
            assert hashlib.sha256(file.read_bytes()).hexdigest()==bag['sha256']
            assert file.read_bytes()==(t.ROOT/'output/submission_round3_bagged_reproduced.csv').read_bytes()
            assert t.read(t.ART/'bagging_probe.json')['passed']
            for name,want in t.read(t.ART/'bagging_freeze.json').items():assert hashlib.sha256((t.HERE/name).read_bytes()).hexdigest()==want,name
            scores=pd.read_csv(file)
            assert scores.SK_ID_CURR.equals(sample.SK_ID_CURR) and np.isfinite(scores.TARGET).all() and scores.TARGET.between(0,1).all()
            checks['three_seed_extension_freeze_and_reproduction_verified']=True
            checks['recommended_submission_sha256']=bag['sha256']
        for name in ['05_round3_hypotheses_and_experiments.ipynb','06_round3_validation_and_reproduction.ipynb']:
            nb=nbformat.read(t.ROOT/name,as_version=4);nbformat.validate(nb)
            executed=t.read(t.ART/'executed_notebook_hashes.json')[name]
            assert hashlib.sha256((t.ROOT/name).read_bytes()).hexdigest()==executed['sha256'],name+' changed after execution'
            assert hashlib.sha256('\n\0\n'.join(c.source for c in nb.cells if c.cell_type=='code').encode()).hexdigest()==executed['code_sha256']
            for cell in nb.cells:
                if cell.cell_type=='code':
                    assert cell.execution_count is not None,(name,'unexecuted cell')
                    assert all(o.output_type!='error' for o in cell.outputs),(name,'cell error')
        checks.update(selection_and_source_freeze_intact=True,submission_schema_and_order_valid=True,
            saved_model_reproduction_verified=True,new_notebooks_fully_executed=True)
    t.dump(t.ART/'verification.json',checks);print(checks)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--final',action='store_true');a=parser.parse_args();main(a.final)
