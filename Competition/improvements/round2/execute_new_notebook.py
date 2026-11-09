"""Run only new second-pass notebooks in a project-local Jupyter kernel."""
import sys,json
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

root=Path(__file__).resolve().parents[2]
assert Path(sys.prefix).resolve()==(root/'.venv').resolve()
name=sys.argv[1]
assert name in ['03_round2_experiment_journal.ipynb','04_round2_validation_and_submission.ipynb']
kernelroot=root/'improvements/round2/artifacts/kernels';kernel=kernelroot/'competition-local';kernel.mkdir(parents=True,exist_ok=True)
(kernel/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
    'display_name':'Competition local venv','language':'python','env':{'OMP_NUM_THREADS':'4','MPLCONFIGDIR':str(root/'improvements/round2/artifacts/matplotlib')}}))
nb=nbformat.read(root/name,as_version=4)
km=KernelManager(kernel_name='competition-local',kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernelroot)]))
try: NotebookClient(nb,km=km,timeout=1800,resources={'metadata':{'path':str(root)}}).execute()
finally: nbformat.write(nb,root/name)
print('Executed',name)
