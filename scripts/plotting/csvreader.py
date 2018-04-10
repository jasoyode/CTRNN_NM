import configparser
import re
import os
import sys
import csv
import glob
import numpy as np
import operator
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LinearSegmentedColormap
from sklearn.decomposition import PCA as sklearnPCA
from sklearn.preprocessing import StandardScaler
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.collections import LineCollection

from scipy.interpolate import spline

PI=3.141592653589

#headless mode
mpl.use('Agg')
import matplotlib.pyplot as plt

#location for DATA from experiments and PLOTS
DATA="../../DATA"
PLOTS="../../PLOTS"

BRIGHT_MODULATION_MODE=False

BRIGHT_SSIO_MODE=True
SSIO_THICKNESS=1
CUSTOM_TRAJECTORY=True

ALIFE2018_ONLY_ACTUAL_SSIO=True

LEG_ANGLE_SENSOR=False
fs=16    #22
tickfs=fs-4

SSIO_MODE=True
SSIO_MODULATION_MODE=True


def customize_mod_color( mod ):
 if BRIGHT_MODULATION_MODE:
  return 1
 else:
  return mod
  
def customize_trajectory( name, m ):
 if CUSTOM_TRAJECTORY:
  
  if name == "FT":
   return "purple"
  elif name == "BS":
   return "orange"
  else:     # name == "FS":
   return "green"
   
 else:
  
  if m < 0:
   return (0,0, customize_mod_color(abs(m)), 0.5)   
  elif m > 0:
   return (customize_mod_color( m),0,0, 0.5)   
  else:
   return (0,0,0, 0.5)  
   
 
def customize_ssio_color( mod ):
 if BRIGHT_SSIO_MODE:
  if mod > 0:
   return 1
  elif mod > 0:
   return -1
  else:
   return mod
 else:
  return mod






#0   SENSORS OFF
#1   SENSORS ON
MPG_EXCLUDE="1"

#X_LIM=25
X_LIM_A=-24   #-5
X_LIM_B=1   #15
#X_LIM_A=-4  #BEER
#X_LIM_B=14  #BEER

XLIM_MODE=True

COMPARE_MODE=0

if len(sys.argv) < 2:
  print(  "Usage: "+ sys.argv[0]+ " experiment_directory_name (inside {}".format( DATA ) )
  quit()


experiment_directory=sys.argv[1]
experiment_title = re.sub(r'.*/','', experiment_directory )

print( sys.argv )
experiment_directories = sys.argv[1:-1]


if len(experiment_title) ==0:
  print( "make sure not to leave a / at the end of the directory!" )
  quit()

comparison_name = sys.argv[-1]

if len( sys.argv) > 2:
  COMPARE_MODE=1


if len( sys.argv) <= 2 and "mutations.csv" in sys.argv[-1]:
 COMPARE_MODE=4
 MUTATION_FILE=sys.argv[-1]
 

elif ".csv" in sys.argv[-1] and len( sys.argv) <= 2:
 comparison_name = comparison_name.replace(".csv","")
 COMPARE_MODE=2
 experiment_directories={}
 experiment_styles={}
 
 with open( sys.argv[-1]  ) as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
   dir =  row['directory'] 
   label = row['label']
   experiment_directories[dir]=  label
   
   if "color" in row:
    print( "yes!")
    #quit()
    experiment_styles[dir] = (  row['color'], row['style'] )

#if we have a CSV file but have multiple arguments
#then we are running special testing analysis on one arch's seeds only




if len( sys.argv) > 2 and ".csv" in sys.argv[-1]:
 comparison_name = comparison_name.replace(".csv","")
 COMPARE_MODE=3
 directory=sys.argv[1]
 csv_path=sys.argv[2]
 
 testing_dict={}
 
 with open( sys.argv[-1]  ) as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
   if not 'column' in row:
    print("Are you sure you specified the correct csv file? It must have a 'column' in the header to work in this mode")
    quit()
   
   dir =  row['directory'] 
   label = row['label']
   r=row['row']
   c=row['column']
   testing_dict[dir]= ( label, r, c )
   
INI_MODE=False
if ".ini" in sys.argv[-1]:
 INI_MODE=True






