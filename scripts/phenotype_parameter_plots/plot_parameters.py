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
#COLOR_BY_METRIC="fitness_at_90"
#COLOR_BY_METRIC="fitness"


#compares the points within their sets instead of absolute
RELATIVE_COLOR_PLOTTING_MODE=False


VIOLIN_MODE=True
#VIOLIN_MODE=False

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

#genomes[ ONE_VALUE ] = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/phenotypes.txt"
#genomes[ ONE_VALUE ] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_MOD_ALL_DATA.csv"


#genomes["CPG3_MOD"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_MOD_ALL_DATA.csv" 
#genomes["CPG3_STD"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_STD_ALL_DATA.csv" 

genomes["RPG3_MOD"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/RPG3_MOD_ALL_DATA.csv" 
genomes["RPG3_STD"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/RPG3_STD_ALL_DATA.csv" 


#genomes["CPG3_STD_DM4"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_STD_ALL_DATA.csv"
#genomes["CPG3_STD_DM6"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_STD_ALL_DATA.csv"
#genomes["CPG3_STD_DM1"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_STD_ALL_DATA.csv"
#genomes["CPG3_STD_DM10"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_STD_ALL_DATA.csv"
#genomes["CPG3_STD_DM15"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_STD_ALL_DATA.csv"



#CPG3_STD
seeds["CPG3_STD_DM4"]=   [2, 5, 9, 15, 21, 25, 28, 30, 35, 37, 41, 45, 51, 54, 63, 65, 67, 75, 85, 86, 87, 91, 92, 96, 97]
seeds["CPG3_STD_DM6"] =  [4, 8, 11, 19, 29, 33, 34, 38, 40, 42, 48, 59, 60, 77, 79, 80, 81, 98]
seeds["CPG3_STD_DM1"] =  [18, 26, 36, 43, 57, 58, 74, 78, 93, 95]
seeds["CPG3_STD_DM10"] = [3, 6, 27, 46, 66, 70, 76]
seeds["CPG3_STD_DM15"] = [12, 20, 32, 56, 83]


 
#CPG3_MOD
seeds["CPG3_MOD_DM5"] =  [5, 9, 15, 16, 18, 21, 24, 25, 30, 33, 35, 37, 39, 41, 46, 50, 51, 52, 56, 60, 63, 65, 68, 69, 81, 82, 87, 92, 96, 98]
seeds["CPG3_MOD_DM10"] = [2, 3, 6, 20, 40, 42, 58, 64, 66, 70, 72, 79, 86, 90,94,100]
seeds["CPG3_MOD_DM4"] =  [10, 27, 29, 44, 45, 47, 54, 67, 75, 95]
seeds["CPG3_MOD_DM8"] =  [8, 12, 73, 74, 80, 93]
seeds["CPG3_MOD_DM9"] =  [14, 19, 55, 78, 84]
seeds["CPG3_MOD_DM29"] = [4, 11, 26, 32, 61]


#genomes["CPG3_MOD_DM5"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_MOD_ALL_DATA.csv" 
#genomes["CPG3_MOD_DM10"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_MOD_ALL_DATA.csv" 
#genomes["CPG3_MOD_DM4"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_MOD_ALL_DATA.csv" 
#genomes["CPG3_MOD_DM8"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_MOD_ALL_DATA.csv" 
#genomes["CPG3_MOD_DM9"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_MOD_ALL_DATA.csv" 
#genomes["CPG3_MOD_DM29"] = "/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/master_data_csv_builder/CPG3_MOD_ALL_DATA.csv" 




seeds["CPG3_MOD_BS_SWITCH"] = (10,27,29,44,45,47,54,75,95,67)
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
exclude_list["CPG3_STD_DM4"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")
exclude_list["CPG3_STD_DM6"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")
exclude_list["CPG3_STD_DM1"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")
exclude_list["CPG3_STD_DM10"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")
exclude_list["CPG3_STD_DM15"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")


exclude_list["CPG3_MOD"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")
exclude_list["CPG3_MOD_DM5"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")
exclude_list["CPG3_MOD_DM10"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")
exclude_list["CPG3_MOD_DM4"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")
exclude_list["CPG3_MOD_DM8"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")
exclude_list["CPG3_MOD_DM9"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")
exclude_list["CPG3_MOD_DM29"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3", "w_AS->1", "w_AS->2","w_AS->3")



parameter_label_map={}
parameter_label_map["bias1"]="bias FT"
parameter_label_map["bias2"]="bias BS"
parameter_label_map["bias3"]="bias FS"
parameter_label_map["w_AS->1"]="sW FT"
parameter_label_map["w_AS->2"]="sW BS"
parameter_label_map["w_AS->3"]="sW FS"


exclude_list["RPG3_STD"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3")
exclude_list["RPG3_MOD"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3")

exclude_list["RPG3_STD"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3","w_1->1","w_1->2","w_1->3","w_2->1","w_2->2","w_2->3","w_3->1","w_3->2","w_3->3" )
exclude_list["RPG3_MOD"]=( "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3","w_1->1","w_1->2","w_1->3","w_2->1","w_2->2","w_2->3","w_3->1","w_3->2","w_3->3" )


always_exclude_list =["fitness","robustness","fitness_at_90", "seed", "recep1","recep2", "recep3", "timConst1", "timConst2","timConst3"]


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
    ax.set_xticklabels(labels, rotation=65, fontsize=fs-2)  #, color=colors )   #'vertical')
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
  
  count = 0
  for header in sorted(parameter_dict.keys()):
    
    if header in exclude_list[label] or header in always_exclude_list:
        continue
    #if not "ss" in header:  #hack to get fitness and robustness removed from plots - can't continue, because 
    #ALIFE2018HACK
    
    
    
    labels0.append( parameter_label_map[header] )
    data0.append(  parameter_dict[header] )
    
    
    
    if COLOR_POINTS_MODE:	
      raw_metric_column = parameter_dict[COLOR_BY_METRIC]
      
      mn=0
      mx=1
      if RELATIVE_COLOR_PLOTTING_MODE:
        mn = min( raw_metric_column )
        mx = max( raw_metric_column ) 
        if mx == mn:
          mx = 1
          mn = 0 
      
      for c in raw_metric_column:
        #if c == mx or c == mn:
        #  print( "c: {}".format(c ))
        
        # scale  min + percentage
        #  0.1  0.9    
        #      0         .8
        #      .8        .8
        c = (c-mn)/ ( mx-mn)
        c =  min( 1, max( 0, c))
        #   if c =0   alpha =1, if c =1 alpha =1
        #  f( 0.5) = 0,  f(0) = 1  f(1) = 1   
        #  f(x) =  (x-1)**2 
        alpha = max(0.1, 4*(c-0.5)**2)
        #alpha=0.5
        
        scatter_color.append( (1-c, c, 0.0,  alpha)  )
        count += 1


  fs = 13  # fontsize
  
  x = len(labels0)
  y= 4
  ALIFE2018_HACK=True
  if ALIFE2018_HACK:
    x=3
    y=4
  
  
  fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(x,y) , squeeze=False)

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
    X = np.array( scatter_color )
    axes[0, 0].scatter( scatter_data_x, scatter_data_y, c=scatter_color )   #'r.',alpha=0.2, marker='o', color=scatter_color) 
    #print( "exit")
    #quit()
  elif not VIOLIN_MODE:
    axes[0, 0].plot( scatter_data_x, scatter_data_y, 'r.',alpha=0.2, marker='o') 
  
  
  
  #ALIFE2018
  
  if label=="RPG3_STD":
    axes[0, 0].set_title("Evolved Without Modulation      ", fontsize=fs)
  elif label =="RPG3_MOD":
    axes[0, 0].set_title("Evolved With Modulation ", fontsize=fs)
  else:
    axes[0, 0].set_title(label, fontsize=fs)
  
  standardAxis = axes[0][0]
  set_axis_style( standardAxis, labels0)
  standardAxis.set_ylabel('Parameter Value',fontsize=fs)  # to Oscillatory Neuromodulation Signal')
     
  #for ax in axes.flatten():
  #    set_axis_style(ax, labels0)
        
  #fig.suptitle("Network Parameter Distributions")
  #fig.tight_layout()
  fig.subplots_adjust(bottom=0.17,left=0.225,right=0.95,top=0.9)

  #fig.subplots_adjust(hspace=0.4)
  if COLOR_POINTS_MODE:
    plt.savefig("parameter_coloredfitnessplot_{}.png".format(label) )
  elif VIOLIN_MODE:
    plt.savefig("parameter_violinplot_{}.png".format(label) )
  else:
    plt.savefig("parameter_boxplot_{}.png".format(label) )

print("got to end")
#print( label )