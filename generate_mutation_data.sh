#!/bin/bash

INI="$1"
DIR="$2"
TITLE="$3"

#needs to be re-done in some way to allow to use the original file, but to have stuff replaced
#DIR="DATA/mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/"



if [ "$TITLE" == "" ]; then
  echo "Usage: $0 ***.ini directory title"
  exit
fi


#bias2  and  3->2
#./runExp $INI $DIR $TITLE 2 2 17 17 &

# 3->2  wALL
#./runExp $INI $DIR $TITLE 17 17 22 22 &

#single parameter sensitivity
for i in $( seq 1 22); do
  ./runExp $INI $DIR $TITLE $i $i 29 29  &
done

exit


#RPG
./runExp $INI $DIR $TITLE 19 19 20 20  &
./runExp $INI $DIR $TITLE 19 19 21 21  &
./runExp $INI $DIR $TITLE 20 20 21 21  &

#exit

./runExp $INI $DIR $TITLE 1 1 14 14 &
./runExp $INI $DIR $TITLE 1 1 22 22 &

#1=bias1, bias2   timingConstant1
for i in $( seq 3 6); do
#RPG
  ./runExp $INI $DIR $TITLE $i $i 19 19  &
  ./runExp $INI $DIR $TITLE $i $i 20 20  &
  ./runExp $INI $DIR $TITLE $i $i 21 21  &  
  ./runExp $INI $DIR $TITLE $i $i 14 14 &
  ./runExp $INI $DIR $TITLE $i $i 22 22 &
  
done


for i in $( seq 10 21); do
  ./runExp $INI $DIR $TITLE 2  2  $i $i  &
  ./runExp $INI $DIR $TITLE $i $i 22 22  &
done



#1->2
#./runExp $INI $DIR $TITLE 11 11 19 19  &

#1->1   vs  1->2

#./runExp $INI $DIR $TITLE 10 10 11 11  &
#./runExp $INI $DIR $TITLE 10 10 12 12  &

#usefuk for the BS-switch neurons
#   compare inhibitng connection from FT to BS and also the BS self loop
#   these should need to change together
./runExp $INI $DIR $TITLE 11 11 14 14  &


exit

#the rest are not nearly as meaningful
#exit

#for i in $( seq 11 6); do
#  ./runExp $INI $DIR $TITLE $i $i 19 19  &
#done

#bias2  and  3->2
#./runExp $INI $DIR $TITLE 2 2 17 17 &


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

