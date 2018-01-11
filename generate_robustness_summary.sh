#!/bin/bash

declare -a JOBS
#DIR="PLAY_DATA/SMALL_SAMPLE_STANDARD/TESTS/"

JOBS[1]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/"
#JOBS[2]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/"
#JOBS[3]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/"

#JOBS[4]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-4_sim-100run-500gen_signal-SINE-1p_M-standard/"
#JOBS[5]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-standard/"
#JOBS[6]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-4_sim-100run-500gen_signal-SINE-1p_M-standard/"

#JOBS[7]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-5_sim-100run-500gen_signal-SINE-1p_M-standard/"
#JOBS[8]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-standard/"
#JOBS[9]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-5_sim-100run-500gen_signal-SINE-1p_M-standard/"


#JOBS[10]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON"
#JOBS[11]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON"
#JOBS[12]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON"


#JOBS[13]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-4_sim-100run-500gen_signal-SINE-1p_M-mod1-ON"
#JOBS[14]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-4_sim-100run-500gen_signal-SINE-1p_M-mod1-ON"
#JOBS[15]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-4_sim-100run-500gen_signal-SINE-1p_M-mod1-ON"


#JOBS[16]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-5_sim-100run-500gen_signal-SINE-1p_M-mod1-ON"
#JOBS[17]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-MPG_size-5_sim-100run-500gen_signal-SINE-1p_M-mod1-ON"
#JOBS[18]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-5_sim-100run-500gen_signal-SINE-1p_M-mod1-ON"


for JOB in ${JOBS[@]}; do

  echo "$JOB"
  DIR="$JOB/TESTS/"

  FILTERS=( AMP_ CONST_POS_ CONST_NEG_- )

  for FILTER in ${FILTERS[@]}; do

    echo $FILTER

    #OUTPUT="PLAY_DATA/SMALL_SAMPLE_STANDARD/RESULTS_${FILTER}.csv"
    OUTPUT="$JOB/RESULTS_${FILTER}.csv"

    echo "seed,fitness,noise," > $OUTPUT


    for file in $( ls $DIR | grep "$FILTER" ); do
      echo $file
      
      NOISE=$( echo $file | sed "s/.*$FILTER//" )
      
      for line in $( cat $DIR/$file/seeds_tested_fitness.csv | grep -v "seed" ); do
        echo "${line}${NOISE}" >> $OUTPUT
      done

    done
  done
done
