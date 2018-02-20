import configparser
import re
import os
import sys
import csv
import glob
import numpy as np
import operator
import matplotlib as mpl
import matplotlib.mlab as mlab

#headless mode
mpl.use('Agg')
import matplotlib.pyplot as plt

MinSearchValue = -1.0
MaxSearchValue = 1.0
ROUND=0
E=2.71828
EQ_THRESHOLD=0.0001
OUTPUT_THRESHOLD=0.001
STEPSIZE=0.1
self_loop_cutoff=4
STEPS=5
VECTOR_STEPS=1

MODULATION=-0.25

ALPHA=0.5
DEBUG=0
SHOW_VECTOR=False
#True
SEED=29

#PHENOTYPE_CSV_PATH="/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CITED_DATA/phenotypes.txt"
#GENOME_TYPE_PATH="/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CITED_DATA/genomes.txt"

PHENOTYPE_CSV_PATH="/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/phenotypes.txt"
GENOME_TYPE_PATH="/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/genomes.txt"

PHENOTYPE_CSV_PATH="/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/phenotypes.txt"
GENOME_TYPE_PATH="/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/genomes.txt"


#x coordinates
CONSTANT_INPUT_LEVELS_PER_UNIT=25

#y coordinates
LEVELS_CURRENT_ACTIVATION=10

#fewer columns
VECTOR_FIELD_DIVIDER=CONSTANT_INPUT_LEVELS_PER_UNIT*8/10

#fewer rows
VECTOR_FIELD_DIVIDER_2=LEVELS_CURRENT_ACTIVATION*2/10

#range of starting activation levels
STARTING_ACTIVATION_EXTREMA=[-25,25]

#range of external inputs to test
CONSTANT_INPUT_EXTREMA=[-20,20]




#if config file passed in use that to set variables instead of hard coding
if len(sys.argv) == 2:
  config = configparser.ConfigParser()
  config.read( sys.argv[1]   )
  
  #set all the values from the config to override the locally set values here
  MODULATION_LEVELS=config["ALL"]["MODULATION_VALUES"]
  SHOW_VECTOR=config["ALL"]["SHOW_VECTOR"]
  SEED=int(config["ALL"]["seed_num"])
  PHENOTYPE_CSV_PATH=config["ALL"]["input_csv"]
  GENOME_TYPE_PATH=config["ALL"]["seed_genomes_txt"]
  OUTPUT_PATH=config["ALL"]["output_dir"]
  print( "Generating SSIOs for modulation levels: {}".format(  MODULATION_LEVELS.split() ))





#returns a dictionary of the parameters and values
def get_phenotype_dictionary( csv_path, SEED ):
  if not "phenotype" in csv_path:
    print("You must provide a phenotype.txt file for this function! Exiting...")
    quit()
  value_dict={}
  
  with open( csv_path  ) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      size=0  
      if int(row["seed"]) == SEED:
        for header in row.keys():
          if not header == None and header.strip() != "":
            print( row[header] )
            value_dict[ header ] =  float( row[header] )
            if "bias" in header:
              if int(header[-1]) > size:
                size = int(header[-1])
        return value_dict, size


#returns a dictionary of the parameters and values
def get_phenotype_from_genotype_dictionary( csv_path, SEED ):
  if not "genome" in csv_path:
    print("You must provide a genomes.txt file for this function! Exiting...")
    quit()
  value_dict={}  
  with open( csv_path  ) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      size=0  
      if int(row["seed"]) == SEED:
        for header in row.keys():
          if not header == None:
            
            if "bias" in header:
              if int(header[-1]) > size:
                size = int(header[-1])
            
            if "timConst" in header:
              x = float( row[header] )
              value_dict[ header ] = mapSearchParameter(x, 0.5, 10 )
            elif "recep" in header:
              x = float( row[header] )
              value_dict[ header ] = mapSearchParameter(x, 1, 1 )
            elif "bias" in header:
              x = float( row[header] )
              value_dict[ header ] = mapSearchParameter(x, -16, 16 )
            elif "w_AS" in header:
              x = float( row[header] )
              value_dict[ header ] = mapSearchParameter(x, -16, 16 )
            elif "w_" in header:
              x = float( row[header] )
              value_dict[ header ] = mapSearchParameter(x, -16, 16 )
            else:
              print("header not interpretted")
            
            if header in value_dict:
              print("{}:  {}".format(header, value_dict[header] ))
        
        #print("printing and exitting")
        #quit()
        return value_dict, size
  



