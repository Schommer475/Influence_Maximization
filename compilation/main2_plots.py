import numpy as np
import os
import pickle
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import math
import pylab
"%matplotlib"
plt.rcParams['figure.figsize'] = [10,8]
plt.rcParams.update({'font.size': 20})
import warnings
warnings.filterwarnings('ignore')

import tikzplotlib

"""___________________"""
"Input"
name_id = '_fb4_new'    # identifier to name the output folder as results_<name_id>
regret_plots = 'yes'      # 'yes' if you want the regret plots as well 
step_size = 1            # step size for plotting
aggregate = 'cumsum'         # aggregation method used in main1_avg
linewidth = 5            # linewidth in the plots
"""___________________"""

"Looking for file and reading"
filename = 'output_adaptive.pkl'
filename_with_path = 'results'+name_id+os.sep+filename
with open(filename_with_path, 'rb') as f:
    output = pickle.load(f) 
    
#filename1 = 'output_adaptive.pkl'
#filename1_with_path = 'results'+name_id+os.sep+filename1
#with open(filename1_with_path, 'rb') as f:
#    output1 = pickle.load(f) 
#    
#filename2 = 'output_adaptive_imlin.pkl'
#filename2_with_path = 'results'+name_id+os.sep+filename2
#with open(filename2_with_path, 'rb') as f:
#    output2 = pickle.load(f)
#    
#output = pd.concat([output1,output2], axis=1)

reward_greedy = [152.194, 182.62, 217.373, 259.401]

colnames = output.columns

seed_sets = [4,8,16,32]
p = 0

NUM_COLORS = 8

for seed_set in seed_sets:
    chosen_for_reward = []
    for colname in colnames:
        #print(colname)
        if colname.split('__')[1] == str(seed_set):
            if ('avg' in colname.split('_') and 'influence' in colname.split('_') and aggregate in colname.split('_')):
                chosen_for_reward.append(colname)              
    
    "plotting"
    df_plot = output.loc[list(np.arange(0,len(output),step_size)),chosen_for_reward]
    
    #setting colors
    color_dict = {df_plot.columns[0]: "lightsalmon", df_plot.columns[1]: "coral", \
              df_plot.columns[2]: "orangered", df_plot.columns[3]: "firebrick",  \
              df_plot.columns[4]: "darkred", df_plot.columns[5]: "limegreen", \
              df_plot.columns[6]: "royalblue", df_plot.columns[7]: "mediumorchid"}

#    cm = pylab.get_cmap('gist_rainbow')
#    c = 0
#    color_dict = {}
#    for col in df_plot.columns:
#        #print(col)
#        color_dict[col] = cm(1.*c/NUM_COLORS)
#        c += 1
        
    # drop the algorithm runs exceed T
    drop = []
    for col in df_plot:
        if not math.isnan(df_plot[col][10000]):
            drop.append(df_plot[col].name)
        
    df_plot = df_plot.drop(columns=drop)
    
    #Plotting
    ax = df_plot.plot(lw=linewidth, color=[color_dict.get(x) for x in df_plot.columns])
    #ax.axhline(y=reward_greedy[p], linestyle='dashed')
    p = p+1
    ax.set_xlabel('$t$')
    
    if aggregate == 'ma':
        ax.set_ylabel("Averaged Observed Reward")
    elif aggregate == 'cumsum':
        ax.set_ylabel("Averaged Cumulative Reward")
        
    #ax.legend(['100', '200', '300', '600', '1000', 'cmab', 'dart', 'imlinucb'])
    ax.get_legend().remove()
    #ax.set_ylim([3, 14])
    #ax.set_xlim([0, 2000])
    
    ax.grid(linestyle='-', linewidth=1)
    ax.set_title('$K$ = '+str(seed_set))
    #ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))  
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))  
    ax.get_figure().savefig('results'+name_id+'/sim_reward_plot_k_'+str(seed_set)+name_id+'.eps')
    ax.get_figure().savefig('results'+name_id+'/sim_reward_plot_k_'+str(seed_set)+name_id+'.jpg')
    
    "saving as a .tex to be used in latex documents"
    #tikzplotlib.clean_figure()
    #tikzplotlib.save('results'+name_id+'/sim_reward_plot_k_'+str(seed_set)+name_id+'.tex')

