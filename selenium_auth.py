from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_binary
import os

CURRENT_DIR = os.getcwd()

LOGIN_URL ='https://www.statista.com/login/'
LOGIN_USERNAME = 'keith.davey@parallaxgeo.com'
LOGIN_PASSWORD = 'D3jaULYw7QKZiUxD'

def get_driver(download_dir=None):
    if download_dir is None:
        download_dir = os.path.join(CURRENT_DIR, 'data')

    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
      "download.default_directory": download_dir,
      "download.prompt_for_download": False,
      "download.directory_upgrade": True,
      "safebrowsing.enabled": True,
      "plugins.always_open_pdf_externally": True
    })
    options.add_argument("--disable-extensions")
    # options.add_argument("--headless")

    driver = webdriver.Chrome(chrome_options=options)
    return driver

def login(driver):
    print('Logging in...')
    driver.get(LOGIN_URL)
    driver.find_element_by_id('loginStat_username').send_keys(LOGIN_USERNAME)
    driver.find_element_by_id('loginStat_password').send_keys(
        LOGIN_PASSWORD + Keys.RETURN)
    pg_loaded = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "content")))
    assert 'login' not in driver.current_url

