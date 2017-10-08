import sys
import csv
import glob
import numpy
import matplotlib as mpl

#headless mode
mpl.use('Agg')
import matplotlib.pyplot as plt


if len(sys.argv) < 2:
  print(  "Usage: "+ sys.argv[0]+ " experiment_directory_name (inside ../DATA/" )
  quit()




experiment_directory=sys.argv[1]

#print( experiment_directory )
#quit()


#  Launch script todo
#    1. save config file to directory
#    2. add test of best evolved walker and record values to file (along with modulation signal!)
#    3. 


#   Plotting todo
#DONE     1. CRAWL PASSED IN DIRECTORY rather than iterate through
#DONE     2. Make plot of all the individual runs in one plot
#DONE     3. Make aggregate plot with shaded regions are error space (1 STD)
#     4. Make comparison plots of all the different runs that are similar
#DEPENDS ON ABOVE     5. Make plot of the agent speed over time, overlayed with neuron activations and modulation signal  


#  Plot speed of agent relative to the modulation signal
#  Plot 

#with open('../DATA/2017-10-06-standard_3neuron/fitness_and_receptors.txt') as csvfile:

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

seed_files =  glob.glob(  '../DATA/{}/seed_*.txt'.format( experiment_directory  ) ) 

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
plt.title( experiment_directory + '\nBest Fitness of Individual Experiment Runs')
plt.grid(True)
plt.savefig("../DATA/{}/individual_runs.png".format( experiment_directory ) )



gen = numpy.asarray( gen )
gen_means = numpy.asarray( gen_means )
gen_errors = numpy.asarray( gen_errors )


plt.figure(1)
plt.plot(gen, gen_means  )

#shaded region indicates standard deviation
plt.fill_between(gen, gen_means-gen_errors, gen_means+gen_errors, facecolor='b', alpha=0.1)


plt.xlabel('Generation')
plt.ylabel('Best Mean Fitness')
plt.title( experiment_directory + '\nMean Best Fitness by Generation with Standard Error')
plt.grid(True)
plt.savefig("../DATA/{}/mean_runs_with_error.png".format( experiment_directory ) )




