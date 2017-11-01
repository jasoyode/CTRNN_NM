#!/bin/bash


#1=bias1, bias2
./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 1 1 3 3 &
#bias2, bias3
./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 2 2 3 3 &
#tim1, tim2
./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 4 4 5 5 &
#tim2, tim3
./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 5 5 6 6 &
#1->2, 3->2
./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 11 11 17 17 &
#1->3, 2->3
./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 12 12 15 15 &

#tim1, tim3
./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 4 4 6 6 &


#./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 1 1 3 3 &
#./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 1 1 3 3 &
#./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 1 1 3 3 &
#./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 1 1 3 3 &
#./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 1 1 3 3 &
#./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 1 1 3 3 &
#./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 1 1 3 3 &
#./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 1 1 3 3 &
#./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 1 1 3 3 &
#./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 1 1 3 3 &
#./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 1 1 3 3 &
#./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 1 1 3 3 &
#./runExp best_seed_config.ini mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON/ mutations 1 1 3 3 &

