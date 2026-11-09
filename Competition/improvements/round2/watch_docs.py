"""Refresh the live ledger; stop only the watcher on its explicit control file."""
import time,importlib,traceback
import document
import round2 as r

previous=None
while True:
    files=list((r.ART/'screen').glob('*.json'))+list((r.ART/'cv').glob('*.json'))
    files += [p for p in [r.ART/'adaptive_plan.json',r.ART/'proxy_followup_plan.json',r.ART/'budget_control_plan.json',
        r.ART/'provisional_selection.json',r.ART/'stability_results.json',r.ART/'selection.json',r.ART/'final_results.json',
        r.ART/'verification.json',r.ART/'validation_plan.json',r.HERE/'document.py'] if p.exists()]
    state=tuple((str(p),p.stat().st_mtime_ns) for p in sorted(files))
    if state!=previous:
        try:
            importlib.reload(document);document.build();previous=state
        except Exception:
            traceback.print_exc()
    if (r.ART/'stop_documentation_watcher.json').exists():
        document.build(); break
    time.sleep(15)
