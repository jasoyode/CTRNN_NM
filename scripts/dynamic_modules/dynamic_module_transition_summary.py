import csv
import sys
import re
import os
import operator

DEFAULT_MODE=False
DEBUG_MODE=False
#Use the relative activity levels of each neuron to determine if it is in a transient state = TRUE
#or try to use derivatives to determine if its in a transient state = FALSE
ABS_MODE=True


CPG_3_EVO_STD =            "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/seed_{}_recorded_activity.csv"
CPG_3_EVO_MOD_TEST_MOD =   "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/seed_{}_recorded_activity.csv"
CPG_3_EVO_MOD_TEST_NOMOD = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/TESTS/AMP_0.0/seed_{}_recorded_activity.csv"

RPG_3_EVO_STD = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/seed_{}_recorded_activity.csv"
RPG_3_EVO_MOD_TEST_MOD = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/seed_{}_recorded_activity.csv"
RPG_3_EVO_MOD_TEST_NOMOD = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/TESTS/AMP_0.0/seed_{}_recorded_activity.csv"

DEFAULT_FILE_TEMPLATE=CPG_3_EVO_STD

RUNS=100
CYCLE_REQ=10

#this seems to be high, but the derivative threshold must be held high in order to make sure
#we are not getting noise at the ends
ON_OFF_THRESHOLD=0.25

#this is a percentage of the maximum peak 
#observed between timestep 1000 and 2000 
#(after initial startin states are evened out)
DERIVATIVE_THRESHOLD=0.005


FT_POS=6
BS_POS=17
FS_POS=28

WRITE_DICTIONARY={}
WRITE_DICTIONARY["CPG_3_EVO_STD.txt"]            = CPG_3_EVO_STD
WRITE_DICTIONARY["CPG_3_EVO_MOD_TEST_MOD.txt"]   = CPG_3_EVO_MOD_TEST_MOD
WRITE_DICTIONARY["CPG_3_EVO_MOD_TEST_NOMOD.txt"] = CPG_3_EVO_MOD_TEST_NOMOD

WRITE_DICTIONARY["RPG_3_EVO_STD.txt"]            = RPG_3_EVO_STD
WRITE_DICTIONARY["RPG_3_EVO_MOD_TEST_MOD.txt"]   = RPG_3_EVO_MOD_TEST_MOD
WRITE_DICTIONARY["RPG_3_EVO_MOD_TEST_NOMOD.txt"] = RPG_3_EVO_MOD_TEST_NOMOD


if len(sys.argv) < 2:
  print("Must provide a seed_activity.csv file!")
  print("Running default values")
  DEFAULT_MODE=True
elif len(sys.argv) == 2:
  SEED_ACTIVITY_FILE=sys.argv[1]
  OUTPUT_DM_SEED_FILE=""
  DEFAULT_FILE_TEMPLATE=SEED_ACTIVITY_FILE
else:
  SEED_ACTIVITY_FILE=sys.argv[1]
  OUTPUT_DM_SEED_FILE=sys.argv[2]
  DEFAULT_FILE_TEMPLATE=SEED_ACTIVITY_FILE


DM_DICT={}


def load_beer_list():
  dm_file="BEER_DM_LIST.csv"
  
  activity_data=[]

  with open( dm_file  ) as file:
    dm_reader = csv.DictReader( file )
    
    if not "transition" in dm_reader.fieldnames:
      print("The file you passed in does not have a transition header, exiting...")
      quit()
    
    for row in dm_reader:
      entry = []
      entry.append( int( row["number"] ) )
      
      entry.append(  row["adjacency"] )
      entry.append(  row["consistency"] )
      entry.append(  row["ordered"] )

      DM_DICT[ row["transition"]    ] = entry
  



