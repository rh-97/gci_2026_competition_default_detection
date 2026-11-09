"""Write the final report and an integrity-checked second-pass reproduction ZIP."""
import hashlib,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import nbformat
import round2 as r

def md_table(frame):
    columns=list(frame.columns)
    out=['| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']
    out+=['| '+' | '.join(str(x) for x in row)+' |' for row in frame.itertuples(index=False,name=None)]
    return '\n'.join(out)

def report():
    final=r.read(r.ART/'final_results.json');primary=r.read(r.ART/'provisional_selection.json')
    stability=r.read(r.ART/'stability_results.json');selection=r.read(r.ART/'selection.json')
    complexity=r.read(r.ART/'complexity_check_results.json')
    averaged=stability['two_seed_diagnostic']
    public=r.read(r.ART/'public_score.json');ledger=r.read(r.ART/'complete_experiment_ledger.json')
    complement=r.read(r.ART/'complementarity_summary.json')
    complement_table=md_table(pd.DataFrame([{'Helper':a['component'],'Individual AUC':f"{a['individual_auc']:.6f}",
        'Best recorded pair AUC':f"{a['best_recorded_pair_auc']:.6f}",'Helper weight':f"{a['component_weight']:.2%}"} for a in complement['comparisons']]))
    rows=[r.read(p) for p in sorted((r.ART/'screen').glob('*.json'))]
    complete=[a for a in rows if a['status']=='complete'];by={a['name']:a for a in complete}
    cvs=[r.read(p) for p in sorted((r.ART/'cv').glob('*.json'))]
    table=md_table(pd.DataFrame([{'Model':a['name'],'OOF AUC':f"{a['auc']:.6f}",'Fold SD':f"{np.std(a['fold_auc'],ddof=1):.6f}",
        'Median trees':int(np.median(a['iterations']))} for a in sorted(cvs,key=lambda a:-a['auc'])]))
    screening=md_table(pd.DataFrame([{'Experiment':a['name'],'Inner AUC':f"{a['auc']:.6f}",'Delta vs old CatBoost':f"{a['auc_delta_vs_pass1_cat']:+.6f}",
        'Seconds':f"{a['seconds']:.1f}"} for a in sorted(complete,key=lambda a:-a['auc'])]))
    mix=', '.join(f"{a['weight']:.2%} {a['name']}" for a in final['models'])
    parameter_decision='The new model recipe passed the declared two-seed gate.' if final['recommended_new_recipe'] else 'The new parameter/feature recipe did not pass the declared robustness gate; the first-pass recipe is retained.'
    bagging_decision='The final model bank averages two fold seeds per family, following the declared averaging diagnostic.' if final['two_seed_bagging'] else 'The final model bank uses one five-fold seed per family; the additional-seed averaging gate was not met.'
    text=f'''# Competition improvement report

## Current result and files

The confirmed public score is **0.7654**, displayed rank **1,094** (`hasanRocky`), for
`output/submission_improved.csv`. This was supplied in a screenshot and explicitly confirmed by the user.
Rank is a snapshot. The private/full-test score remains unknown.

Second-pass recommendation: **{final['recommendation']}**

New CSV: [`output/submission_round2.csv`](output/submission_round2.csv), {final['rows']:,} rows.
Its actual public score is **unknown until uploaded**; local AUCs below are not leaderboard scores.
The original 0.7654 CSV and original reproduction ZIP remain unchanged as fallbacks.

The supplied README/tutorial deck gives the deadline as **November 20, 2026, 01:00 UTC (07:00 Bangladesh time)**
and requires a code ZIP for Honors/Outstanding consideration. These are local provided instructions, not a live platform check.
The reviewed deck and extracted text are retained under `improvements/round2/reference`.

{parameter_decision} {bagging_decision}

Final mixture: **{mix}**.

| Evaluation | Frozen first-pass blend | Provisional second-pass candidate | Difference |
| --- | --- | --- | --- |
| Primary development OOF (selection) | {primary['baseline_auc']:.6f} | {primary['auc']:.6f} | {primary['development_delta']:+.6f} |
| Second development fold seed (fixed iterations/weights) | {stability['baseline_auc']:.6f} | {stability['candidate_auc']:.6f} | {stability['delta']:+.6f} |
| Two-seed development averaging (diagnostic) | {averaged['baseline_averaged_auc']:.6f} | {averaged['candidate_averaged_auc']:.6f} | {averaged['candidate_averaged_auc']-averaged['baseline_averaged_auc']:+.6f} |

Primary per-fold gains: `{primary['fold_gain']}`.
Second-seed per-fold gains: `{stability['fold_gain']}`.
Conditional paired-bootstrap interval for the primary gain: `{primary['conditional_gain_ci95']}`.
This conditions on fitted OOF predictions and excludes training/selection uncertainty.

Full-data final OOF AUC is **{final['full_oof_auc']:.6f}**, a diagnostic after development-based selection.
It is not an independent test estimate. Full-data OOF AP is {final['full_oof_average_precision']:.6f}
and log loss is {final['full_oof_log_loss']:.6f}.

## What was done

The first pass screened 57 configurations, validated 10 finalists and produced the public-scored CSV.
This pass ran **{len(rows)} additional screening configurations** ({len(complete)} completed,
{len(rows)-len(complete)} execution failures), then {len(cvs)} new common-fold CV models and the frozen second-seed check.
The combined ledger contains **{len(ledger)} trial records**. It records negative results, not only winners.

The detailed record is [`EXPERIMENT_LOG.md`](EXPERIMENT_LOG.md), with full machine-readable versions in
`improvements/round2/artifacts/complete_experiment_ledger.json` and `.csv`.
Each trial states its hypothesis, exact explicit configuration, representation, source file,
validation reference, score, iteration count, runtime, interpretation and evidence location.
Initial first-pass rationales are explicitly retrospective; second-pass plans/events record hypotheses before their execution.

New notebooks:

- [`03_round2_experiment_journal.ipynb`](03_round2_experiment_journal.ipynb): baseline equivalence, feature formulas, all screens, ablations, defaults, development-only descriptive plots and per-trial interpretation.
- [`04_round2_validation_and_submission.ipynb`](04_round2_validation_and_submission.ipynb): common-fold CV, frozen second-seed check, learning curves, model bank and byte-identical saved-model prediction.

All five notebooks that existed at the start of this pass are preserved unchanged. Only new notebooks were created.
The first-pass report before this pass is preserved in `improvements/round2/reference/pass1_report_before_round2.md`.

## What worked, what did not, and why

### Financial structure: isolate components instead of adding everything

Old compact CatBoost inner AUC: **{by['r2_cat_baseline']['auc']:.6f}**.
Full finance additions: **{by['r2_cat_finance']['auc']:.6f}**.
Payment-burden/household block alone: **{by['r2_cat_burden']['auc']:.6f}**.
Rate/term-proxy block alone: **{by['r2_cat_term_proxies']['auc']:.6f}**.

Screening identified the joint proxy block as promising, rather than justifying every added amount or household ratio.
Rate-only AUC was {by['r2_cat_rates_only']['auc']:.6f}; distance-only AUC was {by['r2_cat_distances_only']['auc']:.6f}.
Neither reproduced the joint block's gain alone. Common-fold and second-seed checks determine whether that recipe is retained.
The proxy block consists of hypothetical rate transforms under assumed 24/36/60 payment periods and distances to 6/12 multiples in credit/annuity.
These do **not** recover actual loan schedules or interest rates. They re-express information already present in the supplied data.
Rate transforms are monotonic functions of the payment ratio; distance features expose non-monotonic patterns.
Finite tree depth and numeric quantization make representations matter even without new information.
That is a plausible learning explanation, not proof of a causal financial mechanism.

Development-only binned default plots show non-monotonic associations, and feature-only development/test KS differences are about 0.007–0.008 for the loan-ratio/distance variables.
The plots and count tables are retained under `improvements/round2/artifacts/loan_structure_*`.
The plots are descriptive after exploration, with no adjustment for confounding or selection.

### Missing data and categorical learning

Native numeric missing bins screened at **{by['r2_cat_native_missing']['auc']:.6f}**, versus the old -999-sentinel policy at **{by['r2_cat_baseline']['auc']:.6f}**.
Finance plus native missing bins scored **{by['r2_cat_finance_native']['auc']:.6f}**.
Improvements were not simply additive. A -999 sentinel can collide with real negative date offsets, and bin construction can differ with native missing values; the score does not isolate those mechanisms.

The saved baseline actually uses MVS bootstrap and categorical-combination complexity 4.
A five-tree, 300-row parameter preflight found that bagging_temperature alone still resolved to MVS.
The explicitly Bayesian follow-up scored **{by['r2_cat_bayesian_rsm075']['auc']:.6f}** and did not beat the column-sampling MVS variant.
One-hot threshold changes and restricting categorical combinations were tested rather than assumed better.
Resolved parameters and learning curves are preserved where available.

### Other algorithms and regularization

XGBoost was added as an independent algorithm family. Its best original/compact screen was weaker than CatBoost,
but finance features raised its score to **{by['r2_xgb_finance']['auc']:.6f}**.
It was retained for common-fold and complementarity checks rather than dismissed solely on individual AUC.
Linear-leaf LightGBM did not improve its screen. Stronger/weaker CatBoost leaf shrinkage,
more numeric borders, Ordered boosting, column sampling and explicit Bayesian bootstrap were all recorded, including the negative outcomes.

The following are the best **recorded primary-grid** pairs with the lead proxy CatBoost:

{complement_table}

The old LightGBM and XGBoost helpers were effectively tied at this precision. Individual AUC alone did not determine the best mixture;
calibration and correlated errors can also matter. This comparison does not establish universal algorithm superiority.
A balanced-helper probe also tested sharing helper weight between LightGBM and XGBoost while preserving the lead model's weight.
It did not beat the frozen primary candidate and did not trigger another validation cycle.

The patience/cap control scored **{by['r2_cat_budget_control']['auc']:.6f}**.
Its maximum prediction difference from the original compact CatBoost was **{by['r2_cat_budget_control']['maximum_prediction_difference']}**.
This checks whether a longer stopping budget, rather than the intended feature/parameter change, accounts for the gain.

### Common-fold results

{table}

### Every new screening result

{screening}

## Validation discipline and stopping decision

All screening, feature choices and weights use the original development rows only.
Common primary folds use validation AUC early stopping. New recipes must improve primary pooled OOF AUC by at least 0.0002.
The second fold seed fixes both weights and median tree counts, passes no validation labels to training/early stopping,
and requires positive pooled gain with at least three positive folds. This is a robustness check on reused development rows, not a fresh untouched test.

The previously evaluated 20% audit remains historical: first-pass AUC **0.755506** versus **0.666573** for the tutorial RF,
with paired gain interval **0.079682–0.097858**. It was not used for second-pass tuning or given a new independence claim.
Public feedback is the single known 0.7654 score, not a sequence of per-trial leaderboard probes.

The two-seed averaging diagnostic is recorded in `stability_results.json`. It had to beat the better individual seed by more than 0.00015 for both baseline and candidate before doubling the final bank.
When the third model's primary increment was below 0.00015, a prospective rule compared the frozen best pair with the triple.
The rule could simplify only if the third model's secondary increment was nonpositive and the pair passed the original gain gates.
This chooses between two fixed recipes, without a secondary weight search; original winner snapshots are preserved.
The third model's incremental second-seed AUC was **{complexity['third_model_secondary_increment']:+.8f}**,
so it was retained under the recorded rule. This margin is tiny and is not evidence of a statistically established additional benefit.
Most of the recipe gain comes from the term-proxy representation; the frozen pair remains a nearly tied, simpler alternative.
The entire choice was frozen before full-data fitting. Final OOF scores were not used to retune it.

This pass followed the positive feature hypothesis into component ablations and combinations,
tested materially different model families and regularization, and checked whether the gains survived changed folds.
Further tiny gains on the same selection data could be noise. The result is a locally justified candidate or explicit fallback,
not a guarantee of a global optimum or higher hidden public/private AUC.

## Integrity, constraints and reproducibility

- Only the supplied train/test rows were used. No online dataset, recovered test labels, pretrained weights or manual predictions.
- All training and notebook execution used the project `.venv`. XGBoost was a software-only dependency installation.
- Original CSVs, all pre-existing notebooks, first-pass source, the public-scored CSV and its ZIP are checked against preserved SHA-256 hashes.
- Feature tests cover ID/target independence, row/batch invariance, train/test schema, unknown categories, native missing values and the hypothetical-rate equation.
- The final 61,500 probabilities are finite, in [0,1], and match the exact sample ID order.
- Saved-model prediction reproduces the new CSV byte-for-byte. Both new notebooks execute successfully.
- The new selection checksum and implementation hash are frozen before final fitting.

New CSV SHA-256: `{final['sha256']}`.
Original public-scored CSV SHA-256: `{public['sha256']}`.

### Reproduce the complete pass

From `Competition`, retaining the supplied `input` directory and first-pass artifacts:

```sh
.venv/bin/python improvements/round2/round2.py screen
.venv/bin/python improvements/round2/adaptive.py
.venv/bin/python improvements/round2/budget_control.py
.venv/bin/python improvements/round2/proxy_followup.py
.venv/bin/python improvements/round2/secondary_metrics.py
.venv/bin/python improvements/round2/proxy_eda.py
.venv/bin/python improvements/round2/validate.py cv
.venv/bin/python improvements/round2/validate.py select
.venv/bin/python improvements/round2/complementarity.py
.venv/bin/python improvements/round2/balanced_probe.py
.venv/bin/python improvements/round2/validate.py stability
.venv/bin/python improvements/round2/check_complexity.py
.venv/bin/python improvements/round2/finalize.py train_final
.venv/bin/python improvements/round2/finalize.py reproduce
.venv/bin/python improvements/round2/document.py
```

For fast prediction-only replay, run notebook 04 or `finalize.py reproduce`.
`requirements-round2.txt` and `artifacts/environment.json` record exact package versions.
The new reproduction ZIP includes source, notebooks, models, documentation, evidence and the preserved original ZIP for provenance.
It excludes the venv and input CSVs; use the originally supplied data when reproducing.

Upload only the intended CSV to Omnicampus and check the scoring timestamp. The supplied competition README says the **last submitted file** determines the final entry.
Report the new public score against this exact CSV checksum before treating it as a leaderboard improvement.
'''
    (r.ROOT/'IMPROVEMENT_REPORT.md').write_text(text)
    return final

