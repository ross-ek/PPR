import requests
from bs4 import BeautifulSoup
import re

wiki_towns_html = requests.get('https://www.cso.ie/px/pxeirestat/Statire/SelectVarVal/Define.asp?maintable=E2052&PLanguage=0').text
soup = BeautifulSoup(wiki_towns_html,'lxml')

towns_html = soup.findAll('option')

towns_pass1 = []
towns_pass2 = []

for i in towns_html:
    towns_pass1.append(i)

for i in range(0, len(towns_pass1)):

    if ',' in str(towns_pass1[i]):
        x = re.sub('</option>','',str(towns_pass1[i]))
        x = re.sub('^[^>]+>','',x) # match until first '>'
        towns_pass2.append(x)
        print(x)

for i in towns_pass2:
    print(i)    