def main( file_template, output_file="" ):
  load_beer_list()
  #print( DM_DICT )
  #quit()
  #print( OUTPUT_DM_SEED_FILE   )
  DIR=re.sub("[^\/]*.csv","", OUTPUT_DM_SEED_FILE )
  #print( DIR)
  os.system("mkdir -p {}".format( DIR ) )
  
   
  WRITE_TO_FILE_MODE=False
  if output_file != "":
    WRITE_TO_FILE_MODE=True

    fh = open(output_file,"w")
  
  if DEFAULT_MODE:
    pattern_to_seed_map={}
    all_states_pattern_to_seed_map={}
    
    for i in range(1,RUNS+1):
      print("seed: {}".format( i)  )
      #file = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/seed_{}_recorded_activity.csv".format(i)
      #file = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/TESTS/AMP_0.0/seed_{}_recorded_activity.csv".format(i)
      #file = "../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/seed_{}_recorded_activity.csv".format(i)
      file = file_template.format( i )
      
      #print("SEED: {}".format( i ) )
      
      pairs = process_file( file, False )
      pairs_all_states = process_file( file, True )
      
      if len( pairs ) > 1:
        #print("skipping seed {} because it has multiple cycles".format(i) )
        multi_cycle_pattern=""
        for pair in pairs:
          #print( pair )
          multi_cycle_pattern += pair[0][0]+" --- "
        
        #for ps in pairs_all_states:
          #for p in ps:       
          #  print(p)
        
        multi_cycle_pattern = multi_cycle_pattern.strip()
        if not multi_cycle_pattern in pattern_to_seed_map:
          pattern_to_seed_map[ multi_cycle_pattern ] = []
        pattern_to_seed_map[ multi_cycle_pattern ].append( i )
      else:
        if len( pairs ) < 1:
          if WRITE_TO_FILE_MODE:
            fh.write( "Seed {} did not have any cycles, consider lowering the CYCLE_REQ threshold from {}\n".format( i, CYCLE_REQ))
          else:
            print( "Seed {} did not have any cycles, consider lowering the CYCLE_REQ threshold from {}".format( i, CYCLE_REQ))
        else:
          if not pairs[0][0] in pattern_to_seed_map:
            pattern_to_seed_map[ pairs[0][0] ] = []
          pattern_to_seed_map[ pairs[0][0] ].append( i )
      
      if len( pairs_all_states ) > 1:
        #print("skipping seed {} because it has multiple cycles".format(i) )
        multi_cycle_pattern=""
        for pair in pairs_all_states:
          #print( pair )
          multi_cycle_pattern += pair[0][0]+" --- "
        
        multi_cycle_pattern = multi_cycle_pattern.strip()
        if not multi_cycle_pattern in all_states_pattern_to_seed_map:
          all_states_pattern_to_seed_map[ multi_cycle_pattern ] = []
        all_states_pattern_to_seed_map[ multi_cycle_pattern ].append( i )
      else:
        if len( pairs_all_states ) < 1:
          if WRITE_TO_FILE_MODE:
            fh.write( "Seed {} did not have any cycles, consider lowering the CYCLE_REQ threshold from {}\n".format( i, CYCLE_REQ))
          else:
            print( "Seed {} did not have any cycles, consider lowering the CYCLE_REQ threshold from {}".format( i, CYCLE_REQ))
        else:
          if not pairs_all_states[0][0] in all_states_pattern_to_seed_map:
            all_states_pattern_to_seed_map[ pairs_all_states[0][0] ] = []
          all_states_pattern_to_seed_map[ pairs_all_states[0][0] ].append( i )

    
    
    
    
    #order by most common dynamics
    for item in sorted(pattern_to_seed_map.items(), key=lambda x: -len(x[1]) ):
      if WRITE_TO_FILE_MODE:
        #fh.write( "The following pattern appears {} times in the seeds {}:\n".format( len( pattern_to_seed_map[ item[0] ]), pattern_to_seed_map[ item[0] ] ))
        if item[0] in DM_DICT:
          fh.write( "{} was DM #{} in Beers list, has consistency: {} adjacency: {} and  appeared {} times in the seeds {}".format( item[0], DM_DICT[item[0]][0], DM_DICT[item[0]][1], DM_DICT[item[0]][2],  len( pattern_to_seed_map[ item[0] ]), pattern_to_seed_map[ item[0] ] ))
        else:
          fh.write( "{}  appeared {} times in the seeds {}".format( item[0], len( pattern_to_seed_map[ item[0] ]), pattern_to_seed_map[ item[0] ] ))
        fh.write( "\n" )
      else:
        print( "The following pattern appears {} times in the seeds {}:".format( len( pattern_to_seed_map[ item[0] ]), pattern_to_seed_map[ item[0] ] ))
        print( item[0] )

    seeds_out=re.sub(".png","_seeds.png",output_file)
    seeds_out= "seeds_"+output_file
    seeds_fh = open(seeds_out, "w")
    
    #order by most common dynamics
    for item in sorted(all_states_pattern_to_seed_map.items(), key=lambda x: -len(x[1]) ):
      if WRITE_TO_FILE_MODE:
        for seed in all_states_pattern_to_seed_map[ item[0]]:
          #print(seed)
          seeds_fh.write( "{},{}".format(seed, item[0] ))
          seeds_fh.write( "\n" )
    
    
    
      
  else:
    pairs = process_file( SEED_ACTIVITY_FILE, True )
    pairs_all_states = process_file( SEED_ACTIVITY_FILE, False )
    #print( pairs )
    #print( pairs_all_states )
    #for pair in pairs:
    print( "The follow pattern appeared {} times:".format( pairs[0][1] ) )
    #print( pairs)
    print( pairs[0][0] )
    print("Compressed format:")
    print( pairs_all_states[0][0] )
    #print(  reduce_to_dm_transition( pair[0] ) )

    
    if OUTPUT_DM_SEED_FILE != "":
      
      fh_dm = open(OUTPUT_DM_SEED_FILE,"w")
      fh_dm.write("seed,dm,\n")
      seed = re.sub(".*seed_","",SEED_ACTIVITY_FILE)
      seed = re.sub("_recorded_activity.csv","", seed)
      print("Writing seed {} to file: {}".format( seed, OUTPUT_DM_SEED_FILE))
      fh_dm.write("{},{}".format( seed, pairs[0][0] ) )
      fh_dm.close()
    
      
  if WRITE_TO_FILE_MODE  :
    seeds_fh.close()
    fh.close()


