"""Training-fold-only learned feature blocks, with inner OOF training transforms."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'round4'))
import round4 as t
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import r2_score

def frame(df,mode):return t.prev.r.old.features(df,'raw') if mode=='raw' else t.prev.features(df,'signed')

class ScoreReconstruction:
    def _fit(self,x,target,indices):
        enc=t.prev.r.Encoder('lgb',False).fit(x.iloc[indices]);model=lgb.LGBMRegressor(n_estimators=300,learning_rate=.04,
            num_leaves=15,min_child_samples=100,reg_lambda=20,verbosity=-1,n_jobs=4,random_state=t.SEED,
            deterministic=True,force_col_wise=True)
        model.fit(enc.transform(x.iloc[indices]),target[indices]);return model,enc
    def fit_transform(self,df,y,seed):
        base=frame(df,'signed').reset_index(drop=True);raw=frame(df,'raw').reset_index(drop=True);self.models={};self.quality={};out=base.copy()
        folds=list(StratifiedKFold(3,shuffle=True,random_state=seed+41).split(raw,y))
        for col in ['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3']:
            x=raw.drop(columns=col);target=raw[col].to_numpy();observed=np.isfinite(target);pred=np.zeros(len(df))
            for a,b in folds:
                model,enc=self._fit(x,target,a[observed[a]]);pred[b]=model.predict(enc.transform(x.iloc[b]))
            self.quality[col]=dict(observed_rows=int(observed.sum()),auxiliary_oof_r2=float(r2_score(target[observed],pred[observed])))
            self.models[col]=self._fit(x,target,np.flatnonzero(observed))
            out[col+'_RECONSTRUCTED']=pred;out[col+'_RESIDUAL']=target-pred
        return out
    def transform(self,df):
        raw=frame(df,'raw');out=frame(df,'signed').copy()
        for col,(model,enc) in self.models.items():
            pred=model.predict(enc.transform(raw.drop(columns=col)));out[col+'_RECONSTRUCTED']=pred;out[col+'_RESIDUAL']=raw[col].to_numpy()-pred
        return out

class InteractionRisk:
    def keys(self,x):
        z=x.copy();z['AGE5']=((-z.DAYS_BIRTH/365.25)//5).astype('Int64').astype(str)
        z['EXT_MISSING']=z[['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3']].isna().astype(int).astype(str).agg(''.join,axis=1)
        for name,edges in self.edges.items():
            a=z[name].to_numpy();z[name+'_BIN']=np.where(np.isfinite(a),np.searchsorted(edges,a,side='right'),-1).astype(str)
        pairs=[('NAME_CONTRACT_TYPE','TERM_ROUND_6_CATEGORY'),('NAME_EDUCATION_TYPE','AGE5'),('NAME_INCOME_TYPE','OCCUPATION_TYPE'),
            ('CODE_GENDER','AGE5'),('EXT_SOURCE_2_BIN','AGE5'),('EXT_MEAN_BIN','EXT_MISSING'),('AMT_CREDIT_BIN','CREDIT_TERM_BIN'),
            ('CREDIT_TERM_BIN','NAME_CONTRACT_TYPE')]
        return {a+'__'+b:z[a].astype(str)+'|'+z[b].astype(str) for a,b in pairs}
    def maps(self,keys,y,ix):
        mean=float(y[ix].mean());maps={}
        for name,key in keys.items():
            a=pd.DataFrame(dict(key=key.iloc[ix].to_numpy(),y=y[ix])).groupby('key').y.agg(['sum','count'])
            maps[name]=a
        return maps,mean,len(ix)
    def encode(self,keys,ix,statistics):
        maps,mean,n=statistics;out={}
        for name,key in keys.items():
            k=key.iloc[ix];counts=k.map(maps[name]['count']).fillna(0).to_numpy();sums=k.map(maps[name]['sum']).fillna(0).to_numpy()
            for prior in [30,100]:out[name+f'_RISK{prior}']=(sums+prior*mean)/(counts+prior)
            out[name+'_LOG_SUPPORT']=np.log1p(counts);out[name+'_FREQUENCY']=counts/n
        return pd.DataFrame(out)
    def fit_transform(self,df,y,seed):
        x=frame(df,'signed').reset_index(drop=True);self.edges={}
        for name,q in [('EXT_SOURCE_2',20),('EXT_MEAN',20),('AMT_CREDIT',10),('CREDIT_TERM',10)]:
            a=x[name].dropna().to_numpy();self.edges[name]=np.unique(np.quantile(a,np.linspace(0,1,q+1)[1:-1]))
        keys=self.keys(x);out=None
        for a,b in StratifiedKFold(5,shuffle=True,random_state=seed+43).split(x,y):
            part=self.encode(keys,b,self.maps(keys,y,a))
            if out is None:out=pd.DataFrame(np.zeros((len(df),part.shape[1])),columns=part.columns)
            out.iloc[b]=part.to_numpy()
        self.statistics=self.maps(keys,y,np.arange(len(df)));self.quality=dict(inner_folds=5,interactions=len(keys),features=out.shape[1])
        return pd.concat([x,out],axis=1)
    def transform(self,df):
        x=frame(df,'signed').reset_index(drop=True);out=self.encode(self.keys(x),np.arange(len(x)),self.statistics)
        return pd.concat([x,out],axis=1)

def builder(mode):return ScoreReconstruction() if mode=='score_reconstruction' else InteractionRisk()