def plot_fitness2( ):

    print( "plot_fitness2" )

    #each element is a collection of all the generations in 1 run
    gen_all = []
    #each element is a collection of all the fitnesses in 1 run
    fit_all = []
    #each element is a collection of all the fitness in 1 generation
    fit_by_gen = []
    #START FIRST IMAGE FOR PLOTTING
    plt.figure(0)
    #initialize all lists in fitness by generation list to store fitnesses
    #for i in range(0, generations):
    #  fit_by_gen.append( [] )
    seed_files = glob.glob(  '{}/seed_*.txt'.format( experiment_directory  ) ) 
    for seed_file in seed_files:
      gen = []
      fit = []
      with open( seed_file  ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
          g = int( row['Generation'] )
          #grow fit_by_gen_as_needed
          if g + 1 >= len( fit_by_gen) :
            fit_by_gen.append( [] )
            
          #incase the final generation or anything else is duplicated
          if not g in gen:
            gen.append(  g )
            fit.append( float( row['BestPerf'] )   )
            #add fitness value to proper generation
            fit_by_gen[g].append(  float( row['BestPerf'] ) )

            #sanity check        
            #if len( fit_by_gen[g]) > pop:
            #  print( "g:", g )
            #  print( " fit_by_gen[g]", fit_by_gen[g] )
            #  quit()
            #why does this happen???
    #      else:
          #  print("Warning skipping generation", g, "because it was already recorded!")
            
      plt.plot(gen, fit)
      gen_all.append( gen )
      fit_all.append( fit )
    
    if len(gen_all) == 0:
     raise Exception("There was no data, are you sure you specified the correct file?")
      
    # any should work
    gen = gen_all[0]

    means = []


    for i in gen: #range(0, len(fit_by_gen) ):
      current_mean = 0

      #each collection of means
      for f in fit_all:
        current_mean += f[i]
      
      current_mean = current_mean / len(fit_all)
      means.append( current_mean )
      #verify mean calculated properly
      assert(  abs( np.mean( fit_by_gen[i]) - current_mean )  < 0.000001 )
      

    gen_means = []
    gen_errors = []


    for g in gen: #range(0, len(fit_by_gen) ):
      gen_means.append( np.mean( fit_by_gen[g]) )
      gen_errors.append( np.std( fit_by_gen[g] ))
      #print( "gen: {}  mean: {}   std: {}".format( g, gen_means[g], gen_errors[g] ) )


    plt.plot(gen, fit)
    plt.xlabel('Generation')
    plt.ylabel('Best Fitness')

    
    #TODO FIX THIS
    #print( experiment_directory  )
    #print( experiment_title  )
    #quit()
    
    exp_title = re.sub(r'.*/','', experiment_directory )
    exp_base = re.sub(r'.*/DATA/','', experiment_directory )
    plt.title( exp_title + '\nBest Fitness of Individual Experiment Runs')
    plt.grid(True)
    plt.savefig("{0}/{1}/individual_runs_{2}.png".format(PLOTS,  exp_base, exp_title ), dpi=1000 )



    gen = np.asarray( gen )
    gen_means = np.asarray( gen_means )
    gen_errors = np.asarray( gen_errors )


    plt.figure(1)
    plt.plot(gen, gen_means  )

    #shaded region indicates standard deviation
    plt.fill_between(gen, gen_means-gen_errors, gen_means+gen_errors, facecolor='b', alpha=0.1)


    plt.xlabel('Generation')
    plt.ylabel('Best Mean Fitness')
    
    
    exp_title = re.sub(r'.*/','', experiment_directory )       
    exp_base = re.sub(r'.*/DATA/','', experiment_directory )
    plt.title( exp_title +'\nMean Best Fitness by Generation with Standard Error')
    plt.grid(True)
    plt.savefig("{0}/{1}/mean_runs_with_error_{2}.png".format(PLOTS, exp_base, exp_title ),dpi=1000 )

    #print( '{}/{}/seed_*.csv'.format( DATA, experiment_directory  ) )

def plot_fitness( comparisonName, directories, styles_dict,  fromCSV=False):
    
    dirs=[]
    if fromCSV:
     dirs=sorted( directories.keys() )
    else:
     dirs=directories[:]
    
    #START FIRST IMAGE FOR PLOTTING
    fig = plt.figure(0)
    fig.set_size_inches(11, 8)
    
    master_data = []
    
    print ( dirs )
    for dir in dirs:

     print( "plotting: {}".format(dir) )
     #each element is a collection of all the generations in 1 run
     gen_all = []
     #each element is a collection of all the fitnesses in 1 run
     fit_all = []
     #each element is a collection of all the fitness in 1 generation
     fit_by_gen = []
     
     #initialize all lists in fitness by generation list to store fitnesses
     #for i in range(0, generations):
     #  fit_by_gen.append( [] )
     seed_files = glob.glob(  '{}/seed_*.txt'.format(  dir  ) ) 
     for seed_file in seed_files:
       gen = []
       fit = []
       with open( seed_file  ) as csvfile:
         reader = csv.DictReader(csvfile)
         for row in reader:
           g = int( row['Generation'] )
           #grow fit_by_gen_as_needed
           if g + 1 >= len( fit_by_gen) :
             fit_by_gen.append( [] )
             
           #incase the final generation or anything else is duplicated
           if not g in gen:
             gen.append(  g )
             fit.append( float( row['BestPerf'] )   )
             #add fitness value to proper generation
             fit_by_gen[g].append(  float( row['BestPerf'] ) )

       #plt.plot(gen, fit)
       gen_all.append( gen )
       fit_all.append( fit )
       
     if len(gen_all) == 0:
      print( seed_files )
      raise Exception("There was no data, are you sure you specified the correct file?")
      
     
     # any should work
     gen = gen_all[0]

     means = []


     for i in gen: #range(0, len(fit_by_gen) ):
       current_mean = 0

       #each collection of means
       for f in fit_all:
         current_mean += f[i]
       
       current_mean = current_mean / len(fit_all)
       means.append( current_mean )
       #verify mean calculated properly
       assert(  abs( np.mean( fit_by_gen[i]) - current_mean )  < 0.000001 )
       

     gen_means = []
     gen_errors = []

     for g in gen: 
       gen_means.append( np.mean( fit_by_gen[g]) )
       gen_errors.append( np.std( fit_by_gen[g] ))

     gen = np.asarray( gen )
     gen_means = np.asarray( gen_means )
     gen_errors = np.asarray( gen_errors )

     master_data.append(  [gen[:], gen_means[:], gen_errors[:], dir]  )

    for g, gm, ge, dir in master_data:
    
     print( g[0], gm[0], ge[0] )
     print( len(g), len(gm), len(ge) )
     
     
     if fromCSV:
      #plt.plot(g, gm , label=directories[dir] )
      if len( styles_dict.keys() ) > 0:
       print( "color: " + styles_dict[dir][0] )
       print( "style: " + styles_dict[dir][1] )
       plt.plot(g, gm , label=directories[dir], color=styles_dict[dir][0], linestyle=styles_dict[dir][1] )
       plt.fill_between(g, gm-ge, gm+ge, alpha=0.1, facecolor=styles_dict[dir][0])
      else:
       plt.plot(g, gm , label=directories[dir] )
       plt.fill_between(g, gm-ge, gm+ge, alpha=0.1)  # facecolor='b',
     else:
      plt.plot(g, gm , label=dir )
      #shaded region indicates standard deviation
      plt.fill_between(g, gm-ge, gm+ge, alpha=0.1)  # facecolor='b',
    
     
    
    plt.xlabel('Generation')
    plt.ylabel('Best Mean Fitness')
    plt.title( 'Comparing Mean Best Fitness')
    plt.grid(True)
    legend = plt.legend(loc='lower right') #, bbox_to_anchor=(1, 0.5) )
    
    plt.savefig("{0}/COMPARE/comparing_{1}.png".format(PLOTS, comparisonName ),dpi=1000 )


def get_ssio_data_for_plotting( DATA, exp_base, seed_num): 
 
 SSIO_MODE=True
 ssio_files={}
 ssio_data={}
 for i in range(1,4):
  ssio_files[i] = {}
  
  if SSIO_MODULATION_MODE:
   #1. glob get all files matching the mod
   mod_files= glob.glob(  '{}/{}/seed_{}_ssio_n{}_mod_*.csv'.format( DATA,exp_base,seed_num, i   ) )
   #2. strip out the mod value
   for mod_ssio in mod_files:
    ssio_mod_level=re.sub('.*seed_.*_ssio_n.*_mod_',"",mod_ssio)
    ssio_mod_level=re.sub( ".csv","", ssio_mod_level)
    ssio_mod_level=float( ssio_mod_level )
    
    ssio_files[i][ssio_mod_level]=mod_ssio
  
  #normal file is just modulation level 0
  ssio_files[i][0]="{}/{}/seed_{}_ssio_n{}.csv".format(DATA,exp_base,seed_num, i)
  #if we are missing any SSIOs, then cancel ssio plotting mode
  if not os.path.isfile( ssio_files[i][0]  ):
   SSIO_MODE=False
   break
  
  ssio_data[i]={}
  for mod in ssio_files[i].keys():
   #print( mod)
   ssio_data[i][mod]={}
   ssio_data[i][mod]["x"]=[]
   ssio_data[i][mod]["y"]=[]
  
  for mod, ssio_file in ssio_files[i].items():
   #for each neuron
   with open( ssio_file, 'r') as f:
    ssio_reader = csv.DictReader(f)
    for ssio_row in ssio_reader:
     ssio_data[i][mod]["x"].append( float(ssio_row["x"]) )
     ssio_data[i][mod]["y"].append( float(ssio_row["y"]) )

 return ssio_data, SSIO_MODE

def plot_activity(experiment_directory, quantity=1, short_start=0, short_stop=1000, seed=-1, SSIO_MODE=False, alternate_output="", LEG_ANGLE_SENSOR=False, PNG_W=8,PNG_Y=11 ):
    
    figsize_xy=(PNG_W,PNG_Y)
     
    
    print("plot_activity")
    
    if seed != -1:
     quantity=100
    
    #VIEWING WINDOW
    start=0
    stop=-1

    #short_start=0
    #short_stop=1000

    print( "Plotting activity")
    seed_to_fitness_map={}
    
    #print( experiment_directory )
    
    fitness_and_receptors = "{}/fitness_and_receptors.txt".format( experiment_directory  )
    total_receptors=-1
    
    with open( fitness_and_receptors  ) as fitness_file:
     fit_reader = csv.DictReader(fitness_file)
     
     for row in fit_reader:
      entry = []
      f = float( row['fitness'] )
      entry.append( f )
      
      if total_receptors == -1:
       r=1
       
       while "r"+str(r) in row:
        r+=1
        total_receptors=r
      #total_receptors
      for r in range(1, total_receptors):
       if "r"+str(r) in row:
        entry.append( float( row['r'+str(r)   ]  ) )
       else:
        print("why??")
        quit()
      seed_to_fitness_map[  int( row['seed'] ) ] =  entry ;
      
###########################  setup genome map
    seed_to_genome_map = {}
    #actualyl should be using phenotypes
    #genomes = "{}/genomes.txt".format( experiment_directory  )
    genomes = "{}/phenotypes.txt".format( experiment_directory  )
    total_neurons=-1
    with open( genomes  ) as genomes_file:
     genome_reader = csv.DictReader(genomes_file)
     
     for row in genome_reader:
      entry = {}
      
      #calculate total_neurons one time
      if total_neurons == -1:
       n=1
       #check until bias# not found
       while "bias"+str(n) in row:
        total_neurons=n
        n+=1
        
      #total_genomes
      for i in range(1, total_neurons+1):
       for j in range( 1, total_neurons+1 ):
        entry["w{}{}".format(i,j)  ] = float( row[ "w_{}->{}".format(i,j) ] )
       entry["recep{}".format(i)  ] = float( row[ "recep{}".format(i) ] )
       entry["w_AS->{}".format(i)  ] = float( row[ "w_AS->{}".format(i) ] )
      
      
      seed_to_genome_map[  int( row['seed'] ) ] =  entry ;
      
#######################    
    
    sorted_seeds_and_fit =  sorted(seed_to_fitness_map.items(), key=operator.itemgetter(1,0) )
    
    sorted_seeds_and_fit.reverse()
    sorted_seeds_and_fit = sorted_seeds_and_fit[ 0:quantity ]
    
    print( "sorted_seeds_and_fit: " )
    print ( sorted_seeds_and_fit )
    
    top_seeds = [x[0] for x in sorted_seeds_and_fit]
    print( "top_seeds: " )
    print ( top_seeds )

    record_files =  glob.glob(  '{}/seed_*.csv'.format( experiment_directory  ) ) 

    #dictionary( "seed" -> (dictionary ( t -> (data ) )
    
    
    count=0
    for record_file in record_files:
      
      if "ssio" in record_file:
       continue
      
      seed_num = re.sub('.*seed_', '', record_file )
      seed_num = re.sub('_.*', '', seed_num )
      seed_num= int(  seed_num )
      
      if seed != -1:
       if seed_num != seed:
        continue
        
      else:
      #only generate plots for top X
       if seed_num not in top_seeds:
        continue
      
      time = []
      modulation = []
      jointX = []
      jointY = []
      footX   = []
      footY  = []
      footState = []
      distance    = []
      
      n_out = {}
      for i in range(1, total_neurons+1):
       n_out[i] = []
      
      n_input = {}
      for i in range(1, total_neurons +1 ):
       n_input[i] = []
      
      angle = []
      
      pca_data = []
      angle_omega = []
      
      
      max_angle=0
      min_angle=0
      
      with open( record_file  ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
          #TEMPORARY HACK TO GET MPG TO PLOT
          if 'run' in row:
           if row['run'] == MPG_EXCLUDE:
            continue
          
          #print( record_file )
          
          time.append( float( row['time'] ) )
          modulation.append( float( row['modulation'] ) )
          jointX.append( float( row['jointX'] )  )
          jointY.append( float( row['jointY'] ) )
          footX.append( float( row['footX'] )  )
          footY.append( float( row['footY'] ) )
          footState.append( float( row['FootState'] ) )
          distance.append( float( row['cx'] ) )
          angle.append( float( row['angle']   ) )
          angle_omega.append( float( row['omega']   ) )
          
          
          for i in range(1, total_neurons +1 ):
           #print(   row   )
           n_out[i].append( float( row['n{}_out'.format(i) ] ) );

          #total_neurons
          for i in range(1, total_neurons+1 ):
           summed_input =0
           
           
           
           for j in range(1, total_neurons+1 ):
            if i != j:
             #get the latest   OUTPUT  X by
             #TODO CALCULATE BASED ON RECEPTOR STRENGTH
             receptor_str = seed_to_genome_map[seed_num]["recep{}".format(i)]
             receptor_str = 1
             if receptor_str != 1:
              print("Why receptor strength not 1?")
              quit()
             #print( "j: {}  i: {}".format(j, i) )
             #print( n_out[j][-1] )
             #print( seed_to_genome_map[seed_num] )
             #print( "w{}{}".format(j,i) )
             #
             #
             
             summed_input +=  (1 + receptor_str*modulation[-1] ) * ( n_out[j][-1] * seed_to_genome_map[seed_num]["w{}{}".format(j,i)] ) 
           
           #sensor input 
           sensor_input = (1 + receptor_str*modulation[-1] ) * ( angle[-1] * seed_to_genome_map[seed_num]["w_AS->{}".format(i)] ) 
           
           #print( "#1: " + str(sensor_input ) )
           
           summed_input += sensor_input
            
             
           #add calculated input to dataset for input to neuron i
           n_input[i].append( summed_input )
           
          #CLEANUP change to use dictionary and loops
          
          if 'n5_out' in row:
           n_out[4].append( float( row['n4_out'] )   )
           n_out[5].append( float( row['n5_out'] )   )
           pca_data.append(  ( float( row['n1_out'] ), float( row['n2_out'] ), float( row['n3_out'] ), float( row['n4_out'] ), float( row['n5_out'] ) ) )
          elif 'n4_out' in row:
           n_out[4].append( float( row['n4_out'] )   )
           pca_data.append(  ( float( row['n1_out'] ), float( row['n2_out'] ), float( row['n3_out'] ), float( row['n4_out'] ) ) )
          else:
           pca_data.append(  ( float( row['n1_out'] ), float( row['n2_out'] ), float( row['n3_out'] ) ) )
        #print( n_input[1] )
        #quit()
        #CLEANUP change to use dictionary and loops
        
        deriv_n1 = []
        pre_val=n_out[1][0]
        for val in  n_out[1]:
         deriv_n1.append( val - pre_val )
         pre_val=val
        
        deriv_n2 = []
        pre_val=n_out[2][0]
        for val in  n_out[2]:
         deriv_n2.append( val - pre_val )
         pre_val=val
        
        deriv_n3 = []
        pre_val=n_out[3][0]
        for val in  n_out[3]:
         deriv_n3.append( val - pre_val )
         pre_val=val
        
        
####################################        
        plt.close('all')
        fig, ( (ax1A, ax1B), (ax2A, ax2B), (ax3A,ax3B), (ax4A, ax4B), (ax5A, ax5B) ) = plt.subplots(nrows=5, ncols=2, figsize=figsize_xy )
        plt.xlabel('Time', fontsize=fs)
        
        #time = time
        fontsize=fs
        
        
        
        
        
        walking=[]
        for t in time[start:stop]:
         if t%44==0:
          walking.append(1.05)
         else:
          walking.append(1)
        
        #ax1A.scatter( time[start:stop], walking, label="Hypothetical Steps", color="black" )  
        #ax1A.set_ylabel( ylabel , fontsize=fs)
        
        
        config_plot(ax1A, time[start:stop], walking, "Ideal Steps", " Modulation level over time", fs,linecolor="black" ) 
        config_plot(ax1A, time[start:stop], list(map(lambda x: (1+x), modulation[start:stop])), "Modulation Signal", " Modulation level over time", fs,linecolor=(1,0,1) ) 
        
        
        #distance
        fitness_calc = distance[-1]/time[-1];
        
        print( "Calculating fitness based upon final position instead of from file..."  )
        #txt = "Fitness: {}".format(seed_to_fitness_map[seed_num][0] )
        txt = "Fitness: {}".format( fitness_calc )
        
        ymin, ymax = ax1A.get_ylim()
        xmin, xmax = ax1A.get_xlim()
        width=xmax-xmin
        height=ymax-ymin
        
        x=xmin+width/10
        y=ymax+height/10
        ax1A.text(x, y, txt, fontsize=fs, ha="left", va="top")
        
        bs_r = "OFF" if (seed_to_fitness_map[seed_num][1] == 0.0) else  str( seed_to_fitness_map[seed_num][1]  )
        ft_r = "OFF" if (seed_to_fitness_map[seed_num][2] == 0.0) else  str( seed_to_fitness_map[seed_num][2]  )
        fs_r = "OFF" if (seed_to_fitness_map[seed_num][3] == 0.0) else  str( seed_to_fitness_map[seed_num][3]  )
        
        
        
        config_plot(ax2A, time[short_start:short_stop], n_out[1][short_start:short_stop], "FT (r:"+ bs_r+")", "BackSwing neuron output over time", fs, (), "purple")
        config_plot(ax3A, time[short_start:short_stop], n_out[2][short_start:short_stop], "BS (r:"+ ft_r+")", "FootLift neuron output over time",  fs, (), "orange")
        config_plot(ax4A, time[short_start:short_stop], n_out[3][short_start:short_stop], "FS (r:"+ fs_r+")", "ForwardSwing neuron output over time", fs, (), "green")
        
        
        
        
        config_plot(ax5A, time[short_start:short_stop], deriv_n1[short_start:short_stop], r"$\Delta$ FT", " delta BS over time", fs, (), "purple")
        config_plot(ax5A, time[short_start:short_stop], deriv_n2[short_start:short_stop], r"$\Delta$ BS", " delta FT over time", fs, (), "orange" )
        config_plot(ax5A, time[short_start:short_stop], deriv_n3[short_start:short_stop], r"$\Delta$ FS", " delta FS over time", fs, (), "green")
        
        #ax2A.set_ylabel( "FT (r:"+ bs_r+")" , fs=fs )
        #ax3A.set_ylabel( "BS (r:"+ ft_r+")" , fontsize=fs )
        #ax4A.set_ylabel( "FS (r:"+ fs_r+")" , fontsize=fs )
        
        ax5A.set_ylabel( r'$\Delta$ neuron outputs' , fontsize=fs )
        
        
        
        #config_plot(ax1B, time[start:stop], modulation[start:stop], "Modulation", " Modulation level over time", fs)
        config_plot(ax1B, time[short_start:short_stop], angle[short_start:short_stop], "Leg Angle", " Leg Angle over time", fs)
        
        ax1B.text(x, y, txt, fontsize=fs, ha="left", va="top")
        
        
        config_plot(ax2B, time[short_start:short_stop], footState[short_start:short_stop], "FootState", "FootState over time", fs)
        config_plot(ax3B, time[short_start:short_stop], jointX[short_start:short_stop], "jointX", "jointX over time", fs)
        config_plot(ax4B, time[short_start:short_stop], footX[short_start:short_stop], "FootX", "footX over time", fs)
        config_plot(ax5B, time[short_start:short_stop], footY[short_start:short_stop], "FootY", "footY over time",  fs)
        
        plt.tight_layout()
        
        #plt.text(0, 0, "Fitness: {}".format(seed_to_fitness_map[seed_num] ), fontsize=fs)
        
        exp_title = re.sub(r'.*/','', experiment_directory )       
        exp_base = re.sub(r'.*/DATA/','', experiment_directory )    
        if alternate_output== "":
         plt.savefig("{0}/{1}/seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title  ),dpi=1000 )
        else:
         os.system("mkdir -p {}/NormalTrajectories".format(alternate_output) )
         plt.savefig("{0}/NormalTrajectories/seed_{1}_{2}.png".format(alternate_output, seed_num, exp_title  ),dpi=1000 )
##################################################
# just plot the activity of output neurons
##################################################
        

        plt.close('all')
        
        #fig, ( (ax1A), (ax2A), (ax3A), (ax4A), (ax5A), (ax6A) ) = plt.subplots(nrows=6, ncols=1, figsize=figsize_xy )        
        #TEMPHACK
        fig, ( (ax5A), (ax6A) ) = plt.subplots(nrows=2, ncols=1, figsize=figsize_xy )        
        plt.xlabel('Time',fontsize=fs)
        
        config_plot(ax1A, time[start:stop], modulation[start:stop], "Modulation", " Modulation level over time", fs)
        
        ymin, ymax = ax1A.get_ylim()
        xmin, xmax = ax1A.get_xlim()
        width=xmax-xmin
        height=ymax-ymin
        
        ax1A.axvline(x=time[short_start], color='green')
        ax1A.axvline(x=time[short_stop],  color='green')
        
        #ax1A.fill_between( time[start:stop], time[short_start], time[short_stop], facecolor='green', interpolate=True )
        
        x=xmin+width/10
        y=ymax+height/10
        ax1A.text(x, y, txt, fontsize=fs, ha="left", va="top")
        
        
        config_plot(ax2A, time[short_start:short_stop], angle[short_start:short_stop], "Leg Angle ", "Leg Angle over time", fs, (), "black")
        
        
        
        #config_plot(ax3A, time[short_start:short_stop], n_out[1][short_start:short_stop], "FT (r:"+ bs_r+")", "BackSwing neuron output over time", fs, (), "purple")
        #config_plot(ax4A, time[short_start:short_stop], n_out[2][short_start:short_stop], "BS (r:"+ ft_r+")", "FootLift neuron output over time",  fs, (), "orange")
        #config_plot(ax5A, time[short_start:short_stop], n_out[3][short_start:short_stop], "FS (r:"+ fs_r+")", "ForwardSwing neuron output over time", fs, (), "green")
        
        config_plot(ax3A, time[short_start:short_stop], n_out[1][short_start:short_stop], "FT output", "BackSwing neuron output over time", fs, (), "purple")
        config_plot(ax4A, time[short_start:short_stop], n_out[2][short_start:short_stop], "BS output", "FootLift neuron output over time",  fs, (), "orange")
        
        #TEMPHACK
        #config_plot(ax5A, time[short_start:short_stop], n_out[3][short_start:short_stop], "FS output", "ForwardSwing neuron output over time", fs, (), "green")
        
        config_plot(ax5A, time[short_start:short_stop], n_out[1][short_start:short_stop], "FT Output", "ForwardSwing neuron output over time", fs, (), "purple")
        config_plot(ax5A, time[short_start:short_stop], n_out[2][short_start:short_stop], "BS Output", "ForwardSwing neuron output over time", fs, (), "orange")
        config_plot(ax5A, time[short_start:short_stop], n_out[3][short_start:short_stop], "FS Output", "ForwardSwing neuron output over time", fs, (), "green")
        
        ax5A.set_ylabel( "Neuron Output" , fontsize=fs)
        ax5A.legend(loc='center left', fontsize=fs )
        plt.setp(ax5A.get_xticklabels(), visible=False)
              
        
        
        config_plot(ax6A, time[short_start:short_stop], deriv_n1[short_start:short_stop], r"$\Delta$ FT Output", " delta BS over time", fs, (), "purple")
        config_plot(ax6A, time[short_start:short_stop], deriv_n2[short_start:short_stop], r"$\Delta$ BS Output", " delta FT over time", fs, (), "orange")
        config_plot(ax6A, time[short_start:short_stop], deriv_n3[short_start:short_stop], r"$\Delta$ FS Output", " delta FS over time", fs, (), "green")
        
        
        
        #TODO ADD FLAG FOR TURNING THIS ON AND OFF
        if LEG_ANGLE_SENSOR:
         config_plot(ax6A, time[short_start:short_stop], angle_omega[short_start:short_stop], r"$\Delta$ Angular Velocity", " Leg Angular Velocity", fs, (), "black")
         
        
        
        #ax2A.set_ylabel( "FT (r:"+ bs_r+")" , fontsize=fs )
        #ax3A.set_ylabel( "BS (r:"+ ft_r+")" , fontsize=fs )
        #ax4A.set_ylabel( "FS (r:"+ fs_r+")" , fontsize=fs )
        
        ax6A.set_ylabel( r'$\Delta$ Neuron Output' , fontsize=fs )
        
        
        
        plt.tight_layout()
        legend = plt.legend(loc='center right', bbox_to_anchor=(1, 0.5) )
        
        #TEMPHACK
        #tickfs=fs-2
        ax6A.legend(loc='lower left', fontsize=fs  )
        for tick in ax6A.xaxis.get_major_ticks():
         tick.label.set_fontsize(tickfs) 
        for tick in ax6A.yaxis.get_major_ticks():
         tick.label.set_fontsize(tickfs) 
         
        plt.tight_layout()
        
        #plt.text(0, 0, "Fitness: {}".format(seed_to_fitness_map[seed_num] ), fontsize=fs)
        if alternate_output== "":
         plt.savefig("{0}/{1}/single_seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title  ),dpi=1000 )
        else:
         plt.savefig("{0}/NormalTrajectories/single_seed_{1}_{2}.png".format(alternate_output, seed_num, exp_title  ),dpi=1000 )
        
################################################
        #angle plots
        plt.close('all')
        fig, ( ( ax1B) ) = plt.subplots(nrows=1, ncols=1 )
        plt.xlabel(r"$\Theta$")
        fontsize=fs
        fitness_calc = distance[-1]/time[-1];
        print( "Calculating fitness based upon final position instead of from file..."  )
        txt = "Fitness: {}".format( fitness_calc )
        ymin, ymax = ax1A.get_ylim()
        xmin, xmax = ax1A.get_xlim()
        width=xmax-xmin
        height=ymax-ymin
        x=xmin+width/10
        y=ymax+height/10
        ax1A.text(x, y, txt, fontsize=fs, ha="left", va="top")
        config_plot(ax1B, angle[short_start:short_stop], angle_omega[short_start:short_stop], r"$\.\Theta$", "angle over time", fs)
        plt.tight_layout()
        legend = plt.legend(loc='center right', bbox_to_anchor=(1, 0.5) )
        plt.text(0, 0, "Fitness: {}".format(seed_to_fitness_map[seed_num] ), fontsize=fs)
        exp_title = re.sub(r'.*/','', experiment_directory )       
        exp_base = re.sub(r'.*/DATA/','', experiment_directory )    
        
        if alternate_output== "":
         plt.savefig("{0}/{1}/angles_seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title  ),dpi=1000 )
        else:
         plt.savefig("{0}/NormalTrajectories/angles_seed_{1}_{2}.png".format(alternate_output, seed_num, exp_title  ),dpi=1000 )
#############################################################
        
        
        fig = plt.figure()

        dyn1 = fig.gca(projection='3d')
        
        #lowest mapped to blue, zero to black, highest mapped to red
        colors = [(0, 0, 1, 0.1), (0, 0, 0, 0.1), (1, 0, 0, 0.1)]  # R -> G -> B
        
        cdict1 = {'red':   ((0.0, 0.0, 0.0),
                   (0.5, 0.0, 0.1),
                   (1.0, 1.0, 1.0)),

         'green': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'blue':  ((0.0, 0.0, 1.0),
                   (0.5, 0.1, 0.0),
                   (1.0, 0.0, 0.0))
        }


        
        #n_bins = [3, 6, 10, 100]  # Discretizes the interpolation into bins
        cmap_name = 'my_list'

        # Create the colormap
        cm = LinearSegmentedColormap.from_list( cmap_name, colors  )
        #blue_red1 = LinearSegmentedColormap('BlueRed1', cdict1)        
        
        
        co=[]
        transparency=0.5
        thickness=2
        ssio_thickness=SSIO_THICKNESS
        
        
        for m in modulation[start:stop]:
         if m < 0:
          co.append(  (0,0,abs(m), transparency)   )
         elif m > 0:
          co.append(  ( m,0,0, transparency)   )
         else:
          co.append(  (0,0,0, transparency)  )
        
        #norm1 = matplotlib.colors.Normalize(vmin=-0.5, vmax=0.5, clip=True)
        
        X = [ n_out[1][start:stop], n_out[2][start:stop], n_out[3][start:stop] ]
        points = np.array([X[0], X[1], X[2]]).T.reshape(-1, 1, 3)
        segs = np.concatenate([points[:-1], points[1:]], axis = 1)
        lc=Line3DCollection(segs,colors=co )
        plt.setp(lc, linewidth=thickness )
        dyn1.add_collection( lc )
        
        #OLD WAY
        #dyn1.scatter( n_out[1][start:stop], n_out[2][start:stop], n_out[3][start:stop], c=modulation[start:stop], cmap=cm, label='neuron activation dynamics' )
        #dyn1.scatter( n_out[1][start:stop], n_out[2][start:stop], n_out[3][start:stop], c=co, label='neuron activation dynamics')
        dyn1.set_xlabel("FT")
        dyn1.set_ylabel("BS")
        dyn1.set_zlabel("FS")
        
        
        
        dyn1.legend()
        if alternate_output== "":
         plt.savefig("{0}/{1}/dynamics3d_seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title  ),dpi=1000 )
        else:
         plt.savefig("{0}/NormalTrajectories/dynamics3d_seed_{1}_{2}.png".format(alternate_output, seed_num, exp_title  ),dpi=1000 )
        
        #######################################################
        # 2d plots
        
        
        if SSIO_MODE:
         ssio_data, SSIO_MODE = get_ssio_data_for_plotting( DATA, exp_base, seed_num )
        
        
        SHOW_2D_NON_SS=False
###########################################################################################################################        
        if SHOW_2D_NON_SS:
         fig, ( (dyn2), (dyn3), (dyn4) ) = plt.subplots(nrows=3, ncols=1, figsize=figsize_xy )
         
         #old scatter plot
         #dyn2.scatter( n_out[1][start:stop], n_out[2][start:stop], c=modulation[start:stop], cmap=cm, label='neuron activation dynamics' )
         X = [ n_out[1][start:stop], n_out[2][start:stop] ]
         points = np.array([X[0], X[1] ]).T.reshape(-1, 1, 2)
         segs = np.concatenate([points[:-1], points[1:]], axis = 1)
         lc = LineCollection(segs, colors=co)  #cmap=cmap, norm=norm)
         plt.setp(lc, linewidth=thickness )
         dyn2.add_collection( lc )
         if SSIO_MODE:
          ss_i=1
          for mod in ssio_data[i].keys():
           R=min( 1, customize_ssio_color(max(mod*2,0)) )
           G=0
           B=min(1, customize_ssio_color(max(-mod*2,0)) )
           ssio_color=(R,G,B)
           dyn2.plot( ssio_data[ss_i][mod]["x"] , ssio_data[ss_i][mod]["y"], alpha=0.5, color=ssio_color, linewidth=ssio_thickness )
         
         dyn2.set_xlabel("FT")
         dyn2.set_ylabel("BS")
         
         #dyn3.scatter( n_out[1][start:stop], n_out[3][start:stop], c=modulation[start:stop], cmap=cm, label='neuron activation dynamics' )
         X = [ n_out[1][start:stop], n_out[3][start:stop] ]
         points = np.array([X[0], X[1] ]).T.reshape(-1, 1, 2)
         segs = np.concatenate([points[:-1], points[1:]], axis = 1)
         lc = LineCollection(segs, colors=co)  #cmap=cmap, norm=norm)
         plt.setp(lc, linewidth=thickness )
         dyn3.add_collection( lc )
         if SSIO_MODE:
          ss_i=2
          for mod in ssio_data[i].keys():
           R=min( 1, customize_ssio_color(max(mod*2,0)) )
           G=0
           B=min(1, customize_ssio_color(max(-mod*2,0)) )
           ssio_color=(R,G,B)
           dyn3.plot( ssio_data[ss_i][mod]["x"] , ssio_data[ss_i][mod]["y"], alpha=0.5, color=ssio_color, linewidth=ssio_thickness )
         dyn3.set_xlabel("FT")
         dyn3.set_ylabel("FS")
         
         #dyn4.scatter( n_out[2][start:stop], n_out[3][start:stop], c=modulation[start:stop], cmap=cm, label='neuron activation dynamics' )
         X = [ n_out[2][start:stop], n_out[3][start:stop] ]
         points = np.array([X[0], X[1] ]).T.reshape(-1, 1, 2)
         segs = np.concatenate([points[:-1], points[1:]], axis = 1)
         lc = LineCollection(segs, colors=co)  #cmap=cmap, norm=norm)
         plt.setp(lc, linewidth=thickness )
         dyn4.add_collection( lc )
         if SSIO_MODE:
          ss_i=3
          for mod in ssio_data[i].keys():
           R=min( 1, customize_ssio_color(max(mod*2,0)) )
           G=0
           B=min(1, customize_ssio_color(max(-mod*2,0)) )
           ssio_color=(R,G,B)
           dyn4.plot( ssio_data[ss_i][mod]["x"] , ssio_data[ss_i][mod]["y"], alpha=0.5, color=ssio_color, linewidth=ssio_thickness )
         dyn4.set_xlabel("BS")
         dyn4.set_ylabel("FS")
         
         plt.tight_layout()
         
         if alternate_output== "":
          plt.savefig("{0}/{1}/dynamics2d_seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title  ),dpi=1000 )
         else:
          plt.savefig("{0}/NormalTrajectories/dynamics2d_seed_{1}_{2}.png".format(alternate_output, seed_num, exp_title  ),dpi=1000 )
###################################################################################################################         
        
        #######################################################
        # 2d plots fixed
        
        ##############################
        # SSIO include if files exist
        ##############################

        if SSIO_MODE:
         ssio_data, SSIO_MODE = get_ssio_data_for_plotting( DATA, exp_base, seed_num )
        
        
        fig, ( (dyn2), (dyn3), (dyn4) ) = plt.subplots(nrows=3, ncols=1, figsize=figsize_xy )
        
        
        X = [ n_input[1][start:stop], n_out[1][start:stop] ]
        points = np.array([X[0], X[1] ]).T.reshape(-1, 1, 2)
        segs = np.concatenate([points[:-1], points[1:]], axis = 1)
        
        lc = LineCollection(segs, color="purple") # colors=co)  #cmap=cmap, norm=norm)
        plt.setp(lc, linewidth=thickness )
        dyn2.add_collection( lc )
        if SSIO_MODE:
         ss_i=1
         for mod in ssio_data[i].keys():
          R=min( 1, customize_ssio_color(max(mod*2,0)) )
          G=0
          B=min(1, customize_ssio_color(max(-mod*2,0)) )
          ssio_color=(R,G,B)
          dyn2.plot( ssio_data[ss_i][mod]["x"] , ssio_data[ss_i][mod]["y"], alpha=0.5, color=ssio_color, linewidth=ssio_thickness )
        dyn2.set_xlabel("BS+FS")
        dyn2.set_ylabel("FT")
        if XLIM_MODE:
         dyn2.set_xlim(X_LIM_A, X_LIM_B )
        
        X = [ n_input[2][start:stop], n_out[2][start:stop] ]
        points = np.array([X[0], X[1] ]).T.reshape(-1, 1, 2)
        segs = np.concatenate([points[:-1], points[1:]], axis = 1)
        lc = LineCollection(segs, color="orange")  #colors=co)  #cmap=cmap, norm=norm)
        plt.setp(lc, linewidth=thickness )
        dyn3.add_collection( lc )
        if SSIO_MODE:
         ss_i=2
         for mod in ssio_data[i].keys():
          R=min( 1, customize_ssio_color(max(mod*2,0)) )
          G=0
          B=min(1, customize_ssio_color(max(-mod*2,0)) )
          ssio_color=(R,G,B)
          dyn3.plot( ssio_data[ss_i][mod]["x"] , ssio_data[ss_i][mod]["y"], alpha=0.5, color=ssio_color, linewidth=ssio_thickness )         
         
        dyn3.set_xlabel("FT+FS")
        dyn3.set_ylabel("BS")
        if XLIM_MODE:
         dyn3.set_xlim(X_LIM_A, X_LIM_B)
        
        X = [ n_input[3][start:stop], n_out[3][start:stop] ]
        points = np.array([X[0], X[1] ]).T.reshape(-1, 1, 2)
        segs = np.concatenate([points[:-1], points[1:]], axis = 1)
        lc = LineCollection(segs, color="green")  #colors=co)  #cmap=cmap, norm=norm)
        plt.setp(lc, linewidth=thickness )
        dyn4.add_collection( lc )
        if SSIO_MODE:
         ss_i=3
         for mod in ssio_data[i].keys():
          R=min( 1, customize_ssio_color(max(mod*2,0)) )
          G=0
          B=min(1, customize_ssio_color(max(-mod*2,0)) )
          ssio_color=(R,G,B)
          dyn4.plot( ssio_data[ss_i][mod]["x"] , ssio_data[ss_i][mod]["y"], alpha=0.5, color=ssio_color, linewidth=ssio_thickness )
          
        dyn4.set_xlabel("FT+BS")
        dyn4.set_ylabel("FS")
        if XLIM_MODE:
         dyn4.set_xlim(X_LIM_A, X_LIM_B)
        
        plt.tight_layout()
        if alternate_output== "":
         plt.savefig("{0}/{1}/summed_dynamics2d_seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title  ),dpi=1000 )
        else:
         plt.savefig("{0}/NormalTrajectories/summed_dynamics2d_seed_{1}_{2}.png".format(alternate_output, seed_num, exp_title  ),dpi=1000 )
        
        
        #not working
        """        
        fig = plt.figure()
        pca_3d = fig.gca(projection='3d')
        
        sklearn_pca = sklearnPCA(n_components=3)
        
        X_std = StandardScaler().fit_transform( pca_data)
        
        Y_sklearn = sklearn_pca.fit_transform( X_std )
        
        pca_x = Y_sklearn[  0]
        pca_y = Y_sklearn[  1]
        pca_z = Y_sklearn[  2]
        
        
        pca_3d.scatter( pca_x, pca_y, pca_z, label='principal component analysis of neuron activation dynamics' )
        #, c=modulation[start:stop], cmap=cm, label='neuron activation dynamics' )
        pca_3d.set_xlabel("PC1")
        pca_3d.set_ylabel("PC2")
        pca_3d.set_zlabel("PC3")
        
        plt.savefig("{0}/{1}/PCA_3d_seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title  ) )
"""        
      

        if count > quantity:
         return

      print( min_angle )
      print( max_angle )   

def plot_activity2(experiment_directory, testing_dict, comparison_name, quantity=10, short_start=0, short_stop=1000, plot_all_recorded_activity_mode=False, SSIO_MODE=False, PNG_W=8, PNG_Y=11, seed=-1,alternate_output="" ):    
    
    SINGLE_SEED_MODE=True
    if seed == -1:
     SINGLE_SEED_MODE=False
    
    start=0
    stop=-1
    fontsize=fs
    txt = "no txt"
    
    print( "Plotting activity2")
    #quit()
    
    seed_to_fitness_map={}
    fitness_and_receptors = "{}/fitness_and_receptors.txt".format( experiment_directory  )
    total_receptors=-1
    with open( fitness_and_receptors  ) as fitness_file:
     fit_reader = csv.DictReader(fitness_file)
     for row in fit_reader:
      entry = []
      f = float( row['fitness'] )
      entry.append( f )
      if total_receptors == -1:
       r=1
       while "r"+str(r) in row:
        r+=1
        total_receptors=r
      #total_receptors
      for r in range(1, total_receptors):
       if "r"+str(r) in row:
        entry.append( float( row['r'+str(r)   ]  ) )
       else:
        print("why???????????????????????????????????????????????????")
        quit()
      
      
      seed_to_fitness_map[  int( row['seed'] ) ] =  entry ;
    
    sorted_seeds_and_fit =  sorted(seed_to_fitness_map.items(), key=operator.itemgetter(1,0) )
    sorted_seeds_and_fit.reverse()
    sorted_seeds_and_fit = sorted_seeds_and_fit[ 0:quantity ]
    
    #print(sorted_seeds_and_fit)
    #print( seed_to_fitness_map )
    
    #quit()
    
    if plot_all_recorded_activity_mode:
     #print( experiment_directory )
     #print( testing_dict )
     #quit()
     recorded_activity_files =  glob.glob(  '{}/seed_*.csv'.format( list(testing_dict.keys())[0]  ) ) 

     for r in range(0, len(recorded_activity_files)):
      if "recorded" in recorded_activity_files[r]:
       recorded_activity_files[r] = re.sub(".*seed_","",recorded_activity_files[r] ) 
       recorded_activity_files[r] = re.sub("_recorded.*","",recorded_activity_files[r] ) 
      
     sorted_seeds_and_fit =[]
     
     for r in recorded_activity_files:
      sorted_seeds_and_fit.append( (int(r), seed_to_fitness_map[ int(r) ]) )
     #sorted_seeds_and_fit.append( (35, seed_to_fitness_map[35]) )
     #sorted_seeds_and_fit.append( (49, seed_to_fitness_map[49]) )
     
    else:
     print("XXXX")
     quit()

###########################  setup genome map
    seed_to_genome_map = {}
    #should actually be using the phenotype, not genotype
    #genomes = "{}/genomes.txt".format( experiment_directory  )
    genomes = "{}/phenotypes.txt".format( experiment_directory  )
    total_neurons=-1
    with open( genomes  ) as genomes_file:
     genome_reader = csv.DictReader(genomes_file)
     for row in genome_reader:
      entry = {}
      #calculate total_neurons one time
      if total_neurons == -1:
       n=1
       #check until bias# not found
       while "bias"+str(n) in row:
        total_neurons=n
        n+=1
      #total_genomes
      for i in range(1, total_neurons+1):
       for j in range( 1, total_neurons+1 ):
        entry["w{}{}".format(i,j)  ] = float( row[ "w_{}->{}".format(i,j) ] )
       entry["recep{}".format(i)  ] = float( row[ "recep{}".format(i) ] )
       entry["w_AS->{}".format(i)  ] = float( row[ "w_AS->{}".format(i) ] )
      seed_to_genome_map[  int( row['seed'] ) ] =  entry ;
#######################    

    
    print( "sorted_seeds_and_fit: " )
    print ( sorted_seeds_and_fit )
    
    
    top_seeds = [x[0] for x in sorted_seeds_and_fit]
    print( "top_seeds: " )
    print ( top_seeds )

    print( experiment_directory )
    #quit()
    record_files =  glob.glob(  '{}/seed_*_recorded_activity.csv'.format( experiment_directory  ) ) 
    
    count=0
    
    #this will store ALL the data needed for all the various plots to be accessed at a later time
    seed_data_dict = {}
    
    print( "record files {}".format( record_files ))
    #quit()
    
    #loop through all seed activity files in folder
    for record_file in record_files:
      seed_num = re.sub('.*seed_', '', record_file )
      seed_num = re.sub('_.*', '', seed_num )
      seed_num= int(  seed_num )
      
      if SINGLE_SEED_MODE:
      
       if seed != seed_num:
        continue
      
      else:
       #only generate plots for top X
       if seed_num not in top_seeds:
        #print("skipping seed {}".format(seed_num) )
        continue
       else:
        print( "plotting for seed {}".format(seed_num) )
        #continue
      
      seed_data_dict[ seed_num ] = {}
      
      #print( testing_dict.keys() )
      
      for testing_dir in testing_dict.keys():
       print( "Get all data from {} for seed {}".format(  testing_dir, seed_num ) )
       
       #                SEED       TESTING_DIR      DATA
       seed_data_dict[ seed_num ][ testing_dir ] =  {}
       seed_data_dict[ seed_num ][ testing_dir ]["n_out"] = {}
       seed_data_dict[ seed_num ][ testing_dir ]["deriv_n_out"] = {}
       seed_data_dict[ seed_num ][ testing_dir ]["n_input"] = {}
       
       #stats to track from data file
       stats=[ "time", "modulation", "jointX", "jointY", "footX", "footY", "footState", "distance","angle", "omega" ]
       
       
       for i in range(1, total_neurons+1):
        seed_data_dict[ seed_num ][ testing_dir ]["n_out"][i] = []
        seed_data_dict[ seed_num ][ testing_dir ]["deriv_n_out"][i] = []
        seed_data_dict[ seed_num ][ testing_dir ]["n_input"][i] = []
       
       
       for stat in stats:
        seed_data_dict[ seed_num ][ testing_dir ][ stat ] = []
       
       #print( seed_data_dict[ seed_num ][ testing_dir ] )
       
       if not 'angle' in seed_data_dict[ seed_num ][ testing_dir ] :
        print("no angle found in {}".format(testing_dir) )
        quit()
        
       data_csv_path="{}/seed_{}_recorded_activity.csv".format( testing_dir, seed_num )
       
       print( "Opening:" ) 
       print( data_csv_path  )
       #quit()
        
       with open( data_csv_path  ) as csvfile:
         reader = csv.DictReader(csvfile)
         for row in reader:
           #TODO jasonayoder this is a hack to make MPG data plotting work
           #
           if 'run' in row:
            if row['run'] == MPG_EXCLUDE:
             continue
           
           seed_data_dict[ seed_num ][ testing_dir ]["time"].append( float( row['time'] ) );
           seed_data_dict[ seed_num ][ testing_dir ]["modulation"].append( float( row['modulation'] ) );
           seed_data_dict[ seed_num ][ testing_dir ]["jointX"].append( float( row['jointX'] )  / 10 );
           seed_data_dict[ seed_num ][ testing_dir ]["jointY"].append( float( row['jointY'] ) );
           seed_data_dict[ seed_num ][ testing_dir ]["footX"].append( float( row['footX'] ) / 10 );
           seed_data_dict[ seed_num ][ testing_dir ]["footY"].append( float( row['footY'] ) );
           seed_data_dict[ seed_num ][ testing_dir ]["footState"].append( float( row['FootState'] ) );
           seed_data_dict[ seed_num ][ testing_dir ]["distance"].append( float( row['cx'] ) );
           
           if not "angle" in  row:
            seed_data_dict[ seed_num ][ testing_dir ]["angle"].append( 0)
            seed_data_dict[ seed_num ][ testing_dir ]["omega"].append( 0)
            
           else:
            seed_data_dict[ seed_num ][ testing_dir ]["angle"].append( float( row['angle'] ) );
            seed_data_dict[ seed_num ][ testing_dir ]["omega"].append( float( row['omega'] ) );
           
           
           for i in range(1, total_neurons+1):
            seed_data_dict[ seed_num ][ testing_dir ]["n_out"][i].append( float( row['n{}_out'.format(i)] ) );
           
            
           #####calculate the total input to given neurons
           
           #total_neurons
           for i in range(1, total_neurons+1 ):
            summed_input =0
            for j in range(1, total_neurons+1 ):
             if i != j:
              #get the latest   OUTPUT  X by
              #TODO CALCULATE BASED ON RECEPTOR STRENGTH
              receptor_str = seed_to_genome_map[seed_num]["recep{}".format(i)]
              
              receptor_str = 1
              
              if receptor_str != 1:
               print("Why receptor strength not 1?")
               quit()
              
              #other neuron input
              summed_input +=  (1 + receptor_str*seed_data_dict[ seed_num ][ testing_dir ]["modulation"][-1] ) * ( seed_data_dict[ seed_num ][ testing_dir ]["n_out"][j][-1] * seed_to_genome_map[seed_num]["w{}{}".format(j,i)] ) 
             
            #sensor input 
            sensor_input =  (1 + receptor_str*seed_data_dict[ seed_num ][ testing_dir ]["modulation"][-1] ) * ( seed_data_dict[ seed_num ][ testing_dir ]["angle"][-1] * seed_to_genome_map[seed_num]["w_AS->{}".format(i)] )  
            
            #sanity check only valid when running with CPG
            #if sensor_input != 0:
            # print("non-zero answer!")
            # print( "w_AS->{} weight is ".format(i) )
            # print( "weight: "+ str( seed_to_genome_map[seed_num]["w_AS->{}".format(i) ] ) )
            # print( "#2: "+ str(sensor_input) )
            # 
            # quit()
             
            summed_input += sensor_input
              
            #add calculated input to dataset for input to neuron i
            seed_data_dict[ seed_num ][ testing_dir ]["n_input"][i].append( summed_input )
           
            
         for i in range(1, total_neurons+1):
          #print( "seed_num:{}    testing_dir: {}     i:{} ".format(seed_num, testing_dir, i ) )
          #print("1"+ str( seed_data_dict[ seed_num ] ))
          #print("2"+ str( seed_data_dict[ seed_num ][ testing_dir ] ))
          #print("3"+ str( seed_data_dict[ seed_num ][ testing_dir ]["n_out"] ))
          #print("4"+ str( seed_data_dict[ seed_num ][ testing_dir ]["n_out"][i] ))
          pre_val= seed_data_dict[ seed_num ][ testing_dir ]["n_out"][i][0] 
          
          for val in  seed_data_dict[ seed_num ][ testing_dir ]["n_out"][i]:
           seed_data_dict[ seed_num ][ testing_dir ]["deriv_n_out"][i].append( val - pre_val )
           pre_val=val
         
###############################################
# DATA PROCESSED AND LOADED INTO seed_data_dict
###############################################       
       
      plt.close('all')
      
        
      
      #GET MAX VALUES TO KNOW THE GRID EXPECTED
      max_row=0
      max_col=0
      for testing_dir in testing_dict.keys():
       if int(testing_dict[testing_dir][1]) > max_row:
        max_row = int(testing_dict[testing_dir][1])
       if int(testing_dict[testing_dir][2]) > max_col:
        max_col = int(testing_dict[testing_dir][2])
      max_row+=1
      max_col+=1
      
      #
      #
      # 
      plot_data_types=["distance",  "derivs" ]  #"n1_out", "n2_out" ,"n3_out", "derivs"]


      for st in plot_data_types:

       #FIRST AGG PLOT
       fig = plt.figure(1)
       fig.set_size_inches(PNG_W, PNG_Y)

       first=True
      
       #######################################
       for testing_dir in testing_dict.keys():
        print(   testing_dict[testing_dir][1]+" , "+testing_dict[testing_dir][2]  )
        rr=int(testing_dict[testing_dir][1])
        cc=int(testing_dict[testing_dir][2])
        
        
        
        n=( rr* max_col  + cc+1 )
        #ax = fig.add_subplot( 3, 2, n )
        #ax = fig.add_subplot( max_row, max_col, n, sharey=ax1 )
        
        if first:
         ax = fig.add_subplot( max_row, max_col, n )
         firstAx=ax
         first=False
         for tick in ax.yaxis.get_major_ticks():
          tick.label.set_fontsize(tickfs) 
        else:
         ax = fig.add_subplot( max_row, max_col, n, sharey=firstAx )
         plt.setp(ax.get_yticklabels(), visible=False)
         
         
        #print( "seed_num: {} \ntesting_dir: {}\n seed_data_dict[ seed_num ].keys(): {}".format(seed_num, testing_dir, seed_data_dict[ seed_num ].keys() ))
        
        if st == "derivs":
         
         plt.plot( seed_data_dict[ seed_num ][ testing_dir ]["time"][short_start:short_stop], seed_data_dict[ seed_num ][ testing_dir ]["deriv_n_out"][1][short_start:short_stop], label=r"$\Delta$ FT" )
         plt.plot( seed_data_dict[ seed_num ][ testing_dir ]["time"][short_start:short_stop], seed_data_dict[ seed_num ][ testing_dir ]["deriv_n_out"][2][short_start:short_stop], label=r"$\Delta$ BS" )
         plt.plot( seed_data_dict[ seed_num ][ testing_dir ]["time"][short_start:short_stop], seed_data_dict[ seed_num ][ testing_dir ]["deriv_n_out"][3][short_start:short_stop], label=r"$\Delta$ FS" )
         ax.set_ylabel( r'$\Delta$ neuron outputs' )   #, fontsize=fs )
         legend = ax.legend(loc='center right' )
         
        else:
         plt.plot( seed_data_dict[ seed_num ][ testing_dir ]["time"][start:stop], seed_data_dict[ seed_num ][ testing_dir ][ st][start:stop] )      # Or whatever you want in the subplot
         
         ax.set_ylabel( st, fontsize=fs )
        plt.title(  testing_dict[testing_dir][0]    )
        
       plt.tight_layout()
       
       exp_title = re.sub(r'.*/','', experiment_directory )
       exp_base = re.sub(r'.*/DATA/','', experiment_directory )
       
       #plt.savefig("demo_simple_seed_{}.png".format( seed_num  ) )
       
       #print( "mkdir -p {0}/TESTS/{1}/{2}".format(PLOTS, exp_base, comparison_name)  )
       #quit()
       
       if alternate_output=="":
        os.system("mkdir -p {0}/TESTS/{1}/{2}".format(PLOTS, exp_base, comparison_name) )
        plt.savefig("{0}/TESTS/{1}/{5}/{4}_seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title, st, comparison_name  ),dpi=1000 )
       else:
        #print( "mkdir -p {0}/TESTING_TRAJECTORIES/{1}".format(alternate_output, comparison_name) )
        os.system("mkdir -p {0}/TESTING_TRAJECTORIES/{1}".format(alternate_output, comparison_name) )
        plt.savefig("{0}/TESTING_TRAJECTORIES/{4}/{3}_seed_{1}_{2}.png".format(alternate_output, seed_num, exp_title, st, comparison_name  ),dpi=1000 )

       plt.close('all')
       ######################################
       
##################################################
# just plot the activity of output neurons
##################################################



      plt.close('all')
      
      
      fig, ( (ax1A), (axFOOTSTATE), (ax2A), (ax3A), (ax4A), (ax5A), (ax6A) ) = plt.subplots(nrows=7, ncols=1, figsize=(PNG_W, PNG_Y) )        
      plt.xlabel('Time',fontsize=fs)
      
      
      #multiple plots
      for testing_dir in testing_dict.keys():
       
       
       time=seed_data_dict[ seed_num ][ testing_dir ]["time"]
       modulation=seed_data_dict[ seed_num ][ testing_dir ]["modulation"]
       angle = seed_data_dict[ seed_num ][ testing_dir ]["angle"]
       n_out={}
       
       n_out[1]=seed_data_dict[ seed_num ][ testing_dir ]["n_out"][1]
       n_out[2]=seed_data_dict[ seed_num ][ testing_dir ]["n_out"][2]      
       n_out[3]=seed_data_dict[ seed_num ][ testing_dir ]["n_out"][3]
       deriv_n1=seed_data_dict[ seed_num ][ testing_dir ]["deriv_n_out"][1]
       deriv_n2=seed_data_dict[ seed_num ][ testing_dir ]["deriv_n_out"][2]
       deriv_n3=seed_data_dict[ seed_num ][ testing_dir ]["deriv_n_out"][3]
       footState=seed_data_dict[ seed_num ][ testing_dir ]["footState"]
       footY= list( map( lambda x: (x-25.5)/2, seed_data_dict[ seed_num ][ testing_dir ]["footY"]) )
       
       transparency  =0.5
       mod_color =(0,0,0)
       m = seed_data_dict[ seed_num ][ testing_dir ]["modulation"][0]
       
       #XXXXXXXXXXXXXX
       
       if m < 0:
        mod_color = (0,0,customize_mod_color(abs(m) ), transparency )
       elif m > 0:
        mod_color = (customize_mod_color(m),0,0, transparency)  
       else:
        mod_color = (0,0,0, transparency)  
        
       
       config_plot(ax1A, time[start:stop], modulation[start:stop], "Modulation", " Modulation level over time", fontsize, True, mod_color)
       
       if m==0:
        #config_plot(axFOOTSTATE, time[short_start:short_stop], footState[short_start:short_stop], "FootState", " Leg Angle over time", fontsize, True, "black")
        config_plot(axFOOTSTATE, time[short_start:short_stop], footY[short_start:short_stop], "FootY", " Leg Angle over time", fontsize, True, "gray")
       else:
        #config_plot(axFOOTSTATE, time[short_start:short_stop], footState[short_start:short_stop], "FootState", " Leg Angle over time", fontsize, True, mod_color )
        config_plot(axFOOTSTATE, time[short_start:short_stop], footY[short_start:short_stop], "FootY", " Leg Angle over time", fontsize, True, mod_color )
       
       
       config_plot(ax2A, time[short_start:short_stop], angle[short_start:short_stop], "Leg Angle", " Leg Angle over time", fontsize, True, mod_color)
       
       
       ymin, ymax = ax1A.get_ylim()
       xmin, xmax = ax1A.get_xlim()
       width=xmax-xmin
       height=ymax-ymin
       
       ax1A.axvline(x=time[short_start], color='green')
       ax1A.axvline(x=time[short_stop],  color='green')
       
       #ax1A.fill_between( time[start:stop], time[short_start], time[short_stop], facecolor='green', interpolate=True )
       
       x=xmin+width/10
       y=ymax+height/10
       
       
       #CLEANUP
       #config_plot(ax2A, time[short_start:short_stop], n_out[1][short_start:short_stop], "FT (r:"+ bs_r+")", "BackSwing neuron output over time", fontsize)
       #config_plot(ax3A, time[short_start:short_stop], n_out[2][short_start:short_stop], "BS (r:"+ ft_r+")", "FootLift neuron output over time",  fontsize)
       #config_plot(ax4A, time[short_start:short_stop], n_out[3][short_start:short_stop], "FS (r:"+ fs_r+")", "ForwardSwing neuron output over time", fontsize)
       
       if m == 0:  #True
        config_plot(ax3A, time[short_start:short_stop], n_out[1][short_start:short_stop], "FT output", "Foot neuron output over time", fontsize, True, "purple" )
        config_plot(ax4A, time[short_start:short_stop], n_out[2][short_start:short_stop], "BS output", "BackSwing neuron output over time",  fontsize, True, "orange" )
        config_plot(ax5A, time[short_start:short_stop], n_out[3][short_start:short_stop], "FS output", "ForwardSwing neuron output over time", fontsize, True, "green" )
       else:
        config_plot(ax3A, time[short_start:short_stop], n_out[1][short_start:short_stop], "FT output", "Foot neuron output over time", fontsize, True, mod_color )
        config_plot(ax4A, time[short_start:short_stop], n_out[2][short_start:short_stop], "BS output", "BackSwing neuron output over time",  fontsize, True, mod_color )
        config_plot(ax5A, time[short_start:short_stop], n_out[3][short_start:short_stop], "FS output", "ForwardSwing neuron output over time", fontsize, True, mod_color )

       
       
       config_plot(ax6A, time[short_start:short_stop], deriv_n1[short_start:short_stop], r"$\Delta$ FT", " delta FT over time", fontsize, True, "purple")
       config_plot(ax6A, time[short_start:short_stop], deriv_n2[short_start:short_stop], r"$\Delta$ BS", " delta BS over time", fontsize, True, "orange")
       config_plot(ax6A, time[short_start:short_stop], deriv_n3[short_start:short_stop], r"$\Delta$ FS", " delta FS over time", fontsize, True, "green" )
      
      ax1A.text(x, y, txt, fontsize=fs, ha="left", va="top") 
      
      ax2A.set_ylabel( "Leg Angle " , fontsize=fs )
      ax3A.set_ylabel( "FT Output" , fontsize=fs )
      ax4A.set_ylabel( "BS Output" , fontsize=fs )
      ax5A.set_ylabel( "FS Output" , fontsize=fs )
      
      ax6A.set_ylabel( r'$\Delta$ neuron outputs' , fontsize=fs )
      
      plt.tight_layout()
      #legend = plt.legend(loc='center right', bbox_to_anchor=(1, 0.5) )
      #plt.text(0, 0, "Fitness: {}".format(seed_to_fitness_map[seed_num] ), fontsize=fs)
      
      #plt.savefig("{0}/{1}/single_seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title  ) )
      if alternate_output=="":
       plt.savefig("{0}/TESTS/{1}/{5}/neurons_act_seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title, st, comparison_name  ),dpi=1000 )
      else:
       plt.savefig("{0}/TESTING_TRAJECTORIES/{4}/neurons_act_seed_{1}_{2}.png".format(alternate_output, seed_num, exp_title, st, comparison_name  ),dpi=1000 )
      
      
###########################################################

      #FIRST AGG PLOT
      fig = plt.figure(2)
      fig.set_size_inches(PNG_W, PNG_Y)
      
      for testing_dir in testing_dict.keys():
       rr=int(testing_dict[testing_dir][1])
       cc=int(testing_dict[testing_dir][2])
       n=( rr*max_col+ cc+1 )
       ax = fig.add_subplot( max_row, max_col, n,  projection='3d' )
       
      
       #lowest mapped to blue, zero to black, highest mapped to red
       colors = [(0, 0, 1, 0.1), (0, 0, 0, 0.1), (1, 0, 0, 0.1)]  # R -> G -> B
        
       cdict1 = {'red':   ((0.0, 0.0, 0.0),
                  (0.5, 0.0, 0.1),
                  (1.0, 1.0, 1.0)),

        'green': ((0.0, 0.0, 0.0),
                  (1.0, 0.0, 0.0)),
        'blue':  ((0.0, 0.0, 1.0),
                  (0.5, 0.1, 0.0),
                  (1.0, 0.0, 0.0))
       }
       
       cmap_name = 'my_list'
       # Create the colormap
       cm = LinearSegmentedColormap.from_list( cmap_name, colors  )
       co=[]
       transparency=0.5
       thickness=2
       ssio_thickness=SSIO_THICKNESS
       start=0
       stop=-1
       
       #seed_data_dict[ seed_num ][ testing_dir ]["modulation"]
       
       BRIGHT_MODULATION_MODE=True
       
       for m in seed_data_dict[ seed_num ][ testing_dir ]["modulation"][start:stop]:
        if m < 0:
         co.append(  (0,0,customize_mod_color(abs(m)), transparency)   )
        elif m > 0:
         co.append(  ( customize_mod_color(m),0,0, transparency)   )
        else:
         co.append(  (0,0,0, transparency)  )
       
       #norm1 = matplotlib.colors.Normalize(vmin=-0.5, vmax=0.5, clip=True)
       
       X = [ seed_data_dict[ seed_num ][ testing_dir ]["n_out"][1][start:stop], seed_data_dict[ seed_num ][ testing_dir ]["n_out"][2][start:stop], seed_data_dict[ seed_num ][ testing_dir ]["n_out"][3][start:stop] ]
       
       points = np.array([X[0], X[1], X[2]]).T.reshape(-1, 1, 3)
       segs = np.concatenate([points[:-1], points[1:]], axis = 1)
       lc=Line3DCollection(segs,colors=co )
       plt.setp(lc, linewidth=thickness )
       ax.add_collection( lc )
       
       #OLD WAY
       ax.set_xlabel("FT")
       ax.set_ylabel("BS")
       ax.set_zlabel("FS")
       
       #plt.plot( seed_data_dict[ seed_num ][ testing_dir ]["time"], seed_data_dict[ seed_num ][ testing_dir ]["modulation"] )      # Or whatever you want in the subplot
       plt.title(  testing_dict[testing_dir][0]    )
      
       
       
       ax.legend()
       
      #plt.savefig("{0}/{1}/dynamics3d_seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title  ) )
      plt.tight_layout()
      #plt.savefig("demo_seed_{}.png".format( seed_num  ) )
      if alternate_output=="":
       plt.savefig("{0}/TESTS/{1}/{4}/dynamics3d_seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title, comparison_name  ),dpi=1000 )
      else:
       plt.savefig("{0}/TESTING_TRAJECTORIES/{3}/dynamics3d_seed_{1}_{2}.png".format(alternate_output, seed_num, exp_title, comparison_name  ),dpi=1000 )
      
      plt.close('all')
      fig = plt.figure(3)
      fig.set_size_inches(PNG_W, PNG_Y)
      
      
      if SSIO_MODE:
       ssio_data, SSIO_MODE = get_ssio_data_for_plotting( DATA, exp_base, seed_num )
      
      
      ##############FIX THESE
      data2d= [  [1,"FT"], [2,"BS"] , [3,"FS"] ]
      
      for pair in data2d:
       plt.close('all')
       fig = plt.figure(3)
       fig.set_size_inches(PNG_W, PNG_Y)
       num=pair[0]
       label=pair[1]
       
       first=True
       for testing_dir in sorted(testing_dict.keys()):
        rr=int(testing_dict[testing_dir][1])
        cc=int(testing_dict[testing_dir][2])
        n=( rr*max_col+ cc+1 )
        
        #ax = fig.add_subplot( max_row, max_col, n )
        if first:
         ax = fig.add_subplot( max_row, max_col, n )
         firstAx=ax
        else:
         ax = fig.add_subplot( max_row, max_col, n, sharey=firstAx )

#####################       COLOR SETUP
        #lowest mapped to blue, zero to black, highest mapped to red
        colors = [(0, 0, 1, 0.1), (0, 0, 0, 0.1), (1, 0, 0, 0.1)]  # R -> G -> B
        cdict1 = {'red':   ((0.0, 0.0, 0.0),
                   (0.5, 0.0, 0.1),
                   (1.0, 1.0, 1.0)),

         'green': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),
         'blue':  ((0.0, 0.0, 1.0),
                   (0.5, 0.1, 0.0),
                   (1.0, 0.0, 0.0))
        }
        cmap_name = 'my_list'
        # Create the colormap
        cm = LinearSegmentedColormap.from_list( cmap_name, colors  )
        co=[]
        transparency=0.5
        thickness=2
        start=0
        stop=-1
        seed_data_dict[ seed_num ][ testing_dir ]["modulation"]
        for m in seed_data_dict[ seed_num ][ testing_dir ]["modulation"][start:stop]:
         c_to_app = customize_trajectory( label, m)
         co.append( c_to_app )
#         if m < 0:
#          co.append(  (0,0, customize_mod_color(abs(m)), transparency)   )
#         elif m > 0:
#          co.append(  (customize_mod_color( m),0,0, transparency)   )
#         else:
#          co.append(  (0,0,0, transparency)  )
#####################      
        
        #X_LIM=5
        
        X = [ seed_data_dict[ seed_num ][ testing_dir ]["n_input"][num][start:stop], seed_data_dict[ seed_num ][ testing_dir ]["n_out"][num][start:stop] ]
        points = np.array([X[0], X[1] ]).T.reshape(-1, 1, 2)
        segs = np.concatenate([points[:-1], points[1:]], axis = 1)
        
        #if 
        
        lc = LineCollection(segs, colors=co)  #cmap=cmap, norm=norm)
        
        plt.setp(lc, linewidth=thickness )
        ax.add_collection( lc )
        if first:
         ax.set_ylabel( label+ " output",fontsize=fs  )
         first=False
        else:
          plt.setp(ax.get_yticklabels(), visible=False)
        ax.set_xlabel( label+ " input", fontsize=fs  )
        
        if SSIO_MODE:
          ss_i=pair[0]
          for mod in ssio_data[i].keys():
           #ALIFE2018HACK
           if ALIFE2018_ONLY_ACTUAL_SSIO:
            if "M="+str(1+mod) != testing_dict[testing_dir][0]:
             continue
           R=min( 1, customize_ssio_color(max(mod*2,0)) )
           G=0
           B=min(1, customize_ssio_color(max(-mod*2,0)) )
           ssio_color=(R,G,B)
           ax.plot( ssio_data[ss_i][mod]["x"] , ssio_data[ss_i][mod]["y"], alpha=0.5, color=ssio_color, linewidth=ssio_thickness )
           for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(tickfs)
           for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(tickfs)

        
 
        if XLIM_MODE:
         ax.set_xlim(X_LIM_A, X_LIM_B )
        plt.title(  testing_dict[testing_dir][0],fontsize=fs  )
        
       plt.tight_layout()
       if alternate_output=="":
        plt.savefig("{0}/TESTS/{1}/{4}/dynamics2d_{5}_seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title, comparison_name, "n"+label  ),dpi=1000 )
       else:
        plt.savefig("{0}/TESTING_TRAJECTORIES/{3}/dynamics2d_{4}_seed_{1}_{2}.png".format(alternate_output, seed_num, exp_title, comparison_name, "n"+label  ),dpi=1000 )
      
      
      plt.close('all')
      
      fig, ( ( ax1B) ) = plt.subplots(nrows=1, ncols=1 )
      
      for testing_dir in testing_dict.keys(): 
       
       transparency  =0.5
       mod_color =(0,0,0)
       m = seed_data_dict[ seed_num ][ testing_dir ]["modulation"][0]
       
       if m < 0:
        mod_color = (0,0,abs(m), transparency )
       elif m > 0:
        mod_color = (m,0,0, transparency)  
       else:
        mod_color = (0,0,0, transparency)  
       
       
       angle=seed_data_dict[ seed_num ][ testing_dir ]["angle"]
       angle_omega=seed_data_dict[ seed_num ][ testing_dir ]["omega"]
       distance=seed_data_dict[ seed_num ][ testing_dir ]["distance"]
       time=seed_data_dict[ seed_num ][ testing_dir ]["time"]
       fontsize=fs
       ax1B.plot( angle, angle_omega, color=mod_color )

       
      plt.tight_layout()
      legend = plt.legend(loc='center right', bbox_to_anchor=(1, 0.5) )
      plt.text(0, 0, "Fitness: {}".format(seed_to_fitness_map[seed_num] ), fontsize=fs)
      if alternate_output=="":
       plt.savefig("{0}/TESTS/{1}/{4}/angles_seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title,  comparison_name  ),dpi=1000 )
      else:
       plt.savefig("{0}/TESTING_TRAJECTORIES/{3}/angles_seed_{1}_{2}.png".format(alternate_output, seed_num, exp_title,  comparison_name  ),dpi=1000 )

def plot_fitness_landscape( mutation_file_path, alternate_output="",SEED="" ) :
 
 
 BEST_PERF=0.628

 #glob the files with "none" in their filename
 
 #record all the data into one large dict
 
 #parameter_fitness_map={}
# parameter_fitness_map[header]=[x,y,z]
 
 #plot each column of the dict




 with open( mutation_file_path  ) as mutation_fitnesss_file:
     mutation_fitness_reader = csv.DictReader( mutation_fitnesss_file )
     X=[]
     Y=[]
     Z=[]
     colors =[]
     
     for row in mutation_fitness_reader:
      X.append(  float( row['param1'] ) )
      Y.append(  float( row['param2'] ) )
      Z.append(  float( row['fitness'] ) )
      
      
      
      norm_fit = float(row['fitness']) / BEST_PERF
      if norm_fit < 0:
       norm_fit=0
      colors.append( [ norm_fit, norm_fit, norm_fit, 0.5] )
 
 #Make final data point (the original parameter value) be RED
 #X.append( X[-1] )
 #Y.append( Y[-1] )
 colors[-1] = [1.0,0,0, 1.0] 
 
 # seed_49_X-timingConst2_Y-timingConst3_mutations.csv
 
 param_text = re.sub(r'.*/','', mutation_file_path )
 
 xlabel= re.sub(r'.*_X-','', param_text )
 xlabel= re.sub(r'_Y.*','', xlabel )

 ylabel= re.sub(r'.*_Y-','', param_text )
 ylabel= re.sub(r'_mutations.csv','', ylabel )
 
 
 zlabel= "fitness"
 title = "fitness of mutations" 
 
 
 len_xaxis,len_yaxis = 5.,5. #fix here your numbers
 xspace, yspace = .85, .85 # change the size of the void border here.
 x_fig,y_fig = len_xaxis / xspace, len_yaxis / yspace
 
 figure =  plt.figure(figsize=(x_fig,y_fig))
 plt.subplots_adjust(left=1-xspace, right = xspace, top=yspace, bottom = 1-yspace)


 plt.scatter( X,Y, s=5,c=colors )
 #what happens if we double
 
 
 plt.xlabel(xlabel)
 plt.ylabel(ylabel)
 title = re.sub(r'.*/','', mutation_file_path )
 plt.title( title )
 
 
 #print("exp dir: {}".format( experiment_directory ))
 plot_path = re.sub( "/mutations/.*seed[^\\/]*.csv", "/", experiment_directory )
 plot_path = re.sub( DATA, "{}/MUTATIONS/".format(PLOTS), plot_path )
 
 if alternate_output!="":
  plot_path="{}/PARAMETER_SPACE/".format(alternate_output)
  
 os.system( "mkdir -p {}".format( plot_path ) )
 
 savefile = re.sub(".*/seed",'seed', mutation_file_path,dpi=1000 )
 savefile = re.sub(r'mutations.csv','mutation_fitness_landscape.png', savefile,dpi=1000 )
 
 #print( "savefile: {}".format(savefile ))
 #quit()
 plt.savefig( "{}/{}".format(plot_path, savefile ),dpi=1000 )
 #plt.savefig( savefile )
 
 plt.close()


def plot_fitness_landscape_single_plot( mutation_directory_path, alternate_output="",SEED="" ) :
 
 
 BEST_PERF=0.628

 #glob the files with "none" in their filename
 #record all the data into one large dict
 # parameter_fitness_map={}
 # parameter_fitness_map[header]=[x,y,z]
 #plot each column of the dict
 
 parameter_fitness_map={}
 
 len_xaxis,len_yaxis = 5.,5. #fix here your numbers
 xspace, yspace = .85, .85 # change the size of the void border here.
 x_fig,y_fig = len_xaxis / xspace, len_yaxis / yspace
 figure =  plt.figure(figsize=(x_fig,y_fig))
 plt.subplots_adjust(left=1-xspace, right = xspace, top=yspace, bottom = 1-yspace)

 y_tick_dict_num=[]
 y_tick_dict_label=[]
 
 parameter_files = glob.glob(  '{}/seed_{}*none*.csv'.format( mutation_directory_path, SEED  ) )
 inc_x=-1
 for parameter_file in sorted(parameter_files):
  inc_x=inc_x+1
  
  
  with open( parameter_file  ) as csvfile:
   param_text = re.sub(r'.*/','', parameter_file )
   param_text= re.sub(r'.*_X-','', param_text )
   param_text= re.sub(r'_Y.*','', param_text )

   y_tick_dict_num.append(inc_x-1)
   y_tick_dict_label.append(param_text)

   parameter_fitness_map[ param_text ] = {}
   
   parameter_fitness_map[ param_text ]['X'] = []   #[1,1,1]
   parameter_fitness_map[ param_text ]['Y'] = []   #[1,2,3]
   parameter_fitness_map[ param_text ]['Z'] = []   #[0,0.5,1.0]
   parameter_fitness_map[ param_text ]['C'] = []

   mutation_fitness_reader = csv.DictReader( csvfile )
   X       = parameter_fitness_map[ param_text ]['X']
   Y       = parameter_fitness_map[ param_text ]['Y']
   Z       = parameter_fitness_map[ param_text ]['Z']
   colors  = parameter_fitness_map[ param_text ]['C']
   
   #print("parameter_file:{}".format( parameter_file ))
   
   for row in mutation_fitness_reader:
    #print("row: "+ str(row.keys() ))
    X.append(   float( row['param1'] ) )
    Y.append(  inc_x+ float( row['param2'] ) )
    Z.append(  float( row['fitness'] ) )
      
    norm_fit = float(row['fitness']) / BEST_PERF
    if norm_fit < 0:
     norm_fit=0
    colors.append( [ norm_fit, norm_fit, norm_fit, 0.5] )

#####end of loop through parameter file
   #errors out of bounds?
   #print ( X )
   #print( colors )
   if len( colors) >0:
    colors[-1] = [1.0,0,0, 1.0] 

   plt.scatter( X,Y, s=5,c=colors )
 
 plt.yticks(y_tick_dict_num, y_tick_dict_label )    # rotation='vertical')

#####end of for loop through ALL parameter files 
 #plt.xlabel(xlabel)
 #plt.ylabel(ylabel)
 #title = re.sub(r'.*/','', mutation_file_path )
 #plt.title( title )
 
 
 #print("exp dir: {}".format( experiment_directory ))
 #plot_path = re.sub( "/mutations/.*seed[^\\/]*.csv", "/", experiment_directory )
 #plot_path = re.sub( DATA, "{}/MUTATIONS/".format(PLOTS), plot_path )
 
 if alternate_output!="":
  plot_path="{}/PARAMETER_SPACE/".format(alternate_output)
  
 os.system( "mkdir -p {}".format( plot_path ) )
 
 savefile = "{}_parameter_sensitivity_analysis.png".format( SEED )
 plt.savefig( "{}/{}".format(plot_path, savefile ),dpi=1000 )
 plt.close()





def config_plot(ax, time, data, ylabel, title,  fs1=fs, simple=False, mod_color=(), linecolor="" ):

     if len(mod_color) <= 0:
      if linecolor != "":
       ax.plot( time, data, label=ylabel, color=linecolor )
      else:
       ax.plot( time, data, label=ylabel )
     else:
      #print( "using color"+ mod_color )
      #quit()
      ax.plot( time, data, label=ylabel, color=mod_color )
     #ax.locator_params(nbins=3)
     #ax.set_xlabel('time', fontsize=fs)
     if not simple:
      ax.set_ylabel( ylabel , fontsize=fs)
      #legend = ax.legend(loc='center right' )
      legend = ax.legend(loc='lower left' )
     #ax.set_title(title, fontsize=fs)

def main():


    #plotting activity:
    #
    quantity=1
    short_start=350
    short_stop=1100
    seed=35
    SSIO_MODE=True
    OUTPUT_DIR=""
    PNG_W=8
    PNG_Y=12

    if INI_MODE:
     print("Using config file to set the parameters for plotting")
     #quit()
     config = config = configparser.ConfigParser()
     config.read( sys.argv[-1]  )
     
     
     COMPARE_MODE= int(sys.argv[-2])
     if  COMPARE_MODE==4:
      MUTATION_FILE=sys.argv[1]
     
     
     #print( config["ALL"]["output_dir"] )
     short_start= int( config["ALL"]["short_start"])
     short_stop=  int( config["ALL"]["short_stop"] )
     seed= int( config["ALL"]["seed_num"])
     SSIO_MODE=   config["ALL"]["SSIO_MODE"] == "True"
     OUTPUT_DIR=config["ALL"]["output_dir"]
     experiment_directory=config["ALL"]["CTRNN_PATH"]
     experiment_directory+="/"
     experiment_directory+=config["ALL"]["experiment_folder"]
     experiment_title = re.sub(r'.*/','', experiment_directory )
     
     PNG_W=float(config["ALL"]["PNG_W"])
     PNG_Y=float(config["ALL"]["PNG_Y"])
     
     if COMPARE_MODE==3:
      directory = experiment_directory
      comparison_name = re.sub(".*/","", sys.argv[2] ) 
      comparison_name = comparison_name.replace(".csv","")
      
      #print("comparison name {}".format(comparison_name))
      
      #directory=config["ALL"]["CSV_COMPARE_DIR"]
      csv_path=sys.argv[2]
      
      testing_dict={}
      with open( csv_path  ) as csvfile:
       reader = csv.DictReader(csvfile)
       for row in reader:
        if not 'column' in row:
         print("Are you sure you specified the correct csv file? It must have a 'column' in the header to work in this mode")
         quit()
        
        dir =  row['directory'] 
        label = row['label']
        r=row['row']
        c=row['column']
        testing_dict[dir]= ( label, r, c )
      
    
    
    #make sure folder exists
    if COMPARE_MODE==1:
     os.system( "mkdir -p {}/{}".format( PLOTS, "COMPARE" ) )
     plot_fitness(comparison_name, experiment_directories )
     
    elif COMPARE_MODE==2:
     plot_fitness(comparison_name, experiment_directories, experiment_styles, True)
     
    elif COMPARE_MODE==3:
     print( "Special Plotting Testing Results Mode:\nWill plot different attributes for seeds in {}\n   according to the specifications in {}".format( directory, csv_path ))
     #print( testing_dict )
     #True makes this run in plot all activity mode
     
     #testing_dict, quantity=10, short_start=0, short_stop=1000, plot_all_recorded_activity_mode=False, SSIO_MODE
     plot_all_recorded_activity_mode=True
     
     plot_activity2(experiment_directory, testing_dict,comparison_name, quantity=quantity, short_start=short_start, short_stop=short_stop, plot_all_recorded_activity_mode=plot_all_recorded_activity_mode, SSIO_MODE=SSIO_MODE, PNG_W=PNG_W, PNG_Y=PNG_Y, seed=seed, alternate_output=OUTPUT_DIR  )
     #plot_activity2( testing_dict, 1, 0, 500, False  )
     
     quit()
     
    elif COMPARE_MODE==4:
     
     #plots all the parameter values and a colored fitness plot for each
     fitness_plot_mode="single_network_sensitivity"
     
     #plots a single parameter for each network in an ensemble
     fitness_plot_mode="network_ensemble_parameter_sensitivity"
     
     if fitness_plot_mode=="single_network_sensitivity":
      plot_fitness_landscape_single_plot(MUTATION_DIR, alternate_output=OUTPUT_DIR )
     
     print( "Generating plot of the fitness landscape..."  )
     plot_fitness_landscape( MUTATION_FILE, alternate_output=OUTPUT_DIR )
     
     
     
     
     
     
     
     
    
    else:

     exp_base = re.sub(r'.*/DATA/','', experiment_directory )
     os.system( "mkdir -p {}/{}".format( PLOTS, exp_base ) )
     print("plot_actvity ") 
     #plot_activity( 100, 1110, 1350, 68 )
     plot_activity(experiment_directory, quantity=quantity, short_start=short_start, short_stop=short_stop, seed=seed, SSIO_MODE=SSIO_MODE,alternate_output=OUTPUT_DIR, LEG_ANGLE_SENSOR=LEG_ANGLE_SENSOR, PNG_W=PNG_W, PNG_Y=PNG_Y )

     #email plots to jasonayoder@gmail.com
     #this should be handled separately from the data generation
     #os.system( "./email_plots.sh {}".format( experiment_directory )  )
     
   


main()

#hardcoded to produce single sensitivity plot for now
#plot_fitness_landscape_single_plot("/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/mutations", alternate_output="/scratch/jasoyode/github_jasoyode/CTRNN_NM/PLOTS/SINGLE_SEED_ANALYSIS/RPG3_MOD_99/PARAMETER_SPACE" )





