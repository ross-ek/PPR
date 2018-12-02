import re

re_county = '[,.\s](COUNTY|CO)[,.\s].*$'

s = '5 BRAEMOR DRIVE,CHURCHTOWN,CO.DUBLIN'

x = re.sub(re_county, '', s)

print(x)
