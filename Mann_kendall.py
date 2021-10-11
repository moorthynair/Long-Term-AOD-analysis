# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 21:24:49 2021

@author: HP
"""

import pandas as pd
import numpy as np
from scipy import stats
import pymannkendall as mk
import glob

data = pd.read_excel('C:/Users/HP/Desktop/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/stat_individual_raster/bihar_state_stat.xlsx')
data.describe()
data['seq']= np.arange(1,229,1)
tsp = stats.theilslopes(datay['mean'], datay['seq'], 0.95)
tsp
data['mean'].describe()
result = mk.original_test(datay['mean'], alpha=0.05)
result = mk.yue_wang_modification_test(data['mean'], alpha=0.05)


data_yearly = pd.read_excel('C:/Users/HP/Desktop/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/district_stat_yearly/bihar_state_yearlystat.xlsx')
data_yearly.columns
data_yearly['seq']= np.arange(1,20,1)
tsp = stats.theilslopes(data_yearly['mean'], data_yearly['seq'], 0.95)
tsp
result = mk.yue_wang_modification_test(data_yearly['mean'], alpha=0.05)
mk.trend_free_pre_whitening_modification_test(data_yearly['mean'], alpha=0.05)

j=[]
for i in glob.glob('*.xlsx'):
    if i[0:2]==str('20'):
        data = pd.read_excel(i)
        j.append(data)
        
new_data = pd.DataFrame(columns=k.columns)
t=0
while t<len(j):
    k= j[t]
    new_data = pd.concat([new_data,k])
    print(str(t) + 'is completed')
    t=t+1

mk_orignaltrend_test = pd.DataFrame(columns={'District','mk.original_trend','mk.original_slope','mk.original_intercept',
                                             'p','z','sens_slope','sens_intercept','sens_lower', 'sens_upper','mk.tfpwmk_trend','mk.tfpwmk_slope','mk.tfpwmk_intercept','p_tfpwmk','z_tfpwmk'})
dist_list = new_data['DISTRICT'].unique()
n=0
for i in dist_list:
    print(i)
    data = new_data.loc[new_data.DISTRICT==i]
    data['seq']= np.arange(1,20,1)
    result = mk.original_test(data['mean'], alpha=0.05)
    mk_orignaltrend_test .loc[n,'District']=i
    mk_orignaltrend_test .loc[n,'mk.original_trend']=result[0]
    mk_orignaltrend_test .loc[n,'mk.original_slope']=result[7]
    mk_orignaltrend_test .loc[n,'mk.original_intercept']=result[8]
    mk_orignaltrend_test .loc[n,'p']=result[2]
    mk_orignaltrend_test .loc[n,'z']=result[3]
    senslope = stats.theilslopes(data['mean'],data['seq'], alpha=0.95)
    mk_orignaltrend_test .loc[n,'sens_slope']=senslope[0]
    mk_orignaltrend_test .loc[n,'sens_intercept']=senslope[1]
    mk_orignaltrend_test .loc[n,'sens_lower']=senslope[2]
    mk_orignaltrend_test .loc[n,'sens_upper']=senslope[3]
    tfpwmk= mk.trend_free_pre_whitening_modification_test(data['mean'], alpha=0.05)
    mk_orignaltrend_test .loc[n,'mk.tfpwmk_trend']=tfpwmk[0]
    mk_orignaltrend_test .loc[n,'mk.tfpwmk_slope']=tfpwmk[7]
    mk_orignaltrend_test .loc[n,'mk.tfpwmk_intercept']=tfpwmk[8]
    mk_orignaltrend_test .loc[n,'p_tfpwmk']=tfpwmk[2]
    mk_orignaltrend_test .loc[n,'z_tfpwmk']=tfpwmk[3]
    n=n+1
    print(str(n) +'has started')
    
##retrive month data for Mann Kendall & sens slope
j=[]
for i in glob.glob('*.xlsx'):    
    if i[-9:-7]=='20':
        print(i)
        data = pd.read_excel(i)
        j.append(data)

new_data =pd.read_excel('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/stat_individual_raster/Dec-2002.xlsx')
new_data =pd.DataFrame(columns=new_data.columns)
t=0
while t<len(j):
    k=j[t]
    new_data =pd.concat([new_data,k])
    t=t+1

mk_orignaltrend_test = pd.DataFrame(columns={'season','h.mk','District','mk.original_trend','mk.original_slope','mk.original_intercept',
                                             'p','z','sens_slope','sens_intercept','sens_lower', 'sens_upper','mk.tfpwmk_trend','mk.tfpwmk_slope','mk.tfpwmk_intercept','p_tfpwmk','z_tfpwmk'})
dist_list = new_data['DISTRICT'].unique()
seasons = new_data['season'].unique()
n=0
for i in dist_list:
    for j in seasons:        
        data = new_data.loc[(new_data.DISTRICT==i) & (new_data.season==j)]
        data = data.groupby(['year','DISTRICT'])['mean'].mean()
        length = len(data)+1
        data['seq']= np.arange(1,length,1)
        result = mk.original_test(data['mean'], alpha=0.05)
        mk_orignaltrend_test .loc[n,'District']=i
        mk_orignaltrend_test .loc[n,'mk.original_trend']=result[0]
        mk_orignaltrend_test .loc[n,'h.mk']=result[1]
        mk_orignaltrend_test .loc[n,'mk.original_slope']=result[7]
        mk_orignaltrend_test .loc[n,'mk.original_intercept']=result[8]
        mk_orignaltrend_test .loc[n,'p']=result[2]
        mk_orignaltrend_test .loc[n,'z']=result[3]
        senslope = stats.theilslopes(data['mean'],data['seq'], alpha=0.95)
        mk_orignaltrend_test .loc[n,'sens_slope']=senslope[0]
        mk_orignaltrend_test .loc[n,'sens_intercept']=senslope[1]
        mk_orignaltrend_test .loc[n,'sens_lower']=senslope[2]
        mk_orignaltrend_test .loc[n,'sens_upper']=senslope[3]
        tfpwmk= mk.trend_free_pre_whitening_modification_test(data['mean'], alpha=0.05)
        mk_orignaltrend_test .loc[n,'mk.tfpwmk_trend']=tfpwmk[0]
        mk_orignaltrend_test .loc[n,'mk.tfpwmk_slope']=tfpwmk[7]
        mk_orignaltrend_test .loc[n,'mk.tfpwmk_intercept']=tfpwmk[8]
        mk_orignaltrend_test .loc[n,'p_tfpwmk']=tfpwmk[2]
        mk_orignaltrend_test .loc[n,'z_tfpwmk']=tfpwmk[3]
        mk_orignaltrend_test .loc[n,'season']=j
        n=n+1
    print(str(i) +'has started')
    
mk_orignaltrend_test.to_excel('MannKendall_sens_seasonal.xlsx', index=False)

winter = ["Jan",'Feb']
pre_monsoon = ["Mar",'Apr','May']
monsoon =['June','July','Aug']
post_monsoon=['Sept','Oct','Nov','Dec']

conditions = [new_data['month'].isin(winter), new_data['month'].isin(pre_monsoon),new_data['month'].isin(monsoon),new_data['month'].isin(post_monsoon)]
choices =['winter','pre_monsoon','monsoon','post_monsoon']
new_data['season']= np.select(conditions,choices)

##Mann-kendall for Bihar
new_data = pd.read_excel('G:/My on going proj/Satellite-Data-Analysis/Processed_raster/Raster_facets_savgol_updated/stat_individual_raster/bihar_state_stat.xlsx')
new_data[['month','year']]= new_data['month-year'].str.split("-",expand=True)
seasons = new_data['season'].unique().tolist()
month = new_data['month'].unique().tolist()
n=0
for j in month:
    data = new_data.loc[(new_data.month==j)]
    data = data.groupby(['year']).mean()
    length = len(data)+1
    data['seq']= np.arange(1,length,1)
    result = mk.original_test(data['mean'], alpha=0.05)
    mk_orignaltrend_test .loc[n,'District']='Bihar'
    mk_orignaltrend_test .loc[n,'mk.original_trend']=result[0]
    mk_orignaltrend_test .loc[n,'h.mk']=result[1]
    mk_orignaltrend_test .loc[n,'mk.original_slope']=result[7]
    mk_orignaltrend_test .loc[n,'mk.original_intercept']=result[8]
    mk_orignaltrend_test .loc[n,'p']=result[2]
    mk_orignaltrend_test .loc[n,'z']=result[3]
    senslope = stats.theilslopes(data['mean'],data['seq'], alpha=0.95)
    mk_orignaltrend_test .loc[n,'sens_slope']=senslope[0]
    mk_orignaltrend_test .loc[n,'sens_intercept']=senslope[1]
    mk_orignaltrend_test .loc[n,'sens_lower']=senslope[2]
    mk_orignaltrend_test .loc[n,'sens_upper']=senslope[3]
    tfpwmk= mk.trend_free_pre_whitening_modification_test(data['mean'], alpha=0.05)
    mk_orignaltrend_test .loc[n,'mk.tfpwmk_trend']=tfpwmk[0]
    mk_orignaltrend_test .loc[n,'mk.tfpwmk_slope']=tfpwmk[7]
    mk_orignaltrend_test .loc[n,'mk.tfpwmk_intercept']=tfpwmk[8]
    mk_orignaltrend_test .loc[n,'p_tfpwmk']=tfpwmk[2]
    mk_orignaltrend_test .loc[n,'z_tfpwmk']=tfpwmk[3]
    mk_orignaltrend_test .loc[n,'season']=j
    n=n+1 

mk_orignaltrend_test.to_excel('MannKendall_sens_monthly_bihar.xlsx', index=False)