#ported from Randy Beer's  TSearch.h class
def clip(x, min, max):
  temp = x if (x > min) else min
  return temp if (temp < max) else max

#map genome to phenotype
def mapSearchParameter(x, min, max, clipmin = -10000, clipmax = 10000 ):
  m = (max - min)/(MaxSearchValue - MinSearchValue)
  b = min - m * MinSearchValue
  return clip(m * x + b, clipmin, clipmax)

#reverse from phenotype to genome
def inverseMapSearchParameter( x, min, max):
  m = (MaxSearchValue - MinSearchValue)/(max - min)
  b = MinSearchValue - m * min
  return m * x + b;



def main( MODULATION ):
  
  if MODULATION != 0.0:
    CSV_OUTPUT_PATH=re.sub("phenotypes.txt","seed_{}_ssio_mod_{}.csv".format( SEED, MODULATION ) , PHENOTYPE_CSV_PATH )
    SSIO_PLOT_OUTPUT=re.sub("/DATA/","/PLOTS/", PHENOTYPE_CSV_PATH )
    
    PNG_OUTPUT_DIR=re.sub("phenotypes.txt","SSIO/" , SSIO_PLOT_OUTPUT)
    SSIO_PLOT_OUTPUT=re.sub("phenotypes.txt","SSIO/seed_{}_ssio_mod_{}.png".format(SEED, MODULATION), SSIO_PLOT_OUTPUT)
  else:
    CSV_OUTPUT_PATH=re.sub("phenotypes.txt","seed_{}_ssio.csv".format( SEED ) , PHENOTYPE_CSV_PATH )
    SSIO_PLOT_OUTPUT=re.sub("/DATA/","/PLOTS/",PHENOTYPE_CSV_PATH)
    PNG_OUTPUT_DIR=re.sub("phenotypes.txt","SSIO/" , SSIO_PLOT_OUTPUT)
    SSIO_PLOT_OUTPUT=re.sub("phenotypes.txt","SSIO/seed_{}_ssio.png".format( SEED ), SSIO_PLOT_OUTPUT)
  
  if OUTPUT_PATH != "":
    os.system("mkdir -p {}/SSIO/".format(OUTPUT_PATH) )
    if MODULATION == 0.0:
      SSIO_PLOT_OUTPUT="{}/SSIO/seed_{}_ssio.png".format(OUTPUT_PATH, SEED )
    else:
      SSIO_PLOT_OUTPUT="{}/SSIO/seed_{}_ssio_mod_{}.png".format(OUTPUT_PATH, SEED, MODULATION )
  
  print("running with modulation: {}".format(MODULATION) )
  
  #PHENOTYPE_CSV_PATH
  #GENOME_TYPE_PATH
  
  vd ={}
  vd, size = get_phenotype_from_genotype_dictionary( GENOME_TYPE_PATH, SEED )

  constant_input_levels=[]
  starting_states=[]

  for i in range( int(CONSTANT_INPUT_EXTREMA[0]*CONSTANT_INPUT_LEVELS_PER_UNIT),int(( CONSTANT_INPUT_EXTREMA[1]*CONSTANT_INPUT_LEVELS_PER_UNIT+1)) ):
    constant_input_levels.append( i/(CONSTANT_INPUT_LEVELS_PER_UNIT) )
  
  for i in range( int(STARTING_ACTIVATION_EXTREMA[0]*LEVELS_CURRENT_ACTIVATION),int(( STARTING_ACTIVATION_EXTREMA[1]*LEVELS_CURRENT_ACTIVATION+1)) ):
    starting_states.append( i/(LEVELS_CURRENT_ACTIVATION) )
    
  

  state_i=1  #9.88 drops to 0.001
  
  state_i=0.0
  
  value_dict={}
  value_dict, size = get_phenotype_dictionary( PHENOTYPE_CSV_PATH, SEED )
  
  
  for key in vd.keys():
    print("key: {}   from_genome.txt: {}  from phenotype.txt: {}".format( key, vd[key], value_dict[key] ) )
  
  
  #quit()
  
  
  for i in range(1, size+1):
    neuron_ssio=i
  #do all the stuff and generate plots
    if i ==1:
      name="FT"
    elif i ==2:
      name="BS"
    elif i ==3:
      name="FS"
    else:
      name="INT{}".format( i-3 )
    
    w_ii = float( value_dict["w_{0}->{0}".format(i) ] )
    bias_i = float( value_dict["bias{}".format(i) ] )
    time_constant = float( value_dict["timConst{}".format(i) ] )
    
    #FROM PAPER  BEST CPG3
    #BS neuron
    #w_ii, bias_i, time_constant = 15.546387, -9.573342, 7.277699
    #FS neuron NOT folded NOT the parameters for the best FS switch neuron
    #w_ii, bias_i, time_constant = 1.562798, 12.322079, 2.304232
    #FT neuron 
    #w_ii, bias_i, time_constant = 6.167, -7.015, 2.926
    #O_1
    #w_ii, bias_i, time_constant = 2, -2, 1
    #O_2
    #w_ii, bias_i, time_constant = 6, -2.5, 1
    #w_ii=15.546
    #w_ii=3.54
    
    modulation_level=MODULATION
    
    w_ii = w_ii * (1 + modulation_level )
    
    #bias_i=-9.573
    external_input=0
    stepsize=0.1
    #time_constant=7.277
    steps =STEPS
    stepsize=STEPSIZE
    
    
    #external_input=float(sys.argv[1])
    
    #x=calculate_next_activation(5, 10, 4, 0, 0.1, 4.2, 1000  )
    x=calculate_equilibrium_state(state_i, w_ii, bias_i, external_input, stepsize, time_constant, steps  )
    #y=find_equilibrium_sequences( state_i, w_ii, bias_i, external_input, stepsize, time_constant, steps  )
    
    
    if DEBUG == 5:
      pts = find_equilibrium_points(external_input, starting_states, w_ii, bias_i, time_constant, stepsize )
      print(x)
      quit()
      #print( x[-1] -x[-2] )
      print(pts)  
      quit()
    
    equilibrium_plot_data={}
    equilibrium_seq_plot_data={}
    
    count=0
    for external_input_level in constant_input_levels:
      if DEBUG>=0:
        count+=1
        if count %10==0:
          print( "equilibrium points percent done: {}%".format( round( count / len(constant_input_levels) * 100 , 3) ) )
      #EQ POINTS
      eqs=find_equilibrium_points(external_input_level , starting_states, w_ii, bias_i, time_constant, stepsize )
      equilibrium_plot_data[external_input_level] = eqs
    #######################################
    # CALCULATE TRAJECTORIES FOR VECTOR
    #######################################
    if SHOW_VECTOR:
      constant_input_levels=[]
      starting_states=[]
      for j in range( int(CONSTANT_INPUT_EXTREMA[0]*CONSTANT_INPUT_LEVELS_PER_UNIT/VECTOR_FIELD_DIVIDER),int(( CONSTANT_INPUT_EXTREMA[1]*CONSTANT_INPUT_LEVELS_PER_UNIT+1)/VECTOR_FIELD_DIVIDER) ):
        constant_input_levels.append( j/(CONSTANT_INPUT_LEVELS_PER_UNIT/VECTOR_FIELD_DIVIDER) )
      for j in range( int(STARTING_ACTIVATION_EXTREMA[0]*LEVELS_CURRENT_ACTIVATION/VECTOR_FIELD_DIVIDER_2),int(( STARTING_ACTIVATION_EXTREMA[1]*LEVELS_CURRENT_ACTIVATION+1)/VECTOR_FIELD_DIVIDER_2) ):
        starting_states.append( j/(LEVELS_CURRENT_ACTIVATION/VECTOR_FIELD_DIVIDER_2) )
      for external_input_level in constant_input_levels:
        eq_seqs=find_equilibrium_sequences( external_input_level , starting_states, w_ii, bias_i, time_constant, stepsize )
        equilibrium_seq_plot_data[external_input_level] = eq_seqs
    
    #########################################  
    #  CALCULATE EQUILIBRIUM POINTS
    #########################################
    #Equilibrium points
    x_data_1=[]
    y_data_1=[]
    x_y_coordinates=[]
    #equilibrium points only
    for external_input_level in equilibrium_plot_data.keys():
      for eq in equilibrium_plot_data[external_input_level ]:
        if eq:
          x_y_coordinates.append( (external_input_level, eq) )
    x_y_coordinates.sort(key=lambda x:x[1]) 
    for x_y_pair in x_y_coordinates:
      x_data_1.append( x_y_pair[0] )
      y_data_1.append( x_y_pair[1] )
    #############################################
    
    #High res version
    #plt.figure(num=0, figsize=(18, 16), dpi=160)
    print( i )
    plt.figure( i )
    plt.xlim(CONSTANT_INPUT_EXTREMA[0], CONSTANT_INPUT_EXTREMA[1])
    plt.ylim(-0.1, 1.1)

    #############################################
    #  PLOT VECTOR FIELD
    ############################################
    if SHOW_VECTOR:
      for external_input_level in equilibrium_seq_plot_data.keys():
        for eq_seq in equilibrium_seq_plot_data[external_input_level ]:
          x_data=[]
          y_data=[]
          for point in eq_seq:
            x_data.append( external_input_level) 
            y_data.append( point )
          dx=x_data[-1]-x_data[0]
          dy=y_data[-1]-y_data[0]
          if not dy ==0:
            hw= (CONSTANT_INPUT_EXTREMA[1]-CONSTANT_INPUT_EXTREMA[0])/LEVELS_CURRENT_ACTIVATION / VECTOR_FIELD_DIVIDER_2
            hl=0.02
            arrow_size=0.5
            hw*= arrow_size
            hw*= arrow_size
            if dy > 0:
              plt.arrow( x_data[0], y_data[0], dx, dy,  head_width=hw, head_length=hl, color="red", alpha=0.5, length_includes_head=True)
            else:
              plt.arrow( x_data[0], y_data[0], dx, dy,  head_width=hw, head_length=hl, color="blue", alpha=0.5, length_includes_head=True)
      
    #####################################
    # Plot the equilibrium points as a line
    #####################################
    plt.plot( x_data_1, y_data_1, color="black", linewidth=2.0, alpha=ALPHA)  #, alpha=1.0, s=10**2)  #, size=0.5) # label=seed)
    
    plt.ylabel('Output of {}'.format(name) )
    plt.xlabel('Current Input')

    plt.title( 'Steady State Input Output Flow')
    #plt.savefig(experiment_title + "_normalized.png" ) 
    #os.system( "mkdir -p {}/{}/{}".format( PLOTS, experiment_title, job_title ) )
    #plt.savefig( "{}/{}/{}/{}_normalized.png".format( PLOTS, experiment_title, job_title, robust_label) )
    
    #make sure directory exists
    os.system("mkdir -p {}".format(PNG_OUTPUT_DIR) )
    
    
    save_file= re.sub( "_ssio","_ssio_n{}".format(neuron_ssio), SSIO_PLOT_OUTPUT )
    
    plt.savefig( save_file )
    
    ################
    # write all SSIO data to csv file for later plotting overlay
    ###############
    
    save_file= re.sub( "_ssio","_ssio_n{}".format(neuron_ssio), CSV_OUTPUT_PATH )
    
    fh = open( save_file, "w")
    fh.write("x,y,\n")
    for i in range(0, len( x_data_1) ):
      fh.write("{},{},\n".format(x_data_1[i], y_data_1[i] ) )
    fh.close()
    
    #if MODULATION != 0.0:
    #  plt.savefig( "mod_{}_SEED-{}_{}_SSIO.png".format(MODULATION, SEED,name) )
    #else:
    #  plt.savefig( "SEED-{}_{}_SSIO.png".format(SEED,name) )
    