# Create legend
# Create a color palette
palette = dict(zip(['100', '200', '300', '600', '1000', 'cmab', 'dart', 'imlinucb'], \
                   color_dict.values()))
handles = [mpl.patches.Patch(color=palette[x], label=x) for x in palette.keys()]
fig2 = plt.figure()
ax2 = fig2.add_subplot()
ax2.axis('off')
legend = ax2.legend(handles=handles, frameon=False, loc='lower center', ncol=10,)
fig  = legend.figure
fig.canvas.draw()
bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
fig.savefig('results'+name_id+'/reward_legend.png', dpi="figure", bbox_inches=bbox)

if regret_plots == 'yes':
    for seed_set in seed_sets:   
        chosen_for_regret = []
        for colname in colnames:
            if colname.split('__')[1] == str(seed_set):
                if ('avg' in colname.split('_') and 'regret' in colname.split('_') and aggregate in colname.split('_')):
                    chosen_for_regret.append(colname)
    
        "plotting"   
        df_plot = output.loc[list(np.arange(0,len(output),step_size)),chosen_for_regret]
    
        #setting colors
        color_dict = {df_plot.columns[0]: "lightsalmon", df_plot.columns[1]: "coral", \
              df_plot.columns[2]: "orangered", df_plot.columns[3]: "firebrick",  \
              df_plot.columns[4]: "darkred", df_plot.columns[5]: "limegreen", \
              df_plot.columns[6]: "royalblue", df_plot.columns[7]: "mediumorchid"}

#        cm = pylab.get_cmap('gist_rainbow')
#        c = 0
#        color_dict = {}
#        for col in df_plot.columns:
#            #print(col)
#            color_dict[col] = cm(1.*c/NUM_COLORS)
#            c += 1
            
        # drop the algorithm runs exceed T
        drop = []
        for col in df_plot:
            if not math.isnan(df_plot[col][10000]):
                drop.append(df_plot[col].name)
            
        df_plot = df_plot.drop(columns=drop)
        ax = df_plot.plot(lw=linewidth, color=[color_dict.get(x) for x in df_plot.columns])
        ax.set_xlabel('$t$')
        if aggregate == 'ma':
            ax.set_ylabel("Averaged Observed Regret")
        elif aggregate == 'cumsum':
            ax.set_ylabel("Averaged Cumulative Regret")
            
        ax.get_legend().remove()
        #ax.legend(['100', '200', '300', '600', '1000', 'cmab', 'dart','imlinucb'])
        #ax.legend(['Adaptive-Greedy, C = 5','Adaptive-Greedy, C = 10','Adaptive-Greedy, C = 20','Adaptive-Greedy, C = 30'\
        #       ,'DART','CMAB-SM','$\epsilon$-CD, $\epsilon$ = 0.10','$\epsilon$-CD, $\epsilon$ = 0.25','UCB','Greedy'])
        ax.grid(linestyle='-', linewidth=1)
        ax.set_title('$K$ = '+str(seed_set))
        
        #ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))  
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        ax.get_figure().savefig('results'+name_id+'/sim_regret_plot_k_'+str(seed_set)+name_id+'.eps')
        ax.get_figure().savefig('results'+name_id+'/sim_regret_plot_k_'+str(seed_set)+name_id+'.jpg')   
        
        "saving as a .tex to be used in latex documents"
        #tikzplotlib.clean_figure()
        #tikzplotlib.save('results'+name_id+'/sim_regret_plot_k_'+str(seed_set)+name_id+'.tex')
        
# Create legend
# Create a color palette
palette = dict(zip(['100', '200', '300', '600', '1000', 'cmab', 'dart', 'imlinucb'], \
                   color_dict.values()))
handles = [mpl.patches.Patch(color=palette[x], label=x) for x in palette.keys()]
fig2 = plt.figure()
ax2 = fig2.add_subplot()
ax2.axis('off')
legend = ax2.legend(handles=handles, frameon=False, loc='lower center', ncol=10,)
fig  = legend.figure
fig.canvas.draw()
bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
fig.savefig('results'+name_id+'/regret_legend.png', dpi="figure", bbox_inches=bbox)    