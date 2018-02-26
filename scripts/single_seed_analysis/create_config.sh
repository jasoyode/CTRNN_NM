#!/bin/bash



XXX_SEED_XXX="4"
XXX_NAME_XXX="RPG3_STD_$XXX_SEED_XXX"
XXX_CTRNN_PATH_XXX="/scratch/jasoyode/github_jasoyode/CTRNN_NM/"
INNER_FOLDER="JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON"




##################
XXX_CTRNN_PATH_XXX=$( echo "$XXX_CTRNN_PATH_XXX" | sed "s/\//\\\\\//g" )
XXX_EXP_FOLDER_XXX="DATA/CPG_RPG_MPG_345/$INNER_FOLDER"
XXX_EXP_FOLDER_XXX=$( echo "$XXX_EXP_FOLDER_XXX" | sed "s/\//\\\\\//g" )
XXX_JOB_INI_XXX="$INNER_FOLDER.ini"
OUTPUT_CONFIG="config_$XXX_NAME_XXX.ini"



cat config_template.ini | sed "s/XXX_SEED_XXX/$XXX_SEED_XXX/" \
						| sed "s/XXX_NAME_XXX/$XXX_NAME_XXX/" \
						| sed "s/XXX_CTRNN_PATH_XXX/$XXX_CTRNN_PATH_XXX/" \
						| sed "s/XXX_EXP_FOLDER_XXX/$XXX_EXP_FOLDER_XXX/" \
						| sed "s/XXX_JOB_INI_XXX/$XXX_JOB_INI_XXX/" > $OUTPUT_CONFIG