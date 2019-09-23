# Bitcointalk Topic Scraper
A Python 3 Web Scraper that loads a Bitcointalk.org topic URL and scrapes relevant post information for each post into a CSV. 

# Install
This scraper is built with [python3](https://www.python.org/downloads/). Note: You may need to set *alias python=python3*.

```
pip3 install -r requirements.txt
```

### Chromedriver
This scraper uses ChromeDriver - the WebDriver for Chrome. Please make sure you have the correct version installed relative to the version of Chrome/Chromium you have installed on your host machine [Download](https://chromedriver.chromium.org/downloads). Tested with Chrome 76, ChromeDriver 76.0.3809.126. 

Once you have the chromedriver file downloaded, change the *executable_path=* line in *crawler.py* to the correct path where chromedriver is located.

# Usage

## Normal Crawler
```
python crawler.py
```

## Proxy Crawler (Slower) (Work-In-Progress)
```
python proxy_crawler.py
```
Note: The proxy version of the crawler will use a random proxy chosen from **ProxyList.txt** and try to scrape posts with the same procedure contained within the normal crawler. This version is slower as it uses free proxies available online, and errors may occur as Bitcointalk may have banned or flagged these IPs. This version is still a Work-In-Progress and may not function as intended.

# Topic Links to Scrape

Topic Links are stored in a CSV file located in the **data/** directory.
The AnnList.csv file contains a list of Bitcointalk Cryptocurrency ICO announcements using the Name and TopicURL for each Topic. The AnnList CSV is delimited by ',' (comma). NOTE: This format is important to ensure that the reading/writing of the CSV data to the new filtered CSV is done correctly.

The default input for *crawler.py* is currently AnnList.csv.

The console gives the option to set a custom CSV file as the input for Name, TopicUrl into the scraper. When inputting the name of the file, just input the case-sensitive filename (without file extension) and the scraper will find that CSV in the *data/* folder. 

Each line of the CSV is an individual task for the crawler that takes one thread (max currently 4) to launch a webdriver for scraping one topic. The crawler will create a pool of 4 threads that will go through the CSV line by line and rate-limit the scraping of Bitcointalk to avoid aggrevating their scraping limit. 

The output of each scrape attempt will be a single CSV named with the format NameProvidedInCsv-TimeOfScrape.csv and located in the **data/raw_data** folder.

## Search by URL

There is a console menu option in the scraper to input just the Bitcointalk URL and the Name of the coin to search that URL directly, bypassing the need for an input CSV. This will be a single scrap on that URl. 

NOTE: Enter URLs in the format https://bitcointalk.org/index.php?topic=5057721.0 for the best results.

## Search Coinmarketcap for Name/TopicUrl

There is a console menu option to enter a cryptocurrency's name and the scraper will attempt to search CoinMarketCap.com for the Announcement Topic URL (if it is available). 

Note: Misspelling the name of a coin may cause an error in the search.