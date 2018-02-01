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

STEPS=100
VECTOR_STEPS=5

DEBUG=0



def main():

  #FROM PAPER  
  #w_ii, bias_i, time_constant = 15.546387, -9.573342, 7.277699
  
  w_ii, bias_i, time_constant = 0, -5, 2
  
  starting_state=1
  external_input=0
  stepsize=0.1
  steps =STEPS
  stepsize=STEPSIZE
  
  
  starting_states = [-1,-0.5, 0, 0.5, 1] 
  time_constants = [ 0.1, 0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2 ]
  
  I_T_pairs = [  [-4,0.5] , [4,0.5],  [-4,1], [4,1], [-4,2], [4,2], ]  #[4,1], [-4,2], [4,2] ]                    ]
  
  
  #starting_states = [-1, 1]
  plt.figure(0) #num=0, figsize=(18, 16), dpi=160)
  
  plt.xlim(0, STEPS*STEPSIZE )
  plt.ylim(-1,1)
  for starting_state in starting_states:
    times, states, outputs =  get_trajectory( starting_state, w_ii, bias_i, external_input, stepsize, time_constant, steps  )
    #plt.plot(times, outputs )  # , color="green" )
    plt.plot(times, states, label="starting_state: {}".format(starting_state)  )
  
  plt.ylabel('State Information')
  plt.xlabel('Time')
  plt.title( 'Plotting State Over Time')
  legend = plt.legend(loc='lower right')
  plt.savefig( "ctrnn_starting_states-{}_w-{}_bias{}_ext-{}_timCon-{}.png".format(starting_state,w_ii,bias_i,external_input,time_constant)  )

  plt.figure(1) #num=0, figsize=(18, 16), dpi=160)
  
  plt.xlim(0, STEPS*STEPSIZE )
  plt.ylim(0,1)
  
  for time_constant in time_constants:
    times, states, outputs =  get_trajectory( 1, w_ii, bias_i, external_input, stepsize, time_constant, steps, 2  )
    plt.plot(times, states, label="timing_constant: {}".format(time_constant)  )
  
  plt.ylabel('State Information')
  plt.xlabel('Time')
  legend = plt.legend(loc='lower right')
  plt.title( 'Plotting Output Over Time')
  plt.savefig( "ctrnn_timing-{}_w-{}_bias{}_ext-{}_timCon-{}.png".format(starting_state,w_ii,bias_i,external_input,time_constant)  )


  plt.figure(2)
  plt.xlim(0, STEPS*STEPSIZE )
  plt.ylim(-4,4)
  
  for pair in I_T_pairs:
    times, states, outputs =  get_trajectory( 0, w_ii, bias_i, pair[0], stepsize, pair[1], steps, 2  )
    plt.plot(times, states, label="TC{} I{}".format(pair[0], pair[1] )  )
  
  plt.ylabel('State Information')
  plt.xlabel('Time')
  legend = plt.legend(loc='lower right')
  plt.title( 'Plotting Output Over Time')
  plt.savefig( "ctrnn_I_T_-{}_w-{}_bias{}_ext-{}_timCon-{}.png".format(starting_state,w_ii,bias_i,external_input,time_constant)  )







def get_trajectory( state_i, w_ii, bias_i, external_input, stepsize, time_constant, steps, turn_off_input=-1  ):
  prev_state=-99

  #x coordinate
  time=[]
  #y1 coordination
  state=[]
  #y2 coordinate
  output=[]
  
  
  for t in range(0, steps):
    #############RECORD STATE AT START OF TIMESTEP
    time.append( t * stepsize )
    state.append( state_i )
    output.append( sigmoid( state_i) )
    
    
    if turn_off_input != -1 and time[-1] >= turn_off_input:
      external_input = 0
      
    
    #############UPDATE STATE INFORMATION
    #       external input  +  self-loop activation
    input = external_input  +  w_ii * sigmoid(state_i + bias_i ) 
    state_i += (stepsize / time_constant) * (input - state_i )
    
    ##CHECK FOR EQUILIBRIA
    #if abs( abs(state_i) - abs(prev_state) ) <= EQ_THRESHOLD:
    if abs( sigmoid(state_i) - sigmoid(prev_state) ) <= EQ_THRESHOLD:
      print("Found equilibrium point after {} steps, state: {}    output:{}".format(t, state_i,  sigmoid(state_i) ) )
      return time, state, output  
    
    
  return time, state, output
  ######################
  
def sigmoid( x ):
  #      1 / (1 + E^(-x) )
  return 1 / (1 + E ** (-x) )

main()