def process_file( seed_activity_file, show_all=False ):
  
  activity_data, size = parse( seed_activity_file )
  count=0
  last_data=[]
  summary_data=[]
  
  
  lowest_der=  list(map( operator.sub, activity_data[0], activity_data[0] ))
  highest_der= list(map( operator.sub, activity_data[0], activity_data[0] ))
  
  highest = activity_data[0]
  lowest = activity_data[0]
  
  for i in range(1000, 2000 ):
    #used to calculate if in transition or not
    #we want to use the relative peaks of the individual neuron derivatives to give a test of 
    #relative % progress towards peak, say 10% towards peak to be considered in a transition
    
    lowest_der  = list(map(min, lowest_der, list(map( operator.sub, activity_data[i], activity_data[i-1] )) ))
    highest_der = list(map(max, highest_der, list(map( operator.sub, activity_data[i],activity_data[i-1] )) ))
    
    lowest  = list(map(min, lowest,  activity_data[i] ))
    highest = list(map(max, highest, activity_data[i] ))
  
  
  #TEMP FOR TESTING DATA RANGE OBSERVED  
  #for i in range(1100, 1350 ):
  
  #start after noisy states
  for i in range(2000, len(activity_data) ):
    if DEBUG_MODE:
      print("TIMESTEP:   {}    ".format(i))
    
    if ABS_MODE:
      current = transform_abs( activity_data[i-1],  activity_data[i], size, ON_OFF_THRESHOLD, DERIVATIVE_THRESHOLD, lowest_der, highest_der, lowest, highest )
    else:
      current = transform( activity_data[i-1],  activity_data[i], size, ON_OFF_THRESHOLD, DERIVATIVE_THRESHOLD, lowest_der, highest_der, lowest, highest )
    
    
    if last_data != current:
      #summary_data.append( "{} - {} timesteps ".format( last_data, count ) )
      summary_data.append( "{}".format( last_data ) )
      if DEBUG_MODE:
        print(   "{} - {} timesteps ".format( last_data, count )      )
      count=0
    last_data = current
    count+=1
  #summary_data.append( "{} - {} timesteps ".format( last_data, count ) )
  summary_data.append( "{}".format( last_data ) )
  
  
  
  
  current_string=""
  pattern_dict={}
  
  for line in summary_data:
    if line in current_string:
    ################## store cycle
      if std(current_string, show_all) in pattern_dict:
        pattern_dict[ std(current_string, show_all) ] = pattern_dict[ std(current_string, show_all) ] + 1
      else:
        pattern_dict[ std(current_string, show_all) ] = 1
      current_string=""
    else:
    ############################## append to cycle
      current_string+="\n"+line
  
  final_result=[]
  
    
  for s in pattern_dict:
    num= pattern_dict[s]
    if num > CYCLE_REQ:
      final_result.append( ( s, num)   )
      #print(  s  )
    #else:
      #print("Pattern only occured {} times, skipping".format( num  ) )
  return final_result
  
#standardize_cycle to start from the same position
def std( pattern_string, show_all=False ):
  line_rows=pattern_string.split('\n')
  highest_value=0
  highest_index=0
  ###############
  for i in range(0, len(line_rows)):
    if rank_score( line_rows[i] ) > highest_value:
      highest_value=rank_score( line_rows[i] )
      highest_index=i
  ###############
  return_lines=""
  for i in range(highest_index, len(line_rows)+highest_index):
    if not line_rows[ i % len(line_rows) ] == "":
      return_lines+="\n"+line_rows[ i % len(line_rows) ]
  return_lines = return_lines.strip('\n')
  return reduce_to_dm_transition( return_lines, show_all )

