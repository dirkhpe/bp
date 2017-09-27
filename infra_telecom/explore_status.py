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
search = driver.find_element_by_name("ctl00$MainContent$btnSearch")
search.click()
soup = BeautifulSoup(driver.page_source, 'html5lib')
overview = soup.find(id="ctl00_MainContent_gvResults")
fn = "overview {now}.csv".format(now=now)
fh = open(os.path.join(fd, fn), mode='w', buffering=1)
loclist = []
for line in overview.find_all('tr'):
    cnt = 0
    for el in line.find_all('th'):
        fh.write("{e}|".format(e=el.string))
    for el in line.find_all('td'):
        fh.write("{e}|".format(e=el.string))
        cnt += 1
        if cnt == 3:
            loclist.append(el.string)
    fh.write("\n")
fh.close()

# Then for each Location that is discovered, find the location details
fn = "details_list {now}.txt".format(now=now)
fh = open(os.path.join(fd, fn), mode='w', buffering=1)
for loc in sorted(set(loclist)):
    print("Now working on location: {loc}".format(loc=loc))

    # Navigate to the left frame to find link for 'Explore-Status'
    # This is required to reset the variables in the right window.
    driver.switch_to.default_content()
    driver.switch_to.frame("left")
    explore_link = driver.find_element_by_link_text("Explore-Status")
    explore_link.click()

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
