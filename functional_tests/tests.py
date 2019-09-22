import os
import time
#from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By


MAX_WAIT = 10


class AccountTestCase(LiveServerTestCase):

    def setUp(self):
        self.selenium = webdriver.Firefox(executable_path='C:\Selenium\Drivers\geckodriver-v0.24.0-win64\geckodriver.exe')
        super(AccountTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(AccountTestCase, self).tearDown()

    def test_login(self):
        selenium = self.selenium
        #Opening the link we want to test
        selenium.get('http://127.0.0.1:5002/accounts/login/')
        #find the form element
        username = selenium.find_element_by_id('id_username')
        password = selenium.find_element_by_id('id_password')

        submit = selenium.find_element_by_name('submit')

        #Fill the form with data
        username.send_keys('omar')
        password.send_keys('testme123')

        #submitting the form
        submit.send_keys(Keys.RETURN)


        time.sleep(5)

        #lnk = selenium.find_element(By.XPATH, '//a[text()="Nieuwe Aanvraag"]')
        nieuwe_aanvraag_lnk = selenium.find_element(By.XPATH, "//a[@id='id_lnk_nieuwe_aanvraag']")
        print(f"nieuwe_aanvraag_lnk: {nieuwe_aanvraag_lnk}")
        nieuwe_aanvraag_lnk.click()

        time.sleep(5)

        nieuwe_aanvraag_form = selenium.find_element(By.XPATH, "//form[1]")
        print(f"nieuwe_aanvraag_form: {nieuwe_aanvraag_form}")

        time.sleep(5)

        vtm_sdate = selenium.find_element(By.XPATH, "//input[@id='id_dvom_vtmstartdatum']")
        print(f"vtm_sdate: {vtm_sdate}")
        vtm_sdate.click()
        vtm_sdate.click()
        vtm_sdate.clear()
        vtm_sdate.send_keys('10/09/2019')
        vtm_sdate.send_keys(Keys.TAB)

        time.sleep(10)
        #check the returned result
        #assert 'Check your email' in selenium.page_source
        selenium.quit()