#make score to numerically order any given state  
def rank_score( line ):
  FT1=FT_POS
  FT2=FT1+3
  BS1=BS_POS
  BS2=BS1+3
  FS1=FS_POS
  FS2=FS1+3

  if line[FT1:FT2]=="ON ":
    FT=2
  elif line[FT1:FT2]=="OFF":
    FT=0
  else:
    FT=-100000
  
  if line[FS1:FS2]=="ON ":
    FS=2
  elif line[FS1:FS2]=="OFF":
    FS=0
  else:
    FS=-10000
  
  if line[BS1:BS2]=="ON ":
    BS=2
  elif line[BS1:BS2]=="OFF":
    BS=0
  else:
    BS=-1000

  return 100*FT + 10*FS + BS
  

def lookup( n ):
  if n ==1:
    return "FT"
  elif n ==2:
    return "BS"
  elif n ==3:
    return "FS"
  else:
    return "I{}".format( n - 3 )

def transform(prior_activity_entry, activity_entry, size, threshold, derivative_threshold, lowest_der, highest_der, lowest, highest ):
  entry=[]
  
  #if activity_entry[3] > 0.6: #(1 - threshold):
  #  print( activity_entry[3]    )
  #  print( "ddd" )
  #  quit()
  #print("\n------------------")
  for i in range(0, size):
    deriv= activity_entry[i] - prior_activity_entry[i]
    abs_diff = abs( activity_entry[i] - prior_activity_entry[i] )
    
    if DEBUG_MODE and i == 0:
      print( "lowest {}".format(lowest[i]) )
      print( "highest {}".format( highest[i]) )
      print( "{} because deriv: {}  <= {}".format( (deriv <=lowest_der[i] + derivative_threshold), deriv, (lowest_der[i] + derivative_threshold) ) )
      print( "{} because deriv: {}  >= {}".format( (deriv >= (highest_der[i] - derivative_threshold)), deriv, (highest_der[i] - derivative_threshold) ) )
      print( "{} because  activity: {}  < {}".format( (activity_entry[i] < (lowest[i] +  threshold)  ), activity_entry[i], ( lowest[i] +  threshold) ) )
      print( "{} because  activity: {}  > {}".format( (activity_entry[i] > ( highest[i]  - threshold)  ), activity_entry[i], ( highest[i]  - threshold) ) )
      
        
    #if rate of change is high, we are in a transition
    #if abs_diff > derivative_threshold:
    if deriv <= (lowest_der[i] + derivative_threshold) or deriv >= (highest_der[i] - derivative_threshold):
    #if deriv <= -derivative_threshold or deriv >= derivative_threshold:
      entry.append("{}->T  ".format(lookup(i+1) ) )
      #if DEBUG_MODE:
      #  print( "deriv: {}  >= {}".format( deriv, (lowest_der[i] + derivative_threshold) ) )
      #  print( "deriv: {}  <= {}".format( deriv, (highest_der[i] - derivative_threshold) ) )
      #  print("T   " )
    #if not transitioning then if below certain threshold we can expect to be OFF
    elif activity_entry[i] < (lowest[i] +  threshold) :
      entry.append("{}->OFF".format(lookup(i+1) ) )
      #if DEBUG_MODE and i==0:
      #  print( "activity: {}  <= {}".format( activity_entry[i], ( lowest[i] +  threshold) ) )
      #  print( "activity: {}  >= {}".format( activity_entry[i], ( highest[i]  - threshold) ) )
      #  print("OFF " )
    #if not transitioning then if within certain threshold of 1 we can expect to be ON
    elif activity_entry[i] > ( highest[i]  - threshold):
      entry.append("{}->ON ".format(lookup(i+1) ) )
      #if DEBUG_MODE and i==0:
        #print( "lowest {}".format(lowest[i]) )
        #print( "highest {}".format( highest[i]) )
        #print( "activity: {}  <= {}".format( activity_entry[i], ( lowest[i] +  threshold) ) )
        #print( "activity: {}  >= {}".format( activity_entry[i], ( highest[i]  - threshold) ) )
        #print("ON   " )
        

    #if not in transition AND not ON or OFF, then something is weird, like a type of
    # stable equilibrium that is not at 0 or 1, which is quite bizarre
    #in which case I want to throw and error and see what is going on    
    else:
      entry.append("{}->T  ".format(lookup(i+1) ) )
      
      #print("Found an state with non-transitioing state which is NOT ON or OFF")
      #print("(highest - threshold): {}".format(  (highest[i+1] - threshold) ) )
      #print("(lowest + threshold): {}".format(   lowest[i+1] + threshold ) )
      #print("neuron({}) with prior activation: {}  current activation {}".format(i, prior_activity_entry[i], activity_entry[i]) )
      #print("neuron({}) with abs(derivative diff): {} < derive threshold {}".format(i, abs_diff, derivative_threshold) )
      #print("ON OFF threshold: {}".format( threshold ))
      #print( lowest[:3] )
      ##print( highest[:3] )
      #
      #sys.exit(0)
      #quit()
      #entry.append("{}->T  ".format(lookup(i+1) ) )
  return  entry




