#!/bin/bash

# Use this to make sure the latest testing data is used for generating robustness plots
#

if [ "" == "$1" ]; then
  echo "Usage:   $0  [EXPERIMENT_DIRECTORY] "
  echo "Example  $0  DATA/CPG_RPG_MPG_345/ " 
  exit
fi

declare -a JOBS

EXP_DIR="$1"

dir_count=0
for DIR in $( ls $EXP_DIR ); do
  let "dir_count++"
  JOBS[$dir_count]="$EXP_DIR/$DIR"

done

#echo "${JOBS[@]}"
#exit

for JOB in ${JOBS[@]}; do
  echo "$JOB"
  DIR="$JOB/TESTS/"
  #FILTERS=(SA_OFF_AMP_ SA_ON_AMP_ CONSTANT_ )    #CONST_POS_  CONST_NEG_-
#  FILTERS=( SA_OFF_AMP_ )
#  FILTERS=(SA_OFF_CONSTANT_ SA_ON_CONSTANT_  )
  FILTERS=( AMP_ )  # CONSTANT_ )
#  ANTI_FILTER=( SA_O )
  ANTI_FILTER=( XXX )
  for FILTER in ${FILTERS[@]}; do
    echo $FILTER
    OUTPUT="$JOB/RESULTS_${FILTER}.csv"
    echo "seed,fitness,noise," > $OUTPUT
    #sort numerically
    for file in $( ls $DIR | grep -v "$ANTI_FILTER" | grep "$FILTER" |sed "s/$FILTER//" | sort -k1.1n  ); do
      
      #echo $file
      
      NOISE=$( echo "${FILTER}${file}" | sed "s/.*$FILTER//" )
      for line in $( cat $DIR/${FILTER}${file}/seeds_tested_fitness.csv | grep -v "seed" ); do
        echo "${line}${NOISE}" >> $OUTPUT
      done
    done
  done
done


#OLD
#JOBS[1]="DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/"
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

