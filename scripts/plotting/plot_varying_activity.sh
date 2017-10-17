#!/bin/bash

if [ "$1" == "" ]; then
  echo "Must provide a path to a folder inside of DATA!"
  exit
fi

ROOT="$1"
for dir in $( ls ../../DATA/$ROOT | grep -v ".csv" | grep -v ".txt" | grep -v ".ini" ); do
  python csvreader.py ../../DATA/$ROOT/$dir
done