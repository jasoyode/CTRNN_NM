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


ROUND=0
E=2.71828
EQ_THRESHOLD=0.000001
EQ_THRESHOLD=0

STEPSIZE=0.1
self_loop_cutoff=4
STEPS=2500
VECTOR_STEPS=5

DEBUG=0




def main():

  CONSTANT_INPUT_LEVELS_PER_UNIT=2
  LEVELS_CURRENT_ACTIVATION=3

  EXTREMA=[-25,25]

  constant_input_levels=[]
  starting_states=[]

  for i in range( int(-25*CONSTANT_INPUT_LEVELS_PER_UNIT),int( 25*CONSTANT_INPUT_LEVELS_PER_UNIT+1) ):
    constant_input_levels.append( i/CONSTANT_INPUT_LEVELS_PER_UNIT )
  
  for i in range( int(EXTREMA[0]*LEVELS_CURRENT_ACTIVATION),int( EXTREMA[1]*LEVELS_CURRENT_ACTIVATION+1) ):
    starting_states.append( i/LEVELS_CURRENT_ACTIVATION )

  state_i=9.889  #9.88 drops to 0.001
  
  state_i=25
  
  w_ii=15.54
  #w_ii=3.54
  
  bias_i=-9.57
  external_input=-2
  stepsize=0.1
  time_constant=7.277
  steps =STEPS
  stepsize=STEPSIZE
  
  
  #external_input=float(sys.argv[1])
  
  #x=calculate_next_activation(5, 10, 4, 0, 0.1, 4.2, 1000  )
  x=calculate_equilibrium_state(state_i, w_ii, bias_i, external_input, stepsize, time_constant, steps  )
  #y=find_equilibrium_sequences( state_i, w_ii, bias_i, external_input, stepsize, time_constant, steps  )
  
  #pts = find_equilibrium_points(external_input, starting_states, w_ii, bias_i, time_constant, stepsize )
  if DEBUG == 5:
    print(x)
    quit()
  #print( x[-1] -x[-2] )
  #print(pts)  
  #quit()
  
  equilibrium_plot_data={}
  equilibrium_seq_plot_data={}
  
  count=0
  for external_input_level in constant_input_levels:
    if DEBUG>=0:
      count+=1
      print( "percent done: {}%".format( round( count / len(constant_input_levels) * 100 , 3) ) )
    #EQ POINTS
    eqs=find_equilibrium_points(external_input_level , starting_states, w_ii, bias_i, time_constant, stepsize )
    equilibrium_plot_data[external_input_level] = eqs

    #SEQUENCES
    eq_seqs=find_equilibrium_sequences( external_input_level , starting_states, w_ii, bias_i, time_constant, stepsize )
    equilibrium_seq_plot_data[external_input_level] = eq_seqs
    
  
  x_data_1=[]
  y_data_1=[]
  
  #euqilibrium points only
  for external_input_level in equilibrium_plot_data.keys():
    for eq in equilibrium_plot_data[external_input_level ]:
      x_data_1.append( logit(external_input_level) )
      y_data_1.append( eq )
  
  plt.figure(num=0, figsize=(18, 16), dpi=160)
  
  plt.xlim(-25, 25)
  plt.ylim(-0.1, 1.1)

  
  for external_input_level in equilibrium_seq_plot_data.keys():
    #print(external_input_level)
    for eq_seq in equilibrium_seq_plot_data[external_input_level ]:
      #x_data.append( external_input_level )
      #y_data.append( eq_seq )
      #
      x_data=[]
      y_data=[]
      
      #print( eq_seq )
      
      for point in eq_seq:
        x_data.append( logit(external_input_level) )
        y_data.append( point )
      
      #plt.plot( x_data[:-2], y_data[:-2], color="black", alpha=0.1) # label=seed)
      #plt.plot( x_data[-2:-1], y_data[-2:-1], color="red", alpha=1.0) # label=seed)
      
      dx=x_data[-1]-x_data[0]
      dy=y_data[-1]-y_data[0]
      
