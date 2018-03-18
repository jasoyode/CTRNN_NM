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



genomes = {}
seeds ={}



folders={}
folders["CPG3_MOD"] = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/" 

#"fitness_and_receptors.csv"   seed,fitness,r1,r2,r3,
#"phenotypes.txt"  all genome
#"ROBUSTNESS_RESULTS_AMP_.csv"   seed,fitness,fitness_at_90,robustness,


#TODO LATER - WE CAN ENTER SEEDS MANUALLY FOR NOW
#"/scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/dynamic_modules"
#"seeds_CPG_3_EVO_MOD_TEST_NOMOD.csv"



#genomes["CPG3_MOD"] = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/phenotypes.txt" 
#genomes["RPG3_STD"] = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/phenotypes.txt" 
#genomes["RPG3_MOD"] = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/phenotypes.txt"
#genomes["BEER"] = "../../DATA/CITED_DATA/phenotypes.txt"

#seeds["CPG3_MOD_BS_SWITCH"] = (10,27,29,44,45,47,54,75,95)
#seeds["CPG3_STD"] = range(1,101)
#seeds["CPG3_MOD"] = range(1,101)
#seeds["RPG3_STD"] = range(1,101)
#seeds["RPG3_MOD"] = range(1,101)
#seeds["BEER"] = range(2,3)
#seeds = range(1,3)

for label in folders.keys():
  
  OUTPUT_FILE_NAME="{}_ALL_DATA.csv".format(label)
  
  master_data_seed_dict={}
  
  phenotypes_file = "{}/phenotypes.txt".format( folders[ label ] )
  
  with open( phenotypes_file   ) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      if not 'bias1' in row:
        print( folders[label] )
        print("Are you sure you specified the correct csv file? It must have a 'bias1' in the header to work in this mode")
        quit()
        
      seed =  int( row['seed'] )
      #print( seed )
      
      #this always happens its a new seed each time
      if seed in master_data_seed_dict.keys():
        print("seed {} was already in dict, this should not happen.. exiting!".format(seed) )
        quit()
        
      master_data_seed_dict[seed] = {}
      
      for header in row:
        if header.strip() == "":
            continue
        if header in master_data_seed_dict[seed]:
          print("header {} was already in master_data_seed_dict[seed], this should not happen.. exiting!".format(header) )
          quit()
          
        master_data_seed_dict[seed][header] = row[header]

  robustness_file= "{}/ROBUSTNESS_RESULTS_AMP_.csv".format( folders[ label ] )
  
  #print( master_data_seed_dict.keys() )
  
  with open( robustness_file   ) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      if not 'fitness' in row:
        print( folders[label] )
        print("Are you sure you specified the correct csv file? It must have a 'fitness' in the header to work in this mode")
        quit()
        
      seed =  int( row['seed'] )
      if not seed in master_data_seed_dict:
        print("Why was seed {} not found in dictionary, it should have been loaded from phentotypes already".format(seed) )
        quit()
        
      master_data_seed_dict[seed]["fitness"] = row["fitness"]
      master_data_seed_dict[seed]["fitness_at_90"] = row["fitness_at_90"]
      master_data_seed_dict[seed]["robustness"] = row["robustness"]
      
  #print( master_data_seed_dict[1] )
  with open(OUTPUT_FILE_NAME, 'w') as f:
      #f.write('{0},{1}\n'.format(key, value)) for key, value in my_dict.items()]
      
      for header in sorted(master_data_seed_dict[1].keys() ):
        f.write('{},'.format( header ) )
      f.write('\n')
      
      for seed in sorted(master_data_seed_dict.keys() ):
        for header in sorted(master_data_seed_dict[seed].keys() ):
          f.write('{},'.format(master_data_seed_dict[seed][header]) )
        f.write('\n')

  f.close()

      
