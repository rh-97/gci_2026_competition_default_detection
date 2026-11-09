"""Wait for declared gates, then overlap eligible CPU work with GPU fitting."""
from pathlib import Path
import sys,json,time,subprocess,os,signal,traceback
HERE=Path(__file__).resolve().parent;ART=HERE/'artifacts'
def read(path):
    try:return json.loads(path.read_text())
    except (FileNotFoundError,json.JSONDecodeError):return None
def status(**kwargs):(ART/'parallel_later_status.json').write_text(json.dumps(kwargs,indent=2))
def active():
    state=read(ART/'model_pipeline_status.json')
    if state and state['status']=='failed':raise RuntimeError('Main model workflow stopped; stop additional fitting.')
def wait_gate(name):
    while True:
        active();result=read(ART/name)
        if result is not None:return bool(result['passed'])
        time.sleep(5)
def run(mode):
    status(status='running',stage=mode);env=os.environ.copy()
    env['DYLD_LIBRARY_PATH']=str(Path(sys.prefix)/'lib/python3.12/site-packages/torch/lib')
    env['OMP_NUM_THREADS']='4';env['OPENBLAS_NUM_THREADS']='4'
    proc=subprocess.Popen([sys.executable,str(HERE/'h_parallel_later.py'),mode],cwd=HERE,env=env)
    try:
        while proc.poll() is None:active();time.sleep(5)
        assert proc.returncode==0,proc.returncode
    finally:
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)
            try:proc.wait(timeout=30)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=30)
def main():
    try:
        status(status='waiting',stage='confirmation gate')
        if not wait_gate('model_confirmation.json'):status(status='skipped',reason='Confirmation failed; no later work.');return
        run('averaging');status(status='waiting',stage='matching-three-seed gate')
        if not wait_gate('model_averaging.json'):status(status='skipped',reason='Averaging gate failed; no final work.');return
        run('final');status(status='complete',stage='Eligible CPU folds cached; main workflow assembles final results.')
    except BaseException:
        status(status='failed',traceback=traceback.format_exc());raise
if __name__=='__main__':main()