def transform_abs(prior_activity_entry, activity_entry, size, threshold, derivative_threshold, lowest_der, highest_der, lowest, highest ):
  
  entry=[]
  for i in range(0, size):
    if activity_entry[i] < (lowest[i] +  threshold) :
      entry.append("{}->OFF".format(lookup(i+1) ) )
    elif activity_entry[i] > ( highest[i]  - threshold):
      entry.append("{}->ON ".format(lookup(i+1) ) )
    else:
      entry.append("{}->T  ".format(lookup(i+1) ) )
  return  entry
  
  
  


#should be normalized before passed to this method
def reduce_to_dm_transition( string, show_all=False ):
  list=string.split("\n")
  result=""
  if "T  " in list[0]:
    print("This should RARELY happen! Every state includes at least one transient condition, NO quasi-stable states present!")
    #print( list )
    return "{TTT}=>"
    #sys.exit(-1)
    #quit()
  
  current_quasi_state=list[0]
  list.append( current_quasi_state )
  first=True
  # must add transitions, not actual states 
  # result.append( current_quasi_state )
  for state in list:
    if first:
      first=False
    elif not "T  " in state:
      #adjust state prev quasi state
      #compare each part
      #the ones that change need to be included in result with up or down
      trans="{"
      if current_quasi_state[FT_POS:FT_POS+3]!=state[FT_POS:FT_POS+3 ]:
        if state[FT_POS:FT_POS+3 ]=="ON ":
          trans+="FT↑ "
        else:
          trans+="FT↓ "
      elif show_all:
        if state[FT_POS:FT_POS+3 ]=="ON ":
          trans+="FT+ "
        else:
          trans+="FT- "
      if current_quasi_state[BS_POS:BS_POS+3]!=state[BS_POS:BS_POS+3]:
        if state[BS_POS:BS_POS+3 ]=="ON ":
          trans+="BS↑ "
        else:
          trans+="BS↓ "
      elif show_all:
        if state[BS_POS:BS_POS+3 ]=="ON ":
          trans+="BS+ "
        else:
          trans+="BS- "
      if current_quasi_state[FS_POS:FS_POS+3]!=state[FS_POS:FS_POS+3]:
        if state[FS_POS:FS_POS+3 ]=="ON ":
          trans+="FS↑ "
        else:
          trans+="FS↓ "
      elif show_all:
        if state[FS_POS:FS_POS+3 ]=="ON ":
          trans+="FS+ "
        else:
          trans+="FS- "
      trans=trans[:-1]
      trans+="}=>"
      #current quasi state now
      current_quasi_state=state
      result+= trans

  return result



def parse( seed_activity_file ):
  
  activity_data=[]
  with open( seed_activity_file  ) as activity_file:
    activity_reader = csv.DictReader(activity_file)
    size=0
    for header in activity_reader.fieldnames:
      if "_out" in header:
        n= int( header[1:2] )
        if n > size:
          size=n
    
    if not "n1_out" in activity_reader.fieldnames:
      print("The file you passed in does not have a n1_out header, exiting...")
      quit()
    
    for row in activity_reader:
      entry = []
      for i in range(1, size+1):
        entry.append( float( row["n{}_out".format(i) ] ) )
      entry.append( float( row["angle"] ) )
      activity_data.append( entry )
      
  return activity_data, size

if DEFAULT_MODE:
  for outfile in WRITE_DICTIONARY.keys():
    print( "Writing dynamic modules for {}  to file: {}".format(WRITE_DICTIONARY[outfile], outfile ) )
    main( WRITE_DICTIONARY[outfile], outfile )
else:
  main( DEFAULT_FILE_TEMPLATE)
