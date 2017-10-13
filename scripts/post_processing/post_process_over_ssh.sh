#!/bin/bash

if [ "$1" == ""  ]; then
  echo "Please specify a COMPLETED experiment DATA directory!"
  exit
fi


if [[ $HOSTNAME == *"karst"* ]]; then
    echo "on Karst"
    
    SUB_DATA=$( echo "$1" | sed "s/.*DATA///" )
    echo "\$1 = $1"
    rsync -av --progress $1 jasoyode@silo.cs.indiana.edu:/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/$SUB_DATA
    echo "SUBDATA = $SUBDATA"
    ssh jasoyode@silo.cs.indiana.edu "cd /scratch/jasoyode/github_jasoyode/CTRNN_NM/scripts/post_processing/ && ./post_process.sh ../../DATA/$SUB_DATA" 
    echo "PLEASE RUN the following command on silo: "
    echo "./tar_and_store.sh ../../DATA/$SUB_DATA ../../PLOTS/$SUB_DATA" 
    
else
    echo "not on Karst!"
    ./post_process.sh $1
fi

