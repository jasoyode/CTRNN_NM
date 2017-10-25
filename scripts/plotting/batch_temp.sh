#!/bin/bash

#DIR="../../DATA/GENS-2000/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON"
DIR="../../DATA/JASON/JOB_size-3_sim-long10run_signal-SINE-1p_M-standard"

#python csvreader.py $DIR const_mod.csv
#python csvreader $DIR const_mod_NEG.csv
#python csvreader.py $DIR const_mod_POS.csv
#python csvreader.py $DIR periods_1-5.csv
#python csvreader.py $DIR periods.csv
#python csvreader.py $DIR const_mod_extremes.csv



#python csvreader.py $DIR test_standard_plus_minus.csv
python csvreader.py $DIR test_standard_pos.csv
#python csvreader.py $DIR test_standard_pos_neg.csv
#python csvreader.py $DIR test_standard_neg.csv
