import csv
import sys
import re
import random
import numpy as np
import matplotlib as mpl
import matplotlib.mlab as mlab
#headless mode
mpl.use('Agg')
import matplotlib.pyplot as plt




fs = 18
x_fontsize=14

font_rotation=65

#USE_FIRST_FAIL=False  #True
USE_FIRST_FAIL=False

VIOLIN_MODE=False

SUFFIX="ROBUSTNESS_RESULTS_AMP_.csv"
#SUFFIX="ROBUSTNESS_RESULTS_CONST_NEG_-.csv"
#SUFFIX="ROBUSTNESS_RESULTS_CONST_POS_.csv"
#SUFFIX="ROBUSTNESS_RESULTS_CONSTANT_.csv"

MPG_SUFFIX_OFF="ROBUSTNESS_RESULTS_SA_OFF_AMP_.csv"
MPG_SUFFIX_ON="ROBUSTNESS_RESULTS_SA_ON_AMP_.csv"


#location for DATA from experiments and PLOTS
DATA="../../../DATA"
PLOTS="../../../PLOTS/TESTS/"


#save file here
#summary_filename = "{}/TESTS/{}/{}/VIOLIN_ROBUSTNESS_{}.png".format(PLOTS, experiment_title, job_title, robust_label)

###REALLY WE WANT TO COMPARE A LOT HERE


robustness0_csvs=[]
robustness1_csvs=[]

#robustness_csvs.append("../../../DATA/MPG345_FAST/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/ROBUSTNESS_RESULTS_AMP_.csv")
#robustness_csvs.append("../../../DATA/MPG345_FAST/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-standard/ROBUSTNESS_RESULTS_AMP_.csv")
#robustness_csvs.append("../../../DATA/MPG345_FAST/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-standard/ROBUSTNESS_RESULTS_AMP_.csv")
#robustness_csvs.append("../../../DATA/MPG345_FAST/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/ROBUSTNESS_RESULTS_AMP_.csv")
#robustness_csvs.append("../../../DATA/MPG345_FAST/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/ROBUSTNESS_RESULTS_AMP_.csv")
#robustness_csvs.append("../../../DATA/MPG345_FAST/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/ROBUSTNESS_RESULTS_AMP_.csv")

#MODULATION ENABLED



robustness1_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )
robustness1_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-4_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )
robustness1_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-5_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )


#ADD LATER TO COMPARE TO CPG
robustness1_csvs.append( "../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+MPG_SUFFIX_OFF )
robustness1_csvs.append( "../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+MPG_SUFFIX_OFF )
robustness1_csvs.append( "../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+MPG_SUFFIX_OFF )

robustness1_csvs.append( "../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+MPG_SUFFIX_ON )
robustness1_csvs.append( "../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+MPG_SUFFIX_ON )
robustness1_csvs.append( "../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+MPG_SUFFIX_ON )



#robustness1_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )
#robustness1_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )
#robustness1_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )

robustness1_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )
robustness1_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-4_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )
robustness1_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-5_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )



robustness0_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )
robustness0_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-4_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )
robustness0_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-5_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )

#ADD LATER TO COMPARE TO CPG
robustness0_csvs.append( "../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/"+MPG_SUFFIX_OFF )
robustness0_csvs.append( "../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-standard/"+MPG_SUFFIX_OFF )
robustness0_csvs.append( "../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-standard/"+MPG_SUFFIX_OFF )

robustness0_csvs.append( "../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/"+MPG_SUFFIX_ON )
robustness0_csvs.append( "../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-standard/"+MPG_SUFFIX_ON )
robustness0_csvs.append( "../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-standard/"+MPG_SUFFIX_ON )


#robustness0_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )
#robustness0_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )
#robustness0_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )

robustness0_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )
robustness0_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-4_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )
robustness0_csvs.append( "../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-5_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )



pos = range(0, len(robustness0_csvs))
labels0=[ "CPG3","CPG4","CPG5","MPG3-","MPG4-","MPG5-","MPG3+","MPG4+","MPG5+","RPG3","RPG4","RPG5" ]
labels1=[ "CPG3","CPG4","CPG5","MPG3-","MPG4-","MPG5-","MPG3+","MPG4+","MPG5+","RPG3","RPG4","RPG5" ]

#trying to add color
CPG_COLOR='blue'
MPG1_COLOR='lightgreen'
MPG2_COLOR='green'
RPG_COLOR='red'
colors = [CPG_COLOR,CPG_COLOR,CPG_COLOR,MPG1_COLOR,MPG1_COLOR,MPG1_COLOR,MPG2_COLOR,MPG2_COLOR,MPG2_COLOR,RPG_COLOR,RPG_COLOR,RPG_COLOR]

data0=[]
for robustness_csv in robustness0_csvs:
  d=[]
  with open( robustness_csv  ) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      if not 'robustness' in row:
        print( robustness_csv )
        print("Are you sure you specified the correct csv file? It must have a 'noise' in the header to work in this mode")
        quit()
                    
      seed =  row['seed']
      fitness =  row['fitness']
      fitness_at_90 = row['fitness_at_90']
      robustness = float( row['robustness'] )
      
      if USE_FIRST_FAIL:
        d.append( robustness/2 )
      else:
        d.append( robustness )
                              
  data0.append( np.asarray(d) ) 

#################
data1=[]
for robustness_csv in robustness1_csvs:
  d=[]
  with open( robustness_csv  ) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      if not 'robustness' in row:
        print("Are you sure you specified the correct csv file? It must have a 'noise' in the header to work in this mode")
        quit()
                    
      seed =  row['seed']
      fitness =  row['fitness']
      fitness_at_90 = row['fitness_at_90']
      robustness = float( row['robustness'] )
      
      if USE_FIRST_FAIL:
        d.append( robustness/2 )
      else:
        d.append( robustness )
      
                              
  data1.append( np.asarray(d) ) 

#################



#https://stackoverflow.com/questions/19953348/error-when-looping-to-produce-subplots
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(7, 3.5) , squeeze=False)

