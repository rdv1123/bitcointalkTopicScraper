#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : proxy_crawler.py
# Author            : Ronald DeLuca
# Date              : 09.19.2019
# Information       : A web scraper that loads Bitcointalk Topics and scrapes the posts into a CSV using proxies
# -*- coding: utf-8 -*-

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
from consolemenu import *
from consolemenu.items import *
from datetime import datetime, timedelta
from pandas.io.json import json_normalize
from multiprocessing.dummy import Pool as ThreadPool 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.options import Options
from urllib.request import urlopen

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
            driver = webdriver.Chrome(executable_path="/home/example/Downloads/chromedriver", options=chrome_options)
    except:
        print ("REQUEST ERROR...No Proxy will be used...")
        driver = webdriver.Chrome()
    driver.implicitly_wait(3)
    # driver.set_page_load_timeout(300)
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
    # webdriver.Chrome(executable_path="/home/example/Downloads/chromedriver", options=chrome_options)
    driver = open_browser()
    totalScraped = 0
    errors = 0
    i = 0

    driver.get(urlbase)
    os.system('sleep 0.5')
    lastPage = False
    try:
        navPages = driver.find_elements_by_xpath(
            "//a[contains(@class, 'navPages')]"
        )
        navPages[-2].click()
        os.system('sleep 0.5')
    except:
        print('{} failed to load xpath'.format(name))
        return 0
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
    lines = list()
    with open('data/filteredList.csv', 'r') as AnnList:
        reader = csv.reader(AnnList)
        for row in reader:
            lines.append(row)
            for field in row:
                if field == urlbase:
                    lines.remove(row)

    with open('data/filteredList.csv', 'w') as out:
        writer = csv.writer(out)
        writer.writerows(lines)

    print('{} finished scraping!' .format(name))
    print('Total of scraped {} posts : {}'.format(name, totalScraped))
    print('Errors : {}'.format(errors))
    fileDateName = time.strftime("%Y%m%d-%H%M%S")
    bitcointalk_df.to_csv('data/raw_data/' + name + '_' + fileDateName + '.csv', index=False)
    driver.quit()
    return 0

def specificUrlSearch():
        print("Please enter URL in the format https://bitcointalk.org/index.php?topic=5057721.0")
        userPromptURL = input("Topic's URL: ")
        userPromptTopicName = input("Name of Coin/Thread: ")

        urlCustomBase = [ userPromptTopicName, userPromptURL]
        get_bitcointalk_posts(urlCustomBase)

def getCoinmarketcapUrls(crypto_currency):
    """
    Extracts the urls of a bitcointalk [ANN] thread to be parsed and downloaded
    :return: Name of entered crpyto currency, Urls of pages in bitcointalk [ANN] thread
    """

    print(r'Parsing ' + r'"https://coinmarketcap.com/currencies/' + crypto_currency + r'"...')
    try:
        response = urlopen(r'https://coinmarketcap.com/currencies/' + crypto_currency)
        soup = BeautifulSoup(response, 'lxml')
        base_url = soup.find('a', href=True, text='Announcement')['href']
    except:
        print('')
        print('ERROR: Announcement URl not found on coinmarketcap.com')
        print('Stopping script.')
        print('')
        return searchCoinmarketcap()

    return base_url

def searchCoinmarketcap():
    """
    Search for a Cryptocurrency's Bitcointalk Topic URL from its name
    using Coinmarketcap for the information
    """

    promptAns = input('Please enter a Cryptocurrency: ')
    results = getCoinmarketcapUrls(promptAns)
    print('Found coin {} with url {} '.format(promptAns, results))
    args = [promptAns, results]
    get_bitcointalk_posts(args)

def savedSessionCrawler():
    START = time.time()
    print('Scraping Tool Started!')

    with open('data/filteredList.csv', 'r') as AnnList:
        reader = csv.reader(AnnList)
        next(reader)
        AnnCsvList = list(reader)

    pool = ThreadPool(20)
    pool.map(get_bitcointalk_posts, AnnCsvList)
    
    print('Total scrape time in seconds : {}s'.format(time.time()-START))

def crawler_script():
        START = time.time()
        print('Scraping Tool Started!')

        with open('data/AnnList.csv', 'r') as csvfile_input, open('data/filteredList.csv', 'w') as csvfile_output:
            csv_input = csv.reader((x.replace('\0', '') for x in csvfile_input), delimiter=',')
            csv_output = csv.writer(csvfile_output, delimiter=',')
            header = ['Name', 'TopicUrl']
            csv_output.writerow(header)
            csv_output = csv.writer(csvfile_output, delimiter=',')
            next(csv_input)

            for row in csv_input:
                csv_output.writerow(row)

        with open('data/filteredList.csv', 'r') as AnnList:
            reader = csv.reader(AnnList)
            next(reader)
            AnnCsvList = list(reader)

        pool = ThreadPool(20)
        pool.map(get_bitcointalk_posts, AnnCsvList)
        
        print('Total scrape time in seconds : {}s'.format(time.time()-START))

def customCSVScrape():
        START = time.time()
        print('Enter a CSV filename exactly as it appears in the data/ directory')
        print('Example: AnnListCustom')
        print('Finds all URLs from the data/AnnListCustom.csv file')
        customCsvName = input("Filename: ")

        with open('data/' + customCsvName + '.csv', 'r') as csvfile_input, open('data/filteredList.csv', 'w') as csvfile_output:
            csv_input = csv.reader((x.replace('\0', '') for x in csvfile_input), delimiter=',')
            csv_output = csv.writer(csvfile_output, delimiter=',')
            header = ['Name', 'TopicUrl']
            csv_output.writerow(header)
            csv_output = csv.writer(csvfile_output, delimiter=',')
            next(csv_input)

            for row in csv_input:
                csv_output.writerow(row)

        with open('data/filteredList.csv', 'r') as AnnList:
            reader = csv.reader(AnnList)
            next(reader)
            AnnCsvList = list(reader)

        print('Scraping Tool Started!')
        pool = ThreadPool(20)
        pool.map(get_bitcointalk_posts, AnnCsvList)
        
        print('Total scrape time in seconds : {}s'.format(time.time()-START))

def menu_script():

    # Create the menu
    menu = ConsoleMenu("Welcome to Bitcointalk Topic Scraper", "Choose an option: ")

    # A FunctionItem runs a Python function when selected
    csvFunction_item = FunctionItem("Scrape Topic Links from Default AnnList.csv", crawler_script)
    customCsvFunction = FunctionItem("Scrape Topics based on Custom CSV", customCSVScrape)
    savedSessionFunction = FunctionItem("Load the remaining links from last CSV session", savedSessionCrawler)
    specificUrlFunction = FunctionItem("Enter a Specific Topic's URL: ", specificUrlSearch)
    searchCoinFunction = FunctionItem("Search for a Cryptocurrency to scrape", searchCoinmarketcap)

    menu.append_item(csvFunction_item)
    menu.append_item(customCsvFunction)
    menu.append_item(savedSessionFunction)
    menu.append_item(specificUrlFunction)
    menu.append_item(searchCoinFunction)
    menu.show()

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

    menu_script()