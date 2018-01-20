#!/bin/bash

if [ "$1" == "" ] ; then
  echo "Usage $0  [mutations DIRECTORY ] "
  exit
fi

DIR="$1"

for file in $( ls $DIR | grep mutations ); 
do   
	echo "python csvreader.py $DIR/$file "
	python csvreader.py $DIR/$file
done;