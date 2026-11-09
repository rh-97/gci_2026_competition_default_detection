"""Descriptive loan-structure analysis using development labels only."""
import os
import round2 as r
os.environ.setdefault('MPLCONFIGDIR',str(r.ART/'matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

def main():
    train,test,y,split=r.load();dev=split['development']
    a=r.features(train.iloc[dev],'finance');b=r.features(test,'finance')
    definitions=[('CREDIT_TERM',[0,6,12,18,24,36,48,60,96,np.inf],'Credit / annuity ratio (not known term)'),
        ('TERM_MULTIPLE_6_DISTANCE',np.linspace(0,.5,11),'Distance from nearest multiple of 6, normalized'),
        ('TERM_MULTIPLE_12_DISTANCE',np.linspace(0,.5,11),'Distance from nearest multiple of 12, normalized')]
    fig,axes=plt.subplots(1,3,figsize=(16,4.5),layout='constrained');tables=[];shift=[]
    for ax,(column,edges,title) in zip(axes,definitions):
        frame=pd.DataFrame({'bin':pd.cut(a[column],edges,include_lowest=True).astype(str),'target':y[dev]})
        frame=frame[frame['bin'].ne('nan')]
        groups=pd.cut(a[column],edges,include_lowest=True).cat.categories.astype(str)
        table=frame.groupby('bin',sort=False).target.agg(['count','sum','mean']).reindex(groups)
        n=table['count'].to_numpy();p=table['mean'].to_numpy();z=1.96
        center=(p+z*z/(2*n))/(1+z*z/n)
        half=z*np.sqrt((p*(1-p)+z*z/(4*n))/n)/(1+z*z/n)
        table['wilson_lower']=center-half;table['wilson_upper']=center+half
        table['feature']=column;table.to_csv(r.ART/(column.lower()+'_development_bins.csv'))
        tables.append(table.reset_index(names='bin'))
        ax.errorbar(np.arange(len(table)),p,yerr=np.vstack([p-(center-half),(center+half)-p]),fmt='o-',capsize=3,color='#35678e')
        ax.axhline(y[dev].mean(),linestyle='--',color='gray',label='Development prevalence')
        ax.set(title=title,ylabel='Observed default fraction',xticks=np.arange(len(table)),xticklabels=table.index)
        ax.tick_params(axis='x',labelrotation=65,labelsize=7)
        ax.legend(fontsize=7)
        ks=ks_2samp(a[column].dropna(),b[column].dropna())
        shift.append(dict(feature=column,development_missing=a[column].isna().mean(),test_missing=b[column].isna().mean(),KS_statistic=ks.statistic))
    fig.savefig(r.ART/'loan_structure_development.png',dpi=160);plt.close(fig)
    pd.concat(tables).to_csv(r.ART/'loan_structure_development_bins.csv',index=False)
    r.dump(r.ART/'loan_structure_distribution_check.json',{'features':shift,'label_scope':'Original development rows only',
        'interpretation':'Descriptive associations after feature exploration; confidence bars are binomial sampling intervals, not correction for selection/confounding. Ratios do not establish actual loan terms or rates.'})
    print('Saved development-only loan-structure analysis.')

if __name__=='__main__':main()
