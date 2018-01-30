#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Read genome form file and create visual
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

import pygraphviz as pgv
import math
import os
import sys
import csv

PI=3.141592653

ROUND=3

A=pgv.AGraph(strict=False,directed=True,K=0.3,splines='curved')

SEED=48
CRM="CPG"
SIZE="3"
TYPE="standard"

if len(sys.argv) > 1:
  if len(sys.argv) > 1:
    SEED=int(sys.argv[1])
  if len(sys.argv) > 2:
    CRM=sys.argv[2]
  if len(sys.argv) > 3:
    SIZE=int(sys.argv[3])
  if len(sys.argv) > 4:
    TYPE=sys.argv[4]

print("Using SEED:{} CRM:{}  SIZE:{}  TYPE:{}".format(SEED,CRM,SIZE,TYPE) )
#quit()

value_dict = {}


SAVE_PATH="/scratch/jasoyode/github_jasoyode/CTRNN_NM/PLOTS/NETWORK_GRAPHS/"

csv_path="/scratch/jasoyode/github_jasoyode/CTRNN_NM/DATA/CPG_RPG_MPG_345/"
csv_path+="JOB_ctrnn-{}_size-{}_sim-100run-500gen_signal-SINE-1p_M-{}/phenotypes.txt".format(CRM,SIZE,TYPE)


with open( csv_path  ) as csvfile:
  reader = csv.DictReader(csvfile)
  for row in reader:
    size=0
    if int(row["seed"]) == SEED:
      for header in row.keys():
        if not header == "":
          #print( header )
          value_dict[ header ] =  round(  float( row[header] ), ROUND )
          if "bias" in header:
            if int(header[-1]) > size:
              size = int(header[-1])
      break



for i in range(1,size+1):
  x=round( 200*math.cos( i* 2*PI/size ), ROUND)
  y=round( 200*math.sin( i* 2*PI/size ), ROUND)
  
  if i==1:
    name="(BS)"
  elif i==2:
    name="(FT)"
  elif i==3:
    name="(FS)"
  elif i==4:
    name="(INT1)"
  elif i==5:
    name="(INT2)"
  else:
    name="unknown"
  if float( value_dict[ "w_{}->{}".format(i,i) ]) > 4:
    name+="**"
  
  name="N{} {}".format(i,name)
  
  lbl="{}\nB:{}\nTC:{}\nRS: {}".format(name, value_dict["bias{}".format(i) ], value_dict["timConst{}".format(i) ], value_dict["recep{}".format(i) ]   )
  A.add_node(i, label=lbl, color='black',pos='{},{}'.format(x,y) )
  if i ==1:
    A.add_node(99, label="Angle\nSensor", color='black',pos='{},{}'.format(2*x,2*y) )
  #A.add_node(i*10, label="AngleSensor", color='black',pos='{},{}'.format(300,300) )
  

for i in range(1,size+1):
  for j in range(1,size+1):
    print("i:{} j:{}".format(i,j) )
    weight= value_dict[ "w_{}->{}".format(i,j) ]
    
    h=100
    if weight > 0:
      lbl_weight="<<font color=\"red\">{}</font>>".format(weight)
      A.add_edge(i,j, arrowhead="tee", shape='circle',label=lbl_weight,color='red',labelfontcolor='red' )
    elif weight <0:
      lbl_weight="<<font color=\"blue\">{}</font>>".format(weight)
      A.add_edge(i,j, arrowhead="dot", height=h,label=lbl_weight,color='blue',labelfontcolor='blue' )
    else:
      print("weight is zero no showing!")
    
    if (i==j):
      weight= value_dict[ "w_AS->{}".format(i) ]
      A.add_edge(99,i, minlen=100,label=weight,color='black' )
    

#A.add_node(1,color='red',pos='0,0')
#A.add_node(2,color='blue',pos='0,10000')
#A.add_node(3,color='green',pos='10000,5000')


#A.add_edge(1,2, label=0.5)
#A.add_edge(2,3, label=10)
#A.add_edge(1,3)
#A.add_edge(3,1)
#A.add_edge(1,1)
A.graph_attr['epsilon']='0.001'

print(A.string()) # print to screen
print("Wrote simple.dot")
A.write('simple.dot') # write to simple.dot

B=pgv.AGraph('simple.dot') # create a new graph from file
#'dot', 'twopi', 'circo', 'fdp', 'nop'
#B.layout(prog='circo') # layout with default (neato)
B.layout(prog='circo')
# fdp, nop, wc, acyclic, gvpr, gvcolor, ccomps, sccmap, tred, sfdp.
#B.layout( prog="tred")

B.draw('{}/simple_{}_{}_{}_{}.png'.format(SAVE_PATH,CRM,SIZE,TYPE,SEED) ) # draw png
print("Wrote simple.png")
