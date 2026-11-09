"""Verify immutable old artifacts, frozen decisions and new notebook execution."""
import argparse,hashlib,sys
import nbformat
import numpy as np
import pandas as pd
import round4 as t
import r4_validate as v
import r4_final as f

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--allow-package-omissions',action='store_true');args=parser.parse_args()
    assert __import__('pathlib').Path(sys.prefix).resolve()==(t.ROOT/'.venv').resolve()
    checked=[];omitted=[]
    for name,want in t.read(t.HERE/'reference/preserved_hashes.json').items():
        path=t.ROOT/name
        if not path.exists():
            assert args.allow_package_omissions and (name.startswith('input/') or name.endswith('.zip')),name
            omitted.append(name);continue
        assert v.sha(path)==want,name;checked.append(name)
    assert len([s for s in checked if s.endswith('.ipynb')])==9
    v.check_freeze();final=t.read(t.ART/'final_results.json');replay=t.read(t.ART/'reproduction.json')
    assert replay['byte_identical'] and replay['sha256']==final['sha256']
    assert v.sha(t.ROOT/replay['submission'])==v.sha(t.ROOT/final['submission'])==final['sha256']
    sub=pd.read_csv(t.ROOT/final['submission']);sample=pd.read_csv(t.ROOT/'input/sample_submission.csv');test=pd.read_csv(t.ROOT/'input/test.csv')
    assert list(sub)==['SK_ID_CURR','TARGET'] and len(sub)==61500
    assert sub.SK_ID_CURR.equals(sample.SK_ID_CURR) and sub.SK_ID_CURR.equals(test.SK_ID_CURR) and sub.SK_ID_CURR.is_unique
    assert np.isfinite(sub.TARGET).all() and sub.TARGET.between(0,1).all()
    execution=t.read(t.ART/'executed_notebook_hashes.json')
    for name in ['07_round4_experiments.ipynb','08_round4_validation_reproduction.ipynb']:
        assert v.sha(t.ROOT/name)==execution[name]['sha256'];nb=nbformat.read(t.ROOT/name,as_version=4);nbformat.validate(nb)
        assert hashlib.sha256('\n\0\n'.join(c.source for c in nb.cells if c.cell_type=='code').encode()).hexdigest()==execution[name]['code_sha256']
        assert all(c.execution_count is not None and all(o.output_type!='error' for o in c.outputs) for c in nb.cells if c.cell_type=='code')
    if final['accepted']:
        assert t.read(t.ART/'confirmation_results.json')['passed'] and t.read(t.ART/'averaging_results.json')['passed']
        families=t.read(t.ART/'model_manifest.json')['families']
    else:families=list(f.previous_bank().values())
    files={}
    for family in families:
        for seed in family['seeds']:
            for instance in seed['instances']:
                for key in ['model','encoder']:
                    path=t.ROOT/instance[key];assert path.is_file();files[instance[key]]=v.sha(path)
    t.dump(t.ART/'inference_file_hashes.json',files)
    result=dict(passed=True,protected_files_checked=len(checked),protected_files_omitted=omitted,old_notebooks_unchanged=9,
        new_notebooks_fully_executed=True,inference_files_checked=len(files),recommended_submission=final['submission'],
        recommended_submission_sha256=final['sha256'],byte_identical_saved_model_replay=True,selection_freeze_checked=True,local_venv=sys.executable)
    t.dump(t.ART/'verification.json',result);print(result,flush=True)
if __name__=='__main__':main()
