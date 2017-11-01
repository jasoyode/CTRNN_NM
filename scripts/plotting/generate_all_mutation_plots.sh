#!/bin/bash

DIR="$1"

for file in $( ls $DIR | grep mutations ); 
do   
	python csvreader.py $DIR/$file; 

done;