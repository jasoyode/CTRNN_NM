#!/bin/bash

if [ "$1" == ""  ]; then
  echo "Please specify a COMPLETED experiment DATA directory!"
  exit
fi


if [[ $HOSTNAME == *"karst"* ]]; then
    echo "on Karst"

    EXP_DIR="$1"
    SUB_DATA=$( echo "$EXP_DIR" | sed "s/.*DATA///" )
    
    echo "EXP_DIR = $EXP_DIR"
    echo "SUBDATA = $SUBDATA"
    exit
    
    rsync -av --progress $EXP_DIR jasoyode@silo.cs.indiana.edu:/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/$SUB_DATA

    ssh jasoyode@silo.cs.indiana.edu "cd /scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/post_processing/ && ./post_process.sh ../../DATA/$SUB_DATA" 
    echo "PLEASE RUN the following command on silo: "
    echo "./tar_and_store.sh ../../DATA/$SUB_DATA ../../PLOTS/$SUB_DATA" 
    
else
    echo "not on Karst!"
    ./post_process.sh $1
fi

