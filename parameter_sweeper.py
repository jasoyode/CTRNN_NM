from collections import OrderedDict
import csv
import os
import sys
import copy
import datetime

#import subprocess
#def sh( command):
#  output = subprocess.check_output( command , shell=True).decode("utf-8")
#  return output.strip().split("\n")
#user = sh("echo $USER")[0]


if len(sys.argv) < 4:
  print("You must provide 4 parameters: name, template, parameter_list")
  quit()

exp_name=sys.argv[1]
template=sys.argv[2]
parameter_list_file=sys.argv[3]



exp_dir="/u/jasoyode/github_jasoyode/CTRNN_NM/DATA/{}".format( exp_name )
config_dir="/u/jasoyode/github_jasoyode/CTRNN_NM/CONFIG/{}".format( exp_name )
run_dir="/u/jasoyode/github_jasoyode/CTRNN_NM/"

bigred2=os.path.isdir("/N/dc2/scratch/")

if bigred2:
  exp_dir="/N/dc2/scratch/jasoyode/github/jasoyode/CTRNN_NM/DATA/{}".format( exp_name )
  config_dir="/N/dc2/scratch/jasoyode/github/jasoyode/CTRNN_NM/CONFIG/{}".format( exp_name )
  run_dir="/N/dc2/scratch/jasoyode/github/jasoyode/CTRNN_NM/"


generate_batch_mode=False

if len(sys.argv) > 4:
  print("You specified a 5th parameter and it is: {}".format(sys.argv[4]) )
  generate_batch_mode=True


print( "Job name: {}\nTemplate: {}\nParameter List: {}".format( exp_name, template, parameter_list_file ) )


temporary_job_queue_file="resources/JOB_QUEUES/job_queue_"+exp_name+".txt"

#job_path='{}/JOBS_DIR/job_{}.properties'.format(exp_dir, job_count )


#EDIT HERE
DEBUG=False


def dprint(message ):
  if DEBUG:
    print( message )


