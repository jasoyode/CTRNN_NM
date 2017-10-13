import re


exp_dir="../../../DATA/asdasd/asdasdas"

exp_tit = re.sub(r'.*/','', exp_dir )


exp_base = re.sub(r'.*/DATA/','', exp_dir )

print( exp_dir  )
print( exp_tit )
print( exp_base )