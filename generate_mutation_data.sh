#!/bin/bash

INI="$1"
TITLE="$2"

DIR="DATA/mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/"

if [ "$TITLE" == "" ]; then
  echo "Usage: $0 ***.ini title"
  exit
fi


#1=bias1, bias2
for i in $( seq 1 6); do
  ./runExp $INI $DIR $TITLE $i $i 19 19  &
done

#for i in $( seq 11 6); do
#  ./runExp $INI $DIR $TITLE $i $i 19 19  &
#done


#1=bias1, bias2
./runExp $INI $DIR $TITLE 1 1 2 2 &
#bias2, bias3
./runExp $INI $DIR $TITLE 2 2 3 3 &
#tim1, tim2
./runExp $INI $DIR $TITLE 4 4 5 5 &
#tim2, tim3
./runExp $INI $DIR $TITLE 5 5 6 6 &
#1->2, 3->2
./runExp $INI $DIR $TITLE 11 11 17 17 &
#1->3, 2->3
./runExp $INI $DIR $TITLE 12 12 15 15 &
#tim1, tim3
./runExp $INI $DIR $TITLE 4 4 6 6 &
#bias1, bias3
./runExp $INI $DIR $TITLE 1 1 3 3 &

#1->1 2->1
./runExp $INI $DIR $TITLE 10 10 13 13 &
#1->1 3->1
./runExp $INI $DIR $TITLE 10 10 16 16 &

#2->1, 3->1
./runExp $INI $DIR $TITLE 13 13 16 16 &

#2->2 1->2
./runExp $INI $DIR $TITLE 14 14 11 11 &

#2->2 3->2
./runExp $INI $DIR $TITLE 14 14 17 17 &

#3->3 1->3
./runExp $INI $DIR $TITLE 18 18 12 12 &

#3->3 2->3
./runExp $INI $DIR $TITLE 18 18 15 15 &

#./runExp $INI $DIR $TITLE 1 1 3 3 &
#
#./runExp $INI $DIR $TITLE 1 1 3 3 &
#
#./runExp $INI $DIR $TITLE 1 1 3 3 &
#
#./runExp $INI $DIR $TITLE 1 1 3 3 &
#
#./runExp $INI $DIR $TITLE 1 1 3 3 &



