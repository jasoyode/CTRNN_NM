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
EQ_THRESHOLD=0.001
#EQ_THRESHOLD=0

STEPSIZE=0.1
self_loop_cutoff=4

STEPS=500
VECTOR_STEPS=1

DEBUG=0

SHOW_VECTOR=True

SEED=2

#PHENOTYPE_CSV_PATH="/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CITED_DATA/phenotypes.txt"
#GENOME_TYPE_PATH="/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CITED_DATA/genomes.txt"

PHENOTYPE_CSV_PATH="/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CITED_DATA/phenotypes.txt"
GENOME_TYPE_PATH="/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CITED_DATA/genomes.txt"


#x coordinates
CONSTANT_INPUT_LEVELS_PER_UNIT=10

#y coordinates
LEVELS_CURRENT_ACTIVATION=10

#fewer columns
VECTOR_FIELD_DIVIDER=4

#fewer rows
VECTOR_FIELD_DIVIDER_2=2

#range of starting activation levels
STARTING_ACTIVATION_EXTREMA=[-25,25]

#range of external inputs to test
CONSTANT_INPUT_EXTREMA=[-15,15]


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
          if not header == None:
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



def main():
  
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
    
    pts = find_equilibrium_points(external_input, starting_states, w_ii, bias_i, time_constant, stepsize )
    if DEBUG == 5:
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
    plt.plot( x_data_1, y_data_1, color="black", linewidth=4.0)  #, alpha=1.0, s=10**2)  #, size=0.5) # label=seed)
    
    plt.ylabel('Output of {}'.format(name) )
    plt.xlabel('Current Input')

    plt.title( 'Steady State Input Output Flow')
    #plt.savefig(experiment_title + "_normalized.png" ) 
    #os.system( "mkdir -p {}/{}/{}".format( PLOTS, experiment_title, job_title ) )
    #plt.savefig( "{}/{}/{}/{}_normalized.png".format( PLOTS, experiment_title, job_title, robust_label) )
    plt.savefig( "SEED-{}_{}_SSIO.png".format(SEED,name) )
  
  
  
  #print( equilibrium_plot_data_1 )
  

def logit(p):
#  return p
  if p==1 :
    return 50
  if p==0:
    return -50
    
  return np.log(p) - np.log(1 - p)
  
  

def find_equilibrium_points(constant_input_level, starting_activation_levels, self_weight, bias, time_constant, stepsize ):
  #contain the set of all equilibrium points found
  equilibrium_states=[]
  
  #we need to go through all the potential starting states to see where the equilibrium points are found
  for activation_level in starting_activation_levels:
    
    #print( activation_level )
    new_eq=calculate_equilibrium_state(activation_level, self_weight, bias, constant_input_level, stepsize, time_constant, STEPS, False )
    add=True
    for eq in equilibrium_states:
      
      if not eq or not new_eq:
        add=False
      #if we find an equlibrium point already included, set add to false
      elif abs( eq - new_eq ) <= EQ_THRESHOLD*10:
        add=False
    #if there is not already the eq point, then add it
    if add:
      equilibrium_states.append( new_eq )
  
  return equilibrium_states
  
  
def find_equilibrium_sequences(constant_input_level, starting_activation_levels, self_weight, bias, time_constant, stepsize ):
  #contain the set of all equilibrium points found
  equilibrium_sequences=[]
  
  #we need to go through all the potential starting states to see where the equilibrium points are found
  for activation_level in starting_activation_levels:
    
    #print( activation_level )
    new_eq_seq=calculate_equilibrium_state(activation_level, self_weight, bias, constant_input_level, stepsize, time_constant, VECTOR_STEPS, True )
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


    
    if SEQ_MODE:
      if ROUND > 0:
        #seq.append( round( sigmoid( state_i), ROUND) )   
        seq.append( round( output, ROUND) )
      else:
        seq.append( output )
    
    if abs( state_i - prev_state ) <= EQ_THRESHOLD:
      if DEBUG > 1:
        print("Found equilibrium point after {} steps, state: {}    output:{}".format(t, state_i,  sigmoid(state_i) ) )
        
      if SEQ_MODE:
        return seq
      else:
        if ROUND > 0:
          #return round( sigmoid( state_i ), ROUND)
          return round(output, ROUND)
        else:
          #return sigmoid( state_i )
          return output
    
    #print( "state: {}      output:{}".format( state_i, (sigmoid(state_i + bias_i ) ) ))
    
    prev_state=state_i
  if DEBUG > 0:
    print("Did NOT find equilibrium state for {} in {} steps".format(external_input, steps) )

  
  if SEQ_MODE:
    return seq
  else:
    return None
  ######################
  
def sigmoid( x ):
  #      1 / (1 + E^(-x) )
  return 1 / (1 + E ** (-x) )

main()
