import re
from urllib import robotparser
from urllib.parse import urljoin, urlparse
import socket

import requests
from throttle import Throttle
import auth

socket.setdefaulttimeout(120)

USER_AGENT="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0"
# session = requests.Session()
# _, session = auth.login(session=session)


def download(url, num_retries=2, user_agent=USER_AGENT, proxies=None):
    print('Downloading:', url)
    headers = {'User-Agent': user_agent}
    try:
        resp = requests.get(url, headers=headers, proxies=proxies)
        html = resp.text
        if resp.status_code >= 400:
            print('Download error:', resp.text)
            html = None
            if num_retries and 500 <= resp.status_code < 600:
                # recursively retry 5xx HTTP errors
                return download(url, num_retries - 1)
    except requests.exceptions.RequestException as e:
        print('Download error:', e)
        html = None
    return html


def get_robots_parser(robots_url):
    " Return the robots parser object using the robots_url "
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp


def get_links(html):
    webpage_regex = re.compile("""<a[^>]+href=["'](.*?)["']""", re.IGNORECASE)
    return webpage_regex.findall(html)


def link_crawler(start_url, link_regex, robots_url=None, user_agent='statista',
        max_depth=-1, delay=2, proxies=None, num_retries=2, cache=None,
        scraper_callback=None):

    #: Initialze a crawl queue with a seed url to start the crawl from
    crawl_queue = [start_url]

    #: keep track of seen urls
    seen = {}

    #: Keep track of domains and their associated
    #: parsers
    robots = {}

   #: Initialize the downloader
    url_downloader = download

    throttle = Throttle(delay)

   #: start the crawl
    while crawl_queue:
        url = crawl_queue.pop()

        #:
        #: robots.txt
        #:
        robots_file_present = False
        if 'http' not in url:
            continue

        #: Get the root url
        domain = '{}://{}'.format(urlparse(url).scheme, urlparse(url).netloc)

        #: Get the robot parser for this domain from the robots dictionary
        robot_parser = robots.get(domain)
        
        #: set a default robots url and a parser for it if there isn't one
        if not robot_parser and domain not in robots:
            robots_url = '{}/robots.txt'.format(domain)
            robot_parser = get_robots_parser(robots_url)
            if not robot_parser:
                #: continue to crawl even if there are problems finding robots.txt
                #: file
                robots_file_present = True
            # associate each domain with a corresponding parser, whether present or not
            robots[domain] = robot_parser

        elif domain in robots:
            robots_file_present = True

        #: crawl only when url passes robots.txt restrictions
        if robots_file_present or robot_parser.can_fetch(user_agent, url):
            depth = seen.get(url, 0)
            if depth == max_depth:
                #: Skip link if you have crawled it more than max depth
                print('Skipping %s due to depth' % url)
                continue
            throttle.wait(url)
            html= download(url, num_retries=num_retries)
            if not html:
                continue
            if scraper_callback:
                scraper_callback(url, html)

            #: Get all links from page and filter only those matching given pattern
            for link in get_links(html):
                if re.search(link_regex, link):
                    if 'http' not in link:
                        # check if link is well formed and correct
                        if link.startswith('//'):
                            link = '{}:{}'.format(urlparse(url).scheme, link)
                        elif link.startswith('://'):
                            link = '{}{}'.format(urlparse(url).scheme, link)
                        else:
                            link = urljoin(domain, link)

                    if link not in seen:
                        seen[link] = depth + 1
                        crawl_queue.append(link)
        else:
            print('Blocked by robots.txt:', url)



