#!/bin/bash

# This script is used to generate the commands needed to generate testing data
# 
#


if [ "" == "$2" ]; then
  echo "Usage    $0 [ROOT_DIR]            [TEST_DIR]"
  echo "Example: $0 DATA/CPG_RPG_MPG_345/ TestINIs/TESTING_FOLDERS/ "
  exit
fi

ROOT_DIR="$1"
TEST_DIR="$2"

TEST_JOB_QUEUE="test_genomes_job_queue.txt"

echo -n "" > $TEST_JOB_QUEUE

for dir in $( ls $ROOT_DIR); do
  
  echo "cd /scratch/jasoyode/github_jasoyode/CTRNN_NM && ./test_genome.sh $TEST_DIR/${dir}.ini $ROOT_DIR/$dir" >> $TEST_JOB_QUEUE

done

cat $TEST_JOB_QUEUE
echo "cd /u/jasoyode/FARM/gasneat_experiment_farm/job_q_server && python client_add_jobs.py /scratch/jasoyode/github_jasoyode/CTRNN_NM/test_genomes_job_queue.txt"
