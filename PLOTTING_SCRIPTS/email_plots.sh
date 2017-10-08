#!/bin/bash


PLOTS="../PLOTS/"

if [ "$1" == "" ]; then
  echo "Please specify an experiment directory!"
  exit
fi

EXP_NAME="$1"


echo "trying to send plots of $EXP_NAME in email attachment!"
echo "Plots attached" |mutt -s "Experiment $EXP_NAME completed plots attached" $( printf -- '-a %q ' $PLOTS/$EXP_NAME/*.png ) -- jasonayoder@gmail.com
                                
                                  