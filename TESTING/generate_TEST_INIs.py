import os
import sys
import subprocess

#DONT FORGET TO SET PERIOD if running special mode
MIXED_TESTING_MODE=False

#To force generating inis to collect data for every seed in a directory
FORCE_GEN_ALL=False

#Force a seed to generate all levels of modulation
FORCE_SEED_ALL_LEVELS=True

def main():
  # This script copies a given ini and uses it as a template to generate testing configs
  if len(sys.argv) < 2:
    print("Usage:  python generate_TEST_INIs.py [directory containing *.ini file] [OPTIONAL SEED NUMBER ...]")
    quit()

  PLOT_SEED_ACTIVITY_MODE = FORCE_GEN_ALL
  
  
  SEEDS=[]
  if len(sys.argv) >= 3:
    PLOT_SEED_ACTIVITY_MODE=True
    SEEDS=sys.argv[2:]
    print( "PLOT_SEED_ACTIVITY_MODE ENABLED, WILL GENERATE ACTIVITY DATA FOR THE FOLLOW SEEDS:" )
    print( SEEDS )


  original_directory = sys.argv[1]
  original_ini_file= sh("ls {} | grep \".ini\" ".format( original_directory )  )[0]


  if PLOT_SEED_ACTIVITY_MODE and not FORCE_GEN_ALL:
    for SEED in SEEDS:
      print( "Creating special folder for seed {}".format(SEED) )
      create_inis( original_ini_file, original_directory, SEED )
  else:
    create_inis( original_ini_file, original_directory )


def create_inis( original_ini_file, original_directory, SEED=-1  ):
  
  PLOT_SEED_ACTIVITY_MODE=( SEED != -1)
  if FORCE_GEN_ALL:
    PLOT_SEED_ACTIVITY_MODE=True
