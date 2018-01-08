#!/bin/bash


#DIR="PLAY_DATA/SMALL_SAMPLE_STANDARD/TESTS/"

JOB="DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/"

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