"""
Script to explore the website http://www.network.netpost
"""
# import time
import os
from datetime import datetime as dt
from selenium import webdriver
from bs4 import BeautifulSoup

now = dt.now().strftime("%Y%m%d%H%M%S")
fd = "c:/development/python/infra_telecom/temp"
fn = "details_list {now}.txt".format(now=now)
fh = open(os.path.join(fd, fn), mode='w')

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

loc = 0

driver.switch_to.default_content()
driver.switch_to.frame("right")

location = driver.find_element_by_name("ctl00$MainContent$tbSearchFACode")
location.clear()
location.send_keys(loc)

search = driver.find_element_by_name("ctl00$MainContent$btnSearch")
search.click()

details = driver.find_elements_by_link_text("Details")
nr_locs = len(details)
for cnt in range(nr_locs):
    detail = details[cnt]
    detail.click()
    soup = BeautifulSoup(driver.page_source, 'html5lib')
    dettable = soup.find(id="ctl00_MainContent_fvSiteDetails")
    for el in dettable.find_all("span"):
        if el.string == "None":
            val = ""
        else:
            val = el.string
        fh.write("{val}|".format(val=val))
    fh.write("Last Column\n")
    if (cnt + 1) < nr_locs:
        # Click on search again to get Details list
        search = driver.find_element_by_name("ctl00$MainContent$btnSearch")
        search.click()
        details = driver.find_elements_by_link_text("Details")

fh.close()

driver.quit()
