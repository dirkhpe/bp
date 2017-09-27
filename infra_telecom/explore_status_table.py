"""
Script to explore the website http://www.network.netpost
"""
# import time
import os
from datetime import datetime as dt
from selenium import webdriver
from bs4 import BeautifulSoup

now = dt.now().strftime("%Y%m%d%H%M%S")

# Create a new Chrome session
driver = webdriver.Chrome()
driver.implicitly_wait(30)

# Navigate to the application home page
url = "http://www.network.netpost/"
driver.get(url)

# Navigate to the left frame to find link for 'Explore-Status'
driver.switch_to.frame("left")
explore_link = driver.find_element_by_link_text("Explore-Status")
explore_link.click()
# time.sleep(5)

driver.switch_to.default_content()
driver.switch_to.frame("right")
# location = driver.find_element_by_name("ctl00$MainContent$tbSearchFACode")
# location.clear()
# location.send_keys("10")
search = driver.find_element_by_name("ctl00$MainContent$btnSearch")
search.click()
fd = "c:/development/python/infra_telecom/temp"
fn = "page_source {now}.txt".format(now=now)
fh = open(os.path.join(fd, fn), mode='w')
fh.write(driver.page_source)
fh.close()
soup = BeautifulSoup(driver.page_source, 'html5lib')
overview = soup.find(id="ctl00_MainContent_gvResults")
fn = "overview {now}.csv".format(now=now)
fh = open(os.path.join(fd, fn), mode='w')
loclist = []
for line in overview.find_all('tr'):
    cnt = 0
    for el in line.find_all('th'):
        fh.write("{e}|".format(e=el.string))
    for el in line.find_all('td'):
        fh.write("{e}|".format(e=el.string))
        cnt += 1
        if cnt == 3:
            if el.string not in loclist:
                loclist.append(el.string)
    fh.write("\n")
fh.close()

driver.quit()
