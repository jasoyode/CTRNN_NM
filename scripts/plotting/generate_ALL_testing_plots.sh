#!/bin/bash


if [ "$1" == "" ]; then
  echo "Must specify a directory!"
  exit
fi

ROOT_DIR="$1"

FILTER="standard"

for dir in $( ls $ROOT_DIR | grep "$FILTER" ); do
  echo "python generate_testing_plots.py $ROOT_DIR/$dir"
  python generate_testing_plots.py $ROOT_DIR/$dir
done

