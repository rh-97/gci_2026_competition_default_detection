"""Extract resolved pilot models/settings without fitting or changing weights."""
from pathlib import Path
import json,joblib
HERE=Path(__file__).resolve().parent;ART=HERE/'artifacts'
def main():
    plan=json.loads((ART/'model_candidate_plan.json').read_text());out=[]
    for spec in plan:
        path=HERE/'models'/(spec['name']+'_pilot.joblib')
        if not path.exists():continue
        bundle=joblib.load(path);row=dict(name=spec['name'],spec=bundle.spec,diagnostics=bundle.diagnostics)
        if spec['kind']=='tabm':
            row.update(model_representation=str(bundle.model),parameter_shapes={n:list(p.shape) for n,p in bundle.model.named_parameters()},
                encoder=dict(numerical_columns=bundle.encoder.nums,categorical_columns=bundle.encoder.cats,
                    quantile_parameters=bundle.encoder.quantiles.get_params(),kept_dimensions=bundle.encoder.keep.tolist(),cardinalities=bundle.encoder.cardinalities))
        else:
            row['resolved_catboost_parameters']=bundle.model.get_all_params()
            if hasattr(bundle.builder,'models'):
                row['auxiliary_booster_parameters']={name:model.booster_.params for name,(model,encoder) in bundle.builder.models.items()}
            row['encoded_columns']=bundle.encoder.columns
        out.append(row)
    (ART/'model_resolved_settings.json').write_text(json.dumps(out,indent=2,default=str));print('Extracted resolved settings for',len(out),'pilots.')
if __name__=='__main__':main()
