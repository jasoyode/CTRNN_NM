import configparser
import re
import os
import sys
import csv
import glob
import numpy as np
import operator
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LinearSegmentedColormap
from sklearn.decomposition import PCA as sklearnPCA
from sklearn.preprocessing import StandardScaler
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.collections import LineCollection

from scipy.interpolate import spline

PI=3.141592653589

#headless mode
mpl.use('Agg')
import matplotlib.pyplot as plt

#location for DATA from experiments and PLOTS
DATA="../../DATA"
PLOTS="../../PLOTS"


#plots of sensitivity for a single network
def plot_fitness_landscape_single_plot( mutation_directory_path, alternate_output="",SEED="" ) :
 
 BEST_PERF=0.628

 #glob the files with "none" in their filename
 #record all the data into one large dict
 # parameter_fitness_map={}
 # parameter_fitness_map[header]=[x,y,z]
 #plot each column of the dict
 
 parameter_fitness_map={}
 
 len_xaxis,len_yaxis = 5.,5. #fix here your numbers
 xspace, yspace = .85, .85 # change the size of the void border here.
 x_fig,y_fig = len_xaxis / xspace, len_yaxis / yspace
 figure =  plt.figure(figsize=(x_fig,y_fig))
 plt.subplots_adjust(left=1-xspace, right = xspace, top=yspace, bottom = 1-yspace)

 y_tick_dict_num=[]
 y_tick_dict_label=[]
 
 parameter_files = glob.glob(  '{}/seed_{}*none*.csv'.format( mutation_directory_path, SEED  ) )
 inc_x=-1
 for parameter_file in sorted(parameter_files):
  inc_x=inc_x+1
  
  
  with open( parameter_file  ) as csvfile:
   param_text = re.sub(r'.*/','', parameter_file )
   param_text= re.sub(r'.*_X-','', param_text )
   param_text= re.sub(r'_Y.*','', param_text )

   y_tick_dict_num.append(inc_x-1)
   y_tick_dict_label.append(param_text)

   parameter_fitness_map[ param_text ] = {}
   
   parameter_fitness_map[ param_text ]['X'] = []   #[1,1,1]
   parameter_fitness_map[ param_text ]['Y'] = []   #[1,2,3]
   parameter_fitness_map[ param_text ]['Z'] = []   #[0,0.5,1.0]
   parameter_fitness_map[ param_text ]['C'] = []

   mutation_fitness_reader = csv.DictReader( csvfile )
   X       = parameter_fitness_map[ param_text ]['X']
   Y       = parameter_fitness_map[ param_text ]['Y']
   Z       = parameter_fitness_map[ param_text ]['Z']
   colors  = parameter_fitness_map[ param_text ]['C']
   
   #print("parameter_file:{}".format( parameter_file ))
   
   for row in mutation_fitness_reader:
    #print("row: "+ str(row.keys() ))
    X.append(   float( row['param1'] ) )
    Y.append(  inc_x+ float( row['param2'] ) )
    Z.append(  float( row['fitness'] ) )
      
    norm_fit = float(row['fitness']) / BEST_PERF
    if norm_fit < 0:
     norm_fit=0
    colors.append( [ norm_fit, norm_fit, norm_fit, 0.5] )

#####end of loop through parameter file
   #errors out of bounds?
   #print ( X )
   #print( colors )
   if len( colors) >0:
    colors[-1] = [1.0,0,0, 1.0] 

   plt.scatter( X,Y, s=5,c=colors )
 
 plt.yticks(y_tick_dict_num, y_tick_dict_label )    # rotation='vertical')

#####end of for loop through ALL parameter files 
 #plt.xlabel(xlabel)
 #plt.ylabel(ylabel)
 #title = re.sub(r'.*/','', mutation_file_path )
 #plt.title( title )
 
 
 #print("exp dir: {}".format( experiment_directory ))
 #plot_path = re.sub( "/mutations/.*seed[^\\/]*.csv", "/", experiment_directory )
 #plot_path = re.sub( DATA, "{}/MUTATIONS/".format(PLOTS), plot_path )
 
 if alternate_output!="":
  plot_path="{}/PARAMETER_SPACE/".format(alternate_output)
  
 os.system( "mkdir -p {}".format( plot_path ) )
 
 savefile = "{}_parameter_sensitivity_analysis.png".format( SEED )
 plt.savefig( "{}/{}".format(plot_path, savefile ) )
 plt.close()


