#!/bin/bash

FILTER="2017-10-10-BEST_exp_size-3_M-std_recep-POS-OFF-NEG_exp-long_10_modsig-lin-1p";

for dir in $( ls ../DATA/ | grep "$FILTER" ); do
 python csvreader.py $dir
done;