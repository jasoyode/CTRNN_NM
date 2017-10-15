import re
import os
import sys
import csv
import glob
import numpy
import operator
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LinearSegmentedColormap

#headless mode
mpl.use('Agg')
import matplotlib.pyplot as plt

#location for DATA from experiments and PLOTS
DATA="../../DATA"
PLOTS="../../PLOTS"

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


if ".csv" in sys.argv[-1]:
 comparison_name = comparison_name.replace(".csv","")
 COMPARE_MODE=2
 experiment_directories={}
 
 with open( sys.argv[-1]  ) as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
   dir =  row['directory'] 
   label = row['label']
   experiment_directories[dir]=  label


def plot_fitness2( ):

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
      assert(  abs( numpy.mean( fit_by_gen[i]) - current_mean )  < 0.000001 )
      

    gen_means = []
    gen_errors = []


    for g in gen: #range(0, len(fit_by_gen) ):
      gen_means.append( numpy.mean( fit_by_gen[g]) )
      gen_errors.append( numpy.std( fit_by_gen[g] ))
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
    plt.savefig("{0}/{1}/individual_runs_{2}.png".format(PLOTS,  exp_base, exp_title ) )



    gen = numpy.asarray( gen )
    gen_means = numpy.asarray( gen_means )
    gen_errors = numpy.asarray( gen_errors )


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
    plt.savefig("{0}/{1}/mean_runs_with_error_{2}.png".format(PLOTS, exp_base, exp_title ) )




    #print( '{}/{}/seed_*.csv'.format( DATA, experiment_directory  ) )

def plot_fitness( comparisonName, directories,  fromCSV=False):
    
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
       assert(  abs( numpy.mean( fit_by_gen[i]) - current_mean )  < 0.000001 )
       

     gen_means = []
     gen_errors = []

     for g in gen: 
       gen_means.append( numpy.mean( fit_by_gen[g]) )
       gen_errors.append( numpy.std( fit_by_gen[g] ))

     gen = numpy.asarray( gen )
     gen_means = numpy.asarray( gen_means )
     gen_errors = numpy.asarray( gen_errors )

     master_data.append(  [gen[:], gen_means[:], gen_errors[:], dir]  )

    for g, gm, ge, dir in master_data:
    
     print( g[0], gm[0], ge[0] )
     print( len(g), len(gm), len(ge) )
     
     
     if fromCSV:
      plt.plot(g, gm , label=directories[dir] )
     else:
      plt.plot(g, gm , label=dir )
     
     #shaded region indicates standard deviation
     plt.fill_between(g, gm-ge, gm+ge, alpha=0.1)  # facecolor='b',
    
    
    plt.xlabel('Generation')
    plt.ylabel('Best Mean Fitness')
    plt.title( 'Comparing Mean Best Fitness')
    plt.grid(True)
    legend = plt.legend(loc='lower right') #, bbox_to_anchor=(1, 0.5) )
    
    plt.savefig("{0}/COMPARE/comparing_{1}.png".format(PLOTS, comparisonName ) )

    

