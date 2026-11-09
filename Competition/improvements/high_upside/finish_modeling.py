"""Finish documentation after the live model pipeline, then stop for visual QA."""
from pathlib import Path
import sys,json,time,subprocess,traceback
HERE=Path(__file__).resolve().parent;ART=HERE/'artifacts'
def status(**kwargs):(ART/'model_delivery_status.json').write_text(json.dumps(kwargs,indent=2))
def run(script,*args):
    status(status='running',stage=' '.join([script,*args]));print('DELIVERY',script,*args,flush=True)
    subprocess.run([sys.executable,str(HERE/script),*args],cwd=HERE,check=True)
def main():
    try:
        status(status='waiting',stage='Live model pipeline')
        while True:
            path=ART/'model_pipeline_status.json'
            if path.exists():
                state=json.loads(path.read_text())
                if state['status']=='failed':raise RuntimeError('Model pipeline failed: '+state.get('traceback',''))
                if state['status']=='modeling_complete':
                    parallel=ART/'parallel_later_status.json'
                    try:parallel_state=json.loads(parallel.read_text()) if parallel.exists() else None
                    except json.JSONDecodeError:parallel_state=None
                    if parallel_state is None or parallel_state['status']in ['complete','skipped','failed']:break
            time.sleep(10)
        run('h_uncertainty.py');run('h_report.py','--final');run('h_results_notebook.py')
        run('execute_model_notebook.py','09_high_upside_results_reproduction.ipynb')
        status(status='ready_for_visual_review',stage='Inspect model_screen_gains.png, model_neural_curves.png and any model_fold_gains.png before final verification/archive.')
    except BaseException:
        status(status='failed',traceback=traceback.format_exc());raise
if __name__=='__main__':main()
