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


VIOLIN_MODE=False

SUFFIX="ROBUSTNESS_RESULTS_AMP_.csv"
#SUFFIX="ROBUSTNESS_RESULTS_CONST_NEG_-.csv"
#SUFFIX="ROBUSTNESS_RESULTS_CONST_POS_.csv"
SUFFIX="ROBUSTNESS_RESULTS_CONSTANT_.csv"



#location for DATA from experiments and PLOTS
DATA="../../DATA"
PLOTS="../../PLOTS/TESTS/"
if len( sys.argv) < 2:
  print("Usage:   python robustness_plotter.py [DATA.csv] ")
  print("Will save a robustness summary file." )
  quit()

csv_path=sys.argv[1]

re.sub( csv_path, "" ,"" )
experiment_title = re.sub(r'.*DATA/','', csv_path )
experiment_title = re.sub(r'\/.*','', experiment_title )
job_title = re.sub(r'.*DATA/[^/]*/','', csv_path )
job_title = re.sub(r'\/.*','', job_title )
robust_label = re.sub(r'.*DATA/[^/]*/','', csv_path )
robust_label = re.sub(r'.*/','', robust_label )
robust_label = re.sub(r'.csv','', robust_label )

#save file here
summary_filename = "{}/TESTS/{}/{}/VIOLIN_ROBUSTNESS_{}.png".format(PLOTS, experiment_title, job_title, robust_label)

###REALLY WE WANT TO COMPARE A LOT HERE


robustness0_csvs=[]
robustness1_csvs=[]

#robustness_csvs.append("../../DATA/MPG345_FAST/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/ROBUSTNESS_RESULTS_AMP_.csv")
#robustness_csvs.append("../../DATA/MPG345_FAST/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-standard/ROBUSTNESS_RESULTS_AMP_.csv")
#robustness_csvs.append("../../DATA/MPG345_FAST/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-standard/ROBUSTNESS_RESULTS_AMP_.csv")
#robustness_csvs.append("../../DATA/MPG345_FAST/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/ROBUSTNESS_RESULTS_AMP_.csv")
#robustness_csvs.append("../../DATA/MPG345_FAST/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/ROBUSTNESS_RESULTS_AMP_.csv")
#robustness_csvs.append("../../DATA/MPG345_FAST/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/ROBUSTNESS_RESULTS_AMP_.csv")

#MODULATION ENABLED



robustness1_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )
robustness1_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-4_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )
robustness1_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-5_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )



robustness1_csvs.append( "../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )
robustness1_csvs.append( "../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )
robustness1_csvs.append( "../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )

#robustness1_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )
#robustness1_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )
#robustness1_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )

robustness1_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )
robustness1_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-4_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )
robustness1_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-5_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"+SUFFIX )



robustness0_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )
robustness0_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-4_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )
robustness0_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-5_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )


robustness0_csvs.append( "../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )
robustness0_csvs.append( "../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )
robustness0_csvs.append( "../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )


#robustness0_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )
#robustness0_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )
#robustness0_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )

robustness0_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )
robustness0_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-4_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )
robustness0_csvs.append( "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-5_sim-100run-500gen_signal-SINE-1p_M-standard/"+SUFFIX )



pos = range(0, len(robustness0_csvs))
labels0=[ "CPG3","CPG4","CPG5","MPG3","MPG4","MPG5","RPG3","RPG4","RPG5" ]
labels1=[ "CPG3","CPG4","CPG5","MPG3","MPG4","MPG5","RPG3","RPG4","RPG5" ]


data0=[]
for robustness_csv in robustness0_csvs:
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
      
      d.append( robustness )
                              
  data1.append( np.asarray(d) ) 

#################


# fake data
fs = 10  # fontsize
#pos = [1, 2, 4, 5, 7, 8]
#data = [np.random.normal(0, std, size=100) for std in pos]

#https://stackoverflow.com/questions/19953348/error-when-looping-to-produce-subplots
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6) , squeeze=False)

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
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.1)
    ax.set_xlim(0.25, len(labels) + 0.75)
    ax.set_xlabel('Sample name')



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
    axes[0, 0].boxplot(data0, color="blue")

axes[0, 0].set_title('Comparing Network Robustness', fontsize=fs)


if VIOLIN_MODE:
    customize(axes[0, 1], data1 )
else:
    axes[0, 1].boxplot(data1)


axes[0, 1].boxplot(data1)

#axes[0, 1].violinplot(data1, pos, points=20, widths=0.3,
#                      showmeans=True, showextrema=True, showmedians=True)


axes[0, 1].set_title('Comparing Network Robustness', fontsize=fs)








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

standardAxis.set_xlabel('Evolved Without Neuromodulation Groups')
standardAxis.set_ylabel('Robustness to Oscillatory Noise')
modulationAxis.set_xlabel('Evolved With Neuromodulation Groups')
modulationAxis.set_ylabel('Robustness to Oscillatory Noise')

 
#for ax in axes.flatten():
#    set_axis_style(ax, labels0)
    

fig.suptitle("Violin Plotting Examples")

fig.subplots_adjust(hspace=0.4)

if VIOLIN_MODE:
    plt.savefig("violinplot_{}.png".format(SUFFIX) )
else:
    plt.savefig("boxplot_{}.png".format(SUFFIX) )