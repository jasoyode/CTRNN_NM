import os
import sys
import subprocess
import re

#use to get back the output from running commands
def sh( command):
  output = subprocess.check_output( command , shell=True).decode("utf-8")
  return output.strip().split("\n")
    
  
#DONT FORGET THE / AT END OF DIRECTORY!
selected_seeds= []
#selected_seeds.append( ("DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/",  59) )

selected_seeds.append( ("DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/",  35) )
#selected_seeds.append( ("DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/", 49) )
#selected_seeds.append( ("DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/",  64) )
#selected_seeds.append( ("DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/", 29) )
#selected_seeds.append( ("DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/",  87) )
#selected_seeds.append( ("DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/", 75) )

               
#CPG-3-mod, 59
#CPG-3-std, 49
#MPG-3-mod, 64
#MPG-3-std, 29
#RPG-3-mod  87
#RPG-3-std  75

#runs  = 100
#startingSeed = 1


for pair in selected_seeds:

 directory = pair[0]
 SEED = pair[1]
 ini_name = sh("ls {} | grep \".ini\" ".format(directory) )[0]
 INI = "{}/{}".format(directory, ini_name)
 
 #copy the ini to the best_seeds folder and then use it as your ini when running mutations
 sh(  "cat {} | sed \"s/runs.*/runs = 1/\"    | sed \"s/startingSeed.*/startingSeed = {}/\" > {}/seed_{}_{} ".format(INI, SEED, "best_seeds", SEED, ini_name  )   )
 
 mutation_INI = "{}/seed_{}_{}".format( "best_seeds", SEED, ini_name )
 
 #DIRECTORY = re.sub(r'.*DATA/','', directory )

 #print( "./generate_mutation_data.sh {} {} {} {}".format( INI, "mutations", SEED, DIRECTORY ) )
 
 print( "./generate_mutation_data.sh {} {} {} ".format( mutation_INI, directory,  "mutations"  ) )
 #os.system( "./generate_mutation_data.sh {} {} {} ".format( mutation_INI, directory,  "mutations"  ) )




#./generate_mutation_data.sh ***.ini title seed directory
#   DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON.ini
#   CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/
#   mutations 1 1 2 2 87

#./runExp DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON.ini CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/ 
#mutations 1 1 2 2 87