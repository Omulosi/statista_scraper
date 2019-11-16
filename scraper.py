import os
import sys
import string
import re
from lxml.html import fromstring
import requests
from urllib.parse import urljoin, urlparse
import json
import threading
import time

from link_crawler import download
from selenium_auth import get_driver, login

SLEEP_TIME = 1

# save cookies to json file to prevent multiple log ins
try:
    with open('cookies') as f_in:
        cookies = json.load(f_in)
except FileNotFoundError:
    driver = get_driver()
    login(driver)
    cookies = driver.get_cookies()
    driver.quit()
    with open('cookies', 'w') as f_out:
        json.dump(cookies, f_out)
except:
    print('Something went wrong during log in')
    raise

def scraper(url, html, max_threads=10):
    tree = fromstring(html)
    stat_links = tree.xpath('//div[contains(@class,"flex-list")]//ul/li/a/@href')
    domain = '{}://{}'.format(urlparse(url).scheme, urlparse(url).netloc)
    if stat_links:
        stat_links = [urljoin(domain, link) for link in stat_links]
        stat_links = stat_links[:2]

        def process_queue():
            while stat_links:
                stat_url = stat_links.pop()
                if 'statistics' in stat_url:
                    print('# creating folders and downloading files...')
                    dir_path = url[url.find('map'):].split('map')[-1]
                    dir_path = dir_path.split('?')[0]
                    dir_path = './data{}/{}'.format(dir_path, stat_url.rsplit('/',2)[1])
                    os.makedirs(dir_path, exist_ok=True)

                    # create a new instance of browser/driver
                    driver = get_driver(download_dir=dir_path)

                    # set the domain
                    driver.get('https://www.statista.com')
                    for ck in cookies:
                        driver.add_cookie(ck)
                    driver.get(stat_url)
                    # breakpoint()

                    download_btns = driver.find_elements_by_css_selector(
                        'button.statisticDownload')
                    breakpoint()

                    for btn in download_btns:
                        btn.click()

                    driver.quit()

        threads = []

        while threads or stat_links:
            for thread in threads:
                if not thread.is_alive():
                    threads.remove(thread)
            while len(threads) < max_threads and stat_links:
                thread = threading.Thread(target=process_queue)
                thread.setDaemon(True)
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()
            time.sleep(SLEEP_TIME)