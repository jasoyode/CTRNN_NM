import sys
import os
import re

if len(sys.argv) < 2:
  print( "Usage: {}  [jobqueue.txt] ".format( sys.argv[0])  )
  print( "You need to specify a job_queue file, check in resources/JOB_QUEUE_FILES/" )
  quit()
  
job_queue=sys.argv[1]

expected_time="3:45:00"

jobs = []
with open( job_queue, 'r') as jobs_file:
  jobs = jobs_file.readlines()


print( "Scheduling {} jobs for {} (hh:mm:ss) ".format( len(jobs), expected_time )  )

confirm = input("Are you sure you wish to continue? (y/n)")


if confirm != "y":
  print( "Ok, then decide what you want to do..." )
  quit()

for job in jobs:
  print( job )
  

confirm = input("Are you sure you wish to continue? (y/n)")

if confirm != "y":
  print( "Running\n-------------------------------------------------------" )

job_name=re.sub(r".*/","",job_queue)


if os.path.isdir("JOB_SCRIPTS/{}".format( job_name )):
  print( "If you want to resume a job set, please remove quit() below" )
  print( "Scripts have already been generated for that JOB_QUEUE file!\n Exiting...")
  quit()

#make location to store scripts to be run
os.system( "mkdir -p JOB_SCRIPTS/{}".format( job_name ) )

os.system( "mkdir -p COMPLETED_SCRIPTS/{}".format( job_name ) )

count=0
for job in jobs:
  count+=1
  
  #check if already marked as completed!
  job_done = os.path.isfile( "scripts/COMPLETED_SCRIPTS/{0}/job_{1}.script".format( job_name, count) )
  if job_done:
     print("skipping, job already completed!") 
  elif len(job) == 0:
    #do nothing
    print("skipping blank line")
  else:
    #check to see if this is the final job!
    if len(jobs) == count:
      print("not writing final job to file, it will be called by which ever the last running script is!")
    else:
      
      os.system("echo \"#!/bin/bash\n\n{}\" >> JOB_SCRIPTS/{}/job_{}.script".format( job, job_name, count ) )

      cleanup_command="""
touch scripts/COMPLETED_SCRIPTS/{0}/job_{1}.script
#if all jobs are in the completed folder!
script_count=\$( ls scripts/JOB_SCRIPTS/{0}/   | wc -l )
completed_count=\$( ls scripts/COMPLETED_SCRIPTS/{0}/    | wc -l )

if [ \"\$script_count\" == \"\$completed_count\" ]; then
  #run the post processing script!
  {2}
fi
 
""".format(job_name, count, jobs[-1]  )

      os.system("echo \"{2}\" >> JOB_SCRIPTS/{0}/job_{1}.script".format( job_name, count, cleanup_command ) )      
      
      ##file written now it can be made run
      os.system("chmod +x JOB_SCRIPTS/{}/job_{}.script".format(job_name, count) )
      os.system("qsub -m abe -M jasoyode@indiana.edu -N ctrnn_nm -l nodes=1:ppn=16,walltime={} JOB_SCRIPTS/{}/job_{}.script".format(expected_time, job_name, count) )

