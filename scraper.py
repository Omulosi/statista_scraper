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
import selenium
import os
from lxml.html import fromstring
import random

from link_crawler import download
from selenium_auth import get_driver, login
from throttle import Throttle
from helpers import jsonify

SLEEP_TIME = 2
CURRENT_DIR = os.getcwd()
throttle = Throttle(3)

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

def scraper(url, html):
    tree = fromstring(html)
    stat_links = tree.xpath('//div[contains(@class,"flex-list")]//ul/li/a/@href')
    domain = '{}://{}'.format(urlparse(url).scheme, urlparse(url).netloc)
    if stat_links:
        stat_links = [urljoin(domain, link) for link in stat_links]

        while stat_links:
            stat_url = stat_links.pop()
            if 'statistics' in stat_url:
                print('# Downloading files: ', stat_url)
                dir_path = url[url.find('map'):].split('map')[-1]
                dir_path = dir_path.split('?')[0]
                dir_path = 'data{}/{}'.format(dir_path, stat_url.rsplit('/',2)[1])
                dir_path = os.path.join(CURRENT_DIR, dir_path)
                os.makedirs(dir_path, exist_ok=True)

                # create a new instance of browser/driver
                driver = get_driver(download_dir=dir_path)

                # set the domain
                driver.get('https://www.statista.com')
                for ck in cookies:
                    if 'expiry' in ck:
                        del ck['expiry']
                    driver.add_cookie(ck)
                throttle.wait(stat_url)
                driver.get(stat_url)
                time.sleep(2.5)

                download_btns = driver.find_elements_by_css_selector(
                    '#download button.button')
                print('...saving files')

                for btn in download_btns:
                    try:
                        btn.click()
                        time.sleep(random.randint(2,4))
                    except selenium.common.exceptions.ElementNotInteractableException:
                        print('Unable to download file: Upgrade to corporate')
                    except selenium.common.exceptions.ElementClickInterceptedException:
                        continue
                    except selenium.common.exceptions.StaleElementReferenceException:
                        stat_links.append(stat_url)
                        break

                # Extract metadata
                tree = fromstring(driver.page_source)

                # source
                src_keys = tree.xpath('//div[@id="source"]//dt//text()')
                src_vals = tree.xpath('//div[@id="source"]//dd//text()')
                src_vals = [v.strip() for v in src_vals]
                src_metadata = jsonify(src_keys, src_vals)

                # info
                info_keys = tree.xpath('//div[@id="info"]//dt//text()')
                info_keys = [key.strip() for key in info_keys]
                info_vals = tree.xpath('//div[@id="info"]//dd//text()')
                info_vals = [val.strip() for val in info_vals]
                info_metadata = jsonify(info_keys, info_vals) 

                metadata = {**src_metadata, **info_metadata}
                meta_dir = os.path.join(dir_path, 'metadata.json')
                print('...saving metadata')
                with open(meta_dir, 'w') as meta_file:
                    json.dump(metadata, meta_file)

                time.sleep(2)
                driver.quit()

