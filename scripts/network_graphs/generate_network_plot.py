#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Read phenotype from file and create visual
representation of the network.

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

import sys
import pygraphviz as pgv
import math
import os
import csv
import math
import numpy as np

PI=3.141592653

ROUND=3

#K=0.3,strict=False,size=8
#pgv.AGraph(  directed=True ,splines='curved')


MINLEN=3

include_angle_sensors=True
all_details=True
imitate_beer=True

SEED=48
CRM="CPG"
SIZE="3"
TYPE="standard"
SUBFOLDER=""


if len(sys.argv) > 1:
  if len(sys.argv) > 1:
    SEED=int(sys.argv[1])
  if len(sys.argv) > 2:
    CRM=sys.argv[2]
  if len(sys.argv) > 3:
    SIZE=int(sys.argv[3])
  if len(sys.argv) > 4:
    TYPE=sys.argv[4]
  if len(sys.argv) > 5:
    SUBFOLDER=sys.argv[5]
  

print("Using SEED:{} CRM:{}  SIZE:{}  TYPE:{} SUBFOLDER:{}".format(SEED,CRM,SIZE,TYPE,SUBFOLDER) )



#CUSTOM_NAME="BEST_CPG3_"
CUSTOM_NAME=""

SAVE_PATH="/scratch/jasoyode/github_jasoyode/CTRNN_NM/PLOTS/NETWORK_GRAPHS/{}".format(SUBFOLDER)

csv_path="/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CPG_RPG_MPG_345/"
csv_path+="JOB_ctrnn-{}_size-{}_sim-100run-500gen_signal-SINE-1p_M-{}/phenotypes.txt".format(CRM,SIZE,TYPE)


#SEED=2
#csv_path="/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CITED_DATA/phenotypes.txt"

PRE_FIX=""
if imitate_beer:
  PRE_FIX="simple_"



if CUSTOM_NAME != "":
  OUTPUT_FILENAME='{}/{}{}.png'.format(SAVE_PATH,PRE_FIX,CUSTOM_NAME)
else:
  OUTPUT_FILENAME='{}/{}{}_{}_{}_{}.png'.format(SAVE_PATH,PRE_FIX,CRM,SIZE,TYPE,SEED) 



  

if CUSTOM_NAME != "":
  A=pgv.AGraph(  directed=True , overlap=False, splines='curved', labelloc="t",label="simple_{}.png".format(CUSTOM_NAME) )
else:
  A=pgv.AGraph(  directed=True , overlap=False, splines='curved', labelloc="t",label="{}_{}_{}_{}.png".format(CRM,SIZE,TYPE,SEED)  )

value_dict = {}



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


def main( csv_path, include_angle_sensors, all_details, imitate_beer ):
  if imitate_beer:
    all_details=False
    include_angle_sensors=False      

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
      name="INT1"
    elif i==5:
      name="INT2"
    else:
      name="unknown"
    
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
    
    if imitate_beer:
      radius=1
      #A.add_node(i,fontname="times bold", label=lbl,fontsize=14, fixedsize=True, width=radius, height=radius, shape='circle', color='black',pos='{},{}'.format(x,y) )
      A.add_node(i,fontname="times bold", label=lbl,fontsize=12, fixedsize=True, width=radius, height=radius, shape='circle', color='black',pos='{},{}'.format(x,y) )
    else:
      radius=1.5
      #A.add_node(i, label=lbl, shape='circle', color='black',pos='{},{}'.format(x,y) )
      A.add_node(i, label=lbl, fixedsize=True, width=radius, height=radius,shape='circle', color='black',pos='{},{}'.format(x,y) )
    
    if include_angle_sensors:
      if i ==1:
        A.add_node(99, label="Angle\nSensor", color='black',pos='{},{}'.format( 0,0 ) )
  
  
  
  for i in range(1,size+1):
    for j in range(1,size+1):
      #print("i:{} j:{}".format(i,j) )
      weight= value_dict[ "w_{}->{}".format(i,j) ]
      
      
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
  #print(A.string()) # print to screen
  #print("Wrote simple.dot")
  A.write('simple.dot') # write to simple.dot
  B=pgv.AGraph('simple.dot') # create a new graph from file
  #B.layout(prog='circo')
  B.layout(prog='neato')
  if CUSTOM_NAME != "":
    B.draw(OUTPUT_FILENAME)  #'{}/simple_{}_{}.png'.format(SAVE_PATH,CUSTOM_NAME,SUMMARY) ) # draw png
  else:
    B.draw(OUTPUT_FILENAME)  #'{}/simple_{}_{}_{}_{}_{}.png'.format(SAVE_PATH,CRM,SIZE,TYPE,SEED,SUMMARY) ) # draw png
  #print("Wrote simple.png")
  
main( csv_path, include_angle_sensors, all_details, imitate_beer )