#!/bin/bash


ROOT_DIR="../DATA/CPG_RPG_MPG_345/"

for dir in $( ls $ROOT_DIR   ); do

  python dynamically_generate_test_inis.py $ROOT_DIR/$dir
  
done