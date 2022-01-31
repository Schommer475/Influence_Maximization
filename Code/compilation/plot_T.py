# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 22:01:55 2021

@author: niegu
"""

import numpy as np
import os
import pickle
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import operator
import math
import pylab
import glob
"%matplotlib"
plt.rcParams['figure.figsize'] = [10,8]
plt.rcParams.update({'font.size': 20})
import warnings
warnings.filterwarnings('ignore')
from Utilities.global_names import compilation_temp, outputs

def main():
    #==============================================================================
    # Cumulative regret plot
    
    # Mean regret dataframe
    input_dir = os.path.join(compilation_temp,'results_fb4_16_un')
    
    cmabs={}
    cmab_regret=[]
    
    for file in glob.glob(os.path.join(input_dir,"cmab*.pkl")):
        cmabs[file[:-4]]=pd.read_pickle(file)
        cmab_regret.append((len(cmabs[file[:-4]]), cmabs[file[:-4]].iloc[-1,1]))
    
    cmab_regret.sort(key=operator.itemgetter(0))
    
    cmab = [x[1] for x in cmab_regret]
    
    darts={}
    dart_regret=[]
    
    for file in glob.glob(os.path.join(input_dir,"dart*.pkl")):
        darts[file[:-4]]=pd.read_pickle(file)
        dart_regret.append((len(darts[file[:-4]]), darts[file[:-4]].iloc[-1,1]))
    
    dart_regret.sort(key=operator.itemgetter(0))
    
    dart = [x[1] for x in dart_regret]
    
    with open(os.path.join(input_dir,"imlinucb.pkl"), 'rb') as f:
        df_lin = pickle.load(f)
    
    lin_x = range(1,10001)
    lin_y = df_lin.iloc[:,1]
    lin_coef = np.polyfit(lin_x, lin_y, 1)
    poly1d_fn = np.poly1d(lin_coef) 
    # poly1d_fn is now a function which takes in x and returns an estimate for y
    
    
    ucbgr=pd.read_pickle(os.path.join(input_dir,"ucbgr.pkl"))
    ucbgr1000=list(ucbgr.iloc[np.arange(9999, 100000, 10000),1])
    ucbgr2000=list(ucbgr.iloc[np.arange(9999, 100000, 10000),3])
    ucbgr3000=list(ucbgr.iloc[np.arange(9999, 100000, 10000),5])
    ucbgr4000=list(ucbgr.iloc[np.arange(9999, 100000, 10000),7])
    
    
    x = [10000,20000,30000,40000,50000,60000,70000,80000,90000,100000]
    
    mean_plot = pd.DataFrame(list(zip(ucbgr1000,ucbgr2000,ucbgr3000,ucbgr4000,cmab,dart)),\
                           index=x,columns=['ucbgr1000','ucbgr2000','ucbgr3000','ucbgr4000','cmab','dart'])
    
    
    # Std regret dataframe
    input_dir = os.path.join(compilation_temp,'results_fb4_16_un_std')
    
    cmaberr={}
    cmab_std=[]
    
    for file in glob.glob(os.path.join(input_dir,"cmab*.pkl")):
        cmabs[file[:-4]]=pd.read_pickle(file)
        cmab_std.append((len(cmabs[file[:-4]]), cmabs[file[:-4]].iloc[-1,1]))
    
    cmab_std.sort(key=operator.itemgetter(0))
    
    cmab = [x[1] for x in cmab_std]
    
    darterr={}
    dart_std=[]
    
    for file in glob.glob(os.path.join(input_dir,"dart*.pkl")):
        darts[file[:-4]]=pd.read_pickle(file)
        dart_std.append((len(darts[file[:-4]]), darts[file[:-4]].iloc[-1,1]))
    
    dart_std.sort(key=operator.itemgetter(0))
    
    dart = [x[1] for x in cmab_std]
    
    ucbgr_std=pd.read_pickle(os.path.join(input_dir,"ucbgr.pkl"))
    ucbgr1000err=list(ucbgr_std.iloc[np.arange(9999, 100000, 10000),1])
    ucbgr2000err=list(ucbgr_std.iloc[np.arange(9999, 100000, 10000),3])
    ucbgr3000err=list(ucbgr_std.iloc[np.arange(9999, 100000, 10000),5])
    ucbgr4000err=list(ucbgr_std.iloc[np.arange(9999, 100000, 10000),7])
    
    
    err_plot = pd.DataFrame(list(zip(ucbgr1000err,ucbgr2000err,ucbgr3000err,ucbgr4000err,cmab,dart)),\
                           index=x,columns=['ucbgr1000','ucbgr2000','ucbgr3000','ucbgr4000','cmab','dart'])
    
    
    plot_T=['ucbgr1000','ucbgr2000','ucbgr3000','ucbgr4000','cmab','dart']
    mean_plot.loc[0] = [0,0,0,0,0,0]
    mean_plot = mean_plot.sort_index()
    err_plot.loc[0] = [0,0,0,0,0,0]
    err_plot = err_plot.sort_index()
    
    fig, ax = plt.subplots()
    for i in plot_T:
        #ax.plot(mean_plot[i],lw=5, marker='D',markersize=15)
        ax.errorbar(x=[0,10000,20000,30000,40000,50000,60000,70000,80000,90000,100000], y=mean_plot[i], yerr=err_plot[i],\
                    capsize=10,lw=5, marker='D',markersize=15,label=i)
        
    #ax.plot(range(1,100001), poly1d_fn(range(1,100001)), ls='--', lw='3', c='black', label="IMlinUCB")
    ax.plot(lin_y, lw='3', c='black', marker='D',markevery=9999, markersize=15, label="IMlinUCB")
    ax.set_xlabel('Horizon $T$')
    ax.set_ylabel('Cumulative Regret')
    ax.grid(linestyle='-', linewidth=1)
    ax.set_title('Cumulative Regret(k=16)')
    #ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))  
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax.legend(loc='upper left')
    
    output_dir = os.path.join(outputs, 'results_fb4_16_un')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    ax.get_figure().savefig(os.path.join(output_dir,'regret_plot_16'))
    
    #with open('./results_fb4_8_un_ma/imlinucb.pkl', 'rb') as f:
    #    lin = pickle.load(f)
    #
    #lin_x = range(1,9502)
    #lin_y = lin.iloc[:,1]
    #plt.plot(lin_y,lw=5)
    #lin_coef = np.polyfit(lin_x, lin_y, 1)
    #poly1d_fn = np.poly1d(lin_coef)
    #plt.plot(lin_x, lin_y, 'yo', lin_x, poly1d_fn(lin_x), '--k')
    #plt.title('k=8')
    #
    #with open('./results_fb4_new/output_imlinucb__1.00__8__10__10000__100__31079993.pkl', 'rb') as f:
    #    lin = pickle.load(f)
    #
    #lin_x = range(1,10001)
    #lin_y = lin['obs_influences']
    #plt.plot(lin_y)
    #lin_coef = np.polyfit(lin_x, lin_y, 1)
    #poly1d_fn = np.poly1d(lin_coef) 
    #plt.plot(lin_x, lin_y, 'yo', lin_x, poly1d_fn(lin_x), '--k')
    #plt.title('k=8')
    #
    ##==============================================================================
    ## Instantaneous reward plot
    #os.chdir('results_fb4_8_un_ma/')
    #
    #cmabs={}
    #
    #for file in glob.glob("cmab*.pkl"):
    #    cmabs[file[:-4]]=list(pd.read_pickle(file).iloc[:,0])
    #    
    #darts={}
    #
    #for file in glob.glob("dart*.pkl"):
    #    darts[file[:-4]]=list(pd.read_pickle(file).iloc[:,0])
    #
    #ucbgr=pd.read_pickle("ucbgr.pkl")
    #ucbgr1000=list(ucbgr.iloc[:,0])
    #ucbgr2000=list(ucbgr.iloc[:,2])
    #ucbgr3000=list(ucbgr.iloc[:,4])
    #ucbgr4000=list(ucbgr.iloc[:,6])
    #
    #plot1 = pd.DataFrame(list(zip(ucbgr1000[:9501],ucbgr2000[:9501],ucbgr3000[:9501],ucbgr4000[:9501],cmabs['cmab10000'],darts['dart10000'])),\
    #                     columns=['ucbgr1000','ucbgr2000','ucbgr3000','ucbgr4000','cmab','dart'])
    #
    #plot2 = pd.DataFrame(list(zip(ucbgr1000[:19501],ucbgr2000[:19501],ucbgr3000[:19501],ucbgr4000[:19501],cmabs['cmab20000'],darts['dart20000'])),\
    #                     columns=['ucbgr1000','ucbgr2000','ucbgr3000','ucbgr4000','cmab','dart'])
    #
    #plot3 = pd.DataFrame(list(zip(ucbgr1000[:29501],ucbgr2000[:29501],ucbgr3000[:29501],ucbgr4000[:29501],cmabs['cmab30000'],darts['dart30000'])),\
    #                     columns=['ucbgr1000','ucbgr2000','ucbgr3000','ucbgr4000','cmab','dart'])
    #
    #plot4 = pd.DataFrame(list(zip(ucbgr1000[:39501],ucbgr2000[:39501],ucbgr3000[:39501],ucbgr4000[:39501],cmabs['cmab40000'],darts['dart40000'])),\
    #                     columns=['ucbgr1000','ucbgr2000','ucbgr3000','ucbgr4000','cmab','dart'])
    #
    #plot5 = pd.DataFrame(list(zip(ucbgr1000[:49501],ucbgr2000[:49501],ucbgr3000[:49501],ucbgr4000[:49501],cmabs['cmab50000'],darts['dart50000'])),\
    #                     columns=['ucbgr1000','ucbgr2000','ucbgr3000','ucbgr4000','cmab','dart'])
    #
    #plot6 = pd.DataFrame(list(zip(ucbgr1000[:59501],ucbgr2000[:59501],ucbgr3000[:59501],ucbgr4000[:59501],cmabs['cmab60000'],darts['dart60000'])),\
    #                     columns=['ucbgr1000','ucbgr2000','ucbgr3000','ucbgr4000','cmab','dart'])
    #
    #plot7 = pd.DataFrame(list(zip(ucbgr1000[:69501],ucbgr2000[:69501],ucbgr3000[:69501],ucbgr4000[:69501],cmabs['cmab70000'],darts['dart70000'])),\
    #                     columns=['ucbgr1000','ucbgr2000','ucbgr3000','ucbgr4000','cmab','dart'])
    #
    #plot8 = pd.DataFrame(list(zip(ucbgr1000[:79501],ucbgr2000[:79501],ucbgr3000[:79501],ucbgr4000[:79501],cmabs['cmab80000'],darts['dart80000'])),\
    #                     columns=['ucbgr1000','ucbgr2000','ucbgr3000','ucbgr4000','cmab','dart'])
    #
    #plot9 = pd.DataFrame(list(zip(ucbgr1000[:89501],ucbgr2000[:89501],ucbgr3000[:89501],ucbgr4000[:89501],cmabs['cmab90000'],darts['dart90000'])),\
    #                     columns=['ucbgr1000','ucbgr2000','ucbgr3000','ucbgr4000','cmab','dart'])
    #
    #plot10 = pd.DataFrame(list(zip(ucbgr1000[:99501],ucbgr2000[:99501],ucbgr3000[:99501],ucbgr4000[:99501],cmabs['cmab100000'],darts['dart100000'])),\
    #                     columns=['ucbgr1000','ucbgr2000','ucbgr3000','ucbgr4000','cmab','dart'])
    #
    #plots = [plot1,plot2,plot3,plot4,plot5,plot6,plot7,plot8,plot9,plot10]
    #
    #os.chdir('../')
    #
    #os.chdir('results_fb4_8_un_ma_std/')
    #cmaberr = list(pd.read_pickle("cmab100000.pkl").iloc[:,0])
    #darterr = list(pd.read_pickle("dart100000.pkl").iloc[:,0])
    #ucbgrerr=pd.read_pickle("ucbgr.pkl")
    #ucbgr1000err=list(ucbgrerr.iloc[:,0])
    #ucbgr2000err=list(ucbgrerr.iloc[:,2])
    #ucbgr3000err=list(ucbgrerr.iloc[:,4])
    #ucbgr4000err=list(ucbgrerr.iloc[:,6])
    #err100000 = pd.DataFrame(list(zip(ucbgr1000err[:99501],ucbgr2000err[:99501],ucbgr3000err[:99501],ucbgr4000err[:99501],cmaberr,darterr)),\
    #                     columns=['ucbgr1000','ucbgr2000','ucbgr3000','ucbgr4000','cmab','dart'])
    #
    #os.chdir('../')
    #
    #fig, ax = plt.subplots()
    #ax.plot(plot10['ucbgr1000'],lw=5)
    #ax.fill_between(x=range(99501), y1=plot10['ucbgr1000']-err100000['ucbgr1000'],y2=plot10['ucbgr1000']+err100000['ucbgr1000'],alpha=0.2)
    #ax.plot(plot10['ucbgr2000'],lw=5)
    #ax.fill_between(x=range(99501), y1=plot10['ucbgr2000']-err100000['ucbgr2000'],y2=plot10['ucbgr2000']+err100000['ucbgr2000'],alpha=0.2)
    #ax.plot(plot10['ucbgr3000'],lw=5)
    #ax.fill_between(x=range(99501), y1=plot10['ucbgr3000']-err100000['ucbgr3000'],y2=plot10['ucbgr3000']+err100000['ucbgr3000'],alpha=0.2)
    #ax.plot(plot10['ucbgr4000'],lw=5)
    #ax.fill_between(x=range(99501), y1=plot10['ucbgr4000']-err100000['ucbgr4000'],y2=plot10['ucbgr4000']+err100000['ucbgr4000'],alpha=0.2)
    #ax.plot(plot10['cmab'],lw=5)
    #ax.fill_between(x=range(99501), y1=plot10['cmab']-err100000['cmab'],y2=plot10['cmab']+err100000['cmab'],alpha=0.2)
    #ax.plot(plot10['dart'],lw=5)
    #ax.fill_between(x=range(99501), y1=plot10['dart']-err100000['dart'],y2=plot10['dart']+err100000['dart'],alpha=0.2)
    #ax.axhline(y=182.62,xmin=0,xmax=100000,ls='--', lw=5)
    #ax.set_xlabel('$t$')
    #ax.grid(linestyle='-', linewidth=1)
    #ax.set_title('Instantaneous Rewards(k=8)')
    #ax.legend(['ucbgr1000','ucbgr2000','ucbgr3000','ucbgr4000','cmab','dart','greedy'])
    ##ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    #ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))  
    #ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))  
    #ax.get_figure().savefig('results_fb4_8_un_ma/reward_plot_8_{}.jpg'.format((9+1)*10000))
    
