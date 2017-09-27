"""
Script to explore the website http://www.network.netpost
"""
# import time
import os
from bs4 import BeautifulSoup


fd = "c:/development/python/infra_telecom/temp"
fn = "details_source 20170915142032.txt"
fh = open(os.path.join(fd, fn), mode='r')
details = fh.read()
fh.close()

starttext = 'ctl00_MainContent_fvSiteDetails_'
soup = BeautifulSoup(details, 'html5lib')
id = "ctl00_MainContent_fvSiteDetails"
dettable = soup.find(id=id)
for el in dettable.find_all("span"):
    try:
        lbl = el['id'][len(id)+1:]
    except KeyError:
        lbl = el.input['id'][len(id)+1:]
    if 'Label' in lbl:
        lbl = lbl[:-len('Label')]
    print(lbl)
