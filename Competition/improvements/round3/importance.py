"""Summarize saved-model split importance; never fit models or retune selection."""
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from xgboost import XGBClassifier
import lightgbm as lgb
import round3 as t

def main():
    if not t.read(t.ART/'final_results.json')['accepted']:
        print('No new final model; no new importance chart.');return
    manifest=t.read(t.ART/'model_manifest.json');extra={}
    b=t.ART/'bagging_final_results.json'
    if b.exists() and t.read(b).get('accepted'):
        extra={a['name']:a for a in t.read(t.ART/'bagging_model_manifest.json')['families']}
    summaries=[]
    for family in manifest['new_families']:
        instances=[i for seed in family['seeds'] for i in seed['instances']]
        if family['name']in extra:instances+=extra[family['name']]['instances']
        values=[];kind=family['spec']['kind']
        for item in instances:
            path=t.ROOT/item['model']
            if kind=='cat':
                model=CatBoostClassifier();model.load_model(str(path))
                series=pd.Series(model.get_feature_importance(thread_count=4),index=model.feature_names_)
                measure='CatBoost PredictionValuesChange'
            elif kind=='lgb':
                model=lgb.Booster(model_file=str(path));series=pd.Series(model.feature_importance('gain'),index=model.feature_name());measure='LightGBM split gain'
            elif kind=='xgb':
                model=XGBClassifier(enable_categorical=True,n_jobs=4);model.load_model(str(path));booster=model.get_booster()
                series=pd.Series(booster.get_score(importance_type='gain')).reindex(booster.feature_names,fill_value=0);measure='XGBoost average split gain'
            else:continue
            values.append(100*series/series.sum())
        if not values:continue
        matrix=pd.concat(values,axis=1)
        result=pd.DataFrame(dict(mean_importance_pct=matrix.mean(axis=1),model_std_pct=matrix.std(axis=1))).sort_values('mean_importance_pct',ascending=False)
        result.index.name='feature';file=t.ART/(family['name']+'_final_importance.csv');result.to_csv(file)
        summaries.append(dict(name=family['name'],file=str(file.relative_to(t.ROOT)),measure=measure,models=len(values),top_features=result.head(10).reset_index().to_dict('records')))
    t.dump(t.ART/'importance_summary.json',dict(families=summaries,note='Normalized to 100 within each model. Correlated features can share importance. These are descriptive model statistics, not causal effects, and different families use different measures.'))
    print('Saved importance summaries:',[a['name'] for a in summaries])

if __name__=='__main__':main()
