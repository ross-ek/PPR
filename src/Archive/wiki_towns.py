import requests
from bs4 import BeautifulSoup
import re

wiki_towns_html = requests.get('https://en.wikipedia.org/wiki/List_of_towns_and_villages_in_the_Republic_of_Ireland').text
soup = BeautifulSoup(wiki_towns_html,'lxml')
towns_html = soup.findAll('div',{'class':'hlist hlist-separated'})
soup = BeautifulSoup(str(towns_html),'lxml')

links = []

for link in soup.findAll('a'):
    links.append(link)
    #print(link)

towns = []

for link in links:
    towns.append(link.string)
    print(link.string)

