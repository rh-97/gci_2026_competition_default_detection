"""Build feature-enhancement and model-selection reports from saved evidence.

Only deterministic feature constructors are called to inventory column names.
No fit, load-data-and-resplit, training, tuning or prediction routine is called.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'improvements/high_upside/artifacts'
DATA_REPORT = ROOT / 'rounds/round2/reports/DATASET_ENHANCEMENT_REPORT.md'
MODEL_REPORT = ROOT / 'rounds/round5/reports/MODEL_SELECTION_REPORT.md'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(headers, rows):
    clean = lambda v: str(v).replace('|', '/').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(map(clean, row)) + ' |' for row in rows])


def main():
    assert Path(sys.prefix).resolve() == (ROOT / '.venv').resolve(), 'Use the project-local venv.'
    import pandas as pd
    # Importing these modules does not train or call their load/resplit routines.
    for folder in ['', 'round2', 'round3']:
        sys.path.insert(0, str(ROOT / 'improvements' / folder))
    import experiment as first
    import round2 as second
    import round3 as third

    ledger_path = ART / 'model_complete_experiment_ledger.json'
    ledger = read(ledger_path)
    trials = {r['name']: r for r in ledger}
    assert len(ledger) == 135 and len(trials) == len(ledger)
    sample = pd.read_csv(ROOT / 'input/train.csv', nrows=256)
    frames = {mode: first.features(sample, mode) for mode in ['raw','engineered','extended','lean']}
    frames.update({'r2_'+mode: second.features(sample, mode) for mode in ['risk','finance','missing','combined']})
    frames.update({'r3_'+mode: third.features(sample, mode) for mode in ['proxy','signed','rates','crosses','engineered_proxy']})
    assert [len(frames[n].columns) for n in ['raw','lean','r3_proxy','r3_signed']] == [32,46,51,55]
    for frame in frames.values():
        assert len(frame) == len(sample) and frame.index.equals(sample.index)
        assert 'SK_ID_CURR' not in frame and 'TARGET' not in frame
    reconstructed = list(frames['r3_signed']) + [c+s for c in ['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3'] for s in ['_RECONSTRUCTED','_RESIDUAL']]
    assert len(reconstructed) == 61
    memberships = {name:list(frame) for name,frame in frames.items()}
    memberships['score_reconstruction_schema_only'] = reconstructed
    columns = list(dict.fromkeys(c for names in memberships.values() for c in names))
    inventory = [{'column':c,'provided_predictor':c in frames['raw'],**{name:c in names for name,names in memberships.items()}} for c in columns]
    enhancements = DATA_REPORT.parent / 'enhancement'
    selections = MODEL_REPORT.parent / 'selection'
    enhancements.mkdir(exist_ok=True); selections.mkdir(exist_ok=True)
    pd.DataFrame(inventory).to_csv(enhancements/'feature_inventory.csv', index=False)
    pd.DataFrame([{'representation':n,'columns_before_model_encoder':len(cols)} for n,cols in memberships.items()]).to_csv(enhancements/'representation_sizes.csv', index=False)

    decisions=[]
    for row in ledger:
        spec=row.get('spec') or {};blend=row.get('best_blend') or {};cv=row.get('cv') or {};ref=row.get('reference_auc')
        decisions.append({'name':row['name'],'round_group':row['pass_group'],'record_type':row['record_type'],
            'kind':row.get('kind') or spec.get('kind'),'feature_recipe':spec.get('features') or row.get('features'),
            'status':row.get('status'),'standalone_stage_auc':row.get('auc'),'reference_auc':ref,
            'best_screened_blend_auc':blend.get('auc'),
            'standalone_minus_recorded_reference':row['auc']-ref if row.get('auc') is not None and ref is not None else None,
            'best_blend_minus_recorded_reference':blend['auc']-ref if blend.get('auc') is not None and ref is not None else None,
            'pooled_development_cv_auc':row.get('cv_auc') or cv.get('auc'),
            'selected_epochs_or_trees':row.get('count') or row.get('iterations'),
            'recorded_call_seconds':row.get('seconds'),
            'hypothesis':row.get('hypothesis') or spec.get('hypothesis'),
            'rationale_provenance':row.get('rationale_origin') or 'Consult original plan/source for timing; no new prospective claim.',
            'decision':row.get('decision') or row.get('interpretation'),
            'parameters_or_spec':json.dumps(spec or row.get('params'),sort_keys=True),
            'evidence':row.get('artifact') or row.get('source')})
    pd.DataFrame(decisions).to_csv(selections/'model_decision_matrix.csv',index=False)

    selection=read(ART/'model_selection.json');confirmation=read(ART/'model_confirmation.json');average=read(ART/'model_averaging.json')
    final=read(ART/'model_final_results.json');r2=read(ROOT/'improvements/round2/artifacts/selection.json');r3=read(ROOT/'improvements/round3/artifacts/selection.json')
    r3confirm=read(ROOT/'improvements/round3/artifacts/confirmation_results.json');r3average=read(ROOT/'improvements/round3/artifacts/averaging_results.json')
    bagging=read(ROOT/'improvements/round3/artifacts/bagging_probe.json');stack=read(ROOT/'improvements/round3/artifacts/stacking_probe.json')
    original_cv={r['name']:r for r in read(ROOT/'improvements/artifacts/cv_results.json')}
    latest_weights=dict(zip(selection['names'],selection['weights']))
    round3_weights=dict(zip(r3['names'],r3['weights']))
    selected_specs=[]
    for family,weight in zip(r2['models'],r2['weights']):
        selected_specs.append({'name':family['name'],'origin':'round2/reference',
            'expanded_final_probability_weight':latest_weights['round3_reference']*round3_weights['round2_reference']*weight,
            'spec':family['spec'],'recorded_primary_training_counts':family.get('iterations')})
    for family in r3['new_families']:
        selected_specs.append({'name':family['name'],'origin':'round3/reference',
            'expanded_final_probability_weight':latest_weights['round3_reference']*round3_weights[family['name']],
            'spec':family['spec'],'recorded_primary_training_counts':family.get('iterations')})
    for family in selection['new_families']:
        selected_specs.append({'name':family['name'],'origin':'structural additions',
            'expanded_final_probability_weight':latest_weights[family['name']],
            'spec':family['spec'],'recorded_primary_training_counts':family['counts'],'fixed_count':family['fixed_count']})
    assert len(selected_specs)==7 and abs(sum(f['expanded_final_probability_weight'] for f in selected_specs)-1)<1e-12
    (selections/'selected_family_settings.json').write_text(json.dumps({
        'families':selected_specs,'combination':'Probability mean; average seeds/folds within each family first.',
        'note':'Expanded weights are for interpretation. Exact replay retains the original nested combination order.',
        'original_reference_manifest':'improvements/round3/artifacts/bagging_model_manifest.json',
        'new_family_manifest':'improvements/high_upside/artifacts/model_manifest.json'},indent=2)+'\n')
    source_paths=[ledger_path,ART/'model_selection.json',ART/'model_confirmation.json',ART/'model_averaging.json',
        ART/'model_manifest.json',ART/'model_final_results.json',ROOT/'improvements/experiment.py',ROOT/'improvements/round2/round2.py',
        ROOT/'improvements/round3/round3.py',ROOT/'improvements/high_upside/h_features.py',ROOT/'improvements/high_upside/h_models.py',
        ROOT/'improvements/high_upside/MODELING_PLAN.md',ROOT/'improvements/high_upside/COMPLEXITY_POLICY.md',
        ROOT/'input/train.csv',ROOT/'input/test.csv',ROOT/'improvements/artifacts/splits.npz',
        ROOT/'improvements/artifacts/cv_results.json',ROOT/'improvements/artifacts/selection.json',ROOT/'improvements/artifacts/audit_results.json',
        ROOT/'improvements/round2/artifacts/selection.json',ROOT/'improvements/round3/artifacts/selection.json',
        ROOT/'improvements/round3/artifacts/confirmation_results.json',ROOT/'improvements/round3/artifacts/averaging_results.json',
        ROOT/'improvements/round3/artifacts/bagging_probe.json',ROOT/'improvements/round3/artifacts/stacking_probe.json',
        ART/'model_blend_grid.json',ART/'model_resolved_settings.json',Path(__file__).resolve()]
    source_paths += [ART/'pilots'/(r['name']+'.json') for r in ledger if r['pass_group']=='higher_upside']
    provenance={'new_models_fitted':False,'existing_notebooks_changed':False,'raw_data_changed':False,
        'feature_inventory_method':'Column names from deterministic constructors on 256 supplied training rows; no learned encoders fitted. The reconstruction schema appends its six source-defined names without fitting auxiliary teachers.',
        'reconstruction_schema_columns':61,'recorded_configurations_and_probes':len(ledger),
        'sources':{str(p.relative_to(ROOT)):sha(p) for p in source_paths}}
    (enhancements/'report_evidence.json').write_text(json.dumps(provenance,indent=2)+'\n')

    def auc(name):return f"{trials[name]['auc']:.7f}"
    raw_table=table(['Model recipe','Original-column AUC','Engineered-input AUC','Difference'],[
        ('LightGBM',auc('lgb_raw'),auc('lgb_engineered'),f"{trials['lgb_engineered']['auc']-trials['lgb_raw']['auc']:+.7f}"),
        ('CatBoost',auc('cat_raw'),auc('cat_lean'),f"{trials['cat_lean']['auc']-trials['cat_raw']['auc']:+.7f}"),
        ('TabM-mini, piecewise embeddings',auc('hu_tabm_raw_piecewise'),auc('hu_tabm_signed_piecewise'),f"{trials['hu_tabm_signed_piecewise']['auc']-trials['hu_tabm_raw_piecewise']['auc']:+.7f}")])
    r2feature_table=table(['Feature recipe with comparable CatBoost settings','Inner-screen AUC','What happened'],[
        ('Lean control',auc('cat_lean'),'Reference'),('Extra score-risk summaries',auc('r2_cat_risk'),'Not advanced'),
        ('Broad finance block',auc('r2_cat_finance'),'Positive screen; compact proxy follow-up preferred'),
        ('Extra missingness block',auc('r2_cat_missing'),'Not advanced'),('Combined blocks',auc('r2_cat_combined'),'Not advanced'),
        ('Only assumed-rate additions',auc('r2_cat_rates_only'),'No gain over lean control'),
        ('Only term-distance additions',auc('r2_cat_distances_only'),'Small gain; not sufficient alone'),
        ('Three rate proxies plus two distances',auc('r2_cat_term_proxies'),'Retained after CV'),
        ('Same proxy frame, native numeric missingness',auc('r2_cat_proxies_native'),'Retained as complementary family')])
    prune_table=table(['LightGBM input subset','Inner-screen AUC'],[(n,auc(n)) for n in ['lgb_tune_15','lgb_top_25','lgb_top_40','lgb_top_55','lgb_top_70']])
    source_link='[full experiment catalog](../../../docs/EXPERIMENT_CATALOG.md)'
    data_report=f'''# Dataset enhancement: what changed, why, how, and what worked

**Main conclusion:** we improved how the supplied information was represented.
We did not enlarge the dataset, invent labels or import outside rows. Original
CSVs still contain 171,202 training applicants and 61,500 test applicants, with
32 supplied predictors. Derived columns are constructed for the models in memory.

The most useful additions were compact financial/score summaries, loan-structure
proxies, signed term-pattern features, and a later learned score-reconstruction
block. Several broader feature sets failed. The table results below are saved
observations, not newly trained experiments.

Read [the EDA report](../../round1/reports/EDA_REPORT.md) for the observations that
motivated these choices, and [model selection](../../round5/reports/MODEL_SELECTION_REPORT.md)
for the later acceptance tests. This report answers **what inputs we created**.

## 1. What does “enhancement” mean here?

A feature is an input the model receives. For example, income and payment amount
are supplied columns; income divided by payment is a derived feature. It gives
the learner a direct view of a relationship already present in the data.

Enhancement did not guarantee improvement. The reason to keep a feature recipe
was its performance in matched comparisons, including how it contributed to an
ensemble. An explanation such as “this may express affordability” is a hypothesis,
not proof of a causal mechanism. Some early rationales were reconstructed from
the code after the trials; the original ledger retains that provenance. Later
structural recipes were explicitly recorded before fitting.

| Model-input representation | Columns before model-specific encoders | Construction |
| --- | --- | --- |
| Original columns | 32 | Necessary cleaning, no hand-crafted financial block |
| Broad engineered frame | {len(frames['engineered'].columns)} | Original columns plus the first broad set of ratios and summaries |
| Extended frame | {len(frames['extended'].columns)} | Adds logs, crosses and bands to the broad frame; did not win |
| Lean frame | 46 | Original 32 plus 14 selected derived columns |
| Loan-proxy frame | 51 | Lean plus three assumed-rate transforms and two term distances |
| Signed frame | 55 | Proxy frame plus two signed residuals and two rounded categories |
| Score reconstruction | 61 | Signed frame plus three auxiliary predictions and three residuals |

These counts are not neural hidden-unit counts. Group-statistic encoders,
missing indicators, one-hot encoders and numerical embeddings can change the
actual encoded matrix dimensions. [Named base-frame sizes](enhancement/representation_sizes.csv)
and [exact column membership](enhancement/feature_inventory.csv) are provided.
The inventory covers those base frames and the six reconstruction column names;
per-trial subsets/ignored columns and encoder expansions are recorded separately
in the trial catalog. Round 2's `risk` frame means score-summary formulas; it is
different from the later learned interaction-risk block.

## 2. Safe preparation before engineering

**What:** exclude `SK_ID_CURR` and `TARGET` from predictors, mask the employment
placeholder 365243, represent blank categories explicitly, and prevent undefined
ratios. **Why:** identifiers are for alignment, TARGET is the answer, the employment
value represents roughly a thousand years, and division by zero is unusable.
**How:** copy the input frame; replace that employment code with missing; give
blank categories a missing token; replace zero denominators and infinities with
missing. Original source files are not edited.

`EMPLOYED_SENTINEL` records whether the original placeholder appeared. The
`MISSING_COUNT` feature counts raw blank fields, excluding ID/TARGET; it is separate
from the employment flag because the placeholder is not an empty cell. Missing car
age is not automatically interpreted as “does not own a car.”

The original 8.07% default-label prevalence was retained. No SMOTE, duplicated
default rows, random deletion of repayers, pseudo-labeling or extra outside data
was used. Class-weight experiments changed model losses, not the dataset's rows.

## 3. Financial and household comparisons

**Why:** the same loan amount can mean different things relative to income,
payments, the financed goods and household size. Ratios expose those relationships
directly. They are descriptive inputs, not verified affordability decisions.

| Feature/block | How it was computed | Intended information |
| --- | --- | --- |
| Income/payment | `AMT_INCOME_TOTAL / AMT_ANNUITY` | Income relative to payment size |
| Income/loan | `AMT_INCOME_TOTAL / AMT_CREDIT` | Income relative to borrowing |
| Loan/payment, named CREDIT_TERM | `AMT_CREDIT / AMT_ANNUITY` | Payment/loan structure; not a known actual term |
| Loan/goods difference ratio | `(AMT_CREDIT - AMT_GOODS_PRICE) / AMT_GOODS_PRICE` | Difference between financing and goods amounts |
| Income per person | `AMT_INCOME_TOTAL / CNT_FAM_MEMBERS` | Income relative to household size |
| Other explored household blocks | Credit/payment per person; adults = family members − children; per-adult amounts; child fraction; income after payment proxies | Alternative household and cash-flow representations |

For a made-up applicant, income 60,000 and payment 10,000 give an income/payment
ratio of 6. With the same payment but income 20,000, it is 2. The model learns
whether that difference is predictive; we do not assign a manual default label.

**Other explored additions:** amount logarithms; bureau-request totals;
contact-flag totals; education-rank mapping; and age/employment category bands.
The larger engineered frame contained these and other combinations. Only a
subset survived in the lean frame, while the selected LightGBM uses a broader
engineered representation with fold-trained group statistics.

## 4. Time and external-score summaries

Age was derived as `-DAYS_BIRTH / 365.25`, employment years similarly after
masking the placeholder, and approximate age at employment as age minus employment
years. Ratios compared employment, registration, ID and phone-change durations
with birth duration. Negative day values follow the dataset's reference-date
encoding; they were not all treated as errors.

The supplied `EXT_SOURCE_1/2/3` columns were summarized using mean, minimum,
maximum, standard deviation and number observed. Broader frames also tested sums,
products, pairwise differences/products and interactions with age or loan/payment.
For example, scores 0.2/0.6/0.7 and 0.5/0.5/0.5 have the same mean of 0.5 but
different disagreement. A variability feature makes that distinction available.

Round 2 also tested logit, geometric, harmonic, weighted and conservative score
summaries, explicit missing-pattern categories and organization-family labels.
They were plausible hypotheses, not automatically useful additions. “External”
is part of the original column names; it does not mean we imported extra data.

## 5. What did the basic comparisons show?

The following use the same initial inner-validation applicants. They compare
feature recipes within each model family, not leaderboard results:

{raw_table}

TabM's original-column recipe still used automatic median/missing-value handling,
quantile preprocessing and numerical embeddings. “Raw” excludes our hand-crafted
financial feature block; it does not mean no preprocessing at all.

The LightGBM result also held up in five-fold development CV: **{original_cv['lgb_raw']['auc']:.7f}** for
original columns versus **{original_cv['lgb_engineered']['auc']:.7f}** for engineered inputs. The broader extended
LightGBM frame scored only **{auc('lgb_extended')}** in the inner screen, below
the ordinary engineered frame's **{auc('lgb_engineered')}**. More features could
add noisy or redundant split opportunities, so that larger block was not assumed
better. This is a plausible explanation, not an isolated causal finding.

## 6. Loan-structure features and their ablations

Round 2's development-only EDA found non-monotonic default-label patterns across
loan/payment groups and distances from multiples of 6 and 12. That motivated a
small proxy block rather than retaining every finance transformation.

For `t = loan/payment`, the absolute distance features are:

```text
distance_6  = abs(t / 6  - round(t / 6))
distance_12 = abs(t / 12 - round(t / 12))
```

Three more columns solve a hypothetical annuity relationship for assumed period
counts n = 24, 36 and 60:

```text
p = payment / loan
p = r / (1 - (1 + r)^(-n))
```

The implementation uses 28 binary-search steps over r in [0,1], only when the
assumptions admit a solution; otherwise the proxy is missing. These are nonlinear
representations of supplied amounts. They are **not reconstructed contractual
interest rates**, and n is not a verified loan duration.

The matched CatBoost screens were:

{r2feature_table}

The compact combined proxy block reached pooled development CV **0.7622544**;
its native-missing variant reached **0.7615745**. Both survived as complementary
families. By contrast, the broad native-missing lean model reached **0.7605613**
and was not retained in the final round-two blend. Missing-value handling and
feature content were evaluated as recipes, not universal rules.

**Round 3 refinement:** the absolute distance treats ratios 23.8 and 24.2 alike
around 24. Signed residuals distinguish the two sides:

```text
signed_n   = t / n - round(t / n)
category_n = string(round(t / n))       # n = 6 or 12
```

For n=6 those residuals are approximately −0.0333 and +0.0333. The joint signed
and rounded-category frame scored **{auc('r3_cat_signed')}** in the inner screen,
compared with **{auc('r3_cat_signed_only')}** for signed additions alone and
**{auc('r3_cat_term_categories')}** for rounded categories alone. The joint recipe
advanced; the individual ablations did not. A further model combined that frame
with 512 CatBoost quantization borders. Its name `r3_cat_feature_b512` refers to
the selected feature block plus finer quantization, **not top-k column pruning**.

Additional assumed-period transforms for n=12,18,48,72,84 were tested in
`r3_cat_rates` (inner AUC **{auc('r3_cat_rates')}**) and were not advanced. This
records an unsuccessful extension rather than assuming more period assumptions
always improve the representation.

## 7. Category interactions, group statistics and pruning

**What/why:** test category crosses such as occupation × income type, age bands,
category frequencies and amounts relative to a category's typical amount.
**How:** the group encoder learns category shares and numeric medians on training
rows only. It adds frequency or `value / group_median` columns; unseen groups
receive missing derived values rather than statistics fitted on validation/test.
Group fields included organization, occupation, education and income type, plus
an age bin where that representation provided one.

Broad crosses were not consistently useful. Some group statistics remained in
the selected LightGBM, while the broader CatBoost group recipe did not earn a new
final place. High-cardinality crosses can create small groups; that is a reason
to test regularization, not proof of why a particular trial lost.

Importance-based LightGBM pruning also failed to improve its tuned reference:

{prune_table}

The top-70 version was checked in CV but did not beat the retained tuned model.
Low individual importance does not prove a feature is useless jointly, and this
experiment does not establish that every possible selection method would fail.

## 8. Model-specific preprocessing

| Learner | What/how | Why |
| --- | --- | --- |
| LightGBM | Fold-trained category vocabularies; unseen levels map to missing; optional group statistics; numeric missing values retained | Match category semantics and preserve missingness |
| CatBoost | Categorical strings; numeric sentinel −999, native missingness and fold-median alternatives tested | Let validation choose a useful missing-data recipe |
| Logistic/spline/early MLP | Fold-trained median imputation, indicators and numeric scaling/quantiles; one-hot categories | Put numerical inputs on usable scales and represent categories |
| TabM | Training medians; normal-quantile transform; missing flags; removal of constant encoded columns; category vocabulary with unknown code 0; numerical embeddings | Support a neural representation with explicit missingness and stable inputs |

Normal quantiles map values using their rank distribution learned from training
data. Piecewise embeddings let the network learn flexible responses across
numeric ranges; periodic embeddings were tested as an alternative. These are
model inputs/learned representations, not added applicants. The better signed
piecewise TabM recipe was retained; periodic and stronger-regularized variants
did not beat its screened ensemble contribution.

## 9. Learned reconstruction of the supplied scores

**Question:** can other supplied columns predict an external score well enough
to expose useful extra patterns? **How:** for each score, train a LightGBM
regressor on observed values, exclude that same score from its raw inputs, and
generate training-row predictions using three inner folds. Refit the auxiliary
teacher on outer-training observed rows to transform outer-validation/test rows.
TARGET and ID are not auxiliary predictor columns.

Each score adds a reconstructed value and `observed - reconstructed` residual.
Original score columns are retained; missing residuals remain missing before
normal model preprocessing. These six extra columns expand 55 to 61. We did not
replace unknown values with supposedly recovered truth or acquire outside scores.

Pilot reconstruction R2 was approximately **0.4828, 0.2356 and 0.1157** for scores
1, 2 and 3. R2 describes reconstruction on rows whose scores are observed. It is
not default-classification accuracy or a guarantee for truly missing scores.
The auxiliary teachers used 300 trees, learning rate .04, 15 leaves, minimum child
count 100 and L2 penalty 20. Downstream default-ranking comparisons decided use.

The reconstruction CatBoost's best screened blend added **0.0003659 AUC** over
the complete screen reference. The final two-addition recipe also improved primary
AUC by **0.0003962** over the best at-most-one-addition recipe. That comparison
includes blend selection; it does not isolate a causal effect for each new column.
The frozen combined recipe then passed later validation.

## 10. Learned interaction risks: a rejected enhancement

Eight predeclared borrower/loan/score pairs were tested: contract × rounded term;
education × age band; income type × occupation; gender × age band; score-2 bin ×
age band; mean-score bin × missing-score pattern; credit bin × term bin; and term
bin × contract. Bin edges fit outer-training inputs only.

Five inner folds generated training-row risk maps without using that row's target.
Validation/test encodings used maps fitted on all outer-training rows. Smoothed
risk was `(group_defaults + prior * training_default_rate) / (group_size + prior)`,
with prior strengths 30 and 100, plus log-support and frequency. Unseen groups
fall back to the learned training rate. Eight interactions × four outputs add
32 columns to the signed frame.

For an illustrative group with 2 defaults among 10 people and a global rate .08,
prior 30 gives (2 + 30×.08)/(10+30) = .11 instead of the unstable raw .20. This
shows the intended regularization. It is not an actual group from our data.

The screened blend **lost 0.0001325 AUC**, so this block was rejected. Its intended
benefit may have been redundant with CatBoost or outweighed by noise; the result
does not establish the exact cause or rule out all target-encoding methods.

## 11. Final decisions and safeguards

- Keep supplied observations and labels unchanged; no external-data enlargement.
- Keep a compact successful frame for several trees and the neural addition;
  the selected older LightGBM retains its own broader engineered/group frame.
- Retain signed term structure and learned score-reconstruction inputs where
  downstream comparisons supported them.
- Reject automatic “more columns is better,” failed broad blocks, unsupported
  pruning and the latest interaction-risk block.
- Fit all learned medians, vocabularies, maps, bins and auxiliary teachers inside
  permitted training data. Test rows are transformed, not used to fit these maps.
- Freeze feature/model recipes before confirmation; do not manually adjust any
  applicant's test prediction from these observations.

The reports document tested decisions, not proof that every retained column is
individually necessary. Joint blocks and model changes limit causal attribution.

## Evidence and reproducibility

- {source_link}: every recorded trial and rationale provenance.
- [Exact feature membership](enhancement/feature_inventory.csv) and
  [frame sizes](enhancement/representation_sizes.csv).
- [Source hashes and report scope](enhancement/report_evidence.json).
- Actual builders: [first pass](../../../improvements/experiment.py),
  [round two](../../../improvements/round2/round2.py),
  [round three](../../../improvements/round3/round3.py),
  [learned features](../../../improvements/high_upside/h_features.py).
- [Report builder](../../../tools/build_decision_reports.py).

```sh
# From the repository root; no model training:
Competition/.venv/bin/python Competition/tools/build_decision_reports.py
```
'''

    family_table=table(['Recorded recipe','Inner-screen AUC','Pooled development CV AUC','Role'],[
        ('Tutorial Random Forest (five supplied columns)',auc('tutorial_rf'),'Not run','Baseline; not an exhaustive RF study'),
        ('Logistic, C=.01',auc('logistic_0.01'),'Not advanced','Linear baseline; preprocessing/inputs differ from trees'),
        ('Spline/logistic, C=.1',auc('spline_0.1'),f"{trials['spline_0.1']['cv_auc']:.7f}",'Different smooth representation; not retained'),
        ('Histogram boosting, 20 leaves',auc('hgb_20'),f"{trials['hgb_20']['cv_auc']:.7f}",'Validated; not retained'),
        ('LightGBM, raw',auc('lgb_raw'),f"{original_cv['lgb_raw']['auc']:.7f}",'Control'),
        ('LightGBM, engineered',auc('lgb_engineered'),f"{original_cv['lgb_engineered']['auc']:.7f}",'Feature control'),
        ('LightGBM, tuned/group frame',auc('lgb_tune_15'),f"{trials['lgb_tune_15']['cv_auc']:.7f}",'Retained reference family'),
        ('CatBoost, lean',auc('cat_lean'),f"{trials['cat_lean']['cv_auc']:.7f}",'Selected first-pass family'),
        ('XGBoost, finance',auc('r2_xgb_finance'),f"{trials['r2_xgb_finance']['cv_auc']:.7f}",'Validated; not retained'),
        ('CatBoost, compact proxies',auc('r2_cat_term_proxies'),f"{trials['r2_cat_term_proxies']['cv_auc']:.7f}",'Retained reference family'),
        ('CatBoost, native-missing proxies',auc('r2_cat_proxies_native'),f"{trials['r2_cat_proxies_native']['cv_auc']:.7f}",'Retained complementary family'),
        ('CatBoost, signed frame',auc('r3_cat_signed'),f"{trials['r3_cat_signed']['cv_auc']:.7f}",'Retained reference family'),
        ('CatBoost, signed/512 borders',auc('r3_cat_feature_b512'),f"{trials['r3_cat_feature_b512']['cv_auc']:.7f}",'Retained reference family'),
        ('Early MLP, small',auc('r3_mlp_small'),'Not advanced','No screened blend improvement'),
        ('Early MLP, wider',auc('r3_mlp_wide'),'Not advanced','No screened blend improvement')])
    pilots=[r for r in ledger if r['pass_group']=='higher_upside']
    pilot_table=table(['Structural pilot','Standalone inner AUC','Best screened blend gain','Decision'],[
        (r['name'],f"{r['auc']:.7f}",f"{r['delta']:+.7f}",'Advanced' if r['promoted'] else 'Not advanced') for r in pilots])
    validation_table=table(['Comparison; same rows within each row','Reference AUC','Candidate AUC','Gain'],[
        ('Primary development CV; used to select',f"{selection['baseline_auc']:.7f}",f"{selection['auc']:.7f}",f"{selection['gain']:+.7f}"),
        ('New fold partition; frozen recipe',f"{confirmation['baseline']['auc']:.7f}",f"{confirmation['candidate']['auc']:.7f}",f"{confirmation['gain']:+.7f}"),
        ('Matched three-seed development averaging',f"{average['baseline']['auc']:.7f}",f"{average['candidate']['auc']:.7f}",f"{average['gain']:+.7f}")])
    model_report=f'''# Model selection: what we tried, why, how, and what won

**Main conclusion:** we chose a weighted mixture because it ranked applicants
better than its complete previous reference in matched local comparisons. The
latest recipe is **25% older tree ensemble + 37.5% TabM neural model + 37.5%
score-reconstruction CatBoost**. The new neural model was weaker by itself than
the old mixture, but added useful complementary ranking information.

Matched three-seed local AUC improved **{average['baseline']['auc']:.5f} →
{average['candidate']['auc']:.5f}**. The latest user screenshot shows public AUC
0.77029, rank 364, but does not explicitly identify the uploaded filename.
Neither that observation nor the training scores establish a maximum attainable
score or demonstrate 0.8. This report reads saved evidence; it trains no models.

Read [dataset enhancement](../../round2/reports/DATASET_ENHANCEMENT_REPORT.md)
for input formulas, and [EDA](../../round1/reports/EDA_REPORT.md) for the data
observations. Here the focus is **which models/combinations earned their cost**.

## 1. How to read the scores

ROC AUC is the competition metric: higher means better ordering of default versus
repayment cases. A constant score gives AUC .5 even if predicting “repay” for
everyone gets approximately 92% accuracy. We therefore did not select by accuracy.

| Evaluation | Meaning | Appropriate use |
| --- | --- | --- |
| Inner screen | Train on 102,720 rows; score 34,241 development rows | Quickly shortlist hypotheses; repeatedly explored |
| Development five-fold CV | Hold out each part of 136,961 development rows in turn | Compare candidates on common folds and score pooled held-out predictions |
| New partition / seed | Repartition the same development labels | Check robustness; not an independent new test |
| First audit | Originally held-out 34,241 rows | Historical initial evaluation; later explored, so no longer untouched |
| Full-data OOF | Held-out predictions across final training folds | Diagnostic after selection; not a new independent estimate |
| Public leaderboard | Platform score on an unknown test subset | Record actual submissions; not a label source or large search grid |

Compare scores **within the same evaluation row/stage**. A pilot AUC near .75 and
a public AUC near .77 are not a measured .02 improvement. Fold scores are pooled
over their held-out predictions for the main AUC, rather than simply averaging
five separate AUC numbers. Differing fold-model score scales can affect pooling.

The row groups were stratified: each retained roughly the same default/non-default
proportions. This helps avoid a misleading comparison caused by one validation
group containing substantially fewer of the rare default cases.

Average precision checks retrieval of the rarer default cases. Log loss and Brier
score check probability quality; lower is better for those two. ROC AUC remained
the selection objective, with secondary metrics retained as diagnostics.

## 2. What model families were tried?

The models below use their recorded feature/preprocessing recipes. This compares
recipes, not a perfectly controlled isolation of algorithm identity. “Not advanced”
means the later stage was not run; it is not an invented CV result.

{family_table}

**Why these families:** Random Forest supplied the tutorial-equivalent starting
point; its five-column setup was not an exhaustive Random Forest comparison.
LightGBM, CatBoost, histogram boosting and XGBoost tested alternative boosted-tree
recipes. Logistic and spline models tested simpler/ smoother relationships.
MLPs and later TabM tested a different learned representation and potential error
complementarity. The observed results decide their roles; the reasons a loser
might struggle are hypotheses, not proof that the whole family is unsuitable.

## 3. What was tuned, and why?

Depth/leaves control interaction capacity; minimum leaf/child size limits tiny
groups; L2/L1 penalties discourage unstable fits; feature/row sampling and split
noise can reduce reliance on a particular sample; quantization controls candidate
numeric split boundaries; learning rate controls update size. More capacity can
fit extra structure or noise, so validation—not the size of the model—decided.

The first LightGBM search ran 24 Optuna configurations across feature modes,
group statistics, leaves, child counts, row/column sampling, regularization and
numeric bins. Its chosen trial was a **joint recipe**: the improvement cannot be
attributed to one parameter. CatBoost trials varied depth/regularization, borders,
category handling, growth policies, missingness, features and class weights.
Class weighting gives defaults extra influence in the loss; it was tested but
did not earn a place in the retained recipes. No row balancing was applied.

An epoch is a neural pass over training rows; a boosting iteration adds another
tree. Screening/primary CV used validation-based early stopping. Later fits used
fixed counts selected before confirmation. The full trial settings and outcomes
are in the {source_link} and [decision matrix](selection/model_decision_matrix.csv).

## 4. How the earlier ensemble was built

**Round 1:** lean CatBoost had pooled development AUC .7607901; tuned/group
LightGBM had .7573281. Their **2/3 CatBoost + 1/3 LightGBM** mixture reached
.7617724. The benefit of combining them, rather than picking one by standalone
score, supported retaining both. The original audit scored .7555056 versus
.6665727 for the tutorial-equivalent baseline. Those audit labels were later
inspected and are not now an untouched test.

**Round 2:** compact loan proxies and native-missing proxies were compared against
the complete first recipe. The selected weights were **.1875 LightGBM + .5625
proxy CatBoost + .25 native-missing proxy CatBoost**. Primary development AUC
rose **{r2['baseline_auc']:.7f} → {r2['auc']:.7f}**. A fixed-count new partition
also improved by **{r2['stability']['delta']:.7f}**, with all five groups positive.
Two-seed averaging retained the common family recipe and reduced sensitivity to
one partition. A new partition still uses previously explored labels.

**Round 3:** the signed-feature CatBoost and a signed/512-border CatBoost were
added at .25 each, with .5 retained for the round-two mixture. Primary gain was
**{r3['gain']:.7f}**, fixed-count confirmation gain **{r3confirm['gain']:.7f}**, and
matched two-seed gain **{r3average['gain']:.7f}**. The latter comparisons passed
their recorded gates. The 512-border recipe uses the successful signed frame;
it is not an importance-pruned feature subset despite its short trial name.

The third-seed check increased candidate development AUC by approximately
**{bagging['candidate_increment']:.7f}**, with no reweighting or seed-subset search.
The resulting older reference has five families × three seeds × five folds =
75 primary saved models. Its expanded family weights are .09375 LightGBM,
.28125 proxy CatBoost, .125 native-missing proxy CatBoost, .25 signed/512-border
CatBoost and .25 signed CatBoost.

**What did not earn expansion:** early small/wider MLPs did not improve a screened
blend. A learned-logit stacking feasibility probe over the older families added
only **{stack['best_gain']:.8f}**, below its .00020 trigger for expensive nested
validation. The base predictions were not fully nested, so that probe was not
eligible for submission. It does not settle fully nested stacking of newer families.

## 5. Why the search changed direction

Round 4 completed seven nearby CatBoost screens. The best screened mixture gain
was about .0002437, and no downstream validation/submission was completed before
the user prioritized larger gains. The recorded work was retained rather than
presenting the interrupted branch as a completed negative result.

The opportunity audit found a training/held-out gap for one saved model and no
obvious tiny subgroup explaining a large global ranking deficit. The response
was to test new representations/model families across the population. This did
not establish that a larger architecture would reach .8, or that more depth
could never help. The old incremental sweep stayed stopped.

## 6. The six structural pilots and promotion decisions

All six exact recipes were recorded before their pilots. Each screened its own
performance and five probability-blend weights (.10/.25/.50/.75/1.00) against the
complete current reference, whose inner AUC was .7518409. Promotion allowed at
most one neural and one learned-feature CatBoost family, each needing at least
.00030 screened blend gain.

{pilot_table}

![Screened ensemble contributions](../results/model_screen_gains.png)

The signed piecewise TabM was the best neural contribution. Raw inputs were
weaker; periodic embeddings and the stronger-regularized full-TabM recipe did not
beat the chosen contribution. The latter changed several settings jointly, so
its result does not isolate dropout, learning rate or architecture individually.

Reconstruction CatBoost passed the learned-feature slot. Interaction-risk encoding
reduced the screened mixture AUC and was rejected. Auxiliary score R2 alone did
not decide promotion. A useful representation had to help default-risk ranking.

Not every positive pilot advanced: a capacity limit reserved only the best model
in each slot. A screen win was not sufficient to ship a CSV.

## 7. How the final weights were selected and checked

The two finalists ran on the same primary development folds as the reference.
The declared grid compared reference/new and new/new pairs, plus three-way
mixtures, with probability and log-odds averages. The saved grid contains
**{selection['grid_size']}** recipes, not an unreported post-confirmation search.
The winner uses probability averaging.

Pair shares were .10, .25, 1/3, .50, 2/3, .75 and .90. Three-way recipes tested
reference shares .25/.50/.75 and relative shares .25/.50/.75 for the two additions.
For the winning reference share .25 and equal helper split, each helper receives
(1 − .25) × .50 = .375. Equal weights came from the selected grid point, not a
claim that the two model families have identical scientific importance.

```text
final = .25 × previous ensemble
      + .375 × signed TabM
      + .375 × reconstruction CatBoost
```

These are weights on prediction outputs. For a made-up applicant with outputs
.10/.20/.15, the combined score is .15625. They are not feature-importance values.
Probability calibration is checked separately from the ranking metric.

The neural family's standalone pooled primary AUC was about .7606962, below
the older mixture's .7637229. Its addition nevertheless improved the mixture.
This is evidence of useful complementarity for this recipe, not proof that the
models are independent or make entirely different errors.

A **budget amendment** required the second new family to add at least .00030
primary AUC over the best recipe with at most one new family. It was recorded
after neural CV and while tree CV was incomplete, before the complete joint-grid
choice and confirmation. The actual increment was **{selection['second_family_increment']:.7f}**.
The unconstrained winner already met it, so that amendment did not change the
winning recipe. This is adaptive compute allocation, not a statistical test.

The selected weights/method, training counts and sources were then frozen:

{validation_table}

Primary and matched-three-seed eligibility required at least .00030 pooled gain.
Confirmation required positive pooled gain and at least four positive groups;
the matching-seed check also required at least four. The new recipe improved
**all five groups** in each latest comparison. No weights were retuned after
confirmation, and confirmation used no validation early stopping.

The goal for a substantial branch was .002 OOF gain. This branch did **not** meet
that larger target, although it passed the smaller submission gates. The recorded
policy allowed finishing a smaller robust candidate without launching a broader
neural/seed search. That is the compute tradeoff, not an achieved .8 claim.

## 8. Fixed training settings and saved-model counts

The chosen neural model is TabM-mini with 16 shared internal members, two blocks,
width 128, 8-dimensional piecewise embeddings (up to 48 bins), dropout .1, AdamW
learning rate .002, weight decay .0003, batch 1,024 and gradient clipping. Primary
selected epochs **[29,32,40,40,41]** gave a fixed median **40 epochs**. The cosine
schedule retains its originally declared 140-epoch horizon; it was not silently
compressed to 40. Each member's BCE loss is averaged; inference averages member
probabilities.

Reconstruction CatBoost uses depth 5, learning rate .045, L2 leaf penalty 8 and
random strength .5. Primary selected counts **[1166,848,1150,1537,1085]** gave a
fixed **1,150 trees**. Its auxiliary teachers use their separate fixed settings
described in the enhancement report. These are chosen settings, not claims that
each parameter is individually optimal. Library-resolved pilot settings are in
[model_resolved_settings.json](../results/model_resolved_settings.json).
Complete specs, primary training-count records and expanded final weights for
all seven families are in [selected_family_settings.json](selection/selected_family_settings.json).
The expanded weights describe the recipe; exact replay retains its nested
calculation order.

Each new family has three seeds × five folds = 15 primary bundles. Alongside the
older 75, there are **105 primary models/bundles**, plus **45 auxiliary score
regressors** inside reconstruction bundles. TabM's 240 shared internal members
are not 240 separately stored fold models. The 132 main configurations in the
experiment ledger count different tested recipes/controls, not these repeated fits.

The first three neural pilots ran on CPU. A prospective, separately hashed
amendment moved later neural fits to local MPS after a speed benchmark; workers
were stopped before the change. Hyperparameters and gates stayed fixed, original
CPU evidence was retained, and subsequent saved inference uses CPU. Exact replay
from saved weights was verified, while bit-identical GPU retraining is not promised.

Models were trained from locally initialized weights using the supplied rows;
no pretrained checkpoints or extra datasets were introduced. Software/method
sources are recorded in [SOURCE_ATTRIBUTION.md](../code/SOURCE_ATTRIBUTION.md).
Exact packages are recorded in [model_environment.json](../results/model_environment.json)
and [requirements-high-upside.txt](../code/requirements-high-upside.txt).

## 9. Final results and what they do not establish

The matching three-seed comparison improved average precision .2500740 → .2520907,
log loss .2441755 → .2437166 and Brier score .0674623 → .0673702. Its paired row
bootstrap interval for the AUC gain was roughly [.0009880, .0020329], conditional
on fitted predictions. That interval omits fitting/search uncertainty and is not
a search-adjusted significance test or an independent new test.

![Latest local ROC curve](roc_curve.png)

| Delivered stage | Public observation | File attribution |
| --- | --- | --- |
| First improved mixture | .76540 | Explicitly confirmed |
| Round two | .76756 | Inferred from conversation |
| Round three bagged | .76824 | Explicitly confirmed |
| Latest screenshot | .77029, rank 364 | Screenshot confirmed; filename not explicit |

The latest full-data OOF AUC **{final['full_oof']['auc']:.7f}** is diagnostic after
selection, not an independent confirmation. The public screenshot and local
validation evaluate different applicants. Another +.02971 public AUC would be
needed to reach .8 from that screenshot; no tested result supports promising it.
Retrieval/profile models and genuinely nested combinations of the new families
remain untested directions. Negative results here do not establish a global ceiling.

The accepted CSV contains 61,500 finite probabilities in original sample/test ID
order and reproduces byte for byte from saved models on the recorded local runtime.
Its SHA-256 is `{final['sha256']}`. Test labels were never obtained, and no manual
prediction overrides or leaderboard-driven weight changes were used.

## 10. Evidence and glossary

- [All 135 configurations/probes with explanations](../../../docs/EXPERIMENT_CATALOG.md)
  and [selection decision matrix](selection/model_decision_matrix.csv).
- [Recorded latest plan](../code/MODELING_PLAN.md),
  [budget amendment](../code/COMPLEXITY_POLICY.md),
  [GPU amendment](../code/ACCELERATOR_AMENDMENT.md).
- [Complete grid](../results/model_blend_grid.json),
  [frozen choice](../results/model_selection.json),
  [confirmation](../results/model_confirmation.json),
  [matching-seed check](../results/model_averaging.json),
  [final manifest](../results/model_manifest.json).
- [Source/evidence hashes](../../round2/reports/enhancement/report_evidence.json)
  and [report builder](../../../tools/build_decision_reports.py).

**Feature:** an input column. **Fold:** a held-out row group. **OOF:** predictions
for rows excluded from that model's training subset. **Seed:** a reproducible
random arrangement/initialization. **Ensemble/blend:** combined model outputs.
**Ablation:** remove or separate part of a recipe to test it. **Regularization:**
constraints/penalties intended to reduce fragile fitting. **Frozen recipe:** the
recorded choice kept unchanged during later checks. **Hypothesis:** a plausible
reason to try something; it is not a causal conclusion.

No new training or model selection was performed to create this report. Historical
decisions are documented with their actual scope and timing; they are not
retroactively described as if every explanation had been known before fitting.
'''
    DATA_REPORT.write_text(data_report)
    MODEL_REPORT.write_text(model_report)
    print(json.dumps({'reports':[str(p.relative_to(ROOT)) for p in [DATA_REPORT,MODEL_REPORT]],
                      'feature_frames':{k:len(v) for k,v in memberships.items()},'decision_records':len(decisions),'new_models_fitted':False},indent=2))


if __name__ == '__main__':
    main()
