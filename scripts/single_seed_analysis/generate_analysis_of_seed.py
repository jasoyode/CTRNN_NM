import sys
import csv
import os
import math
import numpy as np
import configparser

PI=3.141592653
ROUND=3

BASE_DIR="/scratch/jasoyode/github_jasoyode/CTRNN_NM"

DEBUG_MODE=True
PRINT_MODE=False

if len(sys.argv) <= 1:
  config_file="{}/{}/config.ini".format(BASE_DIR, "scripts/single_seed_analysis" )
else:
  config_file="{}/{}/{}".format(BASE_DIR, "scripts/single_seed_analysis", sys.argv[1] )



config = configparser.ConfigParser() 


def main( config_file ):

  config.read(config_file )    
  
  if DEBUG_MODE:
    show_config_loaded()
  
  
  #0. create folder
  #os.system( "mkdir -p {}".format(config["ALL"]["output_dir"]) )
  
  #1. generate dynamic module analysis of normal network functionality
  generate_dynamic_module_analysis()
  #2.generate network graphs of normal network
  generate_network_graph()
  #3. generate SSIO curves and SSIO.csvs for later plots
  generate_SSIO_curves()
  #4. generate normal activity plots (add SSIO with curves)
  generate_normal_activity_plots()
  #5. generate testing data
  generate_test_data()
  #6. generate testing data plots
  generate_testing_plots()
  #7. generate mutation data
  #generate_mutation_data()
  #8. generate mutation parameter space plots  may want to specify the specific genome positions to mutate?
  #generate_mutation_plots()





def generate_dynamic_module_analysis():
  if DEBUG_MODE:
    print_header( "generate_dynamic_module_analysis()")
  
  command = "cd {0}/scripts/dynamic_modules/ && python dynamic_module_transition_summary.py {1} {2}".format(BASE_DIR,  config["ALL"]["seed_activity_csv"], config["ALL"]["dynamic_modules_csv"]   ) 
  if PRINT_MODE:
    print( command )
  else:
    os.system( command )
  
  

def generate_network_graph():
  if DEBUG_MODE:
    print_header( "generate_network_graph()")
  
  command= "cd {0}/scripts/network_graphs/ && python generate_network_plot.py {1} ".format(BASE_DIR, config_file  ) 
  if PRINT_MODE:
    print( command )
  else:
    os.system( command )
  

def generate_SSIO_curves():
  if DEBUG_MODE:
    print_header( "generate_SSIO_curves()")
  
  command=  "cd {0}/scripts/SSIO_plots/ && python generate_SSIO_plot.py {1} ".format(BASE_DIR, config_file  ) 
  if PRINT_MODE:
    print( command )
  else:
    os.system( command )

def generate_normal_activity_plots():
  if DEBUG_MODE:
    print_header( "generate_normal_activity_plots")
  
  command =  "cd {0}/scripts/plotting/ && python csvreader.py 5 {1} ".format(BASE_DIR, config_file  ) 
  if PRINT_MODE:
    print( command )
  else:
    os.system( command )
    

def generate_test_data():
  if DEBUG_MODE:
    print_header( "generate_test_data()")
  
  #cd /scratch/jasoyode/github_jasoyode/CTRNN_NM/TESTING/
  #python generate_TEST_INIs.py "../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/" 59 67
  
  command = "cd {0}/TESTING/ && python generate_TEST_INIs.py {0}/{1} {2}  ".format(BASE_DIR, config["ALL"]["experiment_folder"], config["ALL"]["seed_num"]  )
  
  command2 ="cd {} && ./test_genome.sh TESTING/TESTING_INI_FOLDERS/{}/SEED_{}/  ".format(BASE_DIR, config["ALL"]["job_ini"], config["ALL"]["seed_num"] )
  command2 += config["ALL"]["experiment_folder"]
  
  if PRINT_MODE:
    print( command )
    print( command2 )
  else:
    os.system( command )
    os.system( command2 )
  
  
  
def generate_testing_plots():
  if DEBUG_MODE:
    print_header( "generate_testing_plots")
  
  command =  "cd {0}/scripts/plotting/ && python generate_testing_plots.py {1} ".format(BASE_DIR, config_file  ) 
  
  
  if PRINT_MODE:
    print( command )
  else:
    os.system( command )    
    
def generate_mutation_data():
  if DEBUG_MODE:
    print_header( "generate_mutation_data")
  
  command =  "cd {0}/ && python generate_ALL_mutation_data.py {1} ".format(BASE_DIR, config_file  ) 
  command2 = "cd /u/jasoyode/FARM/gasneat_experiment_farm/job_q_server && python client_add_jobs.py /scratch/jasoyode/github_jasoyode/CTRNN_NM/mutation_job_queue.txt"
  
  if PRINT_MODE:
    print( command )
    print( command2 )
  else:
    os.system( command )        
    os.system( command2 )
    
    
def generate_mutation_plots():
  if DEBUG_MODE:
    print_header( "generate_mutation_plots")
  
  command =  "cd {0}/scripts/plotting/ && ./generate_all_mutation_plots.sh {0}/{1}/mutations/ {2}  {3} ".format(BASE_DIR, config["ALL"]["experiment_folder"],  config["ALL"]["seed_num"] ,  config_file  ) 
  
  
  if PRINT_MODE:
    print( command )
  else:
    os.system( command )    



def print_header(message):
  print("###############################################")
  print("#   {}".format(message) )
  print("###############################################")
  


def show_config_loaded():
  print_header("Values Loaded From Config")
  for header in config:
    print( header )
    for item in config[header]:
      print( "  {} = {}".format(item, config[header][item]   ) )
      
  print("-----------------------------------------------")

main( config_file )