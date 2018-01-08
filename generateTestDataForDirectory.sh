#!/bin/bash


ROOT_DIR="DATA/CPG_RPG_MPG_345/"
TEST_DIR="TestINIs/TESTING_FOLDERS/"

#/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard.ini/ 

#JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard

for dir in $( ls $ROOT_DIR); do
  
  echo " ./generate_varying_activity.sh $TEST_DIR/${dir}.ini $ROOT_DIR/$dir"

done


