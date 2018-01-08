import os
import sys
import subprocess


DEFAULT_MOD_TYPE = 1
DEFAULT_PERIOD = 1


PERIODS = [1] #,2,5,10,25,50]
DEFAULT_EXTREMA = (-0.5, 0.5)



CONST_POSITIVE = []
CONST_NEGATIVE = []
AMPLITUDE = []

for i in range(0,51):
  value = round( i*0.01, 3)
  CONST_POSITIVE.append( (value, value) )
  CONST_NEGATIVE.append( (-value, -value) )
  AMPLITUDE.append( (-value, value) )


MODULATION_EXTREMA=[ (-0.5, -0.5), (0.5,0.5), (-0.5, 0.5), (-0.25, 0.25), (-0.1, 0.1), (-0.25, -0.25), (0.25, 0.25)    ]


TESTING_FOLDER="TESTING_FOLDERS/"


if len(sys.argv) < 2:
  print("must specify a directory containing an ini file")
  quit()

#use to get back the output from running commands
def sh( command):
  output = subprocess.check_output( command , shell=True).decode("utf-8")
  return output.strip().split("\n")
    

original_directory = sys.argv[1]
original_ini_file= sh("ls {} | grep \".ini\" ".format( original_directory )  )[0]

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


for pair in search_replace_pairs:
  os.system("cat {3}/{0}/template.ini | sed \"s/{1}/{2}/\" > tmp && cat tmp > {3}/{0}/template.ini".format( original_ini_file, pair[0], pair[1], TESTING_FOLDER ) )


os.system("cat {1}/{0}/template.ini".format(original_ini_file,TESTING_FOLDER) )


folder=TESTING_FOLDER+"{0}/".format(original_ini_file)
tmpl=TESTING_FOLDER+"{0}/template.ini".format(original_ini_file)


mod_type=DEFAULT_MOD_TYPE
period=DEFAULT_PERIOD
 


 
#for extrema in MODULATION_EXTREMA:

for extrema in CONST_POSITIVE:
  os.system( "cat {0} | sed \"s/MIN_MOD/{2}/\" | sed \"s/MAX_MOD/{3}/\" | sed \"s/PERIODS/{4}/\" | sed \"s/MOD_TYPE/{5}/\"   > {1}/temptest_CONST_POS_{2}.ini ".format( tmpl, folder, extrema[0], extrema[1], period, mod_type  ) )  
  
for extrema in CONST_NEGATIVE:
  os.system( "cat {0} | sed \"s/MIN_MOD/{2}/\" | sed \"s/MAX_MOD/{3}/\" | sed \"s/PERIODS/{4}/\" | sed \"s/MOD_TYPE/{5}/\"   > {1}/temptest_CONST_NEG_{3}.ini ".format( tmpl, folder, extrema[0], extrema[1], period, mod_type  ) )  

for extrema in AMPLITUDE:
  os.system( "cat {0} | sed \"s/MIN_MOD/{2}/\" | sed \"s/MAX_MOD/{3}/\" | sed \"s/PERIODS/{4}/\" | sed \"s/MOD_TYPE/{5}/\"   > {1}/temptest_AMP_{3}.ini ".format( tmpl, folder, extrema[0], extrema[1], period, mod_type  ) )  

  

#extrema = DEFAULT_EXTREMA
#for period in PERIODS:
#  os.system( "cat {0} | sed \"s/MIN_MOD/{2}/\" | sed \"s/MAX_MOD/{3}/\" | sed \"s/PERIODS/{4}/\" | sed \"s/MOD_TYPE/{5}/\"   > {1}/temptest_X_{2}to{3}_P-{4}_type-{5}.ini ".format( tmpl, folder, extrema[0], extrema[1], period, mod_type  ) )  
  