def main():

  #create experiment directory
  #os.system("mkdir -p {}".format( config_dir ) )
  
  os.system("mkdir -p {}/NAMED_JOBS".format(config_dir) )
  
  #open the csv file which has our list of parameters to examine
  with open( parameter_list_file, 'r') as csvfile:
    reader = csv.DictReader( csvfile )
    
    #we need a list of all the parameters with single permutation
    #single_permutation_parameter_value_map
    single_ppv_map = {}
    
    #we need a list of all permutation parameters values that must all be included
    all_ppv_map = {}

    #each of the values in the body of the template that need to be replaced
    template_replacements={}    
    
    #simply use as a sanity test to make sure we aren't doing things that we shouldn't
    no_duplicates=[]
    
    #a map of parameter names ->   values -> labels
    parameter_value_to_label_maps = {}
    
    
    parameter_names = []
    ordered_parameter_names = {}
    reversed_ordered_parameter_names = {}
    
    for row in reader:
      #append numbers at front to keep order consistent as in csvfile
      if row["parameter_name"] not in ordered_parameter_names.keys():
        num = str(len(ordered_parameter_names))
        ordered_parameter_names[ row["parameter_name"] ] =   num +"X"+ row["parameter_name"] 
        reversed_ordered_parameter_names[ num +"X"+ row["parameter_name"] ] = row["parameter_name"] 
        
      
      row["parameter_name"] = ordered_parameter_names.get( row["parameter_name"] )
      
      #for now we only want summary to included labeled text parameters
      if row["type"] == "text" and row["value_label"] != "":

        if row["parameter_name"] not in parameter_value_to_label_maps:
          parameter_value_to_label_maps[ row["parameter_name"] ] = {}
        if row["value"]  in parameter_value_to_label_maps[row["parameter_name"] ]:
          raise Exception("Cannot have the same value for two different labels of the same parameter!")
        parameter_value_to_label_maps[row["parameter_name"] ][ row["value"] ] = row["value_label"]
      
      #add the numerical values to the summary as well, thus including everything one might want to know
      if row["type"] == "number":

        if row["parameter_name"] not in parameter_value_to_label_maps:
          parameter_value_to_label_maps[ row["parameter_name"] ] = {}
        if row["value"] in parameter_value_to_label_maps[row["parameter_name"] ]:
          raise Exception("Cannot have the same value for two different labels of the same parameter!")
          
        start= float( row["value"].split(";")[0] )
        inc=   float( row["value"].split(";")[1] )
        stop=  float(row["value"].split(";")[2] )
            
        for num in range_f(start, inc, stop ):
          
          parameter_value_to_label_maps[row["parameter_name"] ][ "{}={}".format(row["value_label"], num) ] = num 
      
      #if yes, then we add it to all_ppv_map because single_ppv_map will selectively replace it
      if row["default"] == "yes":
        
        if row["parameter_name"] not in all_ppv_map:
          
          #handle parameters based upon what type they are
          if row["type"] == "template_parameter":
            if row["parameter_name"] in no_duplicates:
              raise Exception("We cannot allow more than one definition of a template parameter in a single file currently.")
            else:
              no_duplicates.append( row["parameter_name"] )
            search=row["value_label"]
            replace=row["value"]
            template_replacements[search]=replace
          elif row["type"] == "text":
            #make sure the text variable is defined
            if row["parameter_name"] not in all_ppv_map:
              all_ppv_map[ row["parameter_name"] ]=[]
            all_ppv_map[ row["parameter_name"] ].append( row["value"] )
          elif row["type"] == "number":
            if row["parameter_name"] in no_duplicates:
              raise Exception("We cannot allow more than one definition of a number parameter, that is the purpose of using increment.")
            else:
              no_duplicates.append( row["parameter_name"] )
            #make sure the number variable is defined
            if row["parameter_name"] not in all_ppv_map:
              all_ppv_map[ row["parameter_name"] ]=[]
            default=  float( row["value"].split(";")[3] )
            
            if default.is_integer():
              default=int(default)
            
            all_ppv_map[ row["parameter_name"] ].append( "{}={}".format(row["value_label"] , default ))
            
            start= float( row["value"].split(";")[0] )
            inc=   float( row["value"].split(";")[1] )
            stop=  float(row["value"].split(";")[2] )
            
            for num in range_f(start, inc, stop ):
              if num != default:
                if row["parameter_name"] not in single_ppv_map:
                  single_ppv_map[row["parameter_name"]] = []
                
                single_ppv_map[ row["parameter_name"] ].append("{}={}".format(row["value_label"] , num) )
              
          elif row["type"] == "file":
            
            if row["parameter_name"] in no_duplicates:
              raise Exception("We cannot allow more than one definition of a file type in a single parameter sweep! External files must be consistent across all parameter permutations")
            else:
              no_duplicates.append( row["parameter_name"] )
            
            with open('{}/{}'.format(exp_dir, row["value_label"] ), 'w') as external_file:
              external_file.write(  row["value"]  )
            external_file.close()
          else:
            #We must have one of these defined or else we don't know how to handle it
            raise Exception("type of element in a row must be text, template-parameter, or number")
        
        else:
          raise Exception("You cannot set multiple default values!")
