"""
Author: Ronald DeLuca
A web scraper that loads a Bitcointalk topic and extracts post information to a CSV using a list of proxies
"""

import requests
import re
import os
import time
import datetime
import numpy as np
import pandas as pd
import csv
import praw
import pytz
import urllib.request
import json
import random
import dateutil.parser
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pandas.io.json import json_normalize
from multiprocessing.dummy import Pool as ThreadPool 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.options import Options

# chrome_options = Options()
# chrome_options.add_argument('--headless')

# co = webdriver.ChromeOptions()
# co.add_argument("log-level=3")
# co.add_argument("--headless")

UTC=pytz.UTC
NOW = datetime.now()
BEGINDATE = datetime(2017, 10, 1)
ROOT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'data/'
)

def open_browser():
    print ("Opening web page...")
    try:
        # f = open('ProxyList.txt', 'r')
        # proxy_ip = f.read()
        # f.close()
        proxy_ip = random.choice(list(open('ProxyList.txt')))
        headers = { 'Accept': '*/*',
            'Accept-Encoding':'gzip, defalte, sdch',
            'Accept-Language':'en-Us,en;q=0.8',
            'Cache-Control':'max-age=0',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36' }
        # for key, value in enumerate(headers):
        #     webdriver.DesiredCapabilities.Chrome['chrome.page.customHeaders.{}'.format(key)] = value
        if len(proxy_ip) <= 1: # Not a valid IP
            print ("No Proxy will be used...")
            driver = webdriver.Chrome()
        else: # Valid Proxy
            print ('Using proxy: ' + proxy_ip)
            PROXY = proxy_ip
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--proxy-server=%s' % PROXY)
            # service_args = [
            #     '--headless',
            #     '--proxy=' + proxy_ip,
            #     '--proxy-type=socks5'
            # ]
            print("test")
            driver = webdriver.Chrome(executable_path="/home/cipher/chromedriver", options=chrome_options)
            print("driver worked")
    except:
        print ("REQUEST ERROR...No Proxy will be used...")
        driver = webdriver.Chrome()
    driver.implicitly_wait(3)
    print("driver waiting")
    # driver.set_page_load_timeout(300)
    print("driver timeout")
    return driver
# def get_proxies(co=co):
#     driver = webdriver.Chrome(chrome_options=co)
#     driver.get("https://www.us-proxy.org/")

#     PROXIES = []
#     proxies = driver.find_elements_by_css_selector("tr[role='row']")
#     for p in proxies:
#         result = p.text.split(" ")

#         if result[-1] == "yes":
#             PROXIES.append(result[0]+":"+result[1])

#     driver.close()
#     return PROXIES


# ALL_PROXIES = get_proxies()

# def get_proxies(co=co):

#     PROXIES = []
#     with open('ProxyList.txt', 'r') as f:
#         for line in f:
#             PROXIES.append(line)

#     return PROXIES


# ALL_PROXIES = get_proxies()


# def proxy_driver(PROXIES, co=co):
#     prox = Proxy()

#     if PROXIES:
#         pxy = PROXIES[-1]
#     else:
#         print("--- Proxies used up (%s)" % len(PROXIES))
#         PROXIES = get_proxies()

#     prox.proxy_type = ProxyType.MANUAL
#     prox.http_proxy = pxy
#     # prox.socks_proxy = pxy
#     prox.ssl_proxy = pxy

#     capabilities = webdriver.DesiredCapabilities.CHROME
#     prox.add_to_capabilities(capabilities)

#     driver = webdriver.Chrome(chrome_options=co, desired_capabilities=capabilities)

#     return driver

def get_bitcointalk_posts(args):
    """ Get posts from Bitcointalk Topics. 

    """

    name, urlbase = args
    print('Scraping: ', name)
    bitcointalk_df = pd.DataFrame(columns=[
        'id',
        'msg_id',
        'parent_id',
        'link_id',
        'Count_read',
        'Forum',
        'Time',
        'Author',
        'Rank',
        'Activity',
        'Merit',
        'Trust',
        'Title',
        'Body',
        'ScamHeader'
    ])

    # chrome_options.add_argument('--proxy-server=%s' % PROXY)
    # driver = \
    # webdriver.Chrome(executable_path="/home/cipher/chromedriver", options=chrome_options)
    driver = open_browser()
    print("returned from timeout")
    totalScraped = 0
    errors = 0
    i = 0

    driver.get(urlbase)
    print("get urlbase")
    os.system('sleep 0.5')
    lastPage = False
    try:
        navPages = driver.find_elements_by_xpath(
            "//a[contains(@class, 'navPages')]"
        )
        navPages[-2].click()
        os.system('sleep 0.5')
    except:
        pass
    test = driver.find_element_by_xpath(".//td[@id='top_subject']")
    res = re.search(r'Topic:\s+(.*?)\s+\(Read (.*) times\)',test.text)
    topic = res.group(1)
    views = res.group(2)
    scamHeader = False
    scamHeaderCheck = re.search(r'One or more bitcointalk.org users have reported that they strongly believe that the creator of this topic is a scammer.',driver.page_source)
    if(scamHeaderCheck != None):
        scamHeader = True
    cId = 1
    while(not lastPage):
        posts = driver.find_elements_by_xpath(
        "//td[contains(@class,'windowbg') or contains(@class,'windowbg2')]"
        )
        pageCount = 0
        parentId = urlbase
        forum = driver.find_element_by_xpath(
            ".//a[contains(@href, 'board=')]"
        ).text
        trust = ''
        for p in posts:
            try:
                username = p.find_element_by_xpath(
                    ".//a[contains(@href, 'action=profile')]"
                ).text
                msgId = p.find_element_by_css_selector('a.message_number').get_attribute('href')
                msgId = msgId.split("#")[1]
                try:
                    linkParId = p.find_element_by_class_name('quoteheader')
                    linkId = linkParId.find_element_by_xpath(
                    "./a[contains(@href, 'msg')]"
                    ).get_attribute('href')
                    linkId = linkId.split("#")[1]
                except NoSuchElementException:
                    linkId = ''
                ranks = p.find_element_by_xpath(
                    ".//td[@class='poster_info']//div"
                ).text.split('\n')
                ranks = list(filter(None, ranks))
                ranks = [rank for rank in ranks if
                            rank!='Online']
                activityD = p.find_element_by_class_name('smalltext').text
                activity = [int(i) for i in activityD.split() if i.isdigit()] 
                date = p.find_element_by_xpath(".//div[@class='smalltext' and position()=2]").text
                date = re.sub('Today at ', NOW.strftime('%B %d, %Y, '), date)
                date = re.sub('\n','', date)
                date = date.split("Last")[0]
                date = datetime.strptime(
                    date, '%B %d, %Y, %I:%M:%S %p'
                )
                try:
                    msgOrg = p.find_element_by_class_name('post')
                    child = msgOrg.find_element_by_class_name('quoteheader')
                    child2 = msgOrg.find_element_by_class_name('quote')
                    msgString = msgOrg.text.replace(child.text, '').replace(child2.text, '')
                    msg = re.sub('\n',' ', msgString)
                except NoSuchElementException:
                    msgString = p.find_element_by_class_name('post').text
                    msg = re.sub('\n',' ', msgString)
                bitcointalk_df = bitcointalk_df.append(
                    pd.DataFrame(
                        [(cId,
                        msgId,
                        parentId,
                        linkId,
                        views,
                        forum,
                        date,
                        username,
                        ranks[0],
                        activity[0],
                        activity[1],
                        trust,
                        topic,
                        msg,
                        scamHeader,
                        )],
                        columns=[
                            'id',
                            'msg_id',
                            'parent_id',
                            'link_id',
                            'Count_read',
                            'Forum',
                            'Time',
                            'Author',
                            'Rank',
                            'Activity',
                            'Merit',
                            'Trust',
                            'Title',
                            'Body',
                            'ScamHeader'
                        ]
                    )
                )
                cId+=1
                pageCount+=1
                totalScraped+=1
            except:
                pass
        try:
            previous = driver.find_elements_by_xpath(
                "//span[contains(@class, 'prevnext')]"
            )
            previous = previous[0]
            if previous.text != '«':
                raise ValueError('')
            previous.click()
            os.system('sleep 0.5')
        except:
            lastPage = True
        print('Scraped {} posts : {}'.format(name, totalScraped))
    print('\n*******************************************************\n')
    print('{} finished scraping!' .format(name))
    print('Total of scraped {} posts : {}'.format(name, totalScraped))
    print('Errors : {}'.format(errors))
    fileDateName = time.strftime("%Y%m%d-%H%M%S")
    bitcointalk_df.to_csv('data/raw_data/' + name + '_' + fileDateName + '.csv', index=False)
    driver.quit()
    return 0

def crawler_script():
    START = time.time()

    print('Bitcointalk Post Scraper')
    start = time.time()
    urlCsvBases = [
        ["JEWEL", "https://bitcointalk.org/index.php?topic=5057721.0"],
    ]
    with open('data/AnnList_Min.csv', 'r') as AnnList:
        reader = csv.reader(AnnList)
        next(reader)
        AnnCsv_list = list(reader)

    pool = ThreadPool(1)
    # pool.map(get_bitcointalk_posts, AnnCsv_list)
    pool.map(get_bitcointalk_posts, urlCsvBases)

    print('Scraping took {}s'.format(time.time()-start))
    '''
    '''
    
    print('Total scrape time in seconds : {}s'.format(time.time()-START))

# creating new driver to use proxy
# driver = proxy_driver(ALL_PROXIES)

# running = True

# while running:
#     try:
#         if __name__ == '__main__':

#             crawler_script()

#     except:
#         new = ALL_PROXIES.pop()

#         # reassign driver if fail to switch proxy
#         pd = proxy_driver(ALL_PROXIES)
#         print("--- Switched proxy to: %s" % new)
#         time.sleep(1)

if __name__ == '__main__':

    crawler_script()