#      print("y_data[0]: {}".format( y_data[0] ))
  #    print("x_data[0]:{}   , y_data[0]:{}, dx:{}, dy:{} x_data[-1]:{}   y_data[-1]:{}".format( x_data[0], y_data[0], dx, dy, x_data[-1], y_data[-1]))
      
      if not dy ==0:
        plt.arrow( x_data[0], y_data[0], dx, dy,  head_width=0.5, head_length=0.02, color="black", alpha=0.25, length_includes_head=True)
      
      #plt.scatter( x_data[:-2], y_data[:-2], color="black", alpha=0.1) # label=seed)
      #plt.scatter( x_data[-2:-1], y_data[-2:-1], color="red", alpha=0.1) # label=seed)
      
      
  
  #
  plt.scatter( x_data_1, y_data_1, color="green", alpha=1.0, s=10**2)  #, size=0.5) # label=seed)

  plt.ylabel('Output')
  plt.xlabel('Input')

  plt.title( 'Steady State Input Output Flow')
  #plt.savefig(experiment_title + "_normalized.png" ) 
  #os.system( "mkdir -p {}/{}/{}".format( PLOTS, experiment_title, job_title ) )
  #plt.savefig( "{}/{}/{}/{}_normalized.png".format( PLOTS, experiment_title, job_title, robust_label) )
  plt.savefig( "demo.png")

  
  
  
  
  #print( equilibrium_plot_data_1 )
  

def logit(p):
  return p
#  if p==1 :
#    return 50
#  if p==0:
#    return -50
#    
#  return np.log(p) - np.log(1 - p)
  
  

def find_equilibrium_points(constant_input_level, starting_activation_levels, self_weight, bias, time_constant, stepsize ):
  #contain the set of all equilibrium points found
  equilibrium_states=[]
  
  #we need to go through all the potential starting states to see where the equilibrium points are found
  for activation_level in starting_activation_levels:
    
    #print( activation_level )
    new_eq=calculate_equilibrium_state(activation_level, self_weight, bias, constant_input_level, stepsize, time_constant, STEPS, False )
    add=True
    for eq in equilibrium_states:
      #if we find an equlibrium point already included, set add to false
      if abs( eq - new_eq ) <= EQ_THRESHOLD*10:
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
      if abs( eq_seq[-1] - new_eq_seq[-1] ) <= EQ_THRESHOLD*10:
        add=False
    
    #if there is not already the eq point, then add it
    if add:
      equilibrium_sequences.append( new_eq_seq )
  
  return equilibrium_sequences
  
  
  
  

def calculate_equilibrium_state(state_i, w_ii, bias_i, external_input, stepsize, time_constant, steps, SEQ_MODE=True  ):
  prev_state=-99

  #store all data points leading up to is
  if SEQ_MODE:
    seq=[]

  for t in range(0, steps):
    #       external input  +  self-loop activation
    input = external_input  +  w_ii * sigmoid(state_i + bias_i ) 
    
    state_i += (stepsize / time_constant) * (input - state_i )
    if SEQ_MODE:
      if ROUND > 0:
        seq.append( round( sigmoid( state_i), ROUND) )   
      else:
        seq.append( sigmoid( state_i) )
    
    #output = sigmoid( state_i + bias_i ) 
    #print( state_i )
    #print( sigmoid(state_i)  )
    #if abs( abs(state_i) - abs(prev_state) ) <= EQ_THRESHOLD:
    if abs( sigmoid(state_i) - sigmoid(prev_state) ) <= EQ_THRESHOLD:
      if DEBUG > 1:
        print("Found equilibrium point after {} steps, state: {}    output:{}".format(t, state_i,  sigmoid(state_i) ) )
        
      if SEQ_MODE:
        return seq
      else:
        if ROUND > 0:
          return round( sigmoid( state_i ), ROUND)
        else:
          return sigmoid( state_i )
    
    #print( "state: {}      output:{}".format( state_i, (sigmoid(state_i + bias_i ) ) ))
    prev_state=state_i
  if DEBUG > 0:
    print("Did NOT find equilibrium state for {} in {} steps".format(external_input, steps) )

  
  if SEQ_MODE:
    return seq
  else:
    return -1  #state_i
  ######################
  
def sigmoid( x ):
  #      1 / (1 + E^(-x) )
  return 1 / (1 + E ** (-x) )

main()