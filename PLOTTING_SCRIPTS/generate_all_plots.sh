#!/bin/bash

FILTER="10-0";

for dir in $( ls ../DATA/ | grep "$FILTER" ); do
 python csvreader.py $dir
done;