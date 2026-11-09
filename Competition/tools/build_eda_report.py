"""Consolidate recorded audits and refresh descriptive EDA; fit no models."""
from pathlib import Path
import hashlib
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'rounds/round1/reports'
ASSETS = DEST / 'eda'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def table(headers, rows):
    clean = lambda v: str(v).replace('|', '/').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(map(clean, row)) + ' |' for row in rows])


def main():
    assert Path(sys.prefix).resolve() == (ROOT / '.venv').resolve(), 'Use the project-local venv.'
    os.environ['MPLCONFIGDIR'] = '/private/tmp/competition-eda-cache/matplotlib'
    os.environ['XDG_CACHE_HOME'] = '/private/tmp/competition-eda-cache'
    import numpy as np
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    ASSETS.mkdir(parents=True, exist_ok=True)
    read = lambda p: json.loads(p.read_text())
    train = pd.read_csv(ROOT / 'input/train.csv')
    test = pd.read_csv(ROOT / 'input/test.csv')
    features = train.drop(columns=['SK_ID_CURR', 'TARGET'])
    test_features = test.drop(columns='SK_ID_CURR')
    assert list(train.drop(columns='TARGET')) == list(test)
    assert set(train.TARGET.unique()) == {0, 1}
    earlier = read(ROOT / 'improvements/artifacts/data_audit.json')
    assert len(train) == earlier['train_rows'] and len(test) == earlier['test_rows']
    assert abs(train.TARGET.mean() - earlier['positive_rate']) < 1e-12

    rows = []
    numerical = list(features.select_dtypes(include='number'))
    categorical = [c for c in features if c not in numerical]
    for column in features:
        row = dict(feature=column,kind='numeric' if column in numerical else 'categorical',
                   train_missing_rows=int(features[column].isna().sum()),
                   train_missing_fraction=float(features[column].isna().mean()),
                   test_missing_fraction=float(test_features[column].isna().mean()),
                   train_distinct_nonmissing=int(features[column].nunique()))
        if column in numerical:
            for label, q in [('min',0),('p01',.01),('median',.5),('p99',.99),('max',1)]:
                row['train_'+label] = float(features[column].quantile(q))
            for label, q in [('min',0),('median',.5),('p99',.99),('max',1)]:
                row['test_'+label] = float(test_features[column].quantile(q))
        rows.append(row)
    profile = pd.DataFrame(rows)
    profile.to_csv(ASSETS / 'feature_profile.csv', index=False)
    missing = profile.sort_values('train_missing_fraction', ascending=False).query('train_missing_rows > 0')

    def rates(series, name):
        data = pd.DataFrame({'group': series, 'TARGET': train.TARGET})
        result = data.groupby('group', observed=True, dropna=False).TARGET.agg(rows='size', defaults='sum', default_rate='mean').reset_index()
        result.insert(0, 'feature', name)
        result['few_cases'] = (result.defaults < 100) | ((result.rows-result.defaults) < 100)
        return result

    category_rates = pd.concat([rates(train[c].fillna('<blank>'), c) for c in categorical], ignore_index=True)
    category_rates.to_csv(ASSETS / 'category_rates.csv', index=False)
    age = -train.DAYS_BIRTH / 365.25
    ages = rates(pd.cut(age,[0,30,40,50,60,100],right=False,labels=['Under 30','30–39','40–49','50–59','60+']), 'age_band')
    ages.to_csv(ASSETS / 'age_rates.csv', index=False)
    ext_names = ['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3']
    ext_missing = rates(train[ext_names].isna().sum(axis=1), 'external_scores_missing')
    ext_missing.to_csv(ASSETS / 'external_missing_rates.csv', index=False)
    quantiles = pd.qcut(train.EXT_SOURCE_2, 5, labels=False, duplicates='drop')
    ext_bins = rates(quantiles.dropna().astype(int).reindex(train.index), 'EXT_SOURCE_2_fifth')
    ext_bins = ext_bins[ext_bins.group.notna()].copy()
    ext_bins['group'] = ext_bins.group.astype(int) + 1
    ext_bins.to_csv(ASSETS / 'external_score_bins.csv', index=False)

    shifts = []
    for column in categorical:
        a = train[column].fillna('<blank>').value_counts(normalize=True)
        b = test[column].fillna('<blank>').value_counts(normalize=True)
        union = a.index.union(b.index)
        shifts.append(dict(feature=column,total_variation_distance=float(.5*(a.reindex(union,fill_value=0)-b.reindex(union,fill_value=0)).abs().sum()),
                           unseen_test_categories=int(len(set(b.index)-set(a.index)))))
    cat_shift = pd.DataFrame(shifts).sort_values('total_variation_distance', ascending=False)
    cat_shift.to_csv(ASSETS / 'categorical_shift.csv', index=False)
    numeric_shift = pd.read_csv(ROOT / 'improvements/artifacts/numeric_shift.csv')
    loan_bins = pd.read_csv(ROOT / 'improvements/round2/artifacts/credit_term_development_bins.csv').rename(columns={'Unnamed: 0':'bin'}).dropna(subset=['count'])
    numeric = features[numerical].copy()
    numeric['DAYS_EMPLOYED'] = numeric.DAYS_EMPLOYED.replace(365243,np.nan)
    correlation = numeric.corr(method='spearman')
    correlation.to_csv(ASSETS / 'numeric_spearman.csv')
    pairs = sorted([(a,b,float(correlation.loc[a,b])) for i,a in enumerate(numerical) for b in numerical[i+1:]
                    if pd.notna(correlation.loc[a,b])], key=lambda x:abs(x[2]), reverse=True)

    quality = dict(train_rows=len(train),test_rows=len(test),predictors=len(features.columns),numeric_predictors=len(numerical),categorical_predictors=len(categorical),
        defaults=int(train.TARGET.sum()),nondefaults=int((train.TARGET==0).sum()),default_rate=float(train.TARGET.mean()),
        train_duplicate_ids=int(train.SK_ID_CURR.duplicated().sum()),test_duplicate_ids=int(test.SK_ID_CURR.duplicated().sum()),
        overlapping_ids=len(set(train.SK_ID_CURR)&set(test.SK_ID_CURR)),train_duplicate_profiles=int(features.duplicated().sum()),test_duplicate_profiles=int(test_features.duplicated().sum()),
        overlapping_profile_hashes=len(set(pd.util.hash_pandas_object(features,index=False))&set(pd.util.hash_pandas_object(test_features,index=False))),
        columns_aligned=True,train_id_range=[int(train.SK_ID_CURR.min()),int(train.SK_ID_CURR.max())],test_id_range=[int(test.SK_ID_CURR.min()),int(test.SK_ID_CURR.max())],
        employment_sentinel_train=int(train.DAYS_EMPLOYED.eq(365243).sum()),employment_sentinel_test=int(test.DAYS_EMPLOYED.eq(365243).sum()),
        organization_XNA_matches_employment_sentinel_train=bool(train.ORGANIZATION_TYPE.eq('XNA').equals(train.DAYS_EMPLOYED.eq(365243))),
        organization_XNA_matches_employment_sentinel_test=bool(test.ORGANIZATION_TYPE.eq('XNA').equals(test.DAYS_EMPLOYED.eq(365243))),
        raw_numeric_infinite_cells=int(np.isinf(features[numerical].to_numpy(dtype=float)).sum()),
        age_years_min=float(age.min()),age_years_max=float(age.max()),
        prior_adversarial_auc=earlier['adversarial_auc'],new_models_fitted=False,original_data_changed=False,
        sources={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'input/train.csv',ROOT/'input/test.csv',ROOT/'improvements/artifacts/data_audit.json',
            ROOT/'improvements/artifacts/numeric_shift.csv',ROOT/'improvements/high_upside/artifacts/audit_summary.json',
            ROOT/'improvements/round2/proxy_eda.py',ROOT/'improvements/round2/artifacts/credit_term_development_bins.csv',
            ROOT/'improvements/round2/artifacts/loan_structure_distribution_check.json',
            ROOT/'rounds/round1/notebooks/01_competition_data_audit.ipynb',ROOT/'rounds/round5/notebooks/07_signal_opportunity_audit.ipynb',Path(__file__).resolve()]})
    (ASSETS / 'quality_summary.json').write_text(json.dumps(quality,indent=2)+'\n')
    assert quality['train_duplicate_ids']==quality['test_duplicate_ids']==quality['overlapping_ids']==0
    assert quality['train_duplicate_profiles']==quality['test_duplicate_profiles']==quality['overlapping_profile_hashes']==0
    assert quality['raw_numeric_infinite_cells']==0

    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig, axes = plt.subplots(1,2,figsize=(12,5.4),layout='constrained')
    counts = [quality['nondefaults'],quality['defaults']]
    axes[0].barh(['No default label','Default label'],counts,color=['#3976a8','#d97043'])
    for i, n in enumerate(counts):axes[0].text(n+1500,i,f'{n:,} ({n/len(train):.2%})',va='center',fontsize=10)
    axes[0].set(xlim=(0,195000),xticks=[0,50000,100000,150000],xticklabels=['0','50k','100k','150k'],xlabel='Training applicants',title='Only about 8% have the default label')
    top = missing.head(8).iloc[::-1];yy=np.arange(len(top))
    axes[1].barh(yy-.18,100*top.train_missing_fraction,.36,label='Train',color='#3976a8')
    axes[1].barh(yy+.18,100*top.test_missing_fraction,.36,label='Test',color='#e4a25e')
    axes[1].set(yticks=yy,yticklabels=top.feature,xlabel='Blank cells (%)',title='Missing values are concentrated in a few fields',xlim=(0,80));axes[1].legend(loc='lower right')
    fig.savefig(ASSETS/'data_overview.png',dpi=150,facecolor='white');plt.close(fig)

    fig, axes = plt.subplots(2,2,figsize=(11,8),layout='constrained')
    axes[0,0].hist(-train.DAYS_BIRTH/365.25,bins=np.linspace(20,71,35),density=True,alpha=.6,label='Train',color='#3976a8')
    axes[0,0].hist(-test.DAYS_BIRTH/365.25,bins=np.linspace(20,71,35),density=True,histtype='step',label='Test',color='#c26827',linewidth=1.7)
    axes[0,0].set(xlabel='Age in years',ylabel='Density',title='Applicant ages');axes[0,0].legend()
    for ax,column,title in [(axes[0,1],'AMT_INCOME_TOTAL','Income has a long upper tail'),(axes[1,0],'AMT_CREDIT','Loan amounts span a wide range')]:
        values=np.r_[train[column].dropna(),test[column].dropna()];values=values[values>0];bins=np.linspace(np.log10(values.min()),np.log10(values.max()),45)
        for frame,label,color,style in [(train,'Train','#3976a8','stepfilled'),(test,'Test','#c26827','step')]:
            data=frame[column].dropna();data=data[data>0]
            ax.hist(np.log10(data),bins=bins,density=True,histtype=style,alpha=.55 if style=='stepfilled' else 1,label=label,color=color,linewidth=1.5)
        ax.set(xlabel='log10(amount in dataset units)',ylabel='Density per log unit',title=title);ax.legend()
    for target,label,color in [(0,'No default label','#3976a8'),(1,'Default label','#d97043')]:
        axes[1,1].hist(train.loc[train.TARGET.eq(target),'EXT_SOURCE_2'].dropna(),bins=np.linspace(0,.9,35),density=True,alpha=.5,label=label,color=color)
    axes[1,1].set(xlabel='Supplied EXT_SOURCE_2 value',ylabel='Density',title='Credit-related score differs by outcome');axes[1,1].legend()
    fig.savefig(ASSETS/'distributions.png',dpi=150,facecolor='white');plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(11,4.6),layout='constrained')
    for ax,frame,labels,title in [(axes[0],ages,ages.group.astype(str),'Default-label rate by age'),
            (axes[1],ext_bins,['Lowest','2','3','4','Highest'],'Default-label rate by EXT_SOURCE_2 fifth')]:
        ax.bar(labels,100*frame.default_rate,color='#3976a8')
        ax.axhline(100*train.TARGET.mean(),color='#d97043',ls='--',label='Overall training rate')
        for i,r in enumerate(frame.itertuples()):ax.text(i,100*r.default_rate+.3,f'n={r.rows:,}',ha='center',fontsize=8)
        ax.set(ylabel='Default-label rate (%)',title=title,ylim=(0,19));ax.legend(fontsize=8)
    fig.savefig(ASSETS/'outcome_patterns.png',dpi=150,facecolor='white');plt.close(fig)

    missing_table=table(['Field','Missing in train','Missing in test'],[(r.feature,f'{r.train_missing_fraction:.2%}',f'{r.test_missing_fraction:.2%}') for r in missing.itertuples()])
    amount_table=table(['Field','Train median','Train 99th percentile','Train maximum','Test maximum'],[(c,f'{train[c].median():,.0f}',f'{train[c].quantile(.99):,.0f}',f'{train[c].max():,.0f}',f'{test[c].max():,.0f}') for c in ['AMT_INCOME_TOTAL','AMT_CREDIT','AMT_ANNUITY']])
    contract=category_rates[category_rates.feature.eq('NAME_CONTRACT_TYPE')]
    contract_table=table(['Contract','Applicants','Default label','Rate'],[(r.group,f'{r.rows:,}',f'{r.defaults:,}',f'{r.default_rate:.2%}') for r in contract.itertuples()])
    ext_table=table(['EXT_SOURCE_2 group','Applicants with observed score','Default-label rate'],[(('Lowest fifth' if r.group==1 else 'Highest fifth' if r.group==5 else f'Fifth {r.group}'),f'{r.rows:,}',f'{r.default_rate:.2%}') for r in ext_bins.itertuples()])
    missing_group_table=table(['Missing external scores','Applicants','Default-label rate'],[(r.group,f'{r.rows:,}',f'{r.default_rate:.2%}') for r in ext_missing.itertuples()])
    numeric_shift_table=table(['Field','Largest CDF difference (KS)'],[(r.feature,f'{r.KS_statistic:.4f}') for r in numeric_shift.head(5).itertuples()])
    correlation_table=table(['Numeric fields','Spearman correlation'],[(a+' / '+b,f'{v:.3f}') for a,b,v in pairs[:5]])
    loan_table=table(['Loan/payment ratio group','Development applicants','Default-label rate'],[(r.bin,f'{int(r.count):,}',f'{r.mean:.2%}') for r in loan_bins.itertuples()])
    audit=read(ROOT/'improvements/high_upside/artifacts/audit_summary.json');slices=pd.read_csv(ROOT/'improvements/high_upside/artifacts/group_slices.csv')
    selected=slices[(slices.group=='EXT_missing_count')&(slices.value.astype(str)=='2')].iloc[0]
    capacity=audit['saved_capacity_diagnostic']
    assert int(loan_bins['count'].sum()) == audit['rows']
    report=f'''# Data audit and exploratory analysis

**EDA means exploring the data before deciding what to model.** It asks what the
rows contain, what looks unusual, which values are missing, and what patterns
appear in the known outcomes. This report explains the findings separately from
the model-tuning history.

The work already existed in [the first data-audit notebook](../notebooks/01_competition_data_audit.ipynb)
and [the later opportunity audit](../../round5/notebooks/07_signal_opportunity_audit.ipynb),
with additional [loan-structure EDA in Round 2](../../../improvements/round2/proxy_eda.py).
For this standalone report, descriptive tables and plots were refreshed from the
same supplied CSVs. The recorded train/test classifier and later saved-model
diagnostics were reused. **No new model was trained, no source data changed, and
no existing notebook was edited.**

## Main findings

- **The labels are imbalanced:** 8.07% show payment difficulties, versus 91.93% that do not.
- **Missing data are common:** roughly 69% of external score 1 and 66% of car age are blank.
- **Employment has a special code:** 365243 appears in 30,898 training rows; it is not a realistic duration.
- **Credit-related scores contain useful associations:** lower EXT_SOURCE_2 groups have higher observed default-label rates.
- **Some groups are tiny:** their extreme-looking rates are unreliable summaries.
- **The measured train/test differences were modest:** this supports, but does not prove, the validation approach used.

## 1. What data do we have?

| Property | Finding |
| --- | --- |
| Training applicants | {len(train):,}, with known outcomes |
| Test applicants | {len(test):,}, without outcomes |
| Supplied predictors | {len(features.columns)}: {len(numerical)} numeric, {len(categorical)} categorical |
| Default label / no default label | {quality['defaults']:,} / {quality['nondefaults']:,} |
| Target meaning | Payment difficulties as defined by the supplied task; “default” is shorthand here |
| Extra external data | None |

All outcome rates below describe **the labeled training data**. We cannot measure
the test set's default rate because its labels are unavailable. “External” in
`EXT_SOURCE_1/2/3` is part of the supplied column names; those columns were already
in the CSV, not fetched online. Amounts are shown in dataset units; no currency
or payment-period assumption is introduced.

![Label imbalance and blank values](eda/data_overview.png)

**Why the imbalance matters:** predicting “no default” for everybody would give
91.93% accuracy but catch nobody with the default label. We therefore evaluated
risk ranking with ROC AUC and used stratified validation groups that preserve a
similar class proportion. We did not delete repayers or manufacture default cases
to make the descriptive data look balanced.

## 2. Are there obvious integrity problems?

The checks found no repeated IDs within either file, no overlapping train/test
IDs, no exact repeated predictor profiles within either file, and no matching
train/test predictor-profile hashes. The train/test feature names and order
match, after removing TARGET. TARGET contains only 0 and 1, and no raw numeric
infinities were found.

Train IDs run from {quality['train_id_range'][0]} to {quality['train_id_range'][1]};
test IDs from {quality['test_id_range'][0]} to {quality['test_id_range'][1]}.
Those ranges would trivially identify which file a row came from. IDs were kept
for submission alignment and excluded from predictive and train/test-difference
models. An ID check does not recover a person's identity or establish that two
similar applicants must be the same person.

### The employment placeholder

`DAYS_EMPLOYED=365243` occurs in **{quality['employment_sentinel_train']:,} training
rows ({quality['employment_sentinel_train']/len(train):.2%})** and
**{quality['employment_sentinel_test']:,} test rows ({quality['employment_sentinel_test']/len(test):.2%})**.
That would be about a thousand years, so models treated it as missing and
engineered inputs kept a separate indicator. Ordinary negative day counts were
not automatically removed: they encode time before a reference date. Age was
interpreted as `-DAYS_BIRTH / 365.25`, giving a training range of approximately
{quality['age_years_min']:.1f}–{quality['age_years_max']:.1f} years.

The ORGANIZATION_TYPE label `XNA` matches the employment-placeholder rows exactly
in both files: **{'yes' if quality['organization_XNA_matches_employment_sentinel_train'] and quality['organization_XNA_matches_employment_sentinel_test'] else 'no'}**.
This pattern is structured rather than an arbitrary collection of empty cells.
The description does not establish why each individual value is unavailable.

Literal category values are distinguished from empty cells. For example,
OCCUPATION_TYPE contains the category `Other`; we did not assume it was a blank
or replace it. Explicit `XNA`/`Unknown` labels were retained as categories where present;
some individual category levels have very few examples.

## 3. Which information is missing?

The following percentages count raw blank/NaN cells, **before** recoding the
employment placeholder. Explicit labels such as `XNA` are not counted as blanks.

{missing_table}

Dropping every applicant with any blank would discard substantial information.
The modeling response was to retain rows, preserve missingness where supported,
and test appropriate missing-value methods. Neural preprocessing used medians
learned within training folds and missing indicators. Missing car age was not
automatically interpreted as “does not own a car.”

Applicants also differ in how many of the three supplied external scores are blank:

{missing_group_table}

These observed rate differences are descriptive. They do not imply that adding
or removing a score causes default, or that a guessed missing value is the truth.

## 4. What do the distributions look like?

![Numeric distributions and an outcome association](eda/distributions.png)

“Density” normalizes each histogram separately so we can compare shapes. Equal
areas in the two outcome histograms do not mean the two classes contain equal
numbers of applicants; their actual counts are shown in the first figure.

The amount variables have long right tails: a small number of applicants have
much larger values than the typical applicant. For example:

{amount_table}

The income and loan charts use log10 values so the tails remain visible. A step
of one on that axis means ten times the amount. The charts retain all positive
values rather than silently deleting the extremes. Large amounts alone are not
proof of a data-entry error. Ratios, regularized learners and neural quantile
preprocessing were tested instead of assuming every large observation was invalid.

Individual test values can still exceed the observed training range: the largest
test income is 117 million, versus 13.5 million in training. Similar bulk
distributions do not remove the need to notice rare extremes. These observations
were reported rather than automatically corrected to an invented value.

Several fields are strongly related. These are the five largest absolute
Spearman correlations among numeric predictors after masking the employment sentinel:

{correlation_table}

Spearman correlation describes whether values tend to increase/decrease together.
It does not prove causation or show that one of the columns can safely be removed.
The full matrix is in [numeric_spearman.csv](eda/numeric_spearman.csv).

## 5. Which groups have different observed outcomes?

The strongest simple example is the supplied EXT_SOURCE_2 score. Splitting
applicants with an observed score into five similarly sized groups gives:

{ext_table}

Higher score groups have lower observed default-label rates here. That is a
useful association for prediction, not proof that changing the score would
change an applicant's outcome. Missing-score applicants are excluded from this
particular five-group table and are covered in the missingness tables above.

![Age and credit-score groups](eda/outcome_patterns.png)

The orange dashed line is the overall training rate, not a policy threshold.
Age groups and contract types also differ:

{contract_table}

The full [category table](eda/category_rates.csv) includes income, education,
housing, occupation, organization and other supplied categories, with counts and
flags for groups having fewer than 100 examples of either outcome. For example,
“Maternity leave” contains only three training applicants, with one default label.
Its 33.33% rate is not a reliable estimate for a wider population. Groups can also
differ in loan mix, age and other characteristics; these comparisons do not
isolate an individual variable's effect.

### Loan/payment patterns explored in Round 2

A separate earlier EDA examined `AMT_CREDIT / AMT_ANNUITY` on the **136,961
development rows**, rather than the full training population used in the tables
above. Its recorded groups were:

{loan_table}

The relationship was not simply “a larger ratio always means more defaults.”
This motivated testing loan-structure features. The ratio is **not a verified
loan term in months**, because actual terms and payment assumptions are not
fully supplied. Distances from nearby multiples of 6 and 12 were also examined;
their outcome patterns motivated later feature experiments, whose usefulness
still required model validation.

The original [binned table](../../../improvements/round2/artifacts/credit_term_development_bins.csv),
[plot](../../../improvements/round2/artifacts/loan_structure_development.png), and
[distribution-check record](../../../improvements/round2/artifacts/loan_structure_distribution_check.json)
are preserved. Its error bars describe sampling uncertainty within bins, not
uncertainty from feature selection or differences in applicant composition.

## 6. Do train and test appear different?

The original audit compared blank rates, numeric distributions, category shares
and a classifier trained to distinguish train rows from test rows, excluding ID.
That diagnostic classifier's recorded AUC was **{earlier['adversarial_auc']:.6f}**.
An AUC near 0.5 means that particular classifier had limited ability to distinguish
the files. It does not prove equal distributions, equal default rates or absence
of hidden shifts. We reuse the recorded result; no classifier was refitted here.

The largest recorded numeric KS differences were:

{numeric_shift_table}

A KS value of 0.0293 means the largest gap between the two cumulative distributions
was about 2.93 percentage points. It is not an AUC or default-rate difference.
Raw blank rates were also close for the heavily missing fields. Category-share
differences and unseen-category counts are in
[categorical_shift.csv](eda/categorical_shift.csv).

Together, the measurements supported stratified random validation as a reasonable
working choice. They did not establish that performance would transfer perfectly.

## 7. What did the later error audit add?

This was a **model-error audit**, separate from basic data exploration. It reused
the older round-three ensemble's saved validation predictions on **{audit['rows']:,}**
development rows, with AUC **{audit['auc']:.5f}**. These are already explored labels,
not an independent new test. No model was fitted or predictions changed in that audit.

One group was missing two external scores: it contained **{int(selected['rows']):,}**
applicants and had within-group AUC **{selected['auc']:.5f}**. Although that AUC was
lower, the group accounted for **{selected['positive_share_of_total_loss']:.2%}** of
ranking errors attributed to positive applicants, compared with **{int(selected['positives'])/audit['positives']:.2%}**
of all positive applicants. In plain language: a weak-looking score on one group
did not show that the group was an unusually large source of the overall problem.

“Within-group AUC” evaluates only applicants inside that group. To judge its
overall importance, the audit also counted its contribution to all ranking errors.

Most contract-group ranking errors occurred within the large groups. This did
not identify a tiny, obviously broken segment whose correction would explain a
large overall score jump. The findings motivated broader model/representation
experiments rather than manually changing predictions for particular people.

One saved CatBoost model scored **{capacity['own_training_sample_auc']:.5f}** on a
20,000-row sample of its own training data, versus **{capacity['heldout_auc']:.5f}**
on its held-out rows. That illustrates a generalization gap. The higher training
score is not a leaderboard prediction or proof that 0.8 is achievable.

See [the later audit notebook](../../round5/notebooks/07_signal_opportunity_audit.ipynb)
and its [group tables](../../../improvements/high_upside/artifacts/group_slices.csv)
for the full decomposition.

## 8. What did we decide because of the EDA?

| Observation | Practical response |
| --- | --- |
| Imbalanced labels | Use ranking metrics and stratified validation; retain the original outcome distribution |
| Many missing scores and car ages | Retain rows, represent missingness and fit preprocessing inside training folds |
| Invalid employment duration | Mask the placeholder and preserve an indicator |
| Related financial amounts | Test ratios such as income/payment and loan/payment against raw-column controls |
| Different external-score values and availability | Test score summaries and later learned reconstructions using only supplied data |
| Tiny categories | Show counts and avoid strong claims from extreme-looking small-sample rates |
| Modest measured train/test differences | Use random stratified validation while acknowledging unobserved shift remains possible |
| No obvious small error segment explaining a large gain | Prioritize generalization across the population instead of hand-adjusted subgroup predictions |

These were hypotheses and safeguards, not guarantees. Feature/model validation
was still needed to determine whether a change helped. The original audit labels
have since been inspected repeatedly, so they cannot now be described as untouched.

## Tables, provenance and reproduction

- [All 32 predictors: types, missingness, distinct values and numeric percentiles](eda/feature_profile.csv).
- [All category counts and default-label rates](eda/category_rates.csv),
  [age groups](eda/age_rates.csv), [external-score groups](eda/external_score_bins.csv).
- [Data-quality summary and input/source SHA-256s](eda/quality_summary.json).
- Original [numeric train/test comparison](../../../improvements/artifacts/numeric_shift.csv),
  [recorded initial audit](../../../improvements/artifacts/data_audit.json),
  [later audit summary](../../../improvements/high_upside/artifacts/audit_summary.json).
- [Report builder](../../../tools/build_eda_report.py).

From the repository root:

```sh
Competition/.venv/bin/python Competition/tools/build_eda_report.py
```

This computes descriptive summaries and figures from the supplied files and reads
recorded audit evidence. It does not train models, tune a candidate, edit a notebook,
change predictions or modify the input CSVs. Observed associations are not causal
findings, fairness guarantees, a performance ceiling or evidence about other entrants.
'''
    (DEST / 'EDA_REPORT.md').write_text(report)
    print(json.dumps({'report':str((DEST/'EDA_REPORT.md').relative_to(ROOT)),'assets':str(ASSETS.relative_to(ROOT)),
        'new_models_fitted':False,'predictors':len(profile),'default_rate':quality['default_rate'],'categorical_shift_max':float(cat_shift.total_variation_distance.max())},indent=2))


if __name__ == '__main__':
    main()
