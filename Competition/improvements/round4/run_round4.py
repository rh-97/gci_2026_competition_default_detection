"""Resume the recorded round-four stages, preserving failures and all caches."""
import json,subprocess,sys,time,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ART=HERE/'artifacts'
def save(**kwargs):(ART/'pipeline_status.json').write_text(json.dumps(kwargs,indent=2))
def run(script,*args):
    stage=' '.join([script,*args]);save(status='running',stage=stage);print('STAGE',stage,flush=True)
    subprocess.run([sys.executable,str(HERE/script),*args],cwd=HERE,check=True)
def main():
    try:
        save(status='waiting',stage='initial screens')
        while True:
            events=ART/'events.jsonl'
            if events.exists() and any(json.loads(s).get('event')=='initial_screen_complete' for s in events.read_text().splitlines()):break
            time.sleep(10)
        run('r4_followup.py');run('r4_cv.py');run('r4_fraction.py')
        for phase in ['select','confirmation','averaging']:run('r4_validate.py',phase)
        for phase in ['train_final','reproduce']:run('r4_final.py',phase)
        save(status='modeling_complete',stage='Ready for documentation, notebooks and final archive verification.')
    except BaseException:
        save(status='failed',traceback=traceback.format_exc());raise
if __name__=='__main__':main()