def logit(p):
  if p==1 :
    return 50
  if p==0:
    return -50
  return np.log(p) - np.log(1 - p)
  


def find_unstable_equilibrium_point(constant_input_level, low_activation_level, high_activation_level, fine_tuning_steps, self_weight, bias, time_constant, stepsize ):
  
  prev_level=-1
  prev_direction=0
  
  for i in range(0, fine_tuning_steps):
    
    activation_level = low_activation_level + i*( high_activation_level- low_activation_level)/fine_tuning_steps

    #print( "low:{}   high:{}  i:{} actLvl: {}".format( low_activation_level, high_activation_level, i, activation_level))

    
    #get state and direction
    new_eq, direction = calculate_equilibrium_state(activation_level, self_weight, bias, constant_input_level, stepsize, time_constant, STEPS, False )
    ####################################
    if new_eq:
      return new_eq
      
    #if we did not find an equilibria but the direction of our trajectory changed, we found an unstable equilibrium point
    if not new_eq and  (prev_direction * direction) < 0:
      new_eq = (sigmoid( 1 * (activation_level + bias)     ) + prevOutput  )/2
      return new_eq
    
    prev_direction=direction
    prev_output=sigmoid( 1 * (activation_level + bias))
  
    
    #####################################
    prev_level=activation_level
    
  return prev_output

