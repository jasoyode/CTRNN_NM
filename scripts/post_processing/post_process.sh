#!/bin/bash

if [ "$1" == ""  ]; then
  echo "Please specify a COMPLETED experiment DATA directory!"
  exit
fi


if [[ "$1" == */DATA/* ]] ; then
  DATA_DIR="$1"
  PLOT_DIR=$( echo "$DATA_DIR" | sed "s/DATA/PLOTS/" )
  
  COMPARING_DIRS=""

  for dir in $( ls $DATA_DIR  ); do
	 COMPARING_DIRS="$COMPARING_DIRS $DATA_DIR/$dir"
     
     #generate plots for each individual parameter set
     python3 ../plotting/csvreader.py $DATA_DIR/$dir
     
     #email individual plots
     ../plotting/email_plots.sh $PLOT_DIR/$dir
     
     #tar and store all data and plots
     ./tar_and_store.sh $DATA_DIR/$dir $PLOT_DIR/$dir
     
  done;
  
  
  EXP_NAME=$( echo "$DATA_DIR" | sed "s/.*\///" )
  
  rm $EXP_NAME.csv
  touch $EXP_NAME.csv
  
  echo "directory,label," >> $EXP_NAME.csv
  for dir in $COMPARING_DIRS; do
    label=$( echo "$dir" | sed "s/.*\///" )
    echo "$dir,$label," >> $EXP_NAME.csv
  done
  
  #could split on underscores and remove anything in common with all
  
  python3 ../plotting/csvreader.py $EXP_NAME.csv
  
  echo "Comparison Plots attached" |mutt -s "Exp: $EXP_NAME Comparison  plots attached" $( printf -- '-a %q ' ../../PLOTS/COMPARE/comparing_$EXP_NAME.png ) -- jasonayoder@gmail.com  
  

else
  echo "You must include the path to the DATA folder (full or relative) in your argument!"
fi