def package():
    report()
    for name in ['03_round2_experiment_journal.ipynb','04_round2_validation_and_submission.ipynb']:
        nb=nbformat.read(r.ROOT/name,as_version=4)
        for i,cell in enumerate(nb.cells):
            for j,out in enumerate(cell.get('outputs',[])):
                if 'image/png'in out.get('data',{}):
                    import base64
                    (r.ART/f'{Path(name).stem}_plot_{i}_{j}.png').write_bytes(base64.b64decode(out.data['image/png']))
    names=['README.ipynb','tutorial.ipynb','preprocessing.ipynb','01_competition_data_audit.ipynb',
           '02_improved_models_and_submission.ipynb','03_round2_experiment_journal.ipynb','04_round2_validation_and_submission.ipynb',
           'IMPROVEMENT_REPORT.md','EXPERIMENT_LOG.md','HomeCredit_columns_description.xlsx','environment.yml','conda-explicit-osx-arm64.txt']
    candidates=[r.ROOT/n for n in names]
    candidates+=list((r.ROOT/'improvements').rglob('*'))
    candidates+=list((r.ROOT/'output').glob('*.csv'))+[r.ROOT/'output/competition_improved_reproduction.zip']
    files=[]
    for file in candidates:
        if not file.is_file(): continue
        rel=file.relative_to(r.ROOT)
        if any(p in rel.parts for p in ['.venv','input','.git','__pycache__','kernels','matplotlib']): continue
        if file.suffix=='.log' or file.name in ['competition_round2_reproduction.zip','package_manifest.json']: continue
        if rel.parts[0]=='output' and file.suffix=='.zip' and file.name!='competition_improved_reproduction.zip':continue
        files.append(file)
    manifest={str(f.relative_to(r.ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    manifest_file=r.ART/'package_manifest.json';r.dump(manifest_file,manifest);files.append(manifest_file)
    archive=r.ROOT/'output/competition_round2_reproduction.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for f in files:z.write(f,arcname=str(Path('Competition')/f.relative_to(r.ROOT)))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip()is None
        for name,sha in manifest.items():assert hashlib.sha256(z.read('Competition/'+name)).hexdigest()==sha,name
    print('Verified reproduction ZIP:',archive,'bytes',archive.stat().st_size,'files',len(manifest))

if __name__=='__main__':package()
