"""Separately hashed MPS training; original CPU predictor/core stay unchanged."""
from pathlib import Path
import copy,hashlib,time,random
import numpy as np
import torch
import torch.nn.functional as F
import tabm
import rtdl_num_embeddings as embeddings
from sklearn.metrics import roc_auc_score
import h_models as cpu
from h_features import t,frame
SOURCE_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

def check_source():
    cpu.check_source();assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==SOURCE_SHA,'MPS fitting source changed while running.'

def gpu_predict(model,numerical,cats):
    model.eval();out=[]
    with torch.inference_mode():
        for start in range(0,len(numerical),2048):
            a=torch.from_numpy(numerical[start:start+2048]).to('mps');c=torch.from_numpy(cats[start:start+2048]).to('mps')
            out.append(model(a,c).squeeze(-1).sigmoid().mean(dim=1).cpu().numpy())
    return np.concatenate(out).astype(float)

def fit_neural(spec,df,y,tr,va=None,fixed=None,seed=t.SEED,progress=None):
    check_source();assert torch.backends.mps.is_available(),'Run the GPU worker outside the sandbox; prediction-only replay remains on CPU.'
    random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);torch.mps.manual_seed(seed)
    x=frame(df,spec['features']);enc=cpu.NeuralEncoder().fit(x.iloc[tr]);a,c=enc.transform(x.iloc[tr]);av,cv=enc.transform(x.iloc[va]) if va is not None else (None,None)
    n_features=a.shape[1]
    if spec['embedding']=='piecewise':
        bins=embeddings.compute_bins(torch.from_numpy(a),n_bins=48);embedding=embeddings.PiecewiseLinearEmbeddings(bins,8,activation=False,version='B')
    else:embedding=embeddings.PeriodicEmbeddings(n_features,8,n_frequencies=16,frequency_init_scale=.05,lite=True)
    model=tabm.TabM.make(n_num_features=n_features,cat_cardinalities=enc.cardinalities,num_embeddings=embedding,d_out=1,
        n_blocks=2,d_block=128,dropout=spec['dropout'],k=16,arch_type=spec['architecture']).to('mps')
    optimizer=torch.optim.AdamW(model.parameters(),lr=spec['learning_rate'],weight_decay=spec['weight_decay'])
    schedule=torch.optim.lr_scheduler.CosineAnnealingLR(optimizer,T_max=spec['max_epochs'],eta_min=spec['learning_rate']*.05)
    an=torch.from_numpy(a).to('mps');ac=torch.from_numpy(c).to('mps');target=torch.from_numpy(y[tr].astype('float32')).to('mps')
    generator=torch.Generator().manual_seed(seed);start=time.time();curve=[];best=-np.inf;best_epoch=0;state=None;best_gpu=None
    stop_reason='fixed count' if va is None else 'epoch cap'
    for epoch in range(1,(fixed or spec['max_epochs'])+1):
        check_source();model.train();order=torch.randperm(len(tr),generator=generator).to('mps');total=torch.zeros((),device='mps')
        for batch in order.split(1024):
            optimizer.zero_grad(set_to_none=True);logits=model(an[batch],ac[batch]).squeeze(-1)
            loss=F.binary_cross_entropy_with_logits(logits,target[batch,None].expand_as(logits));loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(),1.);optimizer.step();total+=loss.detach()*len(batch)
        train_loss=float(total.cpu())/len(tr);assert np.isfinite(train_loss);schedule.step()
        row=dict(epoch=epoch,training_loss=train_loss,learning_rate=float(optimizer.param_groups[0]['lr']),seconds=time.time()-start)
        if va is not None:
            pred=gpu_predict(model,av,cv);score=float(roc_auc_score(y[va],pred));row['validation_auc']=score
            if score>best+1e-6:
                best=score;best_epoch=epoch;state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()};best_gpu=pred.copy()
        curve.append(row)
        if progress:progress(row)
        print('MPS EPOCH',spec['name'],seed,epoch,row.get('validation_auc'),round(row['seconds'],1),flush=True)
        if va is not None and epoch-best_epoch>=spec['patience']:stop_reason='AUC patience';break
        if va is not None and time.time()-start>=spec['max_seconds']:stop_reason='time cap';break
    model=model.cpu().eval()
    if va is not None:model.load_state_dict(state);count=best_epoch
    else:count=fixed
    bundle=cpu.NeuralBundle();bundle.model=model;bundle.encoder=enc;bundle.spec=spec
    p=bundle.predict(df.iloc[va]) if va is not None else None
    difference=float(np.max(np.abs(p-best_gpu))) if va is not None else None
    if difference is not None:assert difference<1e-5,(difference,'GPU/CPU inference discrepancy')
    bundle.diagnostics=dict(stop_reason=stop_reason,epochs_completed=epoch,parameters=sum(p.numel() for p in model.parameters()),numeric_dimensions=n_features,
        categorical_cardinalities=enc.cardinalities,device='mps',inference_device='cpu',gpu_cpu_prediction_max_difference=difference,
        gpu_source_sha256=SOURCE_SHA,source_hashes=cpu.SOURCE_HASHES,retraining_bitwise_determinism_promised=False)
    check_source();return bundle,p,int(count),curve

def fit(spec,*args,**kwargs):return (fit_neural if spec['kind']=='tabm' else cpu.fit_learned)(spec,*args,**kwargs)
