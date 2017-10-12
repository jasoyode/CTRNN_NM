#!/bin/bash

FILTER="2017-1";

for dir in $( ls ../DATA/ | grep "$FILTER" ); do
 python csvreader.py $dir
done;