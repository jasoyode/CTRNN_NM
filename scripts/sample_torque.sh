#!/bin/bash
#PBS -l nodes=1:ppn=16
#PBS -l walltime=1:00:00
#PBS -N ctrnn
#PBS -q cpu
#PBS -l gres=ccm
#PBS -V
#PBS -M jasoyode@indiana.edu
#PBS -abe

module load ccm
module unload python
module load python/3.3.2 

ccmrun ./run_from_queue.sh temp_job_queue_MINI.txt  >>  log.txt 