import time

import constants
import credentials

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class Driver:
    def __init__(self, driver=None):
        self.prefs = {"plugins.always_open_pdf_externally": True}
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
        self.option.add_experimental_option("prefs", self.prefs)
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

    def switch_to_active(self):
        self.driver.switch_to_window(self.driver.window_handles[0])
        return


def get_issues_vols(a_driver):
    """
    :param a_driver: Takes in a Driver Object
    :return: zip list containing (WebElement id of volumes, WebElement of number of issues)
    """
    ids = a_driver.find_elements_by_xpath('//*[@id="VolumeTable"]/tbody/tr/td/a')
    scraped_volumes = []
    for i in range(len(ids)):
        ids[i].click()
        time.sleep(2)
        volumes = a_driver.find_elements_by_css_selector('.authVolIssue_issue_cell a')
        for j in range(len(volumes)):
            volumes[j].click()
            grab_articles_from_volume(a_driver)
        scraped_volumes.append(volumes)
    return list(zip(ids, scraped_volumes))


def grab_articles_from_volume(a_driver):
    pdf_full_text = a_driver.find_elements_by_link_text('PDF Full Text')
    for i in range(len(pdf_full_text)):
        time.sleep(2)
        element = WebDriverWait(a_driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'PDF Full Text'))
        )
        a_driver.execute_script("window.stop();")
        a_driver.find_elements_by_link_text('PDF Full Text')[i].click()

        # Switch to iFrame and download PDF
        element = WebDriverWait(a_driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="pdfIframe"]'))
        )
        a_driver.switch_to.frame('pdfIframe')
        open = a_driver.find_element_by_link_text('Open')
        open.click()
        print("Downloaded article:", str(i + 1))

        # Switch back out of iFrame
        a_driver.switch_to.default_content()
        a_driver.execute_script("window.history.go(-1)")
        # a_driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + '[')


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

    # Switch to HBR Tab
    article_driver.driver.close()
    time.sleep(30)
    article_driver.switch_to_active()

    # Wait until page is loaded
    iss_vol_zl = get_issues_vols(article_driver.driver)
    test = input()

