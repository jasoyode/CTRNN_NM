#!/bin/bash

if [ "$1" == "" ] ; then
  echo "Usage $0  [mutations DIRECTORY ] "
  exit
fi

DIR="$1"
SEED="$2"
INI="$3"

#echo "dir: $DIR"
#echo "seed: $SEED"
#echo "ini: $INI"

for file in $( ls $DIR | grep "mutations.csv" | grep "seed_${SEED}_" )
do   
#	echo $file
	
	if [ "$INI" == "" ] ; then
		echo "python csvreader.py $DIR/$file"
		python csvreader.py $DIR/$file
	else
		echo "python csvreader.py $DIR/$file 4 $INI"
		python csvreader.py $DIR/$file 4 $INI
	fi

done;

