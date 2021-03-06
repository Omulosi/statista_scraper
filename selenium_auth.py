from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv

load_dotenv()

CURRENT_DIR = os.getcwd()

LOGIN_URL = 'https://www.statista.com/login/'
LOGIN_USERNAME = os.getenv('LOGIN_USERNAME')
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")


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
    options.add_argument("--headless")

    driver = webdriver.Chrome(chrome_options=options)

    # prevent bugs due to elements not loading properly in headless mode
    driver.set_window_size(1440, 900)
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

