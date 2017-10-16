import sys
import os
import re
import subprocess

##############################################################
#  This code will delete the latest created seed_X.txt file
#  Based upon that number "X" it will also delete
#    seed_X_recorded_activity.csv
#
#  Any lines after "X," in:
#    genomes.txt
#    fitness_and_receptors.txt
#
##############################################################

DEBUG_MODE=False


#use to get back the output from running commands
def sh( command):
  output = subprocess.check_output( command , shell=True).decode("utf-8")
  return output.strip().split("\n")

#Directory of DATA relative to this script
DATA="../DATA"


if len(sys.argv) < 2:
  print(  "Usage: "+ sys.argv[0]+ " experiment_directory_name" )
  quit()
    
EXP_DIR=sys.argv[1]


if DEBUG_MODE:
  print( "Attempting to restart experiment: {}/{}".format(DATA, EXP_DIR  ) )

#identify latest written seed file, delete it, delete references to that seed in other files
get_latest_seed_command = "ls -rt {}/{}/| grep seed| grep -v recorded | tail -1  ".format( DATA, EXP_DIR   )
latest_seed_filename=sh( get_latest_seed_command)[0]


LATEST_SEED_NUM=re.sub("seed_","", latest_seed_filename )
LATEST_SEED_NUM=re.sub(".txt","", LATEST_SEED_NUM )

if DEBUG_MODE:
  print( "#: " + LATEST_SEED_NUM )

if DEBUG_MODE:
  print( "Latest created seed file: "+ latest_seed_filename )
genome_filename_path = "{}/{}/genomes.txt".format( DATA, EXP_DIR   )
fitness_and_receptors_path = "{}/{}/fitness_and_receptors.txt".format( DATA, EXP_DIR   )


os.system( "rm {}/{}/seed_{}_recorded_activity.csv".format( DATA, EXP_DIR, LATEST_SEED_NUM ) )
os.system( "rm {}/{}/{}".format( DATA, EXP_DIR, latest_seed_filename ) )

if DEBUG_MODE:
  print( "Removing {} from {} ".format( latest_seed_filename, genome_filename_path  )  )

with open( genome_filename_path, 'r' ) as txt_file:
  lines = txt_file.readlines()
new_text_contents=""
stopper_match=LATEST_SEED_NUM+","
for line in lines:
  if line.startswith( stopper_match  ):
    if DEBUG_MODE:
      print( "Found [{}] not including this in the file and stopping parsing!".format( stopper_match ) )
    #should not be needed
    break
  else:
    new_text_contents += line

if DEBUG_MODE:
  print("Writing new text content:\n"+new_text_contents )



#write the replacement text which ommits the final seed
with open( genome_filename_path+'_temp', 'w' ) as txt_file:
  txt_file.write( new_text_contents  )
  
os.system( "mv {0}_temp {0} ".format( genome_filename_path ) )

if DEBUG_MODE:
  print( "Removing {} from {} ".format( latest_seed_filename, fitness_and_receptors_path  )  )

with open( fitness_and_receptors_path, 'r' ) as txt_file:
  lines = txt_file.readlines()

new_text_contents=""
stopper_match=LATEST_SEED_NUM+","

for line in lines:
  if line.startswith( stopper_match  ):
    if DEBUG_MODE:
      print( "Found [{}] not including this in the file and stopping parsing!".format( stopper_match ) )
    #should not be needed...
    break
  else:
    new_text_contents += line

if DEBUG_MODE:
  print("Writing new text content:\n"+new_text_contents )



#write the replacement text which ommits the final seed
with open( fitness_and_receptors_path+"_temp", 'w' ) as txt_file:
  txt_file.write( new_text_contents  )

os.system( "mv {0}_temp {0} ".format( fitness_and_receptors_path ) )
 
print( LATEST_SEED_NUM )


