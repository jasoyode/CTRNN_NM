import os

#DIR="../../DATA/GENS-2000/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON"
#DIR="../../DATA/JASON/JOB_size-3_sim-long10run_signal-SINE-1p_M-standard"
DIR="../../DATA/mod1_345_100jobs/JOB_size-3_sim-long10run-2000gen_signal-SINE-1p_M-mod1-ON"

DIR= DIR.replace("/", "\/" )

SEARCH="XXX"

#CSVs = [ "const_mod.csv", "const_mod_NEG.csv", "const_mod_POS.csv", "const_mod_extremes.csv"]
#"periods_1-5.csv", "periods.csv" ]
CSVs = ["test_standard_plus_minus.csv", "test_standard_pos.csv", "test_standard_pos_neg.csv", "test_standard_neg.csv" ]



os.system( "mkdir temp_files" )

for CSV in CSVs:
  os.system( "cat CSV/{0} | sed \"s/{1}/{2}/\" > temp_files/{0} ".format(CSV, SEARCH, DIR) )
  print(  "cat CSV/{0} | sed \"s/{1}/{2}/\" > temp_files/{0} ".format(CSV, SEARCH, DIR) )
  
for CSV in CSVs:
  os.system( "python csvreader.py {} temp_files/{} &".format(DIR, CSV) )
  print( "python csvreader.py {} CSV/{} &".format(DIR, CSV) )
  