#plotting sensitivity of every network on a particular parameer
def plot_fitness_landscape_single_param( mutation_directory_path, alternate_output="",PARAM="" ) :
 
 
 BEST_PERF=0.628

 #glob the files with "none" in their filename
 #record all the data into one large dict
 # parameter_fitness_map={}
 # parameter_fitness_map[header]=[x,y,z]
 #plot each column of the dict
 
 parameter_fitness_map={}
 
 len_xaxis,len_yaxis = 5.,5. #fix here your numbers
 xspace, yspace = .85, .85 # change the size of the void border here.
 x_fig,y_fig = len_xaxis / xspace, len_yaxis / yspace
 figure =  plt.figure(figsize=(x_fig,y_fig))
 plt.subplots_adjust(left=1-xspace, right = xspace, top=yspace, bottom = 1-yspace)

 y_tick_dict_num=[]
 y_tick_dict_label=[]
 
 parameter_files = glob.glob(  '{}/seed_*{}*none*.csv'.format( mutation_directory_path, PARAM  ) )
 inc_x=-1
 for parameter_file in sorted(parameter_files):
  inc_x=inc_x+1
  
  
  with open( parameter_file  ) as csvfile:
   seed_text = re.sub(r'.*/seed_','', parameter_file )
   seed_text= re.sub(r'_.*','', seed_text )

   y_tick_dict_num.append(inc_x-1)
   y_tick_dict_label.append(seed_text)
   param_text = seed_text
   
   parameter_fitness_map[ param_text ] = {}
   
   parameter_fitness_map[ param_text ]['X'] = []   #[1,1,1]
   parameter_fitness_map[ param_text ]['Y'] = []   #[1,2,3]
   parameter_fitness_map[ param_text ]['Z'] = []   #[0,0.5,1.0]
   parameter_fitness_map[ param_text ]['C'] = []

   mutation_fitness_reader = csv.DictReader( csvfile )
   X       = parameter_fitness_map[ param_text ]['X']
   Y       = parameter_fitness_map[ param_text ]['Y']
   Z       = parameter_fitness_map[ param_text ]['Z']
   colors  = parameter_fitness_map[ param_text ]['C']
   
   #print("parameter_file:{}".format( parameter_file ))
   
   for row in mutation_fitness_reader:
    #print("row: "+ str(row.keys() ))
    X.append(   float( row['param1'] ) )
    Y.append(  inc_x+ float( row['param2'] ) )
    Z.append(  float( row['fitness'] ) )
      
    norm_fit = float(row['fitness']) / BEST_PERF
    if norm_fit < 0:
     norm_fit=0
    colors.append( [ norm_fit, norm_fit, norm_fit, 0.5] )

#####end of loop through parameter file
   #errors out of bounds?
   #print ( X )
   #print( colors )
   if len( colors) >0:
    colors[-1] = [1.0,0,0, 1.0] 

   plt.scatter( X,Y, s=5,c=colors )
 
 plt.yticks(y_tick_dict_num, y_tick_dict_label )    # rotation='vertical')

#####end of for loop through ALL parameter files 
 #plt.xlabel(xlabel)
 #plt.ylabel(ylabel)
 #title = re.sub(r'.*/','', mutation_file_path )
 #plt.title( title )
 
 
 #print("exp dir: {}".format( experiment_directory ))
 #plot_path = re.sub( "/mutations/.*seed[^\\/]*.csv", "/", experiment_directory )
 #plot_path = re.sub( DATA, "{}/MUTATIONS/".format(PLOTS), plot_path )
 
 if alternate_output!="":
  plot_path="{}/PARAMETER_SPACE/".format(alternate_output)
  
 os.system( "mkdir -p {}".format( plot_path ) )
 
 savefile = "{}_parameter_sensitivity_analysis.png".format( PARAM )
 plt.savefig( "{}/{}".format(plot_path, savefile ) )
 plt.close()





     #ax.set_title(title, fontsize=fontsize)



#hardcoded to produce single sensitivity plot for now
#plot_fitness_landscape_single_plot("/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/mutations", alternate_output="/scratch/jasoyode/github_jasoyode/CTRNN_NM/PLOTS/SINGLE_SEED_ANALYSIS/RPG3_MOD_99/PARAMETER_SPACE" )

params=["bias1","bias2","bias3","w_AS-to-1","w_AS-to-2","w_AS-to-3"]

for param in params:
 plot_fitness_landscape_single_param("/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON/mutations", alternate_output="/scratch/jasoyode/github_jasoyode/CTRNN_NM/PLOTS/PARAMETER_SPACE/RPG_MOD", PARAM=param )
 plot_fitness_landscape_single_param("/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard/mutations", alternate_output="/scratch/jasoyode/github_jasoyode/CTRNN_NM/PLOTS/PARAMETER_SPACE/RPG_STD", PARAM=param )
