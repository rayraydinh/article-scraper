import constants

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


import constants

option = webdriver.ChromeOptions()
option.add_argument(" - incognito")

driver = webdriver.Chrome(executable_path=constants.EXECUTABLE_PATH, options=option)

try:
    # Navigate to Laurier Library URL
    driver.get(constants.LIBRARY_URL)
    driver.find_element_by_css_selector('#quickset-search_tabs-titles > dd:nth-child(3) > a').click()

    # Navigating to HBR
    driver.find_element_by_css_selector('#block-laurier-custom-content-front-search-tab-journals > div > p:nth-child(3) > a:nth-child(2)').click()
    driver.find_element_by_css_selector('#tr_1_basic1 > td:nth-child(2) > div > div > div.service > a').click()

except TimeoutException:
    print("Timed out waiting for page to load")
finally:
    test = input()
    driver.quit()
