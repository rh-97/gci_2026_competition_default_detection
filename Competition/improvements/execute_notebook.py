"""Execute only the newly created notebooks, always in the project venv."""
import os, sys, json
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

root=Path(__file__).resolve().parents[1]
assert Path(sys.prefix).resolve()==(root/'.venv').resolve()
kernelroot=root/'improvements/artifacts/kernels'
kernel=kernelroot/'competition-local'; kernel.mkdir(parents=True,exist_ok=True)
(kernel/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
    'display_name':'Competition local venv','language':'python','env':{'MPLCONFIGDIR':str(root/'improvements/artifacts/matplotlib'),'OMP_NUM_THREADS':'4'}}))
name=sys.argv[1]
assert name in ['01_competition_data_audit.ipynb','02_improved_models_and_submission.ipynb']
nb=nbformat.read(root/name,as_version=4)
km=KernelManager(kernel_name='competition-local',kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernelroot)]))
client=NotebookClient(nb,km=km,timeout=1200,resources={'metadata':{'path':str(root)}})
try:
    client.execute()
finally:
    nbformat.write(nb,root/name)
print('Executed',name)