################################### END OF YES CASE##################################      
          
      elif row["default"] == "*":
        
        #handle parameters based upon what type they are
        if row["type"] == "template_parameter":
          if row["parameter_name"] in no_duplicates:
            raise Exception("We cannot allow more than one definition of a template parameter in a single file currently.")
          else:
            no_duplicates.append( row["parameter_name"] )
          search=row["value_label"]
          replace=row["value"]
          template_replacements[search]=replace
        elif row["type"] == "text":
          #make sure the text variable is defined
          if row["parameter_name"] not in all_ppv_map:
            all_ppv_map[ row["parameter_name"] ]=[]
          all_ppv_map[ row["parameter_name"] ].append( row["value"] )
        elif row["type"] == "number":
          #make sure the number variable is defined
          if row["parameter_name"] not in all_ppv_map:
            all_ppv_map[ row["parameter_name"] ]=[]
          
          
          start= float( row["value"].split(";")[0] )
          inc=   float( row["value"].split(";")[1] )
          stop=  float(row["value"].split(";")[2] )
          for num in range_f(start, inc, stop ):
            all_ppv_map[ row["parameter_name"] ].append( "{}={}".format(row["value_label"] , num ))
        elif row["type"] == "file":
          if row["parameter_name"] in no_duplicates:
            raise Exception("We cannot allow more than one definition of a file type in a single parameter sweep! External files must be consistent across all parameter permutations")
          else:
            no_duplicates.append( row["parameter_name"] )
          with open('{}/{}'.format(exp_dir, row["value_label"] ), 'w') as external_file:
            external_file.write(  row["value"]  )
          external_file.close()
        else:
          #We must have one of these defined or else we don't know how to handle it
          raise Exception("type of element in a row must be text, template-parameter, or number")
        
      else:
        
        ##################THESE ARE SINGLE ONLY PARAMETERS##################################B
        #handle parameters based upon what type they are
        if row["type"] == "template_parameter":
          if row["parameter_name"] in no_duplicates:
            raise Exception("We cannot allow more than one definition of a template parameter in a single file currently.")
          else:
            no_duplicates.append( row["parameter_name"] )
          search=row["value_label"]
          replace=row["value"]
          template_replacements[search]=replace
        elif row["type"] == "text":
          #make sure the text variable is defined
          if row["parameter_name"] not in single_ppv_map:
            single_ppv_map[ row["parameter_name"] ]=[]
          single_ppv_map[ row["parameter_name"] ].append( row["value"] )
        elif row["type"] == "number":
          #make sure the number variable is defined
          if row["parameter_name"] not in single_ppv_map:
            single_ppv_map[ row["parameter_name"] ]=[]

          if len( row["value"].split(";") ) > 3:
            raise Exception("You should specify that you are using a default value if you are including 4 values in a number cell")

          start= float( row["value"].split(";")[0] )
          inc=   float( row["value"].split(";")[1] )
          stop=  float(row["value"].split(";")[2] )
          for num in range_f(start, inc, stop ):
            single_ppv_map[ row["parameter_name"] ].append( "{}={}".format(row["value_label"] , num ))
        elif row["type"] == "file":
          if row["parameter_name"] in no_duplicates:
            raise Exception("We cannot allow more than one definition of a file type in a single parameter sweep! External files must be consistent across all parameter permutations")
          else:
            no_duplicates.append( row["parameter_name"] )
          with open('{}/{}'.format(exp_dir, row["value_label"] ), 'w') as external_file:
            external_file.write(  row["value"]  )
          external_file.close()
        else:
          #We must have one of these defined or else we don't know how to handle it
          raise Exception("type of element in a row must be text, template-parameter, or number")
        
#      if row["parameter_name"] not in parameter_property_labels:
#        parameter_property_labels[ row["parameter_name"] ] = []
      
      
  csvfile.close()  
  
  #make sure ordering stays the same
  all_ppv_map = OrderedDict(sorted(all_ppv_map.items(), key=lambda t: t[0]))
  single_ppv_map = OrderedDict(sorted(single_ppv_map.items(), key=lambda t: t[0]))
  
  #initially everything needs to be selected, nothing is currently selected, and we are starting at job0
  select_parameters( all_ppv_map, {}, single_ppv_map, template_replacements, parameter_value_to_label_maps, reversed_ordered_parameter_names )

  #AFTER everything else has been done add the post-processing commands
  with open(temporary_job_queue_file, 'a') as job_file:
    #date= datetime.datetime.today().strftime('%Y-%m-%d')
    job_command = "cd {0}/scripts/post_processing && ./post_process_over_ssh.sh {0}/DATA/{1}\n".format(run_dir, exp_name  )
    job_file.write( job_command  )
    job_file.close()