#  print( SEED )
#  quit()
  
  TESTING_FOLDER="TESTING_INI_FOLDERS/"
  DEFAULT_MOD_TYPE = 1
  DEFAULT_PERIOD = 1
  PERIODS = [1] #,2,5,10,25,50]
  DEFAULT_EXTREMA = (-0.5, 0.5)
  CONSTANT = []
  AMPLITUDE = []
  
  
  steps=50
  step_size=0.01
  
  
  if PLOT_SEED_ACTIVITY_MODE and not FORCE_SEED_ALL_LEVELS:
    steps=5
    step_size=0.1
  
  
  if MIXED_TESTING_MODE:
    steps=5
    step_size=0.1
  
  #51 values including noise = 0
  for i in range(0,steps+1):
    value = round( i*step_size, 3)
    AMPLITUDE.append( (-value, value) )

  for i in range(-steps,steps+1):
    value = round( i*step_size, 3)
    CONSTANT.append( (value, value) )

  if PLOT_SEED_ACTIVITY_MODE and not FORCE_GEN_ALL:
    #create folder for inis for testing this network
    os.system("mkdir -p {}/{}/SEED_{}/ ".format(TESTING_FOLDER, original_ini_file, SEED  )   )
    #copy ini to new folder as template to be modified
    os.system("cp {0}/{1}  {2}/{1}/SEED_{3}/template.ini".format(original_directory, original_ini_file, TESTING_FOLDER, SEED   )   )
    
  else:
    #create folder for inis for testing this network
    os.system("mkdir -p {}/{} ".format(TESTING_FOLDER, original_ini_file  )   )
    #copy ini to new folder as template to be modified
    os.system("cp {0}/{1}  {2}/{1}/template.ini".format(original_directory, original_ini_file, TESTING_FOLDER   )   )

  #remove the original values for period and extrema
  search_replace_pairs = []
  search_replace_pairs.append( ("minModulation.*" , "minModulation = MIN_MOD" ))
  search_replace_pairs.append( ("maxModulation.*" , "maxModulation = MAX_MOD" ))
  search_replace_pairs.append( ("externalModulationPeriods.*" , "externalModulationPeriods = PERIODS") )
  search_replace_pairs.append( ("NeuromodulationType.*" , "NeuromodulationType = MOD_TYPE" ))
  search_replace_pairs.append( ("maxReceptor.*" , "maxReceptor = 1" ))
  search_replace_pairs.append( ("minReceptor.*" , "minReceptor = 1" ))
  
  if MIXED_TESTING_MODE:
    #run test with single run mode
    search_replace_pairs.append( ("mixedPatternGen.*" , "mixedPatternGen = true\\nmixedPatternGenSingleRun = true" ))

  #do not make every log file 2MB long unless in PLOT SEED ACTIVTY MODE!
  if PLOT_SEED_ACTIVITY_MODE and not FORCE_GEN_ALL:
    search_replace_pairs.append( ("runs.*" , "runs  = 1" ))
    search_replace_pairs.append( ("startingSeed.*" , "startingSeed = {}".format(SEED) ))
  elif FORCE_GEN_ALL:
    print("leaving ini intact")
  else:
    search_replace_pairs.append( ("\\[exp\\].*" , "[exp]\\nrecordAllActivity = false" ))
    
  #make sure to put INIs in correct directory
  if PLOT_SEED_ACTIVITY_MODE and not FORCE_GEN_ALL:
    for pair in search_replace_pairs:
      os.system("cat {3}/{0}/SEED_{4}/template.ini | sed \"s/{1}/{2}/\" > tmp && cat tmp > {3}/{0}/SEED_{4}/template.ini".format( original_ini_file, pair[0], pair[1], TESTING_FOLDER, SEED ) )
    os.system("cat {1}/{0}/SEED_{2}/template.ini".format(original_ini_file,TESTING_FOLDER, SEED) )
    folder=TESTING_FOLDER+"{0}/SEED_{1}/".format(original_ini_file, SEED)
    tmpl=TESTING_FOLDER+"{0}/SEED_{1}/template.ini".format(original_ini_file, SEED)
  else:
    for pair in search_replace_pairs:
      os.system("cat {3}/{0}/template.ini | sed \"s/{1}/{2}/\" > tmp && cat tmp > {3}/{0}/template.ini".format( original_ini_file, pair[0], pair[1], TESTING_FOLDER ) )
    os.system("cat {1}/{0}/template.ini".format(original_ini_file,TESTING_FOLDER) )
    folder=TESTING_FOLDER+"{0}/".format(original_ini_file)
    tmpl=TESTING_FOLDER+"{0}/template.ini".format(original_ini_file)
  #############

  mod_type=DEFAULT_MOD_TYPE
  period=DEFAULT_PERIOD
   
  for extrema in CONSTANT:
    if MIXED_TESTING_MODE:
      os.system( "cat {0} | sed \"s/MIN_MOD/{2}/\" | sed \"s/MAX_MOD/{3}/\" | sed \"s/PERIODS/{4}/\" | sed \"s/MOD_TYPE/{5}/\"   > {1}/temptest_MIXED_CONSTANT_{2}.ini ".format( tmpl, folder, extrema[0], extrema[1], period, mod_type  ) )  
    else:
      os.system( "cat {0} | sed \"s/MIN_MOD/{2}/\" | sed \"s/MAX_MOD/{3}/\" | sed \"s/PERIODS/{4}/\" | sed \"s/MOD_TYPE/{5}/\"   > {1}/temptest_CONSTANT_{2}.ini ".format( tmpl, folder, extrema[0], extrema[1], period, mod_type  ) )        

  for extrema in AMPLITUDE:
    if MIXED_TESTING_MODE:
      os.system( "cat {0} | sed \"s/MIN_MOD/{2}/\" | sed \"s/MAX_MOD/{3}/\" | sed \"s/PERIODS/{4}/\" | sed \"s/MOD_TYPE/{5}/\"   > {1}/temptest_MIXED_AMP_{3}.ini ".format( tmpl, folder, extrema[0], extrema[1], period, mod_type  ) )  
    else:
      os.system( "cat {0} | sed \"s/MIN_MOD/{2}/\" | sed \"s/MAX_MOD/{3}/\" | sed \"s/PERIODS/{4}/\" | sed \"s/MOD_TYPE/{5}/\"   > {1}/temptest_AMP_{3}.ini ".format( tmpl, folder, extrema[0], extrema[1], period, mod_type  ) )  

#use to get back the output from running commands
def sh( command):
  output = subprocess.check_output( command , shell=True).decode("utf-8")
  return output.strip().split("\n")


#call main
main()
