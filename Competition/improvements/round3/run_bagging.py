"""Run the prospective averaging check only after the original gates finish."""
import time,traceback,importlib
import round3 as t
import bagging,document

def main():
    while True:
        path=t.ART/'pipeline_status.json'
        status=t.read(path) if path.exists() else {}
        if status.get('failed'):raise RuntimeError('Original pipeline failed: '+status.get('error',''))
        if status.get('complete'):break
        time.sleep(15)
    importlib.reload(bagging)
    for phase in ['probe','train']:
        print('BAGGING PHASE',phase,flush=True);t.event('bagging_phase_start',phase=phase)
        getattr(bagging,phase)();t.event('bagging_phase_finish',phase=phase)
    if t.read(t.ART/'bagging_final_results.json').get('accepted'):
        print('BAGGING PHASE reproduce',flush=True);bagging.reproduce()
    else:print('No seed-bank extension; original bank already passed its saved-model replay.',flush=True)
    importlib.reload(document);document.main()
    t.dump(t.ART/'bagging_pipeline_status.json',dict(complete=True,failed=False));print('BAGGING PIPELINE COMPLETE',flush=True)

if __name__=='__main__':
    try:main()
    except Exception:
        t.dump(t.ART/'bagging_pipeline_status.json',dict(failed=True,error=traceback.format_exc()));raise
