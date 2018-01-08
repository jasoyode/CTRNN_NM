import re
import os
import sys
import csv
import glob
import numpy as np
import operator  
import matplotlib as mpl
#from mpl_toolkits.mplot3d import Axes3D
#from matplotlib.colors import LinearSegmentedColormap
#from sklearn.decomposition import PCA as sklearnPCA
#from sklearn.preprocessing import StandardScaler
#from mpl_toolkits.mplot3d.art3d import Line3DCollection
#from matplotlib.collections import LineCollection

PI=3.141592653589

#headless mode
mpl.use('Agg')
import matplotlib.pyplot as plt

#location for DATA from experiments and PLOTS
DATA="../../DATA"
PLOTS="../../PLOTS/TESTS/"



if len( sys.argv) < 2:
  print("Usage:   python robustness_plotter.py [DATA.csv] ")
  #comparison_name = comparison_name.replace(".csv","")
  #COMPARE_MODE=3
  quit()
  
 
#directory=sys.argv[1]
csv_path=sys.argv[1]

re.sub( csv_path, "" ,"" )

experiment_title = re.sub(r'.*DATA/','', csv_path )
experiment_title = re.sub(r'\/.*','', experiment_title )

#print( experiment_title )


job_title = re.sub(r'.*DATA/[^/]*/','', csv_path )
job_title = re.sub(r'\/.*','', job_title )

robust_label = re.sub(r'.*DATA/[^/]*/','', csv_path )
robust_label = re.sub(r'.*/','', robust_label )
robust_label = re.sub(r'.csv','', robust_label )

#print( experiment_title )
#print( job_title )
#print( robust_label )

seed_data_dict={}

plt.figure(0)


with open( sys.argv[-1]  ) as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:   
    if not 'noise' in row:
      print("Are you sure you specified the correct csv file? It must have a 'noise' in the header to work in this mode")
      quit()
    
    seed =  row['seed']
    noise = row['noise']
    fitness = row['fitness']
    
    if not seed in seed_data_dict:
      seed_data_dict[seed] = {}
    
    seed_data_dict[seed][noise]= fitness
  
  
  noise_data={}
  fitness_data={}
  normalized_fitness_data={}
  
  for seed in seed_data_dict.keys():
    noise_data[seed] = []
    fitness_data[seed] = []
    normalized_fitness_data[seed] = []
    #print( sorted( seed_data_dict[seed].keys() ) )
    baseline = float( seed_data_dict[seed]['0.0'] )
    
    for noise in sorted( seed_data_dict[seed].keys() ):
      noise_data[seed].append( float(noise) )
      fitness_data[seed].append( float(seed_data_dict[seed][noise]) )
      normalized_fitness_data[seed].append( float(seed_data_dict[seed][noise])/baseline )
      
    plt.ylim(-0, 1.5)
    plt.plot( noise_data[seed], normalized_fitness_data[seed], label=seed)
    
  legend = plt.legend(loc='lower right') #, bbox_to_anchor=(1, 0.5) )
  plt.xlabel('Noise')   
  plt.ylabel('Fitness')
  
  plt.title( 'Measuring Normalized Fitness to Neuromodulatory Noise')                    
  #plt.savefig(experiment_title + "_normalized.png" ) 
  os.system( "mkdir -p {}/{}/{}".format( PLOTS, experiment_title, job_title ) )
  plt.savefig( "{}/{}/{}/{}_normalized.png".format( PLOTS, experiment_title, job_title, robust_label) )  

  print ("{}/{}/{}".format( PLOTS, experiment_title, job_title ) )
  
  
  
  plt.figure(1)
  
  for seed in seed_data_dict.keys():
    plt.ylim(0, .628)
    plt.plot( noise_data[seed], fitness_data[seed], label=seed)
  legend = plt.legend(loc='lower right')
  plt.xlabel('Noise')   
  plt.ylabel('Fitness')
  
  plt.title( 'Measuring Absolute Fitness to Neuromodulatory Noise')                    
  
  plt.savefig( "{}/{}/{}/{}_absolute.png".format( PLOTS, experiment_title, job_title, robust_label) )
  
  
  #aggregate 
  plt.figure(2) 
  
  
  
  #first only include the networks with a fitness over threshold
  FITNESS_THRESHOLD = 0.3
  
  
  aggregated_fitness_by_noise_level = {}
  
  total_successful_networks=0
  for seed in seed_data_dict.keys():
    
    print( seed_data_dict[seed]['0.0'] )
    
    #only include networks which did sufficiently well
    if float( seed_data_dict[seed]['0.0'] ) > FITNESS_THRESHOLD :
      
      #count them for later data listing
      total_successful_networks+=1
      
      #make sure there is a noise slot for the data
      for noise_key in seed_data_dict[seed].keys():
        #make a list if there is not one yet
        if not noise_key in aggregated_fitness_by_noise_level:
          aggregated_fitness_by_noise_level[noise_key] = []
        #append to the data
        aggregated_fitness_by_noise_level[noise_key].append( float(seed_data_dict[seed][noise_key]) )
    
  print( "Successful networks: "+ str(total_successful_networks ) )
  
  
  fitness_means = []
  fitness_errors = []
  
  noise_levels =[]
  
  #sort by noise level 0....0.5
  for noise_key in sorted(aggregated_fitness_by_noise_level.keys() ):
    noise_levels.append( noise_key )
    fitness_means.append( np.mean( aggregated_fitness_by_noise_level[noise_key]) )
    fitness_errors.append( np.std( aggregated_fitness_by_noise_level[noise_key] ))
                    
                  
  #plt.plot(aggregated_fitness_by_noise_level.keys() ,fitness_means)
  noise_levels = np.asarray( noise_levels )
  
  #print( aggregated_fitness_by_noise_level.keys() )
  #quit()
  
  fitness_means = np.asarray( fitness_means )
  fitness_errors = np.asarray( fitness_errors )
                                                                                
  plt.plot(noise_levels, fitness_means  )
                                                                                        
  #shaded region indicates standard deviation
  plt.fill_between(noise_levels, fitness_means-fitness_errors, fitness_means+fitness_errors, facecolor='b', alpha=0.1)
                                                                                                
  #for seed in seed_data_dict.keys():
  
  
  plt.ylim(0, .628)
  #plt.plot( noise_data[seed], fitness_data[seed], label=seed)
  
  legend = plt.legend(loc='lower right')
  plt.xlabel('Noise')   
  plt.ylabel('Fitness')
  
  plt.title( 'Measuring Aggregate Absolute Fitness to Neuromodulatory Noise')                    
  
  plt.savefig( "{}/{}/{}/{}_aggregate_absolute.png".format( PLOTS, experiment_title, job_title, robust_label) )
   
   
                                      