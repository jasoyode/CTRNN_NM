from collections import OrderedDict
import csv
import os
import sys
import copy



if len(sys.argv) < 4:
  print("You must provide 4 parameters: name, template, parameter_list")
  quit()


exp_name=sys.argv[1]


#tmp_exp_dir=exp_dir.replace("/scratch/jasoyode/EXPERIMENTS/EXPERIMENTS/", "/tmp/")


template=sys.argv[2]
parameter_list_file=sys.argv[3]

exp_dir="/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/{}".format( exp_name )

generate_batch_mode=False

if len(sys.argv) > 4:
  print("You specified a 5th parameter and it is: {}".format(sys.argv[4]) )
  generate_batch_mode=True


print( "Job name: {}\nTemplate: {}\nParameter List: {}".format( exp_name, template, parameter_list_file ) )


temporary_job_queue_file="temp_job_queue.txt"

#job_path='{}/JOBS_DIR/job_{}.properties'.format(exp_dir, job_count )


#EDIT HERE
DEBUG=False

job_count=0

def dprint(message ):
  if DEBUG:
    print( message )


def main():

  #create experiment directory
  os.system("mkdir -p {}".format( exp_dir ) )
  
  #create JOBS directory for properties files
  os.system("mkdir -p {}/JOBS_DIR".format(exp_dir) )
  
#  job_names = []
  
  os.system("mkdir -p {}/NAMED_JOBS".format(exp_dir) )
  
  #create JOBS COMEPLTEdirectory for properties files
  os.system("mkdir -p {}/JOBS_COMPLETED".format(exp_dir) )
  
  
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
    
    
    for row in reader:
      
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
  select_parameters( all_ppv_map, {}, single_ppv_map, template_replacements, parameter_value_to_label_maps)


#make a recursive function which has a list of SELECTED parameters AND parameters TO BE SELECTED
#when the recursive function has no more parameters TO BE SELECTED
#then go through the one time inclusion list, with a flag saying WRITE which replaces a single default value
def select_parameters( unselected_parameters_map, selected_parameters_map, single_ppv_map, template_replacements, parameter_value_to_label_maps):
  
  if len(unselected_parameters_map) == 0:
    # We have processed everything we can up to this point, we need to now go through replacing each single permutation parameter
    # one at a time, with a need for a deepcopy
    write_selected_parameters_to_file( copy.deepcopy( selected_parameters_map ), copy.deepcopy(single_ppv_map), template_replacements, parameter_value_to_label_maps )
    
  else:
    #choosing one parameter ti iterate over
    key, values = unselected_parameters_map.popitem()
  
    for value in values:
      dprint( "Iterating:  {} -> {}".format(key, value) )
      selected_parameters_map[key] = value
      select_parameters( copy.deepcopy(unselected_parameters_map), copy.deepcopy(selected_parameters_map), single_ppv_map, template_replacements, parameter_value_to_label_maps)
  
