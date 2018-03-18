import re
import operator
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
levels=[ 0.90 ]

HARD_LEVEL=0.90
abs_level=0.45


SOFT_MODE=True


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


#print( job_title )
#print( robust_label )

#quit()

#print( "{},{},".format( job_title,  robust_label), end="" )
#print(  "{}  /  {}  /  {}  /  {}_normalized.png".format( PLOTS, experiment_title, job_title, robust_label) )
#quit()

summary_filename = "{}/{}/{}/ROBUSTNESS_{}.csv".format(DATA, experiment_title, job_title, robust_label)

#print(  summary_filename  )
#quit()


seed_summary ={}


seed_data_dict={}

if SAVE_PLOTS_MODE:
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
    #print (seed )
    noise_data[seed] = []
    fitness_data[seed] = []
    normalized_fitness_data[seed] = []
    #print( sorted( seed_data_dict[seed].keys() ) )
    
    #if not '0.0' in seed_data_dict[seed]:
    #baseline = float( max( seed_data_dict[seed] ) )
    #print("baseline: " + str( baseline))
    #else:
    #should use max of all tests, not just baseline
    #baseline = float( seed_data_dict[seed]['0.0'] )
    
    #print( seed_data_dict[seed] )
    #print( max( seed_data_dict[seed].items(), key=operator.itemgetter(1))[0] )

    #get max value from all noise levels and use that as the metric to measure robustness against
    baseline =  max( seed_data_dict[seed].items(), key=operator.itemgetter(1))[1]  

    #print("max" + str(  max(seed_data_dict[seed]   )  )  )
    #print("baseline: " + str( baseline))
    
    for noise in sorted( seed_data_dict[seed].keys(), key=float ):
      noise_data[seed].append( float(noise) )
      fitness_data[seed].append( float(seed_data_dict[seed][noise]) )
      normalized_fitness_data[seed].append( float(seed_data_dict[seed][noise])/baseline )
    
    if SAVE_PLOTS_MODE:  
      #plt.ylim(0, 1.0)
      plt.xlim(0, 1.0)
      plt.ylim(-0.5, 0.5)
      if not SCATTER:
        #plt.plot( noise_data[seed], normalized_fitness_data[seed], label=seed)
        plt.plot( normalized_fitness_data[seed], noise_data[seed], color="black", alpha=0.1, label=seed)
      
      else:
        plt.scatter( noise_data[seed], normalized_fitness_data[seed], label=seed)
        
  
  if SAVE_PLOTS_MODE:  
    #legend = plt.legend(loc='lower right') #, bbox_to_anchor=(1, 0.5) )
    plt.ylabel('Noise')   
    plt.xlabel('Fitness %')
  
    plt.title( 'Measuring Normalized Fitness to Neuromodulatory Noise')                    
    #plt.savefig(experiment_title + "_normalized.png" ) 
    os.system( "mkdir -p {}/{}/{}".format( PLOTS, experiment_title, job_title ) )
    plt.savefig( "{}/{}/{}/{}_normalized.png".format( PLOTS, experiment_title, job_title, robust_label) )  

  #print ("{}/{}/{}".format( PLOTS, experiment_title, job_title ) )
  
  
  if SAVE_PLOTS_MODE:
    plt.figure(1)
  
    for seed in seed_data_dict.keys():
      #plt.ylim(0, .628)
      plt.xlim(0, .628)
      plt.ylim(-0.5, 0.5)
      
      if not SCATTER:
        #plt.plot( noise_data[seed], fitness_data[seed], label=seed)
        plt.plot( fitness_data[seed], noise_data[seed], color="black", alpha=0.1, label=seed)
      else:
        plt.scatter( noise_data[seed], fitness_data[seed], label=seed)
        
        
    #legend = plt.legend(loc='lower right')
    plt.xlabel('Fitness')   
    plt.ylabel('Noise')
  
    
  
    plt.title( 'Measuring Absolute Fitness to Neuromodulatory Noise')                    
  
    plt.savefig( "{}/{}/{}/{}_absolute.png".format( PLOTS, experiment_title, job_title, robust_label) )
  
  
  if SAVE_PLOTS_MODE:
    #aggregate 
    plt.figure(2) 
  
  
  
  #first only include the networks with a fitness over threshold
  #include all to be a fair comparison
  FITNESS_THRESHOLD = 0.0
  
  
  aggregated_fitness_by_noise_level = {}
  aggregated_normalized_fitness_by_noise_level = {}
  
  total_successful_networks=0
  for seed in seed_data_dict.keys():
    #print( seed )
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
    
  print( "Successful networks: "+ str(total_successful_networks ) +" out of " + str(len(seed_data_dict.keys())) )
  print( "  From file: {}".format( sys.argv[-1] ))
  
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
                  
  #plt.plot(aggregated_fitness_by_noise_level.keys() ,fitness_means)
  noise_levels = np.asarray( noise_levels )
  
  #print( aggregated_fitness_by_noise_level.keys() )
  #quit()
  
  fitness_means = np.asarray( fitness_means )
  fitness_errors = np.asarray( fitness_errors )
  
  norm_fitness_means = np.asarray( norm_fitness_means )
  norm_fitness_errors = np.asarray( norm_fitness_errors )
  
  
  if SAVE_PLOTS_MODE:                                                                              
    if not SCATTER:
      #plt.plot(noise_levels, fitness_means  )
      plt.plot(fitness_means, noise_levels )
    else:
      plt.scatter(noise_levels, fitness_means  )
    
                                                                                        
    #shaded region indicates standard deviation
    #plt.fill_between(noise_levels, fitness_means-fitness_errors, fitness_means+fitness_errors, facecolor='b', alpha=0.1)
    #plt.ylim(0, .628)
    #plt.axhline(y=0.314, xmin=0, xmax=1.0, color="red")
    
    plt.fill_betweenx( noise_levels, fitness_means-fitness_errors, fitness_means+fitness_errors, facecolor='b', alpha=0.1)
    plt.ylim(-0.5, 0.5)
    plt.xlim(0.0, 0.628)
    
    
    legend = plt.legend(loc='lower right')
    plt.ylabel('Noise')   
    plt.xlabel('Fitness')
    plt.title( 'Measuring Aggregate Absolute Fitness to Neuromodulatory Noise')                    
    
    #plt.gca().invert_yaxis()
    
    plt.savefig( "{}/{}/{}/{}_aggregate_absolute.png".format( PLOTS, experiment_title, job_title, robust_label) )
   
  if SAVE_PLOTS_MODE:
    plt.figure(3)
  
    if not SCATTER:
      #plt.plot(noise_levels, norm_fitness_means  )
      plt.plot(norm_fitness_means, noise_levels  )
    else:
      plt.scatter(noise_levels, norm_fitness_means  )
                                                                                        
    #shaded region indicates standard deviation
    #plt.fill_between(noise_levels, norm_fitness_means-norm_fitness_errors, norm_fitness_means+norm_fitness_errors, facecolor='b', alpha=0.1)
    #plt.ylim(0, 1.0)
    #plt.axhline(y=0.5, xmin=0, xmax=1.0, color="red")
    
    plt.fill_betweenx( noise_levels, norm_fitness_means-norm_fitness_errors, norm_fitness_means+norm_fitness_errors, facecolor='b', alpha=0.1)
    plt.ylim(-0.5, 0.5)
    plt.xlim(0.0, 1.0)
    
    legend = plt.legend(loc='lower right')
    plt.ylabel('Noise')   
    plt.xlabel('Fitness %')
    plt.title( 'Measuring Aggregate Normalized Fitness to Neuromodulatory Noise')                    
    
    #plt.gca().invert_yaxis()
    plt.savefig( "{}/{}/{}/{}_aggregate_normalized.png".format( PLOTS, experiment_title, job_title, robust_label) )
   
  
  if SAVE_PLOTS_MODE:
    plt.figure(4)
    #percentage of noise levels where 50%+ is achieved (small chance of jumping back up)
  
  
  
  #total=len(seed_data_dict.keys() )
  seed_robustness_dict={}
  for level in levels:
    seed_robustness_dict[level] ={}
  
  for seed in seed_data_dict.keys():
    total=len(normalized_fitness_data[seed] )
    
    for level in levels:
      seed_robustness_dict[level][seed] = 0
    
    for i in range(len(normalized_fitness_data[seed]) ) :
      for level in levels:
        
        #This is the cutoff of whether we include the test as a pass or not
        
        if not SOFT_MODE:
          if normalized_fitness_data[seed][i] > level and fitness_data[seed][i] > abs_level :
            seed_robustness_dict[level][seed] += 1
        else:
          #alternate form we just add the percentage
          seed_robustness_dict[level][seed] += normalized_fitness_data[seed][i]
        
        #elif normalized_fitness_data[seed][i] > level:
        #  print( "failed because abs == {}".format(  fitness_data[seed][i] ) )
        #else:
        #  print( "failed because normalized == {}".format( normalized_fitness_data[seed][i]  ))
    
    
    for level in levels:
      seed_robustness_dict[level][seed] = round( seed_robustness_dict[level][seed] / total, 3)
  
  
  for s in seed_robustness_dict[HARD_LEVEL].keys():
    seed_summary[s]['robustness'] = seed_robustness_dict[HARD_LEVEL][s]
  
  #this is all seeds and their robustness
  #print("Sorted seeds by their robustness score:  " )
  #print( seed_summary )
  #print(  sorted( seed_summary.items(), key=operator.itemgetter(1)  ) )
  #print(   sorted( seed_robustness_dict[0.9].items(), key=operator.itemgetter(1)  ) )
  
  summary_csv = open (summary_filename, "w+")
  summary_csv.write(  "seed,fitness,fitness_at_90,robustness,\n" )
  
  for seed in seed_summary.keys():
    summary_csv.write( "{},{},{},{},\n".format( seed,  seed_summary[seed]['fitness'],seed_summary[seed]['fitness_at_90'] , seed_summary[seed]['robustness'] ) ) 
  
  print("Wrote summary to: {}".format( summary_filename ) )
  
  values = {}
  
  for level in levels:
    values[level] = seed_robustness_dict[level].values() 
  
  if SAVE_PLOTS_MODE:
    # the histogram of the data
    n, bins, patches = plt.hist(values[ levels[-1]   ], 10,  facecolor='green', alpha=0.75)  #normed=1
  
  # add a 'best fit' line
  ##y = mlab.normpdf( bins, mu, sigma)
  #l = plt.plot(bins, y, 'r--', linewidth=1)
  #print( values   )

  robust_mean={}
  
  for level in levels:
    robust_mean[level]=[]
    mean_calc=[]
    for v in values[level]:
      mean_calc.append( v )
    robust_mean[level] = round( np.mean( mean_calc  ), 3)

  
  output = ""
  for level in levels:
    output+= "{},".format( robust_mean[level])
  #print(output)
  
  if SAVE_PLOTS_MODE:
    plt.xlabel('Robustness')   
    plt.ylabel('Frequency')
    plt.title( "Robustness Frequency Distribution: {}".format(  str(robust_mean[HARD_LEVEL] )  ) )
    plt.savefig( "{}/{}/{}/{}_robustness_histogram.png".format( PLOTS, experiment_title, job_title, robust_label) )
  
  
  