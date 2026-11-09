"""Verify completed work and create a new hash/CRC-checked reproduction archive."""
from pathlib import Path
import sys,json,hashlib,argparse,zipfile
import nbformat
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'round4'))
import round4 as t
import r4_final as old
HERE=Path(__file__).resolve().parent;ART=HERE/'artifacts'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def verify():
    assert Path(sys.prefix).resolve()==(t.ROOT/'.venv').resolve()
    protected=t.read(HERE/'reference/modeling_preserved_hashes.json')
    for name,want in protected.items():assert sha(t.ROOT/name)==want,name
    environment=t.read(ART/'model_environment.json')
    for name,want in environment['identity']['sources'].items():assert sha(HERE/name)==want,name
    freeze=t.read(ART/'model_selection_freeze.json')
    for name,want in freeze['hashes'].items():assert sha(HERE/name)==want,name
    assert freeze['engine']==environment['signature']
    execution=t.read(ART/'model_executed_notebooks.json')
    for name in ['08_high_upside_modeling_plan.ipynb','08b_local_gpu_amendment.ipynb','08c_compute_budget_policy.ipynb','09_high_upside_results_reproduction.ipynb']:
        assert sha(t.ROOT/name)==execution[name]['sha256'];nb=nbformat.read(t.ROOT/name,as_version=4);nbformat.validate(nb)
        assert hashlib.sha256('\n\0\n'.join(c.source for c in nb.cells if c.cell_type=='code').encode()).hexdigest()==execution[name]['code_sha256']
        assert all(c.execution_count is not None and all(o.output_type!='error' for o in c.outputs) for c in nb.cells if c.cell_type=='code')
    final=t.read(ART/'model_final_results.json');replay=t.read(ART/'model_reproduction.json')
    assert sha(t.ROOT/final['submission'])==final['sha256']==replay['sha256'] and replay['byte_identical']
    sub=pd.read_csv(t.ROOT/final['submission']);sample=pd.read_csv(t.ROOT/'input/sample_submission.csv');test=pd.read_csv(t.ROOT/'input/test.csv')
    assert list(sub)==['SK_ID_CURR','TARGET'] and len(sub)==61500
    assert sub.SK_ID_CURR.equals(sample.SK_ID_CURR) and sub.SK_ID_CURR.equals(test.SK_ID_CURR) and sub.SK_ID_CURR.is_unique
    assert np.isfinite(sub.TARGET).all() and sub.TARGET.between(0,1).all()
    inference={}
    if final['accepted']:
        assert t.read(ART/'model_confirmation.json')['passed'] and t.read(ART/'model_averaging.json')['passed']
        assert replay['saved_model_replay'] and sha(t.ROOT/replay['path'])==final['sha256']
        manifest=t.read(ART/'model_manifest.json')
        for family in manifest['families']:
            for seed in family['seeds']:
                for instance in seed['instances']:inference[instance['model']]=sha(t.ROOT/instance['model'])
        need_old='round3_reference'in manifest['recipe']['names']
    else:need_old=True
    if need_old:
        for family in old.previous_bank().values():
            for seed in family['seeds']:
                for instance in seed['instances']:
                    for key in ['model','encoder']:inference[instance[key]]=sha(t.ROOT/instance[key])
    t.dump(ART/'model_inference_hashes.json',inference)
    result=dict(passed=True,protected_files_unchanged=len(protected),old_notebooks_unchanged=sum(name.endswith('.ipynb') for name in protected),
        new_plan_result_notebooks_executed=True,submission=final['submission'],sha256=final['sha256'],accepted_new_submission=final['accepted'],
        new_submission_saved_model_replay=bool(final['accepted'] and replay.get('saved_model_replay')),
        reference_checksum_preserved=sha(t.ROOT/'output/submission_round3_bagged.csv')==protected['output/submission_round3_bagged.csv'],
        fallback_to_reference=not final['accepted'],
        inference_files_checked=len(inference),source_selection_freezes_checked=True,local_venv=sys.executable)
    t.dump(ART/'model_verification.json',result);print('VERIFIED',result,flush=True)

def package():
    verification=t.read(ART/'model_verification.json');assert verification['passed'];final=t.read(ART/'model_final_results.json');assert verification['sha256']==final['sha256']
    files=list(t.ROOT.glob('*.ipynb'))
    files += [p for p in t.ROOT.iterdir() if p.is_file() and p.suffix in ['.md','.txt','.xlsx','.json','.yaml','.yml','.csv']]
    exclude={'__pycache__','.ipynb_checkpoints','catboost_info','kernels','model_kernels','matplotlib'}
    for p in (t.ROOT/'improvements').rglob('*'):
        if not p.is_file() or exclude.intersection(p.parts) or p.suffix in ['.log','.zip','.tmp']:continue
        if p in [ART/'model_package_manifest.json',ART/'model_package_result.json']:continue
        files.append(p)
    files+=list((t.ROOT/'output').glob('*.csv'));files=sorted(set(files))
    manifest={str(p.relative_to(t.ROOT)):sha(p) for p in files};manifestpath=ART/'model_package_manifest.json';t.dump(manifestpath,manifest);files.append(manifestpath)
    path=t.ROOT/'output/competition_high_upside_reproduction.zip'
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for p in files:archive.write(p,p.relative_to(t.ROOT))
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip()is None
        assert len(archive.namelist())==len(files)==len(set(archive.namelist()))
        for name,want in manifest.items():assert hashlib.sha256(archive.read(name)).hexdigest()==want,name
    result=dict(archive=str(path.relative_to(t.ROOT)),bytes=path.stat().st_size,members=len(files),sha256=sha(path),
        all_member_sha256_checked=True,zip_crc_checked=True,manifest_self_hash='Excluded from its own manifest; covered by ZIP CRC.',
        excluded='Supplied input directory, venv, kernel/cache folders, raw .log files and earlier ZIPs.')
    t.dump(ART/'model_package_result.json',result);print('PACKAGED',result,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['verify','package']);a=p.parse_args();globals()[a.phase]()
