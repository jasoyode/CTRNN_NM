import re
import os
import sys
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



PLOT_MODES=["IND_ABS","AGG_ABS","AGG_PERC","IND_PERC"]

SAVE_PLOTS_MODE=True
SCATTER=False

#headless mode
mpl.use('Agg')
import matplotlib.pyplot as plt

#location for DATA from experiments and PLOTS
DATA="../../DATA"
PLOTS="../../PLOTS/TESTS/"

if len( sys.argv) < 2:
  print("Usage:   python robustness_plotter.py [DATA.csv] ")
  print("Will save a robustness summary file." )
  quit()
 

EVO_COND="standard"
#EVO_COND="mod1-ON"

ROB_FILENAME="RESULTS_CONSTANT_.csv"
MPG_ON_FILENAME="RESULTS_SA_ON_CONSTANT_.csv"
MPG_OFF_FILENAME="RESULTS_SA_OFF_CONSTANT_.csv"

numplots=12


for PLOT_MODE in PLOT_MODES:
  fig, axes = plt.subplots(nrows=1, ncols=numplots, figsize=(numplots, 6), squeeze=False)

  axes_data_dict={}        #r,c
  axes_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[0,0]
  axes_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[0,1]
  axes_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[0,2]

  
  #MPG_GOOD_345
  axes_data_dict["../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_OFF_FILENAME] = axes[0,3]
  axes_data_dict["../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_OFF_FILENAME] = axes[0,4]
  axes_data_dict["../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_OFF_FILENAME] = axes[0,5]
  
  axes_data_dict["../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_ON_FILENAME] = axes[0,6]
  axes_data_dict["../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_ON_FILENAME] = axes[0,7]
  axes_data_dict["../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_ON_FILENAME] = axes[0,8]

  
  #axes_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[0,3]
  #axes_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[0,4]
  #axes_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[0,5]

  axes_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[0,9]
  axes_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[0,10]
  axes_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = axes[0,11]


  label_data_dict={}
  label_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "CPG3"
  label_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "CPG4"
  label_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "CPG5"
  
  label_data_dict["../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_OFF_FILENAME] = "MPG3-"
  label_data_dict["../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_OFF_FILENAME] = "MPG4-"
  label_data_dict["../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_OFF_FILENAME] = "MPG5-"


  label_data_dict["../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_ON_FILENAME] = "MPG3+"
  label_data_dict["../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_ON_FILENAME] = "MPG4+"
  label_data_dict["../../DATA/MPG_GOOD_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + MPG_ON_FILENAME] = "MPG5+"


  #label_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "MPG3"
  #label_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "MPG4"
  #label_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "MPG5"


  label_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "RPG3"
  label_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-4_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "RPG4"
  label_data_dict["../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-5_sim-100run-500gen_signal-SINE-1p_M-"+EVO_COND+"/" + ROB_FILENAME] = "RPG5"
  
  
  
  for csv_path in axes_data_dict.keys():
    print(csv_path  )
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
          
        ######################################
        # individual percentage
        ######################################        
        if PLOT_MODE == "IND_PERC":
          #if SAVE_PLOTS_MODE:  
          cur_plot.set_xlim(0, 1.0)
          cur_plot.set_ylim(-0.5, 0.5)
          cur_plot.set_xlabel( label_data_dict[csv_path] )
          cur_plot.plot( normalized_fitness_data[seed], noise_data[seed], color="black", alpha=0.1, label=seed)
        #########################################
        # individual absolute
        #########################################
        if PLOT_MODE == "IND_ABS":
          cur_plot.set_xlabel( label_data_dict[csv_path] )
          cur_plot.set_xlim(0, .628)
          cur_plot.set_ylim(-0.5, 0.5)
          cur_plot.plot( fitness_data[seed], noise_data[seed], color="black", alpha=0.1, label=seed)

      
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
        
      #  print( "Successful networks: "+ str(total_successful_networks ) +" out of " + str(len(seed_data_dict.keys())) )
      fitness_means = []
      fitness_errors = []
      norm_fitness_means = []
      norm_fitness_errors = []
      noise_levels =[]
      #sort by noise level 0....0.5
      for noise_key in sorted(aggregated_fitness_by_noise_level.keys(), key=float ):
        noise_levels.append( float(noise_key) )
        fitness_means.append( np.mean( aggregated_fitness_by_noise_level[noise_key]) )
        fitness_errors.append( np.std( aggregated_fitness_by_noise_level[noise_key] ))
        norm_fitness_means.append( np.mean( aggregated_normalized_fitness_by_noise_level[noise_key]) )
        norm_fitness_errors.append( np.std( aggregated_normalized_fitness_by_noise_level[noise_key] ))
      noise_levels = np.asarray( noise_levels )
      fitness_means = np.asarray( fitness_means )
      fitness_errors = np.asarray( fitness_errors )
      
      norm_fitness_means = np.asarray( norm_fitness_means )
      norm_fitness_errors = np.asarray( norm_fitness_errors )
        
      #########################################
      # aggregate absolute   
      #########################################
      if PLOT_MODE == "AGG_ABS":
        cur_plot.plot(fitness_means, noise_levels )
        cur_plot.fill_betweenx( noise_levels, fitness_means-fitness_errors, fitness_means+fitness_errors, facecolor='b', alpha=0.1)
        cur_plot.set_ylim(-0.5, 0.5)
        cur_plot.set_xlim(0.0, 0.628)
        cur_plot.set_xlabel( label_data_dict[csv_path] )
        #plt.ylabel('Noise')   
        #plt.xlabel('Fitness')
        #plt.title( 'Measuring Aggregate Absolute Fitness to Neuromodulatory Noise')                    
      
      if PLOT_MODE=="AGG_PERC":
        cur_plot.plot(norm_fitness_means, noise_levels  )
        cur_plot.fill_betweenx( noise_levels, norm_fitness_means-norm_fitness_errors, norm_fitness_means+norm_fitness_errors, facecolor='b', alpha=0.1)
        cur_plot.set_ylim(-0.5, 0.5)
        cur_plot.set_xlim(0.0, 1.0)
        cur_plot.set_xlabel( label_data_dict[csv_path] )
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
    axes[0,0].set_ylabel('All Weights Change %')
    fig.suptitle("Fitness Landscape")
    plt.savefig( PLOT_MODE+"_AGG_DEMO.png" )
