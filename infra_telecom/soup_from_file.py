"""
Script to explore the website http://www.network.netpost
"""
# import time
from bs4 import BeautifulSoup


soup = BeautifulSoup(driver.page_source, 'html5lib')
restable = soup.find(id="ctl00_MainContent_gvResults")
"""
print(type(restable))
for row in restable.find_all('<tr>'):
    print(row.prettify())
"""
fn = "c:/development/python/infra_telecom/temp/restable_5.html"
fh = open(fn, mode='w')
fh.write(restable.prettify())
fh.close()

driver.quit()
