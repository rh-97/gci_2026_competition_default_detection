"""Create a new archive; never overwrite any earlier competition archive."""
import hashlib,zipfile
from pathlib import Path
import round4 as t

def main():
    verified=t.read(t.ART/'verification.json');final=t.read(t.ART/'final_results.json')
    assert verified['passed'] and verified['new_notebooks_fully_executed']
    assert verified['recommended_submission_sha256']==final['sha256']
    files=list(t.ROOT.glob('*.ipynb'))
    files += [p for p in t.ROOT.iterdir() if p.is_file() and p.suffix in ['.md','.txt','.xlsx','.json','.yaml','.yml','.csv']]
    excludedparts={'__pycache__','.ipynb_checkpoints','catboost_info','kernels','matplotlib'}
    for p in (t.ROOT/'improvements').rglob('*'):
        if not p.is_file() or excludedparts.intersection(p.parts) or p.suffix in ['.log','.zip','.tmp']:continue
        if p in [t.ART/'package_manifest.json',t.ART/'package_result.json']:continue
        files.append(p)
    files+=list((t.ROOT/'output').glob('*.csv'));files=sorted(set(files))
    manifest={str(p.relative_to(t.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    manifestpath=t.ART/'package_manifest.json';t.dump(manifestpath,manifest);files.append(manifestpath)
    path=t.ROOT/'output/competition_round4_reproduction.zip'
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for p in files:archive.write(p,p.relative_to(t.ROOT))
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip()is None
        for name,want in manifest.items():assert hashlib.sha256(archive.read(name)).hexdigest()==want,name
        assert len(archive.namelist())==len(files) and len(set(archive.namelist()))==len(files)
    result=dict(archive=str(path.relative_to(t.ROOT)),bytes=path.stat().st_size,members=len(files),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),all_member_hashes_checked=True,zip_crc_checked=True,
        excluded='Supplied input directory, project venv, caches/kernels, raw .log files and older ZIP archives.',
        manifest_self_hash_note='Manifest does not contain its own hash; ZIP CRC covers the manifest member.')
    t.dump(t.ART/'package_result.json',result);print(result,flush=True)
if __name__=='__main__':main()