#print( len(data0) )
#print( len( pos ))

#axes[0, 0].violinplot(data0, pos, points=20, widths=0.3,
#                      showmeans=True, showextrema=True, showmedians=True)


######
def adjacent_values(vals, q1, q3):
    upper_adjacent_value = q3 + (q3 - q1) * 1.5
    upper_adjacent_value = np.clip(upper_adjacent_value, q3, vals[-1])

    lower_adjacent_value = q1 - (q3 - q1) * 1.5
    lower_adjacent_value = np.clip(lower_adjacent_value, vals[0], q1)
    return lower_adjacent_value, upper_adjacent_value

def set_axis_style(ax, labels):
    ax.get_xaxis().set_tick_params(direction='out')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks(np.arange(1, len(labels) + 1))
    
    ax.set_xticklabels(labels, rotation=font_rotation,fontsize=x_fontsize )  #, color=colors )   #'vertical')
    if USE_FIRST_FAIL:
        ax.set_ylim(0, 0.525)
    else:
        ax.set_ylim(0, 1.05)
    ax.set_xlim(0.25, len(labels) + 0.75)
    ax.set_xlabel('Sample name')
    
    #colors defined above
    for xtick, color in zip(ax.get_xticklabels(), colors):
        xtick.set_color(color)



########################

#ax2 = axes[0, 0]
#data = data0



def customize(ax2, data):

  parts = ax2.violinplot(
          data,  showmeans=False, showmedians=False,
          showextrema=False)

  for pc in parts['bodies']:
      pc.set_facecolor('#D43F3A')
      pc.set_edgecolor('black')
      pc.set_alpha(1)

  quartile1, medians, quartile3 = np.percentile(data, [25, 50, 75], axis=1)
  whiskers = np.array([
      adjacent_values(sorted_array, q1, q3)
      for sorted_array, q1, q3 in zip(data, quartile1, quartile3)])
  whiskersMin, whiskersMax = whiskers[:, 0], whiskers[:, 1]

  inds = np.arange(1, len(medians) + 1)
  ax2.scatter(inds, medians, marker='o', color='white', s=30, zorder=3)
  ax2.vlines(inds, quartile1, quartile3, color='k', linestyle='-', lw=5)
  ax2.vlines(inds, whiskersMin, whiskersMax, color='k', linestyle='-', lw=1)


if VIOLIN_MODE:
    customize(axes[0, 0], data0 )
else:
    bplot1 = axes[0, 0].boxplot(data0, patch_artist=True)  #, color="blue")


#axes[0, 0].set_title('Networks Evolved Without Neuromodulation', fontsize=fs)


if VIOLIN_MODE:
    customize(axes[0, 1], data1 )
else:
    bplot2 = axes[0, 1].boxplot(data1, patch_artist=True)

    
    for bplot in (bplot1, bplot2):
        for patch, color in zip(bplot['boxes'], colors):
            patch.set_facecolor(color)


#axes[0, 1].violinplot(data1, pos, points=20, widths=0.3,
#                      showmeans=True, showextrema=True, showmedians=True)

#axes[0, 1].set_title('Networks Evolved With Neuromodulation', fontsize=fs)
#


#for ax in axes.flatten():
#    ax.set_yticklabels([])

def set_axis_style2(ax, labels):
    #ax.get_xaxis().set_tick_params(direction='out')
    #ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks(np.arange(0, len(labels) ))
    ax.set_xticklabels(labels)
#    ax.set_xlim(0.25, len(labels) + 0.75)


standardAxis = axes[0][0]
modulationAxis = axes[0][1] 


set_axis_style( standardAxis, labels0)
set_axis_style( modulationAxis, labels0)

standardAxis.set_xlabel('Brittle Networks', fontsize=fs)
modulationAxis.set_xlabel('Robust Networks',fontsize=fs)

if USE_FIRST_FAIL:
    standardAxis.set_ylabel('Max AMP Success',fontsize=fs)  # to Oscillatory Neuromodulation Signal')
    #modulationAxis.set_ylabel('Max AMP Success',fontsize=fs)  # to Oscillatory Neuromodulation Signal')
else:
    standardAxis.set_ylabel('Robustness',fontsize=fs)  # to Oscillatory Neuromodulation Signal')
    #modulationAxis.set_ylabel('Robustness',fontsize=fs)  # to Oscillatory Neuromodulation Signal')

plt.setp(modulationAxis.get_yticklabels(), visible=False)

plt.setp(standardAxis.get_yticklabels(), fontsize=x_fontsize)
 
#for ax in axes.flatten():
#    set_axis_style(ax, labels0)
    
#fig.subplots_adjust(hspace=0.4)

fig.tight_layout()

if USE_FIRST_FAIL:
    PREFIX="FAIL_FIRST_"
else:
    PREFIX=""
    
SUFFIX =re.sub("_.csv","",SUFFIX)
    
if VIOLIN_MODE:
    plt.savefig("{}violinplot_{}_fontsize{}_{}.png".format(PREFIX, SUFFIX, fs, x_fontsize) )
else:
    plt.savefig("{}boxplot_{}_fontsize{}_{}.png".format(PREFIX, SUFFIX, fs, x_fontsize) )
