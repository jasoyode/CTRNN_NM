import re
import os
import csv
import glob
import numpy as np
import operator  
import matplotlib as mpl
import matplotlib.mlab as mlab
#from mpl_toolkits.mplot3d import Axes3D
#from matplotlib.colors import LinearSegmentedColormap
#from sklearn.decomposition import PCA as sklearnPCA
#from sklearn.preprocessing import StandardScaler
#from mpl_toolkits.mplot3d.art3d import Line3DCollection
#from matplotlib.collections import LineCollection



PI=3.141592653589

#levels=[ 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]
levels=[ 0.9 ]


ORIENTATION="HORIZONTAL"
ORIENTATION="VERTICAL"


fs=15

MODULATION_LEVEL="0.5"

PLOT_MODES=[0.3,0.4,0.5,0.6]

#for i in range(10):
#  PLOT_MODES.append(0.05*i)
#0.1,0.2,0.3,0.4,0.5]   #,"AGG_ABS","AGG_PERC","IND_PERC"]

SAVE_PLOTS_MODE=True
SCATTER=False

#headless mode
mpl.use('Agg')
import matplotlib.pyplot as plt

import sys
sys.path.insert(0,'lib/python3.5/site-packages/')

import seaborn as sns



#location for DATA from experiments and PLOTS
DATA="../../../DATA"
PLOTS="../../../PLOTS/TESTS/"

if len( sys.argv) < 2:
  print("Usage:   python robustness_plotter.py [DATA.csv] ")
  print("Will save a robustness summary file." )
  quit()
 

EVO_COND="standard"
#EVO_COND="mod1-ON"

ROB_FILENAME="RESULTS_CONSTANT_.csv"
MPG_ON_FILENAME="RESULTS_SA_ON_CONSTANT_.csv"
MPG_OFF_FILENAME="RESULTS_SA_OFF_CONSTANT_.csv"

numplots=1

def convert_to_orientation( value, x_or_y ):
  if x_or_y =="x":
    if ORIENTATION=="VERTICAL":
      return value
    else:
      return 0
  else:
    if ORIENTATION=="VERTICAL":
      return 0
    else:
      return value

w=3
h=4



