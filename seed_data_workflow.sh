#!/bin/bash


SEED=67
CRM="CPG"
SIZE=3
TYPE="mod1-ON"

DIRECTORY="DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON"

echo "First find the seeds you want to get more data for"

echo "cd /scratch/jasoyode/github_jasoyode/pygraphviz"
echo "myenv/bin/python examples/generate_network_plot.py 67 CPG 3 mod1-ON"

echo
echo "ssh silo"
echo "screen -ls"
echo "if not farm running"
echo "gasfarm1"
echo "exit"

echo "[generation mutation data]"
echo "ctrnn"
echo "joe generate_ALL_mutation_data.py"
echo "add in directory and seed"

echo "python generate_ALL_mutation_data.py"
echo "run command suggested:"
echo "cd /u/jasoyode/FARM/gasneat_experiment_farm/job_q_server && python client_add_jobs.py /scratch/jasoyode/github_jasoyode/CTRNN_NM/mutation_job_queue.txt"

echo "ctrnn"
echo "wait until jobs are complete, the data files will be in the DATA under a mutation folder"
echo "cd scripts/plotting"
echo "./generate_all_mutation_plots.sh ../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/mutations/"

echo "TO GENERATE TESTING DATA FOR SEED(S)"
echo "cd /scratch/jasoyode/github_jasoyode/CTRNN_NM/TESTING/"
echo "python generate_TEST_INIs.py ../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/ 59 67"

echo "TEST THE GENOME"
echo "ctrnn"
echo "./test_genome.sh TESTING/TESTING_INI_FOLDERS/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON.ini/SEED_59/ DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/"

echo "TO PLOT THE DATA"
ctrnn
cd scripts/plotting

echo "joe generate_testing_plots.py"
echo "python generate_testing_plots.py"


