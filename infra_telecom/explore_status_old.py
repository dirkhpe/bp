"""
Script to explore the website http://www.network.netpost
"""
import time
from selenium import webdriver

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
time.sleep(5)

driver.switch_to.default_content()
driver.switch_to.frame("right")
# location = driver.find_element_by_name("ctl00$MainContent$tbSearchFACode")
# location.clear()
# location.send_keys("10")
search = driver.find_element_by_name("ctl00$MainContent$btnSearch")
search.click()
# details = driver.find_element_by_link_text("Details")
# details.click()
# time.sleep(5)

# location = driver.find_element_by_name("ctl00$MainContent$tbSearchFACode")
# location.clear()
# location.send_keys("100")
# search = driver.find_element_by_name("ctl00$MainContent$btnSearch")
# search.click()
# time.sleep(10)
# details = driver.find_element_by_link_text("Details")
"""
details.click()
time.sleep(5)

location = driver.find_element_by_name("ctl00$MainContent$tbSearchFACode")
location.clear()
location.send_keys("1000")
search = driver.find_element_by_name("ctl00$MainContent$btnSearch")
search.click()
time.sleep(10)
details = driver.find_element_by_link_text("Details")
details.click()
time.sleep(5)


driver.quit()
"""