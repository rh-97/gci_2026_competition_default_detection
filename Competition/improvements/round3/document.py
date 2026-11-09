"""Generate a complete, evidence-linked third-pass journal without changing notebooks."""
import json
from datetime import datetime,timezone
import round3 as t

def table(columns,rows):
    return '\n'.join(['| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']+
        ['| '+' | '.join(str(v).replace('|','/') for v in row)+' |' for row in rows])

def main():
    specs=t.read(t.ART/'candidate_plan.json') if (t.ART/'candidate_plan.json').exists() else t.candidates()
    if (t.ART/'followup_plan.json').exists():specs+=t.read(t.ART/'followup_plan.json')
    rows=t.screen_rows();by={a['name']:a for a in rows};ledger=[]
    decisions={a['name']:a['promoted'] for a in t.read(t.ART/'promotion.json')['decisions']} if (t.ART/'promotion.json').exists() else {}
    selected=t.read(t.ART/'selection.json').get('names',[]) if (t.ART/'selection.json').exists() else []
    publicpath=t.ART/'round3_public_result.json'
    if publicpath.exists():
        public=t.read(publicpath)
        publicintro=f"The user explicitly confirmed submitting `submission_round3_bagged.csv` and supplied a screenshot showing **{public['score']:.5f}, rank {public['rank']:,}**. The exact CSV checksum is recorded in `improvements/round3/artifacts/round3_public_result.json`. The gain is **{public['gain_vs_round2']:+.5f}** over round two and **{public['gain_vs_first_pass']:+.5f}** over the first pass. Ranks are snapshots; private/full-test performance remains unknown. This feedback was recorded after the recipe was frozen and did not tune this pass."
        publicintro+=' Frozen training-result JSON files and executed notebook outputs retain their pre-submission score fields; the post-submission result is recorded separately. The public gain does not isolate the extra third seed from the other recipe changes.'
    else:
        publicintro='The user supplied a screenshot showing **0.76756, rank 568**, up from 0.7654. The file attribution to `submission_round2.csv` follows the conversation; the screenshot does not show a filename. Public feedback is recorded and does not tune this pass.'
    lines=['# Third-pass experiment journal','',
        'Generated from retained evidence. Previous experiments remain in `EXPERIMENT_LOG.md`; this journal documents the new pass.',
        '',f'Last generated: {datetime.now(timezone.utc).isoformat()}','',
        '## Public feedback and scope','',
        publicintro,
        '', 'The plan was written before any third-pass fit: [`PLAN.md`](improvements/round3/PLAN.md). The prospectively recorded quantization amendment is [`FOLLOWUP_PLAN.md`](improvements/round3/FOLLOWUP_PLAN.md). Existing notebooks and prior-pass sources are protected by a SHA-256 manifest. All fits use the project `.venv`; only supplied data are used.',
        '', '## Screening results','',
        'Every configuration uses the same original inner split. This split has been repeatedly explored and is not independent evidence. The reference is the complete frozen round-two mixture. Blend probes use new-model weights 0.10, 0.25, 0.50, 0.75 and 1.00; these are screening probes, not final weights.',
        '', table(['Trial','Status','Individual AUC','Best inner blend AUC','Gain over reference','Iterations','Seconds'],[
            [s['name'],by.get(s['name'],{}).get('status','pending'),
             f"{by[s['name']]['auc']:.6f}" if s['name'] in by and by[s['name']]['status']=='complete' else '—',
             f"{by[s['name']]['best_blend']['auc']:.6f}" if s['name'] in by and by[s['name']]['status']=='complete' else '—',
             f"{by[s['name']]['best_blend']['auc']-by[s['name']]['reference_auc']:+.6f}" if s['name'] in by and by[s['name']]['status']=='complete' else '—',
             by.get(s['name'],{}).get('iterations','—'),round(by.get(s['name'],{}).get('seconds',0),1)] for s in specs]),'']
    for spec in specs:
        row=by.get(spec['name'],dict(name=spec['name'],spec=spec,status='pending'))
        complete=row['status']=='complete'
        interpretation='Pending; no result exists yet.'
        if complete:
            delta=row['best_blend']['auc']-row['reference_auc']
            if spec['name']=='r3_cat_baseline': interpretation='Implementation control; maximum prediction difference from the previous proxy screen is '+str(row['baseline_max_difference'])+'. This is not a new improvement.'
            elif delta>=.0001: interpretation='Promising inner complementarity under the predeclared promotion threshold. Requires matching development CV before any claim of a useful improvement.'
            elif delta>0: interpretation='A small screening gain below the promotion threshold. No reliable improvement is established; selection noise and training variation remain plausible.'
            else: interpretation='No screened blend beat the complete current reference. This does not prove that the idea is universally ineffective.'
        elif row['status']=='failed': interpretation='Execution failure: '+row['error']+'. No performance conclusion is drawn.'
        comparisons=[]
        if complete and spec['kind']=='cat' and spec['name']!='r3_cat_baseline':
            parents={'r3_cat_depth4_b512':['r3_cat_depth4','r3_cat_borders512'],
                'r3_cat_native_b512':['r3_cat_borders512'],
                'r3_cat_signed_only':['r3_cat_signed'],'r3_cat_term_categories':['r3_cat_signed'],
                'r3_cat_feature_b512':['r3_cat_signed','r3_cat_borders512']}.get(spec['name'],['r3_cat_baseline'])
            for parent in parents:
                if parent in by and by[parent]['status']=='complete':
                    comparisons.append(dict(parent=parent,parent_auc=by[parent]['auc'],individual_auc_delta=row['auc']-by[parent]['auc']))
        if spec['name'] in decisions:
            interpretation+=' Promotion decision: '+('advanced to common-fold CV.' if decisions[spec['name']] else 'did not advance under the recorded threshold and finalist cap.')
        cvpath=t.ART/'cv'/(spec['name']+'.json');cv=t.read(cvpath) if cvpath.exists() else None
        if cv is not None:
            interpretation+=' Common-fold standalone OOF AUC: '+f"{cv['auc']:.9f}"+'.'
        if selected and spec['name']in selected:interpretation+=' Included in the frozen primary recipe; later gates determine deployment.'
        entry={**row,'interpretation':interpretation,'parent_comparisons':comparisons,
            'promoted':decisions.get(spec['name']),'cv_auc':cv['auc'] if cv else None,
            'cv_fold_auc':cv['fold_auc'] if cv else None,'included_in_frozen_primary_recipe':spec['name']in selected};ledger.append(entry)
        if row.get('implementation_hash') and row['implementation_hash']!=t.implementation_hash():
            assert t.signature_matches(row['implementation_hash'],t.implementation_hash())
            entry['implementation_signature_note']='Raw signature is the proven inspect.getsource line-offset metadata alias. Identical feature/encoder/fitting ASTs and exact phantom-hash reproduction are retained in reference/signature_alias_proof.json. Raw evidence is unchanged.'
        lines += ['## '+spec['name'],'','**Question:** '+spec['hypothesis'],'',
            '**How:** '+('Quantile-normalized numeric values with median imputation/missing indicators, one-hot categoricals, and a scratch-trained neural network; all preprocessing fits on training rows.' if spec['kind']=='mlp' else 'Build the named row-local representation, fit categorical vocabularies and optional group aggregates on training rows only, then fit the declared tree model.'),'',
            '**Exact configuration:**','```json',json.dumps(spec,indent=2),'```','',
            '**Outcome and interpretation:** '+interpretation,'']
        if comparisons:lines += ['**Reference comparisons:** `'+json.dumps(comparisons)+'`. Exact settings above determine which changes are isolated; joint parameter changes cannot identify a single cause.','']
        if complete:
            lines += ['**Evidence:** AUC '+f"{row['auc']:.9f}"+', AP '+f"{row['average_precision']:.9f}"+', log loss '+f"{row['log_loss']:.9f}"+', Brier '+f"{row['brier']:.9f}"+'.',
                'Best inner blend: '+str(row['best_blend'])+'. Correlation with reference: '+str(row['correlation'])+'.',
                'Convergence: '+str(row['iterations'])+' retained iterations; saturated='+str(row['saturated'])+'.',
                'Full result, resolved parameters, saved predictions and learning curve: `improvements/round3/artifacts/screen/'+spec['name']+'*`.','']
    for name,title in [('incidents.json','Implementation incidents and corrections'),('pair_grid_amendment.json','Primary pair-grid correction before fresh confirmation'),('early_blend_diagnostic.json','Early saved-prediction blend diagnostic'),('stacking_probe.json','Cross-fitted learned-combination feasibility probe'),('stored_helper_probe.json','Late stored-model combination check'),('blend_methods.json','Probability, log-odds and percentile blending'),('promotion.json','Screening promotion decisions'),
        ('selection.json','Primary development selection'),('winner_complementarity.json','Frozen-winner marginal complexity'),('confirmation_results.json','Frozen new-fold-seed confirmation'),
        ('averaging_results.json','Comparison against the complete two-seed reference'),('final_results.json','Original two-seed submission or fallback'),
        ('bagging_probe.json','Prospective three-seed averaging check'),('bagging_final_results.json','Three-seed extension decision'),
        ('verification.json','Integrity and reproduction checks'),('round3_public_result.json','Post-submission public result')]:
        path=t.ART/name
        if path.exists(): lines += ['## '+title,'','```json',json.dumps(t.read(path),indent=2),'```','']
    for subdir,title in [('cv','Common-fold development validation'),('confirmation','Fixed-iteration new-seed model results'),('secondary','Matching secondary-seed model results')]:
        records=[t.read(p) for p in sorted((t.ART/subdir).glob('*.json'))] if (t.ART/subdir).exists() else []
        if records:
            lines += ['## '+title,'',table(['Model','OOF AUC','Fold AUCs','Iterations','Seconds'],[
                [a['name'],f"{a['auc']:.9f}",a['fold_auc'],a['iterations'],round(a['seconds'],1)] for a in records]),'']
    if (t.ART/'current_model_slice_diagnostic.csv').exists():
        lines += ['## Exploratory error slices','',
            'Two-seed development OOF was summarized by external-score missing count, contract, income type, age band and gender. The large slices show small average calibration residuals; low slice AUC alone does not justify a specialist. Tiny categories are unstable and will not receive manually adjusted predictions. Counts, rates, residuals, AUC and loss are in `improvements/round3/artifacts/current_model_slice_diagnostic.csv`.','']
    lines += ['## Limits and stopping','',
        'The primary validation labels have already been explored. A new fold seed changes training/validation assignment, not the available evidence. Conditional bootstrap intervals do not include the uncertainty introduced by searching. Full-data OOF is diagnostic after selection. Public/private performance of a new file remains unknown until it is evaluated.',
        '', 'A failed gate retains the existing submission. No global-optimum or exhaustive-search claim is made. The final report records which hypotheses were tested, which remain untested, and why the pass stopped.','']
    t.dump(t.ART/'experiment_ledger.json',ledger)
    import pandas as pd
    pd.DataFrame([dict(name=a['name'],status=a['status'],hypothesis=a['spec']['hypothesis'],auc=a.get('auc'),
        best_blend_auc=a.get('best_blend',{}).get('auc'),seconds=a.get('seconds'),iterations=a.get('iterations'),
        interpretation=a['interpretation'],spec=json.dumps(a['spec'],sort_keys=True)) for a in ledger]).to_csv(t.ART/'experiment_ledger.csv',index=False)
    previous=t.read(t.r.ART/'complete_experiment_ledger.json')
    combined=[dict(pass_group='previous passes',record_type='main screening configuration',**a) for a in previous]
    combined += [dict(pass_group='third pass',record_type='main screening configuration',**a) for a in ledger]
    if (t.ART/'stacking_probe.json').exists():
        for a in t.read(t.ART/'stacking_probe.json')['results']:
            combined.append(dict(pass_group='third pass',record_type='auxiliary meta-learning probe',
                name=a['spec']['name'],status='complete',hypothesis='Test cross-fitted learned prediction combination before considering fully nested stacking.',
                interpretation='Screening only: precomputed base OOF features are not fully nested. Gain below the recorded threshold does not warrant a larger nested run.' if a['gain']<.0002 else 'Approximate screen warrants a separate, prospectively planned fully nested test; cannot deploy from this probe.',**a))
    t.dump(t.ART/'complete_experiment_ledger.json',combined)
    pd.DataFrame([dict(pass_group=a['pass_group'],record_type=a['record_type'],name=a['name'],status=a['status'],auc=a.get('auc'),
        hypothesis=a.get('hypothesis',a.get('spec',{}).get('hypothesis')),interpretation=a.get('interpretation'),
        configuration=json.dumps(a.get('spec',{}),sort_keys=True)) for a in combined]).to_csv(t.ART/'complete_experiment_ledger.csv',index=False)
    (t.ROOT/'ROUND3_EXPERIMENT_LOG.md').write_text('\n'.join(lines))
    print('Updated third-pass journal:',sum(a['status']=='complete' for a in ledger),'complete,',sum(a['status']=='failed' for a in ledger),'failed,',sum(a['status']=='pending' for a in ledger),'pending.')

if __name__=='__main__': main()
