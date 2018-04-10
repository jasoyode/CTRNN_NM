#!/bin/bash


for i in `seq 1 100`; do

	#python generate_analysis_of_seed.py RPG3_MOD/config_RPG3_MOD_${i}.ini
	python generate_analysis_of_seed.py RPG3_STD/config_RPG3_STD_${i}.ini

done