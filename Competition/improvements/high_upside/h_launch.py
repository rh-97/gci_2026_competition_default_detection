"""Launch model work with a single OpenMP runtime, without disabling its checks."""
import os,sys
from pathlib import Path
if __name__=='__main__':
    env=os.environ.copy();lib=Path(sys.prefix)/'lib/python3.12/site-packages/torch/lib'
    env['DYLD_LIBRARY_PATH']=str(lib);env['OMP_NUM_THREADS']='4';env['OPENBLAS_NUM_THREADS']='4'
    assert 'KMP_DUPLICATE_LIB_OK' not in env
    os.execve(sys.executable,[sys.executable,str(Path(__file__).with_name('h_pipeline.py')),*sys.argv[1:]],env)