def find_equilibrium_points(constant_input_level, starting_activation_levels, self_weight, bias, time_constant, stepsize ):
  #contain the set of all equilibrium points found
  equilibrium_states=[]
  
  prev_direction=0
  prevEq=0
  #we need to go through all the potential starting states to see where the equilibrium points are found
  for activation_level in starting_activation_levels:
    
    new_eq, direction = calculate_equilibrium_state(activation_level, self_weight, bias, constant_input_level, stepsize, time_constant, STEPS, False )
    #print("input:{}   act: {}     direction: {}".format(constant_input_level, activation_level, direction ))
    add=True
    
    #if we did not find an equilibria but the direction of our trajectory changed, we found an unstable equilibrium point
    if not new_eq and (prev_direction * direction) < 0:
      #print( "new_eq:{}   prev_dir:{}   dir:{}".format( new_eq, prev_direction, direction))
      new_eq = find_unstable_equilibrium_point(constant_input_level, prev_activation, activation_level, 100, self_weight, bias, time_constant, stepsize )
      #print( new_eq )
      #quit()
    
    for eq in equilibrium_states:
      if not eq:
        #print( "eq empty")
        x=5
      elif not new_eq:
        add=False
        
      #if we find an equlibrium point already included, set add to false
      elif abs( eq - new_eq ) <= EQ_THRESHOLD*10:
        add=False
    
    GAIN=1
    
    #if there is not already the eq point, then add it
    if add:
      equilibrium_states.append( new_eq )
  
    prev_direction=direction
    prev_activation=activation_level
  
  #quit()
  
  return equilibrium_states
  
  
