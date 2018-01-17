#!/bin/bash

# This file takes a directory with a genomes.txt file and then runs a series of tests
# based on the implicitly determined directory set by the local variable INIs
# It then generates all data for each different config on each genome

if [ "$2" == "" ]; then
  echo "Usage: ./$0 [PATH_TO_FOLDER_OF_INIS] [PATH_TO_DATA_FOLDER]"
  echo "Must provide a path to a folder that has a genomes.txt file!" 
  exit
fi

INIs="$1"
TEST_DIR="$2"

FILTER=""

for temp in $( ls $INIs |grep "$FILTER" ); do

  #echo $temp
  label=$( echo  $INIs/$temp | sed "s/.*temptest_/TESTS\//" | sed "s/.ini//" )
  
  #runExp  config.ini  genome_dir label_for_created_folder
  ./runExp $INIs/$temp $TEST_DIR/ $label

done

# Example usage
#./runExp temptest.ini 2017-10-11/2017-10-11-SIZE5_P1_exp_exp-long_10_M-mod1_recep-ON_size-5_modsig-lin-1p/ modlevel_FIXED