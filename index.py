import constants
import credentials

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class Driver:
    def __init__(self, driver=None):
        self.option = webdriver.ChromeOptions()
        self.driver = driver

    def __del__(self):
        try:
            self.driver.quit()
        except:
            pass

    def options_init(self, arguments):
        for arg in arguments:
            self.option.add_argument(arg)
        return

    def driver_init(self):
        self.driver = webdriver.Chrome(executable_path=constants.EXECUTABLE_PATH, options=self.option)
        return

    def click_css(self, css_selector):
        self.driver.find_element_by_css_selector(css_selector).click()
        return

    def safe_navigate(self, url):
        try:
            self.driver.get(url)
        except TimeoutException:
            raise Exception('Timed out while trying to navigate to', url)


if __name__ == '__main__':
    # Init Driver
    article_driver = Driver()
    article_driver.options_init([
        ' - incognito'
    ])
    article_driver.driver_init()

    # Ask to login
    article_driver.safe_navigate(constants.LIBRARY_URL)
    article_driver.click_css('#header-app-links-list > li:nth-child(2) > a')
    article_driver.driver.find_element_by_css_selector('#username').send_keys(credentials.USERNAME)
    article_driver.driver.find_element_by_css_selector('#password').send_keys(credentials.PASSWORD)
    article_driver.click_css('#login > section:nth-child(3) > input')

    # Navigating to HBR
    article_driver.driver.get(constants.LIBRARY_URL)
    article_driver.click_css('#quickset-search_tabs-titles > dd:nth-child(3) > a')
    article_driver.click_css('#block-laurier-custom-content-front-search-tab-journals > div > p:nth-child(3) > a:nth-child(2)')
    article_driver.click_css('#tr_1_basic1 > td:nth-child(2) > div > div > div.service > a')

    test = input()
