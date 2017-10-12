#!/bin/bash


if [ "$1" == "" ]; then
  echo "Please specify an experiment directory!"
  exit
fi


FILTER="$2"

if [ "$FILTER" == "" ]; then
  echo "No filter specified, all directories will have plots generated"
else
  echo "Filter selected:  $FILTER will only generate plots in $1 that have $2 in their name."
fi
    

if [[ "$1" == */DATA/* ]] ; then
  EXP_DIR="$1"
  
  for dir in $( ls $EXP_DIR | grep "$FILTER" ); do
     python csvreader.py $dir
  done;

else
  echo "You must include the path to the DATA folder (full or relative) in your argument!"
fi
    
