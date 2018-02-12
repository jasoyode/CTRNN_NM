import os
import sys

#DIR="../../DATA/GENS-2000/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON"
#DIR="../../DATA/JASON/JOB_size-3_sim-long10run_signal-SINE-1p_M-standard"
#DIR="../../DATA/mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON"
#DIR="../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard"

#DIR="../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard"
#DIR="../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-RPG_size-3_sim-100run-500gen_signal-SINE-1p_M-standard"
DIR="../../DATA/CPG_RPG_MPG_345/JOB_ctrnn-CPG_size-3_sim-100run-500gen_signal-SINE-1p_M-mod1-ON"

#DIR="../../DATA/CITED_DATA"
#DIR="../../DATA/TEMP_DATA/DUD"


if len(sys.argv) < 2:
  print("No directory given, using default {}".format(DIR) )
else:
  DIR=sys.argv[1]

DIR= DIR.replace("/", "\/" )

SEARCH="XXX"

#CSVs = [ "const_mod.csv", "const_mod_NEG.csv", "const_mod_POS.csv", "const_mod_extremes.csv"]
#"periods_1-5.csv", "periods.csv" ]
#CSVs = ["test_standard_plus_minus.csv", "test_standard_pos.csv", "test_standard_pos_neg.csv", "test_standard_neg.csv" ]

#CSVs = [ "CPG_test_standard_EXTREMA.csv", "CPG_test_standard_PERIODS.csv", "CPG_test_standard_plus_minus.csv" ]
#CSVs = [ "CPG_MPG_RPG_STANDARD_CONST.csv", "CPG_MPG_RPG_STANDARD_SIN_AMPLITUDE.csv", "CPG_MPG_RPG_STANDARD_PERIODS.csv" ]


#CSVs=[ "const_mod_extremes_NOAMP.csv","const_mod_extremes2_NOAMP.csv", "amp_mod_5_levels.csv", "const_mods_NOAMP.csv"]
#CSVs=[ "amp_mod_5_levels.csv"]

#CSVs=["const_mod_lows_NOAMP.csv", "const_mod_-0.05.csv", "const_mod_0.05.csv", "const_mod_lows2.csv", "amp_mod_5_LOW_levels.csv", "const_mod_0.1.csv", "const_mod_-0.1.csv"]
#CSVs=["const_mod_0.1.csv"]
CSVs=["amp_mod_5_levels.csv"]

os.system( "mkdir temp_files" )

for CSV in CSVs:
  os.system( "cat CSV/{0} | sed \"s/{1}/{2}/\" > temp_files/{0} ".format(CSV, SEARCH, DIR) )
  print(  "cat CSV/{0} | sed \"s/{1}/{2}/\" > temp_files/{0} ".format(CSV, SEARCH, DIR) )
  
for CSV in CSVs:
  os.system( "python csvreader.py {} temp_files/{} &".format(DIR, CSV) )
  print( "python csvreader.py {} CSV/{} &".format(DIR, CSV) )
