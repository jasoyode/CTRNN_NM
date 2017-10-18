#!/bin/bash

INIs="TestINIs"

if [ "$1" == "" ]; then
  echo "Must provide a path to a folder inside of DATA/!" 
  exit
fi

TEST_DIR="$1"

FILTER=""

for temp in $( ls $INIs |grep "$FILTER" ); do

  echo $temp
  
  label=$( echo  $INIs/$temp | sed "s/temptest_//" | sed "s/.ini//" )
  
  echo "./runExp $INIs/$temp $TEST_DIR/ $label"

done


#./runExp temptest.ini 2017-10-11/2017-10-11-SIZE5_P1_exp_exp-long_10_M-mod1_recep-ON_size-5_modsig-lin-1p/ modlevel_FIXED