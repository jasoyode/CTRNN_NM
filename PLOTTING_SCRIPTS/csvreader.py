import os
import sys
import csv
import glob
import numpy
import matplotlib as mpl

#headless mode
mpl.use('Agg')
import matplotlib.pyplot as plt

#location for DATA from experiments and PLOTS
DATA="../DATA"
PLOTS="../PLOTS"


if len(sys.argv) < 2:
  print(  "Usage: "+ sys.argv[0]+ " experiment_directory_name (inside {}".format( DATA ) )
  quit()

experiment_directory=sys.argv[1]



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

seed_files =  glob.glob(  '{}/{}/seed_*.txt'.format( DATA, experiment_directory  ) ) 

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


#make sure folder exists
os.system( "mkdir -p {}/{}".format( PLOTS, experiment_directory ) )


plt.plot(gen, fit)
plt.xlabel('Generation')
plt.ylabel('Best Fitness')
plt.title( experiment_directory + '\nBest Fitness of Individual Experiment Runs')
plt.grid(True)
plt.savefig("{0}/{1}/individual_runs_{1}.png".format(PLOTS,  experiment_directory ) )



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
plt.savefig("{0}/{1}/mean_runs_with_error_{1}.png".format(PLOTS, experiment_directory ) )