def find_equilibrium_sequences(constant_input_level, starting_activation_levels, self_weight, bias, time_constant, stepsize ):
  #contain the set of all equilibrium points found
  equilibrium_sequences=[]
  
  #we need to go through all the potential starting states to see where the equilibrium points are found
  for activation_level in starting_activation_levels:
    
    #print( activation_level )
    new_eq_seq, direction=calculate_equilibrium_state(activation_level, self_weight, bias, constant_input_level, stepsize, time_constant, VECTOR_STEPS, True )
    add=True
    
    for eq_seq in equilibrium_sequences:
      #if we find an equlibrium point already included, set add to false
      #
      if not eq_seq or not new_eq_seq:
        add=False
      elif abs( eq_seq[-1] - new_eq_seq[-1] ) <= EQ_THRESHOLD*10:
        add=False
    
    #if there is not already the eq point, then add it
    if add:
      equilibrium_sequences.append( new_eq_seq )
  
  return equilibrium_sequences
  
  
  

# Integrate a circuit one step using Euler integration.
def eulerStep(stepsize, external_input, weight, bias, time_constant, state, output):
  gain=1

  if output != sigmoid( gain * ( state + bias) ):
    print("output does not match!")
    quit()
  #output = sigmoid( gain * ( state + bias) )
  
  # Update the state of all neurons.
  #for (int i = 1; i <= size; i++) {
  input = external_input
  #for (int j = 1; j <= size; j++)
  input += weight * output

  Rtaus=(1/time_constant)
  #Rtaus=time_constant

  state += stepsize * Rtaus * (input - state)

  #Update the outputs of all neurons.
  #for (int i = 1; i <= size; i++)
  output = sigmoid(   gain * (state + bias)   )

  return state, output


  

  

