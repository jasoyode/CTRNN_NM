#!/bin/bash

./gen_all.sh > output.csv
cat output.csv |sed "s/JOB_ctrnn-//" | sed "s/_sim-100run-500gen_signal-SINE-1p//" | sed "s/RESULTS_//" > formatted.csv
cat formatted.csv | sed "s/_size-/,/" | sed "s/_M-/,/" > formatted_best.csv

