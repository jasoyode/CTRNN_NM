#!/bin/bash

./robustness_PLOT_directory.sh ../../DATA/CPG_RPG_MPG_345/ && ./robustness_PLOT_directory.sh ../../DATA/MPG_GOOD_345/ && python robustness_violin_plots.py gfds