def calculate_equilibrium_state(state_i, w_ii, bias_i, external_input, stepsize, time_constant, steps, SEQ_MODE=True  ):
  
  
  prev_state=state_i
  
  GAIN=1
  
  output = sigmoid( GAIN * (state_i + bias_i)     )
  
  #record first  output for comparison
  startingState=output
  
  #store all data points leading up to is
  if SEQ_MODE:
    seq=[]
    if ROUND > 0:
      #seq.append( round( sigmoid( state_i), ROUND) )   
      seq.append( round(output, ROUND) )
    else:
      #seq.append( sigmoid( state_i) )
      seq.append( output )
  
  
  
  for t in range(0, steps):
    #OUTPUT ALREADY SET ABOVE
    #       external input  +  self-loop activation
    #input = external_input  +  w_ii * output   # sigmoid( GAIN*  (state_i + bias_i )   )
    #state_i += (stepsize / time_constant) * (input - state_i )
    #output = sigmoid( GAIN * (state_i+bias_i)       )

    state_i, output = eulerStep(stepsize, external_input, w_ii, bias_i, time_constant, state_i, output )

    direction = startingState-output
    
    if SEQ_MODE:
      if ROUND > 0:
        #seq.append( round( sigmoid( state_i), ROUND) )   
        seq.append( round( output, ROUND) )
      else:
        seq.append( output )
    
    stuck_low=  sigmoid( state_i + bias_i ) < OUTPUT_THRESHOLD and (state_i - prev_state) < 0
    
    stuck_high= sigmoid( state_i + bias_i ) > ( 1 - OUTPUT_THRESHOLD) and (state_i - prev_state) > 0
    
    stuck_stable=abs( state_i - prev_state ) <= EQ_THRESHOLD
    
    if stuck_low or stuck_high or stuck_stable:
    
      if DEBUG > 1:
        print("Found equilibrium point after {} steps, state: {}    output:{}".format(t, state_i,  sigmoid(state_i) ) )
        
      if SEQ_MODE:
        return seq, direction
      else:
        if ROUND > 0:
          #return round( sigmoid( state_i ), ROUND)
          return round(output, ROUND), direction
        else:
          #return sigmoid( state_i )
          return output, direction
    
    #print( "state: {}      output:{}".format( state_i, (sigmoid(state_i + bias_i ) ) ))
    
    prev_state=state_i
  if DEBUG > 0:
    print("Did NOT find equilibrium state for {} in {} steps".format(external_input, steps) )

  
  if SEQ_MODE:
    return seq, direction
  else:
    return None, direction
  ######################
  
def sigmoid( x ):
  #      1 / (1 + E^(-x) )
  return 1 / (1 + E ** (-x) )

if MODULATION_LEVELS:
  for m in MODULATION_LEVELS.split():
    main( float(m) )
else:
  main( MODULATION )

