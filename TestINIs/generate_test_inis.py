import os


tmpl="temptest_tmpl.ini"

levels=[]

max=0.7
min=-0.7
inc=0.1

i = min

while i < max:
  levels.append( round( i, 3) )
  i += inc

print( levels )

#AAA_MIN

for level in levels:
  os.system( "cat {0} | sed \"s/AAA_MIN/{1}/\"    |  sed  \"s/BBB_MAX/{1}/\" > TestingChamber/temptest_const_{1}.ini  ".format( tmpl, level ) )
  
