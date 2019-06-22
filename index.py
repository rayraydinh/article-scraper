import time

import constants
import credentials

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class Driver:
    """
    Selenium Driver class for Harvard Business Review
    Follow Issue (iss) - Volume (vol) - Article (art) Notation
    """
    def __init__(self, driver=None):
        self.prefs = {
            "plugins.always_open_pdf_externally": True,
            "download.default_directory": "/Users/rdinh/Downloads/hbr",
            "profile.managed_default_content_settings.images": 2
        }
        self.caps = DesiredCapabilities().CHROME
        self.option = webdriver.ChromeOptions()
        self.driver = driver

        # Totals
        self.hbr_iss_curr = 0
        self.hbr_vol_curr = 0
        self.hbr_art_curr = 0

    def __del__(self):
        print(self.hbr_iss_curr)
        print(self.hbr_vol_curr)
        print(self.hbr_art_curr)
        self.driver.quit()

    def options_init(self, arguments):
        for arg in arguments:
            self.option.add_argument(arg)
        self.option.add_experimental_option("prefs", self.prefs)
        return

    def driver_init(self):
        self.driver = webdriver.Chrome(
            executable_path=constants.EXECUTABLE_PATH,
            options=self.option,
            desired_capabilities=self.caps
        )
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

    def reinitialize_to_point(self, iss, vol, start=False, click=True):
        # Ask to login
        self.driver_init()
        self.safe_navigate(constants.LIBRARY_URL)
        self.click_css('#header-app-links-list > li:nth-child(2) > a')
        self.driver.find_element_by_css_selector('#username').send_keys(credentials.USERNAME)
        self.driver.find_element_by_css_selector('#password').send_keys(credentials.PASSWORD)
        self.click_css('#login > section:nth-child(3) > input')

        # Navigating to HBR
        self.driver.get(constants.LIBRARY_URL)
        self.click_css('#quickset-search_tabs-titles > dd:nth-child(3) > a')
        self.click_css('#block-laurier-custom-content-front-search-tab-journals > div > p:nth-child(3) > a:nth-child(2)')
        self.click_css('#tr_1_basic1 > td:nth-child(2) > div > div > div.service > a')

        # Switch to HBR Tab
        self.driver.close()
        time.sleep(10)
        self.switch_to_active()
        self.driver.execute_script("window.stop();")

        # Reinitialize current iss - vol - art
        if not start:
            ids = self.driver.find_elements_by_xpath('//*[@id="VolumeTable"]/tbody/tr/td/a')
            ids[iss].click()
            time.sleep(2)

        if click:
            volumes = self.driver.find_elements_by_css_selector('.authVolIssue_issue_cell a')
            volumes[vol].click()
        return

    def get_issues_vols(self):
        """
        :return: zip list containing (WebElement id of volumes, WebElement of number of issues)
        """
        ids = self.driver.find_elements_by_xpath('//*[@id="VolumeTable"]/tbody/tr/td/a')
        for i in range(self.hbr_iss_curr, len(ids)):
            ids[i].click()
            time.sleep(2)
            print("########## ISSUE ", i, " ########## ")
            volumes = self.driver.find_elements_by_css_selector('.authVolIssue_issue_cell a')
            for j in range(self.hbr_vol_curr, len(volumes)):
                print("--------- VOLUME ", j, " ---------")
                volumes = self.driver.find_elements_by_css_selector('.authVolIssue_issue_cell a')
                volumes[j].click()
                self.grab_articles_from_volume()
                self.hbr_vol_curr += 1
                self.hbr_art_curr = 0
                time.sleep(15)
                self.driver.quit()
                self.reinitialize_to_point(self.hbr_iss_curr, self.hbr_vol_curr, click=False)
            self.hbr_vol_curr = 0
            self.hbr_iss_curr += 1
        return

    def grab_articles_from_volume(self):
        # Find number of articles
        pdf_full_text = self.driver.find_elements_by_link_text('PDF Full Text')
        curr_handles_open = len(self.driver.window_handles)

        while self.hbr_art_curr < len(pdf_full_text):
            try:
                pdf_full_texts = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_all_elements_located((By.LINK_TEXT, 'PDF Full Text'))
                )
                pdf_full_texts[self.hbr_art_curr].click()
            except TimeoutException:
                WebDriverWait(self.driver, 7).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="ctl00_ctl00_MainContentArea_MainContentArea_ErrorMessageLabel"]'))
                )
                # Let downloads finish
                time.sleep(15)
                self.driver.quit()
                self.reinitialize_to_point(self.hbr_iss_curr, self.hbr_vol_curr)
                continue

            try:
                WebDriverWait(self.driver, 7).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="downloadLink"]'))
                ).click()
                time.sleep(1)
            except TimeoutException:
                time.sleep(15)
                self.driver.quit()
                self.reinitialize_to_point(self.hbr_iss_curr, self.hbr_vol_curr)
                continue

            # Switch back out of iFrame
            self.driver.execute_script("window.history.go(-1)")

            if len(self.driver.window_handles) > curr_handles_open:
                print("Article download failed, retrying:", str(self.hbr_art_curr + 1))
                curr_handles_open = len(self.driver.window_handles)
            else:
                self.hbr_art_curr += 1

        return


if __name__ == '__main__':
    # Init Driver
    article_driver = Driver()
    article_driver.options_init([
        ' - incognito'
    ])
    article_driver.driver_init()
    article_driver.reinitialize_to_point(0, 0, True, False)
    article_driver.get_issues_vols()
    test = input()
