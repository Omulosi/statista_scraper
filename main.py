from scraper import scraper
from link_crawler import link_crawler

START_URL='https://www.statista.com/map/'

if __name__ == '__main__':
    follow = r'/map/'
    link_crawler(START_URL, link_regex=follow, scraper_callback=scraper)
