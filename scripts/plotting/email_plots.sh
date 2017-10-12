#!/bin/bash


if [ "$1" == "" ]; then
  echo "Please specify an experiment directory!"
  exit
fi

if [[ "$1" == */PLOTS/* ]] ; then
  #echo "yes"
  EXP_NAME="$1"
  echo "trying to send plots of $EXP_NAME in email attachment!"
  echo "Plots attached" |mutt -s "Experiment $EXP_NAME completed plots attached" $( printf -- '-a %q ' $EXP_NAME/*.png ) -- jasonayoder@gmail.com
  
else
  echo "You must include the path to the PLOTS folder (full or relative) in your argument!"
fi



                                
                                  