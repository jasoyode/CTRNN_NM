#!/bin/bash

PWD=$( pwd )

#need to be in base folder to run ./runExp
#cd ..

if [ "$1" == "" ]; then
  echo "Usage  $0  [JOB_QUEUE_FILE.txt]"
  exit
fi


while read -r job_command
do
  cd $PWD
  cd ..
  echo "Running command: $job_command"
  eval $job_command

done < "$1"

