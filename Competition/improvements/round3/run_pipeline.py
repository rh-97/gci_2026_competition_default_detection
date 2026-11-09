"""Resume the declared phases after initial screening; never silently ignore errors."""
import time,traceback,importlib
import round3 as t
import followup,validate,finalize,diagnostics,document

def main():
    plan=t.read(t.ART/'candidate_plan.json')
    while True:
        by={a['name']:a for a in t.screen_rows()}
        if all(s['name']in by for s in plan):break
        time.sleep(15)
    assert by['r3_cat_baseline']['status']=='complete'
    # Prospective amendments may be finalized while initial screens run. Load
    # the recorded source before any follow-up or frozen validation phase.
    for module in [followup,validate,finalize,diagnostics,document]:importlib.reload(module)
    if (t.ART/'stacking_probe.json').exists():
        assert not t.read(t.ART/'stacking_probe.json')['warrants_nested_followup'],'Nested stacking requires its separate prospective plan before freezing a choice.'
    phases=[('quantization_followup',followup.main),('document_screens',document.main),
        ('common_fold_cv',validate.cv),('freeze_primary_selection',validate.select),
        ('new_seed_confirmation',validate.confirmation),('two_seed_comparison',validate.averaging),
        ('gated_final_training',finalize.train_final),('saved_model_reproduction',finalize.reproduce),
        ('conditional_uncertainty',diagnostics.main),('document_final',document.main)]
    for name,function in phases:
        t.event('pipeline_phase_start',phase=name);print('PHASE',name,flush=True)
        function();t.event('pipeline_phase_finish',phase=name)
        t.dump(t.ART/'pipeline_status.json',dict(last_completed_phase=name,failed=False))
    t.dump(t.ART/'pipeline_status.json',dict(complete=True,failed=False));print('PIPELINE COMPLETE',flush=True)

if __name__=='__main__':
    try:main()
    except Exception:
        error=traceback.format_exc();t.dump(t.ART/'pipeline_status.json',dict(failed=True,error=error))
        t.event('pipeline_error',traceback=error);raise
