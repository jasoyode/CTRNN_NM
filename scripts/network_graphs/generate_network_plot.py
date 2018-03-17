#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Read phenotype from csv file and create visual representation of the network.

"""
#    Copyright (C) 2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Manos Renieris, http://www.cs.brown.edu/~er/
#    Distributed with BSD license.     
#    All rights reserved, see LICENSE for details.

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

__author__ = """Jason Yoder (jasoyode@indiana.edu)"""
import re
import sys
import pygraphviz as pgv
import math
import os
import os.path
import csv
import math
import numpy as np
import configparser

PI=3.141592653
ROUND=3


if len(sys.argv) <= 1:
  CONFIG_FILE="config.ini"
else:
  CONFIG_FILE=sys.argv[1]
    

def main( config_file ):

  config = configparser.ConfigParser()

  config.read(config_file )

  ROUND                = int( config["ALL"]["rounding_digits"] )
  MINLEN               = int( config["ALL"]["edge_length"] )
  include_angle_sensors= "True" ==  config["ALL"]["include_angle_sensors"] 
  
  
  
  all_details          = "True" ==  config["ALL"]["all_details"]
  plotting_mode        =  config["ALL"]["plotting_mode"] 
  #######
  STARTING_SEED        = int( config["ALL"]["seed_start"] )
  STOPPING_SEED        = int( config["ALL"]["seed_stop"] )
  
  #SUBFOLDER = config["ALL"]["InputOutput"][""]
  csv_path           = config["ALL"]["seed_phenotype_txt"]
  SAVE_PATH          = config["ALL"]["output_dir"]
  CUSTOM_NAME        = config["ALL"]["custom_output_name"]
  DYNAMIC_MODULE_CSV = config["ALL"]["dynamic_modules_csv"]
  PLOT_DYNAMIC_MODULES= config["ALL"]["plot_dynamic_modules"]


  if plotting_mode=="simple":
    imitate_beer=True
    all_details=False
  elif plotting_mode=="both":
    imitate_beer=True
    all_details=True
  elif plotting_mode=="detail":
    imitate_beer=False
    all_details=True
  else:
    print("Invalid plotting mode specified, must be simple, detail, or both")
    quit()
  
  

  for SEED in range(STARTING_SEED,STOPPING_SEED+1):

    CUSTOM_SEED_NAME = re.sub( r'XSEEDX', str(SEED), CUSTOM_NAME)

    if PLOT_DYNAMIC_MODULES:
      os.system("mkdir -p {}/DM/".format(SAVE_PATH) )
      OUTPUT_FILENAME="{}/DM/{}".format(SAVE_PATH, CUSTOM_SEED_NAME)
      generate_dynamic_module_graphs( csv_path, include_angle_sensors, SEED, CUSTOM_SEED_NAME, OUTPUT_FILENAME, MINLEN, PLOT_DYNAMIC_MODULES, DYNAMIC_MODULE_CSV )    

    #quit()
       
    if imitate_beer:
      OUTPUT_FILENAME="{}/simple_{}".format(SAVE_PATH, CUSTOM_SEED_NAME)
      generate_graph( csv_path, include_angle_sensors, False, True, SEED, CUSTOM_SEED_NAME, OUTPUT_FILENAME, MINLEN)
    if all_details:
      OUTPUT_FILENAME="{}/{}".format(SAVE_PATH, CUSTOM_SEED_NAME)
      generate_graph( csv_path, include_angle_sensors, True, False, SEED, CUSTOM_SEED_NAME, OUTPUT_FILENAME, MINLEN )      
    

def is_bistable( left, right):
  return left < 0 and right > 0

def ln( x  ):
  return math.log(x, math.e)

def sqrt(x):
  return math.sqrt(x)

def calculate_edges(  w, b ):
  if w < 4:
    return -99,-99
  #print( "w: " + str(w) + " b:" + str(b))
  # equation (3a) from Evolution and analysis of model CPGs for walking: I. Dynamical modules
  I_L = 2 * ln(   (sqrt(w) + sqrt(w -4) )/2 ) - (w + sqrt( w * (w - 4)))/2 - b
  #print( "I_L " +str(I_L ) )
  # equation (3b) from Evolution and analysis of model CPGs for walking: I. Dynamical modules
  I_R = -2 * ln(    ( sqrt(w) + sqrt( w -4))/2 ) - (w - sqrt( w * ( w - 4)))/2 - b
  #print( "I_R " +str(I_L ) )
  return I_L, I_R


def generate_dynamic_module_graphs( csv_path, include_angle_sensors, SEED, CUSTOM_SEED_NAME, OUTPUT_FILENAME, MINLEN, PLOT_DYNAMIC_MODULES, DYNAMIC_MODULE_CSV ):
  if PLOT_DYNAMIC_MODULES:
    print( "Attempting to represent DM for seed {} in {}".format(SEED, DYNAMIC_MODULE_CSV) )
    
    with open( DYNAMIC_MODULE_CSV  ) as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        size=0
        if int(row["seed"]) == SEED:
          dm = row["dm"]
          dm = re.sub("{","", dm)
          dm = re.sub("}","", dm)
          dm_list=dm.split("=>")
          #print( dm_list )
          break

    index=1
    for dm in dm_list:
      if not dm == "":
        #print(dm)
        DM_VALS={}
        for neuron in dm.split(" "):
          #print( neuron )
          DM_VALS[ neuron[:2] ]= neuron[2]
        OUTPUT_F = re.sub(".png","{}.png".format(index), OUTPUT_FILENAME)
        generate_graph( csv_path, include_angle_sensors, False, True, SEED, CUSTOM_SEED_NAME, OUTPUT_F, MINLEN, DM_VALS, "{} {}".format(index, dm) )
        index+=1
    

#returns a dictionary of the parameters and values
def get_phenotype_from_genotype_dictionary( csv_path, SEED ):
  if not "genome" in csv_path:
    print("You must provide a genomes.txt file for this function! Exiting...")
    print( csv_path )
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




def generate_graph( csv_path, include_angle_sensors, all_details, imitate_beer, SEED, CUSTOM_NAME, OUTPUT_FILENAME, MINLEN, DYNAMIC_MODULE_VALUES=[], DM_LABEL="" ):
  
  if len(DYNAMIC_MODULE_VALUES) == 0:
    PLOT_DYNAMIC_MODULES=False
  else:
    PLOT_DYNAMIC_MODULES=True
  #print( PLOT_DYNAMIC_MODULES )
  print( DYNAMIC_MODULE_VALUES )
  #return
  #quit()
  #######################################
  # INDENT ALL BELOW
  #######################################
  
  #CUSTOM_NAME = re.sub("XSEEDX", SEED, CUSTOM_NAME)
  if PLOT_DYNAMIC_MODULES:
    A=pgv.AGraph(  directed=True , overlap=False, splines='curved', labelloc="t",label="{}".format(  DM_LABEL )  )
  else:
    A=pgv.AGraph(  directed=True , overlap=False, splines='curved', labelloc="t",label="{}".format(CUSTOM_NAME )  )

  value_dict = {}


  if imitate_beer:
    all_details=False
    include_angle_sensors=False      
  
  if not os.path.isfile( csv_path ):
  #if phenotype does not exist, use genome and convert
    genome_path = re.sub("phenotypes.txt", "genomes.txt", csv_path)
    value_dict = get_phenotype_from_genotype_dictionary( genome_path, SEED )

  else:
    with open( csv_path  ) as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        size=0
        if int(row["seed"]) == SEED:
          for header in row.keys():
            #print(header)
            if not header == None and not header=="":
              #print( header )
              if not header == "seed":
                value_dict[ header ] =  round(  float( row[header] ), ROUND )
                
              if "bias" in header:
                if int(header[-1]) > size:
                  size = int(header[-1])
          break
  


  for i in range(1,size+1):
    STARTING_ANGLE=3*PI/2
    x=round( 100*math.cos( -(i-1)* 2*PI/size + STARTING_ANGLE  ), ROUND)
    y=round( 100*math.sin( -(i-1)* 2*PI/size + STARTING_ANGLE  ), ROUND)
    
    if i==1:
      name="FT"
    elif i==2:
      name="BS"
    elif i==3:
      name="FS"
    elif i==4:
      name="I1"
    elif i==5:
      name="I2"
    else:
      name="unknown"
    n=name
    
    if all_details:
      name="N{} ({})".format(i,name)
    
    if float( value_dict[ "w_{}->{}".format(i,i) ]) > 4:
      name="*\n"+name
    
    w=float( value_dict[ "w_{}->{}".format(i,i) ])
    b=float(value_dict["bias{}".format(i) ] )
    
    l,r = calculate_edges(w, b)
    
    if is_bistable( l, r):
      if all_details:
        stability="bi-stable @0"
      else:
        stability=""
    else:
      if b > 0:
        stability="+"
      elif b < 0:
        stability="-"
      else:
        stability="zero"
        
    if all_details:
      if l != -99:
        stability+="\nL:{} R:{}".format( round(l,1)  ,round(r, 1) )
      else:
        stability+="\nNO FOLD"
    #lbl="{}\nB:{}\nTC:{}\nRS: {}".format(name, value_dict["bias{}".format(i) ], value_dict["timConst{}".format(i) ], value_dict["recep{}".format(i) ]   )
    if all_details:
      lbl="{}\nB:{}\nTC:{}\n {}".format(name, value_dict["bias{}".format(i) ], value_dict["timConst{}".format(i) ], stability   )
    else:
      lbl="{}\n{}".format(name,stability)
    
    dm_font_size=20
    ON_thickness=3
    
    if PLOT_DYNAMIC_MODULES:
      radius=1
      if DYNAMIC_MODULE_VALUES[n]=="+":
        A.add_node(i,fontname="times bold", label=lbl,fontsize=dm_font_size,style="bold", fixedsize=True, width=radius, height=radius, shape='circle', color='black',pos='{},{}'.format(x,y), penwidth=ON_thickness )
      elif DYNAMIC_MODULE_VALUES[n]=="↑":
        A.add_node(i,fontname="times bold", label=lbl,fillcolor="gray",style="filled",fontsize=dm_font_size, fixedsize=True, width=radius, height=radius, shape='circle', color='black',pos='{},{}'.format(x,y) )
      elif DYNAMIC_MODULE_VALUES[n]=="↓":
        A.add_node(i,fontname="times bold", label=lbl,fillcolor="gray",style="bold,filled",fontsize=dm_font_size, fixedsize=True, width=radius, height=radius, shape='circle', color='black',pos='{},{}'.format(x,y), penwidth=ON_thickness )
      elif DYNAMIC_MODULE_VALUES[n]=="-":
        A.add_node(i,fontname="times bold", label=lbl,fontsize=dm_font_size, fixedsize=True, width=radius, height=radius, shape='circle', color='black',pos='{},{}'.format(x,y) )
      else:
        print("No state detected exiting")
        quit()
        
    else:
      if imitate_beer:
        radius=1
        A.add_node(i,fontname="times bold", label=lbl,fontsize=dm_font_size, fixedsize=True, width=radius, height=radius, shape='circle', color='black',pos='{},{}'.format(x,y) )
      else:
        radius=1.5
        A.add_node(i, label=lbl, fixedsize=True, width=radius, height=radius,shape='circle', color='black',pos='{},{}'.format(x,y) )

      if include_angle_sensors:
        if i ==1:
          A.add_node(99, label="Angle\nSensor", color='black',pos='{},{}'.format( 0,0 ) )
    
  
  
  for i in range(1,size+1):
    for j in range(1,size+1):
      #print("i:{} j:{}".format(i,j) )
      weight= value_dict[ "w_{}->{}".format(i,j) ]
      
      
      if PLOT_DYNAMIC_MODULES:
        if i==1:
          n="FT"
        elif i==2:
          n="BS"
        elif i==3:
          n="FS"
        elif i==4:
          n="I1"
        elif i==5:
          n="I2"
        else:
          n="unknown"
        
        if DYNAMIC_MODULE_VALUES[n] in "-↑":
          #must include to keep shape
          A.add_edge(i,j,len=MINLEN/2, arrowhead="tee", style="invis"  )
        elif i!=j:
          if weight > 0:
            A.add_edge(i,j,len=MINLEN/2, arrowhead="tee",  )
          elif weight <0:
            A.add_edge(i,j,len=MINLEN/2, arrowhead="dot" )
          else:
            print("weight is zero no showing!")
      
      else:
        
        if imitate_beer:
          h=100
          if i != j:
            if weight > 0:
              A.add_edge(i,j,len=MINLEN/2, arrowhead="tee",  )
            elif weight <0:
              A.add_edge(i,j,len=MINLEN/2, arrowhead="dot" )
            else:
              print("weight is zero no showing!")
        
        else:
        
          if weight > 0:
            lbl_weight="<<font color=\"red\">{}</font>>".format(weight)
            A.add_edge(i,j,len=MINLEN, arrowhead="tee", label=lbl_weight,color='red' )
          elif weight <0:
            lbl_weight="<<font color=\"blue\">{}</font>>".format(weight)
            A.add_edge(i,j,len=MINLEN, arrowhead="dot", label=lbl_weight,color='blue' )
          else:
            print("weight is zero no showing!")
          
          
          if include_angle_sensors:
            if (i==j):
              weight= value_dict[ "w_AS->{}".format(i) ]
            A.add_edge(99,i, len=MINLEN,label=weight,color='black' )
        
  A.graph_attr['epsilon']='0.001'
  A.write('simple.dot') # write to simple.dot
  B=pgv.AGraph('simple.dot') # create a new graph from file
  B.layout(prog='neato')
  if CUSTOM_NAME != "":
    B.draw(OUTPUT_FILENAME)
  else:
    B.draw(OUTPUT_FILENAME)  
  
main( CONFIG_FILE )