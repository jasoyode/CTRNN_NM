#!/bin/bash

if [ "$1" == ""  ]; then
  echo "Please specify a COMPLETED experiment DATA directory!"
  exit
fi


if [[ $HOSTNAME == *"karst"* ]]; then
    echo "on Karst"
    echo "$1"
    echo "rsync -av --progress $1 jasoyode@silo.cs.indiana.edu:~/github_jasoyode/CTRNN_NM/DATA/"
    
    echo "ssh jasoyode@silo.cs.indiana.edu 'cd /u/jasoyode/github_jasoyode/CTRNN_NM/scripts/post_processing/ && ./post_process.sh $1' "
else
    echo "not on Karst!"
    ./post_process.sh $1
fi

