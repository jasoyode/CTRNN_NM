#!/bin/bash

if [ "$1" == "" ]; then
  echo "Usage  $0  [JOB_QUEUE_FILE.txt]"
  exit
fi


while read -r job_command
do

  echo "Running command: $job_command"
  eval $job_command

done < "$1"