def plot_activity( quantity=4 ):    
    
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
        print("why??")
        quit()
      
      
      seed_to_fitness_map[  int( row['seed'] ) ] =  entry ;
    
    sorted_seeds_and_fit =  sorted(seed_to_fitness_map.items(), key=operator.itemgetter(1,0) )
    
    sorted_seeds_and_fit.reverse()
    sorted_seeds_and_fit = sorted_seeds_and_fit[ 0:quantity ]
    
    print ( sorted_seeds_and_fit )
    top_seeds = [x[0] for x in sorted_seeds_and_fit]
    print ( top_seeds )

    record_files =  glob.glob(  '{}/seed_*.csv'.format( experiment_directory  ) ) 

    #dictionary( "seed" -> (dictionary ( t -> (data ) )
    
    
    count=0
    for record_file in record_files:
    
      seed_num = re.sub('.*seed_', '', record_file )
      seed_num = re.sub('_.*', '', seed_num )
      seed_num= int(  seed_num )
      
      #only generate plots for top X
      if seed_num not in top_seeds:
       continue
      
      print( record_file )
      
      time = []
      modulation = []
      jointX = []
      jointY = []
      footX   = []
      footY  = []
      footState = []
      distance    = []
      n1_out = []
      n2_out = []
      n3_out = []
      
      with open( record_file  ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
          time.append( float( row['time'] ) );
          modulation.append( float( row['modulation'] ) );
          jointX.append( float( row['jointX'] )  / 10 );
          jointY.append( float( row['jointY'] ) );
          footX.append( float( row['footX'] ) / 10 );
          footY.append( float( row['footY'] ) );
          footState.append( float( row['FootState'] ) );
          distance.append( float( row['cx'] ) );
          n1_out.append( float( row['n1_out'] ) );
          n2_out.append( float( row['n2_out'] ) );
          n3_out.append( float( row['n3_out'] ) );
        
        
        deriv_n1 = []
        pre_val=n1_out[0]
        for val in  n1_out:
         deriv_n1.append( val - pre_val )
         pre_val=val
        
        deriv_n2 = []
        pre_val=n2_out[0]
        for val in  n2_out:
         deriv_n2.append( val - pre_val )
         pre_val=val
        
        deriv_n3 = []
        pre_val=n3_out[0]
        for val in  n3_out:
         deriv_n3.append( val - pre_val )
         pre_val=val
        
        
        
        plt.close('all')
        
        fig, ( (ax1A, ax1B), (ax2A, ax2B), (ax3A,ax3B), (ax4A, ax4B), (ax5A, ax5B) ) = plt.subplots(nrows=5, ncols=2, figsize=(8, 11) )
        
        #plt.figure(2)
        
        #plt.gca().set_color_cycle(['red', 'green', 'blue', 'yellow'])
        
        
        plt.xlabel('Time')
    #    plt.ylabel('Distance Travelled')
        
        #VIEWING WINDOW
        start=0
        stop=-1
        
        time = time[start:stop]
        
        
        fontsize=12
        
        

        config_plot(ax1A, time, modulation[start:stop], "Modulation", " Modulation level over time", fontsize)
        
        txt = "Fitness: {}".format(seed_to_fitness_map[seed_num][0] )
        
        
        
        ymin, ymax = ax1A.get_ylim()
        xmin, xmax = ax1A.get_xlim()
        width=xmax-xmin
        height=ymax-ymin
        
        x=xmin+width/10
        y=ymax+height/10
        
        ax1A.text(x, y, txt, fontsize=12, ha="left", va="top")
        
        
        bs_r = "OFF" if (seed_to_fitness_map[seed_num][1] == 0.0) else  str( seed_to_fitness_map[seed_num][1]  )
        ft_r = "OFF" if (seed_to_fitness_map[seed_num][2] == 0.0) else  str( seed_to_fitness_map[seed_num][2]  )
        fs_r = "OFF" if (seed_to_fitness_map[seed_num][3] == 0.0) else  str( seed_to_fitness_map[seed_num][3]  )
        
        
        config_plot(ax2A, time, n1_out[start:stop], "BS (r:"+ bs_r+")", "BackSwing neuron output over time", fontsize)
        config_plot(ax3A, time, n2_out[start:stop], "FT (r:"+ ft_r+")", "FootLift neuron output over time",  fontsize)
        config_plot(ax4A, time, n3_out[start:stop], "FS (r:"+ fs_r+")", "ForwardSwing neuron output over time", fontsize)
        
        config_plot(ax5A, time, deriv_n1[start:stop], r"$\Delta$ BS", " delta BS over time", fontsize)
        config_plot(ax5A, time, deriv_n2[start:stop], r"$\Delta$ FT", " delta FT over time", fontsize)
        config_plot(ax5A, time, deriv_n3[start:stop], r"$\Delta$ FS", " delta FS over time", fontsize)
        

        ax5A.set_ylabel( r'$\Delta$ neuron outputs' , fontsize=fontsize )
        
        
        config_plot(ax1B, time, modulation[start:stop], "Modulation", " Modulation level over time", fontsize)
        ax1B.text(x, y, txt, fontsize=12, ha="left", va="top")
        
        
        config_plot(ax2B, time, footState[start:stop], "FootState", "FootState over time", fontsize)
        config_plot(ax3B, time, jointX[start:stop], "jointX", "jointX over time", fontsize)
        config_plot(ax4B, time, footX[start:stop], "FootX", "footX over time", fontsize)
        config_plot(ax5B, time, footY[start:stop], "FootY", "footY over time",  fontsize)
        #config_plot(ax, time, jointY[start:stop], "jointY", " jointY over time", fontsize)
        
        
        plt.tight_layout()
        
    #    plt.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        
        #legend = plt.legend(loc='upper right', shadow=True)
        legend = plt.legend(loc='center right', bbox_to_anchor=(1, 0.5) )
        
        
        plt.text(0, 0, "Fitness: {}".format(seed_to_fitness_map[seed_num] ), fontsize=12)
        #plt.title("Fitness: {}".format(seed_to_fitness_map[seed_num] ) , fontsize=fontsize)
        
        exp_title = re.sub(r'.*/','', experiment_directory )       
        exp_base = re.sub(r'.*/DATA/','', experiment_directory )    
        
        plt.savefig("{0}/{1}/seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title  ) )
        
        
        
        
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
        for m in modulation[start:stop]:
         if m < 0:
          co.append(  'b'   )
         elif m > 0:
          co.append(  'r'   )
         else:
          co.append(  'g'  )
        
        #norm1 = matplotlib.colors.Normalize(vmin=-0.5, vmax=0.5, clip=True)
        
        
        dyn1.scatter( n1_out[start:stop], n2_out[start:stop], n3_out[start:stop], c=modulation[start:stop], cmap=cm, label='neuron activation dynamics' )
#        ax.scatter( n1_out[start:stop], n2_out[start:stop], n3_out[start:stop], c=co, label='neuron activation dynamics')
        
        dyn1.set_xlabel("BS")
        dyn1.set_ylabel("FT")
        dyn1.set_zlabel("FS")
        
        
        
        dyn1.legend()
        
        plt.savefig("{0}/{1}/dynamics3d_seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title  ) )
        
        fig, ( (dyn2), (dyn3), (dyn4) ) = plt.subplots(nrows=3, ncols=1, figsize=(8, 11) )
        
        
        dyn2.scatter( n1_out[start:stop], n2_out[start:stop], c=modulation[start:stop], cmap=cm, label='neuron activation dynamics' )
        dyn2.set_xlabel("BS")
        dyn2.set_ylabel("FT")
        
        dyn3.scatter( n1_out[start:stop], n3_out[start:stop], c=modulation[start:stop], cmap=cm, label='neuron activation dynamics' )
        dyn3.set_xlabel("BS")
        dyn3.set_ylabel("FS")
        
        dyn4.scatter( n2_out[start:stop], n3_out[start:stop], c=modulation[start:stop], cmap=cm, label='neuron activation dynamics' )
        dyn4.set_xlabel("FT")
        dyn4.set_ylabel("FS")
        
        plt.tight_layout()
        
        plt.savefig("{0}/{1}/dynamics2d_seed_{2}_{3}.png".format(PLOTS, exp_base, seed_num, exp_title  ) )
        
         
        if count >= 10:
         return
        
        


def config_plot(ax, time, data, ylabel, title,  fontsize=12):
     ax.plot( time, data, label=ylabel )
     #ax.locator_params(nbins=3)
     #ax.set_xlabel('time', fontsize=fontsize)
     ax.set_ylabel( ylabel , fontsize=fontsize)
     legend = ax.legend(loc='center right' )
     #ax.set_title(title, fontsize=fontsize)

def main():

    
    #make sure folder exists
    if COMPARE_MODE==1:
     os.system( "mkdir -p {}/{}".format( PLOTS, "COMPARE" ) )
     plot_fitness(comparison_name, experiment_directories)
     
    elif COMPARE_MODE==2: 
     plot_fitness(comparison_name, experiment_directories, True)
     
    else:

     exp_base = re.sub(r'.*/DATA/','', experiment_directory )
     os.system( "mkdir -p {}/{}".format( PLOTS, exp_base ) )

     plot_fitness2()
     plot_activity( 4 )

     #email plots to jasonayoder@gmail.com
     #this should be handled separately from the data generation
     #os.system( "./email_plots.sh {}".format( experiment_directory )  )


main()







