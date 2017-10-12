#!/bin/bash

BASE_DIR="/N/dc2/scratch/jasoyode/github/jasoyode/CTRNN_NM"

PLOTS="PLOTS"
DATA="DATA"

if [ "$1" == "" ]; then
  echo "Please specify an experiment directory!"
  exit
fi

EXP_DIR="$1"


export HPSS_AUTH_METHOD=kerberos
module load hpss

htar -c -f ${DATA}/${EXP_DIR}_data.tar ${BASE_DIR}/${DATA}/${EXP_DIR}/*
htar -c -f ${PLOTS}/${EXP_DIR}_plots.tar ${BASE_DIR}/${PLOTS}/${EXP_DIR}/*

