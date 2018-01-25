#!/bin/bash

if [ "" == "$1" ]; then
  echo "Usage:    $0  [EXPERIMENT_DIR]  "
  echo "Example   $0  ../DATA/CPG_RPG_MPG_345/ "
  exit
fi

ROOT_DIR="$1"

for dir in $( ls $ROOT_DIR   ); do

  python generate_TEST_INIs.py $ROOT_DIR/$dir
  
done