from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
import chromedriver_binary

LOGIN_URL ='https://www.statista.com/login/'
LOGIN_USERNAME = 'keith.davey@parallaxgeo.com'
LOGIN_PASSWORD = 'D3jaULYw7QKZiUxD'

def get_driver2(download_dir=None):
    download_dir = download_dir or './data'

    profile = webdriver.FirefoxProfile()
    options = Options()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", download_dir)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "application/octet-stream,application/vnd.ms-excel,application/pdf")
    options.add_argument("--headless")
    return webdriver.Chrome(executable_path=r"./chromedriver")


def get_driver(download_dir=None):
    download_dir = download_dir or './data'

    options = Options()
    options.add_experimental_option("prefs", {
      "download.default_directory": download_dir,
      "download.prompt_for_download": False,
      "download.directory_upgrade": True,
      "safebrowsing.enabled": True,
      "plugins.always_open_pdf_externally": True
    })
    options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(chrome_options=options)
    # driver.get("http://www.python.org")
    # assert "Python" in driver.title
    return driver

def login(driver):
    print('Loggin in...')
    driver.get(LOGIN_URL)
    driver.find_element_by_id('loginStat_username').send_keys(LOGIN_USERNAME)
    driver.find_element_by_id('loginStat_password').send_keys(
        LOGIN_PASSWORD + Keys.RETURN)
    pg_loaded = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "content")))
    print(driver.current_url)
    assert 'login' not in driver.current_url
