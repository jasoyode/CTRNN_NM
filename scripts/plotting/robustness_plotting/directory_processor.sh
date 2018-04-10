#!/bin/bash


if [ "" == "$1" ]; then
  echo "Usage:  $0  [EXPERIMENT_DIRECTORY]"
  echo "Example $0  ../../../DATA/DEMO3_CPG_RPG_3/"
  exit
fi

EXP_DIR="$1"

for DIR in $( ls $EXP_DIR ); do

  #echo "Entering $EXP_DIR/$DIR"
  for RESULT in $( ls $EXP_DIR/$DIR | grep "RESULT" | grep -v "ROBUSTNESS" ); do
    #echo "Result File Found: $RESULT"
    #NEEDS TO BE FIXED!
    COMMAND=$( echo "python robustness_process_and_plot_ind.py $EXP_DIR/${DIR}/${RESULT}"  | sed "s/\/\//\//" )
    #python robustness_plotter.py $EXP_DIR/$DIR/$RESULT
    eval $COMMAND 
  done

done

#python robustness_plotter.py ../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/RESULTS_AMP_.csv