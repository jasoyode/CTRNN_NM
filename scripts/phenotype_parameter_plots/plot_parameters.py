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


COLOR_POINTS_MODE=False

COLOR_BY_METRIC="robustness"


#VIOLIN_MODE=True
VIOLIN_MODE=False

SUFFIX="ROBUSTNESS_RESULTS_AMP_.csv"

#location for DATA from experiments and PLOTS
DATA="../../DATA"
PLOTS="../../PLOTS/TESTS/"

#IF we decide to add config later
#if len( sys.argv) < 2:
#  print("Usage:   python plot_parameters.py config.csv ")
#  print("Will save a robustness summary file." )
#  quit()
#csv_path=sys.argv[1]
#re.sub( csv_path, "" ,"" )
#experiment_title = re.sub(r'.*DATA/','', csv_path )
#experiment_title = re.sub(r'\/.*','', experiment_title )

#save file here
#summary_filename = "{}/TESTS/{}/{}/VIOLIN_ROBUSTNESS_{}.png".format(PLOTS, experiment_title, job_title, robust_label)

genomes = {}
seeds ={}




ONE_VALUE="CPG3_MOD_BS_SWITCH"

genomes[ ONE_VALUE ] = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/phenotypes.txt"



#genomes["CPG3_MOD"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_MOD_ALL_DATA.csv" 
#genomes[ ONE_VALUE ] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_MOD_ALL_DATA.csv" 


#genomes["CPG3_MOD"] = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/phenotypes.txt" 
#genomes["RPG3_STD"] = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/phenotypes.txt" 
#genomes["RPG3_MOD"] = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/phenotypes.txt"
#genomes["BEER"] = "../../DATA/CITED_DATA/phenotypes.txt"

seeds["CPG3_MOD_BS_SWITCH"] = (10,27,29,44,45,47,54,75,95)
seeds["CPG3_STD"] = range(1,101)
seeds["CPG3_MOD"] = range(1,101)
seeds["RPG3_STD"] = range(1,101)
seeds["RPG3_MOD"] = range(1,101)
seeds["BEER"] = range(2,3)
#seeds = range(1,3)

exclude_list = {}
exclude_list["CPG3_MOD_BS_SWITCH"] = ( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")
exclude_list["BEER"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")

exclude_list["CPG3_STD"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")
exclude_list["CPG3_MOD"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")

exclude_list["RPG3_STD"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3")
exclude_list["RPG3_MOD"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3")


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
    ax.set_xticklabels(labels, rotation=45)  #, color=colors )   #'vertical')
    ax.set_ylim(-16, 16)
    ax.set_xlim(0.25, len(labels) + 0.75)
    #ax.set_xlabel('Sample name')
    


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


def set_axis_style2(ax, labels):
    ax.set_xticks(np.arange(0, len(labels) ))
    ax.set_xticklabels(labels)


for label in genomes.keys():
  seed_to_parameter_dict_dict={}
  parameter_dict={}
  data0=[]
  with open( genomes[label]  ) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      if not 'bias1' in row:
        print( genomes[label] )
        print("Are you sure you specified the correct csv file? It must have a 'bias1' in the header to work in this mode")
        quit()
        
      seed =  int( row['seed'] )
      
      if seed not in seeds[ label ]:
        continue
      
      seed_to_parameter_dict_dict[seed] = {}
      
      for header in row:
        if header.strip() == "":
            continue
        #print("header: {}   row[header]: {}".format(header,  row[header] ))
        
        seed_to_parameter_dict_dict[seed][header] = row[header]
        
        if not header in parameter_dict:
          parameter_dict[header] = []
        
        parameter_dict[header].append( float(row[header]) )

  data0=[]
  labels0=[]
  if COLOR_POINTS_MODE:
    scatter_color=[]
  
  
  #####TODO need to redo the way this gets created so I can assign a color to each data point
  ###The data in master is not apparently showing the same values so there could be a problem there...
  
  
  for header in sorted(parameter_dict.keys()):
    
    if header in exclude_list[label]:
        continue
    labels0.append( header )
    data0.append(  parameter_dict[header] )
    
    
    if COLOR_POINTS_MODE:	
      c = parameter_dict[COLOR_BY_METRIC]
      print( "c: {}".format(c ))
      scatter_color.append( [c, 0.0, 0.0, 0.5] )


  fs = 10  # fontsize
  fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(len(labels0), 6) , squeeze=False)

  if not COLOR_POINTS_MODE:
    if VIOLIN_MODE:
      customize(axes[0, 0], data0 )
    else:
      bplot1 = axes[0, 0].boxplot( data0 ) #, patch_artist=True)  #, color="blue")
  
  
  scatter_data_x=[]
  scatter_data_y=[]
  
  
  count=1
  for data_row in data0:
    for data_item in data_row:
      scatter_data_x.append( count )
      scatter_data_y.append( data_item )
    count+=1
  
  
  #print( len( scatter_data_x) )
  #print( len(scatter_data_y ))
  if COLOR_POINTS_MODE:
    axes[0, 0].scatter( scatter_data_x, scatter_data_y)   #,c=scatter_color )   #'r.',alpha=0.2, marker='o', color=scatter_color) 
  elif not VIOLIN_MODE:
    axes[0, 0].plot( scatter_data_x, scatter_data_y, 'r.',alpha=0.2, marker='o') 
  
  

  axes[0, 0].set_title(label, fontsize=fs)
  standardAxis = axes[0][0]
  set_axis_style( standardAxis, labels0)
  standardAxis.set_ylabel('Parameter Value')  # to Oscillatory Neuromodulation Signal')
     
  #for ax in axes.flatten():
  #    set_axis_style(ax, labels0)
        
  fig.suptitle("Network Parameter Distributions")

  #fig.subplots_adjust(hspace=0.4)
  if COLOR_POINTS_MODE:
    plt.savefig("parameter_coloredfitnessplot_{}.png".format(label) )
  elif VIOLIN_MODE:
    plt.savefig("parameter_violinplot_{}.png".format(label) )
  else:
    plt.savefig("parameter_boxplot_{}.png".format(label) )

print("got to end")
#print( label )