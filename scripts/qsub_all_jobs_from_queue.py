import sys
import os

if len(sys.argv) < 2:
  print( "Usage: {}  [jobqueue.txt] ".format( sys.argv[0])  )
  print( "You need to specify a job_queue file, check in resources/JOB_QUEUE_FILES/" )
  quit()
  
job_queue=sys.argv[1]

expected_time="1:00:00"

jobs = []
with open( job_queue, 'r') as jobs_file:
  jobs = jobs_file.readlines()


print( "Scheduling {} jobs for {} (hh:mm:ss) ".format( len(jobs), expected_time )  )

confirm = input("Are you sure you wish to continue? (y/n)")


if confirm != "y":
  print( "Ok, here are the jobs:" )
  quit()

for job in jobs:
  print( job )
  

confirm = input("Are you sure you wish to continue? (y/n)")

if confirm != "y":
  print( "Running\n-------------------------------------------------------" )

#make location to store scripts to be run
os.system( "mkdir -p JOB_SCRIPTS/{}".format( job_queue )

count=0
for job in jobs:
  count++
  if len(job) == 0:
    #do nothing
    print("skipping blank line")
  else:

    os.system("echo \"qsub -m abe -M jasoyode@indiana.edu -N ctrnn_nm -l nodes=1:ppn=16,walltime={0} {1}\" >> JOB_SCRIPTS/{}/job_{}.script   ".format( expected_time, job, job_queue, count ) )

    
    
    