#then simply go through the selected list and write the necessary components to file
def write_selected_parameters_to_file( selected_parameters_map, single_ppv_map,  template_replacements, parameter_value_to_label_maps):
  
  
  if len(single_ppv_map) == 0:
    
        copy_map = selected_parameters_map
        global job_count
        job_count += 1
        summary_top_text=";SUMMARY: "
        
        
        summary_filename="exp"
        
        for k in copy_map.keys():
          if k in parameter_value_to_label_maps:
            if copy_map[k] in parameter_value_to_label_maps[k]:
              display_value = parameter_value_to_label_maps[k][ copy_map[k] ]
              summary_top_text+= "{}->{},".format(k, display_value )
              summary_filename+= "_{}-{}".format(k, display_value )
        
        summary_top_text+= "\n\n"
        
        #job_names.append( summary_filename )
        
               
        print( "Writing to file job_{}.ini".format( job_count ) )
        
        with open( template , 'r') as template_file:
          template_contents = template_file.read()
        template_file.close()
        
        for k in template_replacements:
          if template_replacements[k] =="$JOB_COUNT$":
            template_contents = template_contents.replace( k, str(job_count) )
          else:
            template_contents = template_contents.replace( k, template_replacements[key] )
        
        
        with open('{}/JOBS_DIR/job_{}.ini'.format(exp_dir, job_count ), 'w') as prop_file:
          prop_file.write( summary_top_text )
          prop_file.write( template_contents + "\n"  )
          
          for k in copy_map.keys():
            prop_file.write( copy_map[k] )
            prop_file.write( "\n\n" )
          
        prop_file.close()
        
        #write with the summary name in file as well
        
        with open('{}/NAMED_JOBS/{}.ini'.format(exp_dir, summary_filename  ), 'w') as prop_file:
          prop_file.write( summary_top_text )
          prop_file.write( template_contents + "\n"  )
          
          for k in copy_map.keys():
            prop_file.write( copy_map[k] )
            prop_file.write( "\n\n" )
          
        prop_file.close()
        
        
        
        
        with open(temporary_job_queue_file, 'a') as job_file:
          
          summary = summary_filename.replace(".ini", "")
          job_command = "cd /nfs/nfs7/home/jasoyode/github_jasoyode/CTRNN_NM/ && ./runExp {}/NAMED_JOBS/{}.ini {} \n".format( exp_dir, summary_filename,  exp_name+"_"+summary )

        
          job_file.write( job_command  )
        job_file.close()
  
  
  for key in single_ppv_map.keys():
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
        
        global job_count
        job_count += 1
        copy_map[key]= value



        summary_filename="exp"
        
        
        summary_top_text=";SUMMARY: "
        
        for k in copy_map.keys():
          if k in parameter_value_to_label_maps:
            if copy_map[k] in parameter_value_to_label_maps[k]:
              display_value = parameter_value_to_label_maps[k][ copy_map[k] ]
              summary_top_text+= "{}->{},".format(k, display_value )
              summary_filename+= "_{}-{}".format(k, display_value )

        
        summary_top_text+= "\n\n"
        
        #job_names.append( summary_filename )
        
        print( "Writing to file job_{}.ini".format( job_count ) )
        
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
        
        
        with open('{}/JOBS_DIR/job_{}.ini'.format(exp_dir, job_count ), 'w') as prop_file:
          prop_file.write( summary_top_text )
          prop_file.write( template_contents+ "\n"  )
          
          for k in copy_map.keys():
            prop_file.write( copy_map[k] )
            prop_file.write( "\n\n" )
          
        prop_file.close()
        
        #write with the summary name in file as well

        with open('{}/NAMED_JOBS/{}.ini'.format(exp_dir, summary_filename  ), 'w') as prop_file:
          prop_file.write( summary_top_text )
          prop_file.write( template_contents + "\n"  )

          for k in copy_map.keys():
            prop_file.write( copy_map[k] )
            prop_file.write( "\n\n" )

        prop_file.close()

        
        
        
        
        
        
        with open(temporary_job_queue_file, 'a') as job_file:
          
          #job_command = "cd /nfs/nfs7/home/jasoyode/github_jasoyode/CTRNN_NM/ && ./runExp {}/NAMED_JOBS/{}.ini {} \n".format( exp_dir, summary_filename,  exp_name )
          summary = summary_filename.replace(".ini", "")
          job_command = "cd /nfs/nfs7/home/jasoyode/github_jasoyode/CTRNN_NM/ && ./runExp {}/NAMED_JOBS/{}.ini {} \n".format( exp_dir, summary_filename,  exp_name+"_"+summary )

          
          
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

#print("DONE!")      
#with open(temporary_job_queue_file, 'r') as job_file: 
#  print(job_file.read() )
#job_file.close()

with open('{}/check_list.txt'.format(exp_dir ), 'w') as check_file:

  #make check list for firing emails
  for i in range( job_count ):
    n = i+1
    check_file.write( "job_{}.txt\n".format( n ) )
    
    
check_file.close()

#print("don't forget to rm temp")
#quit()
#os.system( "echo '{}'".format(temporary_job_queue_file ) )

if generate_batch_mode:
  os.system( "cat {}".format(temporary_job_queue_file) )

else:
  os.system( "python job_q_server/client_add_jobs.py {}".format( temporary_job_queue_file ) )
  os.system( "rm {}".format( temporary_job_queue_file ))


#os.system( "printed job queue" )



