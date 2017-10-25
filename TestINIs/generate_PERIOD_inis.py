import os


tmpl="temptest_PERIOD_tmpl.ini"

levels=[1,2,3,4,5,6,8,10]


print( levels )

#AAA_MIN

for level in levels:
  os.system( "cat {0} | sed \"s/AAA_MIN/{1}/\"    |  sed  \"s/BBB_MAX/{1}/\" > TestingChamberPeriod/temptest_period_{1}.ini  ".format( tmpl, level ) )
  
