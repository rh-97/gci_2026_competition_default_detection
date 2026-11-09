"""Immutable pilot fitting core. Run through h_launch.py for one OpenMP runtime."""
import os,sys,time,copy,hashlib,random
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
import tabm
import rtdl_num_embeddings as embeddings
from sklearn.preprocessing import QuantileTransformer
from sklearn.metrics import roc_auc_score
from h_features import t,frame,builder

SOURCE_HASHES={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(__file__).with_name('h_features.py')]}
torch.set_num_threads(4)

def check_source():
    for name,want in SOURCE_HASHES.items():assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==want,name+' changed during fitting.'

class NeuralEncoder:
    def fit(self,x):
        self.columns=list(x);self.cats=list(x.select_dtypes(include=['object','str']).columns);self.nums=[c for c in x if c not in self.cats]
        values=x[self.nums].to_numpy(dtype=float);self.medians=np.nanmedian(values,axis=0);self.medians=np.nan_to_num(self.medians)
        filled=np.where(np.isfinite(values),values,self.medians);self.quantiles=QuantileTransformer(n_quantiles=min(256,len(x)),output_distribution='normal',subsample=None,random_state=t.SEED).fit(filled)
        z=np.c_[self.quantiles.transform(filled),~np.isfinite(values)];self.keep=np.ptp(z,axis=0)>0
        self.vocab={c:{value:k+1 for k,value in enumerate(sorted(x[c].fillna('<MISSING>').astype(str).unique()))} for c in self.cats}
        self.cardinalities=[len(self.vocab[c])+1 for c in self.cats];return self
    def transform(self,x):
        values=x[self.nums].to_numpy(dtype=float);filled=np.where(np.isfinite(values),values,self.medians)
        numerical=np.c_[self.quantiles.transform(filled),~np.isfinite(values)][:,self.keep].astype('float32')
        cats=np.column_stack([x[c].fillna('<MISSING>').astype(str).map(self.vocab[c]).fillna(0).to_numpy(dtype='int64') for c in self.cats])
        assert np.isfinite(numerical).all();return numerical,cats

class NeuralBundle:
    def predict(self,df):
        z,c=self.encoder.transform(frame(df,self.spec['features']));return neural_predict(self.model,z,c)

def neural_predict(model,numerical,cats):
    model.eval();values=[]
    with torch.inference_mode():
        for start in range(0,len(numerical),2048):
            a=torch.from_numpy(numerical[start:start+2048]);c=torch.from_numpy(cats[start:start+2048])
            values.append(model(a,c).squeeze(-1).sigmoid().mean(dim=1).numpy())
    return np.concatenate(values).astype(float)

def fit_neural(spec,df,y,tr,va=None,fixed=None,seed=t.SEED,progress=None):
    check_source();random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
    x=frame(df,spec['features']);enc=NeuralEncoder().fit(x.iloc[tr]);a,c=enc.transform(x.iloc[tr]);av,cv=enc.transform(x.iloc[va]) if va is not None else (None,None)
    n_features=a.shape[1]
    if spec['embedding']=='piecewise':
        bins=embeddings.compute_bins(torch.from_numpy(a),n_bins=48)
        embedding=embeddings.PiecewiseLinearEmbeddings(bins,8,activation=False,version='B')
    else:embedding=embeddings.PeriodicEmbeddings(n_features,8,n_frequencies=16,frequency_init_scale=.05,lite=True)
    model=tabm.TabM.make(n_num_features=n_features,cat_cardinalities=enc.cardinalities,num_embeddings=embedding,
        d_out=1,n_blocks=2,d_block=128,dropout=spec['dropout'],k=16,arch_type=spec['architecture'])
    optimizer=torch.optim.AdamW(model.parameters(),lr=spec['learning_rate'],weight_decay=spec['weight_decay'])
    schedule=torch.optim.lr_scheduler.CosineAnnealingLR(optimizer,T_max=spec['max_epochs'],eta_min=spec['learning_rate']*.05)
    an=torch.from_numpy(a);ac=torch.from_numpy(c);target=torch.from_numpy(y[tr].astype('float32'));generator=torch.Generator().manual_seed(seed)
    start=time.time();curve=[];best=-np.inf;best_epoch=0;state=None;stop_reason='fixed count' if va is None else 'epoch cap'
    for epoch in range(1,(fixed or spec['max_epochs'])+1):
        check_source();model.train();order=torch.randperm(len(tr),generator=generator);total=0.
        for batch in order.split(1024):
            optimizer.zero_grad(set_to_none=True);logits=model(an[batch],ac[batch]).squeeze(-1)
            loss=F.binary_cross_entropy_with_logits(logits,target[batch,None].expand_as(logits));assert torch.isfinite(loss)
            loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);optimizer.step();total+=float(loss.detach())*len(batch)
        schedule.step();row=dict(epoch=epoch,training_loss=total/len(tr),learning_rate=float(optimizer.param_groups[0]['lr']),seconds=time.time()-start)
        if va is not None:
            pred=neural_predict(model,av,cv);score=float(roc_auc_score(y[va],pred));row['validation_auc']=score
            if score>best+1e-6:best=score;best_epoch=epoch;state=copy.deepcopy(model.state_dict())
        curve.append(row)
        if progress:progress(row)
        print('EPOCH',spec['name'],seed,epoch,row.get('validation_auc'),round(row['seconds'],1),flush=True)
        if va is not None and epoch-best_epoch>=spec['patience']:stop_reason='AUC patience';break
        if va is not None and time.time()-start>=spec['max_seconds']:stop_reason='time cap';break
    if va is not None:model.load_state_dict(state);count=best_epoch
    else:count=fixed
    bundle=NeuralBundle();bundle.model=model.cpu().eval();bundle.encoder=enc;bundle.spec=spec
    bundle.diagnostics=dict(stop_reason=stop_reason,epochs_completed=epoch,parameters=sum(p.numel() for p in model.parameters()),
        numeric_dimensions=n_features,categorical_cardinalities=enc.cardinalities,device='cpu',source_hashes=SOURCE_HASHES)
    p=bundle.predict(df.iloc[va]) if va is not None else None;check_source();return bundle,p,int(count),curve

class LearnedTreeBundle:
    def predict(self,df):return self.model.predict_proba(self.encoder.transform(self.builder.transform(df)))[:,1]

def fit_learned(spec,df,y,tr,va=None,fixed=None,seed=t.SEED,progress=None):
    check_source();b=builder(spec['learned']);x=b.fit_transform(df.iloc[tr].reset_index(drop=True),y[tr],seed)
    if va is not None:
        other=b.transform(df.iloc[va]);x=pd.concat([x,other],ignore_index=True);target=np.r_[y[tr],y[va]];validation=np.arange(len(tr),len(target))
    else:target=y[tr];validation=None
    model,enc,p,count=t.fit(spec,x,target,np.arange(len(tr)),validation,fixed=fixed,seed=seed)
    curve=model.get_evals_result();bundle=LearnedTreeBundle();bundle.model=model;bundle.encoder=enc;bundle.builder=b;bundle.spec=spec
    bundle.diagnostics=dict(auxiliary=b.quality,source_hashes=SOURCE_HASHES)
    check_source();return bundle,p,count,curve

def fit(spec,df,y,tr,va=None,fixed=None,seed=t.SEED,progress=None):
    return (fit_neural if spec['kind']=='tabm' else fit_learned)(spec,df,y,tr,va,fixed,seed,progress)
