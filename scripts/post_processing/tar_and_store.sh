#!/bin/bash

#BASE_DIR="/u/jasoyode/github/jasoyode/CTRNN_NM"

PLOTS="PLOTS"
DATA="DATA"

if   [  "$2" == "" ] ; then
  echo "Please specify an experiment DATA and PLOTS directory!"
  exit
fi


DATA_DIR="$1"
PLOT_DIR="$2"

EXP_NAME=$( echo "$DATA_DIR" | sed "s/.*DATA\///" )

export HPSS_AUTH_METHOD=kerberos
#module load hpss

htar -c -P -f ${DATA}/${EXP_NAME}_data.tar ${DATA_DIR}/*
htar -c -P -f ${PLOTS}/${EXP_NAME}_plots.tar ${PLOT_DIR}/*