#make a recursive function which has a list of SELECTED parameters AND parameters TO BE SELECTED
#when the recursive function has no more parameters TO BE SELECTED
#then go through the one time inclusion list, with a flag saying WRITE which replaces a single default value
def select_parameters( unselected_parameters_map, selected_parameters_map, single_ppv_map, template_replacements, parameter_value_to_label_maps, reversed_ordered_parameter_names):
  
  if len(unselected_parameters_map) == 0:
    # We have processed everything we can up to this point, we need to now go through replacing each single permutation parameter
    # one at a time, with a need for a deepcopy
    write_selected_parameters_to_file( copy.deepcopy( selected_parameters_map ), copy.deepcopy(single_ppv_map), template_replacements, parameter_value_to_label_maps, reversed_ordered_parameter_names )
    
  else:
    #choosing one parameter ti iterate over
    key, values = unselected_parameters_map.popitem()
  
    for value in values:
      dprint( "Iterating:  {} -> {}".format(key, value) )
      selected_parameters_map[key] = value
      select_parameters( copy.deepcopy(unselected_parameters_map), copy.deepcopy(selected_parameters_map), single_ppv_map, template_replacements, parameter_value_to_label_maps, reversed_ordered_parameter_names)
  
#then simply go through the selected list and write the necessary components to file
def write_selected_parameters_to_file( selected_parameters_map, single_ppv_map,  template_replacements, parameter_value_to_label_maps, reversed_ordered_parameter_names):
  
  
  if len(single_ppv_map) == 0:
    
        copy_map = selected_parameters_map
        summary_top_text=";SUMMARY: "
        
        summary_filename="JOB"
        
        for k in sorted(copy_map.keys()):
          if k in parameter_value_to_label_maps:
            if copy_map[k] in parameter_value_to_label_maps[k]:
              display_value = parameter_value_to_label_maps[k][ copy_map[k] ]
              k = reversed_ordered_parameter_names[k]
              summary_top_text+= "{}->{},".format(k, display_value )
              summary_filename+= "_{}-{}".format(k, display_value )
        
        summary_top_text+= "\n\n"
        
        #job_names.append( summary_filename )
        
               
        with open( template , 'r') as template_file:
          template_contents = template_file.read()
        template_file.close()
        
        for k in template_replacements:
          if template_replacements[k] =="$JOB_COUNT$":
            template_contents = template_contents.replace( k, str(job_count) )
          else:
            template_contents = template_contents.replace( k, template_replacements[key] )
        
        
        #write with the summary name in file as well
        
        with open('{}/NAMED_JOBS/{}.ini'.format(config_dir, summary_filename  ), 'w') as prop_file:
          prop_file.write( summary_top_text )
          prop_file.write( template_contents + "\n"  )
          
          for k in sorted(copy_map.keys()):
            prop_file.write( copy_map[k] )
            prop_file.write( "\n\n" )
          
        prop_file.close()
        
        
        
        
        with open(temporary_job_queue_file, 'a') as job_file:
          
          summary = summary_filename.replace(".ini", "")
          job_command = "cd {} && ./runExp {}/NAMED_JOBS/{}.ini {} \n".format(run_dir, config_dir, summary_filename,  exp_name+"/"+summary )

          #job_command = "cd {}/scripts/post_processing/ && post_process.sh {} "
          #job_command += "cd {0}/scripts/plotting/ && ./generate_all_plots.sh {0}/DATA/{1} \n".format(run_dir,  exp_name )
          #job_command += "cd {0}/scripts/plotting/ && ./send_all_emails.sh {0}/PLOTS/{1} \n".format(run_dir,  exp_name )
          #job_command += "cd {0}/scripts/post_processing && ./tar_and_store.sh {0}/PLOTS/{1} \n".format(run_dir,  exp_name )
          
          #date= datetime.datetime.today().strftime('%Y-%m-%d')
          #job_command += "cd {0}/scripts/post_processing && ./post_process.sh {0}/DATA/{1}-{2}\n".format(run_dir, date, exp_name  )
        
          job_file.write( job_command  )
        job_file.close()
  
  
  for key in sorted(single_ppv_map.keys()):
    #must make copy so we don't make the temporary swaps affect future permutations
    copy_map = copy.deepcopy( selected_parameters_map )
    
    if key not in copy_map.keys():
      print( key )
      raise Exception("This should not happen, this means that you have a single use parameter which has no default value!")
    else:
      
      dprint( "{} in {}".format(key, copy_map.keys() ) )
      
      
      
      
      for value in single_ppv_map[key]:
        dprint("########")
        dprint( "key:"+key)
        dprint( "value:"+value)
        dprint("##########################################")
        dprint("replacing \n  {} \nWITH  \n  {}\n".format(copy_map[key], value))
        dprint("##########################################")
        dprint("Labeling this:{}->{}".format(key, parameter_value_to_label_maps[key][value] ) )
        
        copy_map[key]= value



        summary_filename="JOB"
        
        
        summary_top_text=";SUMMARY: "
        
        for k in sorted(copy_map.keys()):
          if k in parameter_value_to_label_maps:
            if copy_map[k] in parameter_value_to_label_maps[k]:
              display_value = parameter_value_to_label_maps[k][ copy_map[k] ]
              k = reversed_ordered_parameter_names[k]
              summary_top_text+= "{}->{},".format(k, display_value )
              summary_filename+= "_{}-{}".format(k, display_value )

        
        summary_top_text+= "\n\n"
        
        #job_names.append( summary_filename )
        
        #read in template contents
        #search and replace
        #append all parameters at start of file
        #first line abbreviations?
        
        with open( template , 'r') as template_file:
          template_contents = template_file.read()
        template_file.close()
        
        for k in template_replacements:
        
          if template_replacements[k] =="$JOB_COUNT$":
            template_contents = template_contents.replace( k, str(job_count) )
          else:
            template_contents = template_contents.replace( k, template_replacements[key] )
        
        
        #write with the summary name in file as well

        with open('{}/NAMED_JOBS/{}.ini'.format(config_dir, summary_filename  ), 'w') as prop_file:
          prop_file.write( summary_top_text )
          prop_file.write( template_contents + "\n"  )

          for k in sorted(copy_map.keys()):
            prop_file.write( copy_map[k] )
            prop_file.write( "\n\n" )

        prop_file.close()

        
        
        
        
        
        
        with open(temporary_job_queue_file, 'a') as job_file:
          summary = summary_filename.replace(".ini", "")
          job_command =  "cd {} && ./runExp {}/NAMED_JOBS/{}.ini {} \n".format(run_dir, config_dir, summary_filename,  exp_name+"/"+summary )
          
          job_file.write( job_command  )
        job_file.close()


#just a simple function like range() but for floats
def range_f(start, increment, stop):
  if increment <= 0:
    raise Exception('increment value must be positive in call to range_f in order to guarantee completion!')
  values=[]
  while start <= stop:
    if start.is_integer():
      start = int(start)
    values.append(start)
    start += increment
  return values

main()


#print("don't forget to rm temp")
#quit()
#os.system( "echo '{}'".format(temporary_job_queue_file ) )

if generate_batch_mode or bigred2:
  os.system( "cat {} | tail -n 2".format(temporary_job_queue_file) )
  print( "temporary job file will only be appended to!" )
else:
  os.system( "python job_q_server/client_add_jobs.py {}".format( temporary_job_queue_file ) )
  os.system( "rm {}".format( temporary_job_queue_file ))


#os.system( "printed job queue" )



