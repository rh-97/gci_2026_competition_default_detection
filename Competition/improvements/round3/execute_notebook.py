"""Execute only the new third-pass notebooks in the project-local venv kernel."""
import sys,json,hashlib
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
ROOT=Path(__file__).resolve().parents[2]
assert Path(sys.prefix).resolve()==(ROOT/'.venv').resolve()
name=sys.argv[1]
assert name in ['05_round3_hypotheses_and_experiments.ipynb','06_round3_validation_and_reproduction.ipynb']
kernelroot=ROOT/'improvements/round3/artifacts/kernels';kernel=kernelroot/'competition-local';kernel.mkdir(parents=True,exist_ok=True)
(kernel/'kernel.json').write_text(json.dumps(dict(argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
    display_name='Competition local venv',language='python',env=dict(OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',MPLCONFIGDIR=str(ROOT/'improvements/round3/artifacts/matplotlib')))))
nb=nbformat.read(ROOT/name,as_version=4)
km=KernelManager(kernel_name='competition-local',kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernelroot)]))
try:NotebookClient(nb,km=km,timeout=1800,resources=dict(metadata=dict(path=str(ROOT)))).execute()
finally:nbformat.write(nb,ROOT/name)
recordfile=ROOT/'improvements/round3/artifacts/executed_notebook_hashes.json'
records=json.loads(recordfile.read_text()) if recordfile.exists() else {}
records[name]=dict(sha256=hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),
    code_sha256=hashlib.sha256('\n\0\n'.join(c.source for c in nb.cells if c.cell_type=='code').encode()).hexdigest(),
    executable=sys.executable)
recordfile.write_text(json.dumps(records,indent=2))
print('Executed',name)