for PLOT_MODE in PLOT_MODES:
  if ORIENTATION=="VERTICAL":
    fig, axes = plt.subplots(nrows=numplots, ncols=1, figsize=(w, h), squeeze=False, sharex=True, sharey=True)
  else:
    fig, axes = plt.subplots(nrows=1, ncols=numplots, figsize=(numplots, 6), squeeze=False, sharex=True, sharey=True)
  

  axes_data_dict={}        #r,c
  """
  axes_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[ convert_to_orientation( 0, "x" ), convert_to_orientation( 0, "y" ) ]
  axes_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[ convert_to_orientation( 1, "x" ), convert_to_orientation( 1, "y" ) ]
  axes_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[ convert_to_orientation( 2, "x" ), convert_to_orientation( 2, "y" ) ]

  
  #MPG_GOOD_345
  axes_data_dict["../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_OFF_FILENAME] = axes[ convert_to_orientation( 3, "x" ), convert_to_orientation( 3, "y" ) ]
  axes_data_dict["../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_OFF_FILENAME] = axes[ convert_to_orientation( 4, "x" ), convert_to_orientation( 4, "y" ) ]
  axes_data_dict["../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_OFF_FILENAME] = axes[ convert_to_orientation( 5, "x" ), convert_to_orientation( 5, "y" ) ]
  
  axes_data_dict["../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_ON_FILENAME] = axes[ convert_to_orientation( 6, "x" ), convert_to_orientation( 6, "y" ) ]
  axes_data_dict["../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_ON_FILENAME] = axes[ convert_to_orientation( 7, "x" ), convert_to_orientation( 7, "y" ) ]
  axes_data_dict["../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_ON_FILENAME] = axes[ convert_to_orientation( 8, "x" ), convert_to_orientation( 8, "y" ) ]

  
  #axes_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[0,3]
  #axes_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[0,4]
  #axes_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[0,5]

  axes_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[ convert_to_orientation( 9, "x" ), convert_to_orientation( 9, "y" ) ]
  axes_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[ convert_to_orientation( 10, "x" ), convert_to_orientation( 10, "y" ) ]
  axes_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[ convert_to_orientation( 11, "x" ), convert_to_orientation( 11, "y" ) ]
  """
  ##########
  axes_data_dict={}        #r,c
  axes_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[ convert_to_orientation( 0, "x" ), convert_to_orientation( 0, "y" ) ]
  #MPG_GOOD_345
  axes_data_dict["../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_OFF_FILENAME] = axes[ convert_to_orientation(0, "x" ), convert_to_orientation( 0, "y" ) ]
  
  axes_data_dict["../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_ON_FILENAME] = axes[ convert_to_orientation( 0, "x" ), convert_to_orientation( 0, "y" ) ]

  axes_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[ convert_to_orientation( 0, "x" ), convert_to_orientation( 0, "y" ) ]
  


  label_data_dict={}
  label_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "CPG3"
  label_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "CPG4"
  label_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "CPG5"
  
  label_data_dict["../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_OFF_FILENAME] = "MPG3-"
  label_data_dict["../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_OFF_FILENAME] = "MPG4-"
  label_data_dict["../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_OFF_FILENAME] = "MPG5-"


  label_data_dict["../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_ON_FILENAME] = "MPG3+"
  label_data_dict["../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_ON_FILENAME] = "MPG4+"
  label_data_dict["../../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_ON_FILENAME] = "MPG5+"


  #label_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "MPG3"
  #label_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "MPG4"
  #label_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "MPG5"


  label_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "RPG3"
  label_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "RPG4"
  label_data_dict["../../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "RPG5"
  
  
  order={}
  order["CPG3"]=1
  order["MPG3-"]=2
  order["MPG3+"]=3
  order["RPG3"]=4
  
  
  
  CPG_COLOR='blue'
  MPG1_COLOR='lightgreen'
  MPG2_COLOR='green'
  RPG_COLOR='red'
  colors = {}
  for i in range(3,6):
    colors["CPG{}".format(i)] = CPG_COLOR
    colors["MPG{}-".format(i)] = MPG1_COLOR
    colors["MPG{}+".format(i)] = MPG2_COLOR
    colors["RPG{}".format(i)] = RPG_COLOR
  
  for csv_path in sorted(axes_data_dict.keys(), key=lambda x: order[label_data_dict.get(x)]   ):
    color = colors[ label_data_dict[csv_path] ]
    #indent ALL
    cur_plot=axes_data_dict[csv_path]
    
    re.sub( csv_path, "" ,"" )

    experiment_title = re.sub(r'.*DATA/','', csv_path )
    experiment_title = re.sub(r'\/.*','', experiment_title )

    #print( experiment_title )


    job_title = re.sub(r'.*DATA/[^/]*/','', csv_path )
    job_title = re.sub(r'\/.*','', job_title )

    robust_label = re.sub(r'.*DATA/[^/]*/','', csv_path )
    robust_label = re.sub(r'.*/','', robust_label )
    robust_label = re.sub(r'.csv','', robust_label )

    #print( "{},{},".format( job_title,  robust_label), end="" )
    #print(  "{}  /  {}  /  {}  /  {}_normalized.png".format( PLOTS, experiment_title, job_title, robust_label) )

    summary_filename = "{}/{}/{}/ROBUSTNESS_{}.csv".format(DATA, experiment_title, job_title, robust_label)


    seed_summary ={}
    seed_data_dict={}

    with open( csv_path  ) as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:   
        if not 'noise' in row:
          print("Are you sure you specified the correct csv file? It must have a 'noise' in the header to work in this mode")
          quit()
        
        seed =  row['seed']
        noise = row['noise']
        #if noise !=  "0.5":
        #  continue
        
        fitness = row['fitness']
        
        if not seed in seed_summary:
          seed_summary[seed] = {}
        
        if noise == '0.0':
          seed_summary[seed]['fitness'] = fitness
      
        if noise == '0.45':
          seed_summary[seed]['fitness_at_90'] = fitness
      
        #if seed == "9":
        #  print( noise  )
        
        if not seed in seed_data_dict:
          seed_data_dict[seed] = {}
        
        
        seed_data_dict[seed][noise]= float(fitness)
      
      
      noise_data={}
      fitness_data={}
      normalized_fitness_data={}
      

      for seed in seed_data_dict.keys():
        noise_data[seed] = []
        fitness_data[seed] = []
        normalized_fitness_data[seed] = []
        baseline = float( seed_data_dict[seed]['0.0'] )
        
        for noise in sorted( seed_data_dict[seed].keys(), key=float ):
          noise_data[seed].append( float(noise) )
          fitness_data[seed].append( float(seed_data_dict[seed][noise]) )
          normalized_fitness_data[seed].append( float(seed_data_dict[seed][noise])/baseline )
          
      
      ####DO MORE
      #first only include the networks with a fitness over threshold
      FITNESS_THRESHOLD = 0.2
      aggregated_fitness_by_noise_level = {}
      aggregated_normalized_fitness_by_noise_level = {}
      total_successful_networks=0

      for seed in seed_data_dict.keys():
        #baseline = float( max( seed_data_dict[seed] ) )
        baseline =  seed_data_dict[seed]['0.0'] 
        #only include networks which did sufficiently well
        if float( baseline ) > FITNESS_THRESHOLD :
          #count them for later data listing
          total_successful_networks+=1
          #make sure there is a noise slot for the data
          for noise_key in seed_data_dict[seed].keys():
            #make a list if there is not one yet
            if not noise_key in aggregated_fitness_by_noise_level:
              aggregated_fitness_by_noise_level[noise_key] = []
            if not noise_key in aggregated_normalized_fitness_by_noise_level:
              aggregated_normalized_fitness_by_noise_level[noise_key] = []
            #append to the data
            aggregated_fitness_by_noise_level[noise_key].append( float(seed_data_dict[seed][noise_key]) )
            #append to the data
            aggregated_normalized_fitness_by_noise_level[noise_key].append( float(seed_data_dict[seed][noise_key])/baseline)  
      
      
      n_bins=100
      b_bins="freedman"
      #cur_plot.hist(aggregated_normalized_fitness_by_noise_level["0.5"], bins=n_bins)
      sns.set_style('whitegrid')
      bw = PLOT_MODE
      #https://seaborn.pydata.org/tutorial/distributions.html
      sns.set(font_scale=1.25) 
      sns.kdeplot(np.array(aggregated_normalized_fitness_by_noise_level[MODULATION_LEVEL]), bw=bw, color= colors[ label_data_dict[csv_path] ],shade=True, label=label_data_dict[csv_path] )        
      
        
      cur_plot.set_xlim(-0.25, 1.25)
      
#          cur_plot.set_xlabel( label_data_dict[csv_path], color=color   )
          #cur_plot.ylabel('Noise')   
          #cur_plot.xlabel('Fitness %')
          #cur_plot.title( 'Measuring Aggregate Normalized Fitness to Neuromodulatory Noise')                    
          

            
  if SAVE_PLOTS_MODE:  
    #legend = plt.legend(loc='lower right') #, bbox_to_anchor=(1, 0.5) )
    #plt.title( 'Measuring Normalized Fitness to Neuromodulatory Noise')                    
    #plt.savefig(experiment_title + "_normalized.png" ) 
    #os.system( "mkdir -p {}/{}/{}".format( PLOTS, experiment_title, job_title ) )
    #plt.savefig( "{}/{}/{}/{}_normalized_AGG.png".format( PLOTS, experiment_title, job_title, robust_label) )  

    #print ("{}/{}/{}".format( PLOTS, experiment_title, job_title ) )
    #fig.set_ylabel('Noise')
    
    modulation_label="Robustness when M={}     ".format(1+float(MODULATION_LEVEL))
    
    
    if ORIENTATION=="VERTICAL":
      axes[numplots-1,0].set_xlabel(modulation_label, fontsize=fs )
      axes[numplots-1,0].set_ylabel("frequency", fontsize=fs )
      axes[numplots-1,0].tick_params(labelsize=12)
      #axes[0,0].title("Fitness Landscape")
      cur_plot.xaxis.set_visible(True)
    else:
      axes[0,0].set_ylabel(modulation_label)
    fig.suptitle("Kernel Density Estimation:\nRobustness",fontsize=fs)
    #fig.tight_layout()
    fig.subplots_adjust(bottom=0.125,left=0.175,right=0.95,top=0.87)
    plt.savefig( "{}_DIST_{}.png".format(PLOT_MODE, ORIENTATION ), pdi=1000)
  



