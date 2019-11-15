# Bitcointalk Topic Scraper & VADER Sentiment Analysis
A Python 3 Web Scraper that loads a Bitcointalk.org topic URL and scrapes relevant post information for each post into a CSV. 

## Install
This scraper is built with [python3](https://www.python.org/downloads/). Note: You may need to set *alias python=python3*.

Once you have python3 properly installed on your machine, change to the directory of this downloaded project and run:

```
pip3 install -r requirements.txt
```

#### Chromedriver
This scraper uses ChromeDriver - the WebDriver for Chrome. Please make sure you have the correct version installed relative to the version of Chrome/Chromium you have installed on your host machine [Download](https://chromedriver.chromium.org/downloads). Tested with Chrome 76, ChromeDriver 76.0.3809.126. Also tested with Chrome 78 using ChromeDriver 78.0.3904.70.

Once you have the chromedriver file downloaded, change the *driver_path =* line in *crawler.py* & *proxy_crawler.py* to the correct path where chromedriver is located. 

## Usage

This repository contains two separate python3 files *crawler.py* & *proxy_crawler.py*. Each program contains similar options that will attempt to scrape Bitcointalk Topic URLs into a CSV output. The main difference is that the normal crawler uses up to 4 scraping threads (instances of a single scrape) at a time to scrape up to 4 URLs simultaneously. This is done over a single IP address (the IP address of the host machine this program is running on).

As Bitcointalk enforces a rate limit to not exceed a request threshold, the normal crawler is limited to 4 threads and a specific wait period for changing URLs. If desired, the proxy_crawler.py allows the same crawler to run up to 20 threads simultaneously, each using a different proxy IP address located in the *ProxyList.txt* file. As these are freely provided, publicly available proxies, they are often much slower to connect and perform the same amount of work as the normal crawler.py. 

### Normal Crawler
```
python crawler.py
```

(may need to use python3 crawler.py if your system's PATH does not alias python=python3)

### Proxy Crawler (Slower) (Work-In-Progress)
```
python proxy_crawler.py
```
(may need to use python3 proxy_crawler.py if your system's PATH does not alias python=python3)

Note: The proxy version of the crawler will use a random proxy chosen from **ProxyList.txt** and try to scrape posts with the same procedure contained within the normal crawler. This version is slower as it uses free proxies available online, and errors may occur as Bitcointalk may have banned or flagged these IPs. This version is still a Work-In-Progress and may not function as intended.

### Topic Links to Scrape

Topic Links are stored in a CSV file located in the **data/** directory.
The AnnList.csv file contains a list of Bitcointalk Cryptocurrency ICO announcements using the Name and TopicURL for each Topic. The AnnList CSV is delimited by ',' (comma). NOTE: This format is important to ensure that the reading/writing of the CSV data to the new filtered CSV is done correctly.

The default input for *crawler.py* is currently AnnList.csv. (Console-menu option #1)

The console gives the option to set a custom CSV file as the input for Name, TopicUrl into the scraper (Console-menu option #2). When inputting the name of the file, just enter the case-sensitive filename (without file extension) into the prompt that appears and the scraper will find that CSV in the *data/* folder. 

Each line of the CSV is an individual task for the crawler that takes one thread (max currently 4) to launch a webdriver for scraping one topic. The crawler will create a pool of 4 threads that will go through the CSV line by line and rate-limit the scraping of Bitcointalk to avoid aggrevating their scraping limit. 

The output of each scrape attempt will be a single CSV named with the format NameProvidedInCsv-TimeOfScrape.csv and located in the **data/raw_data** folder.

### Search by URL

There is a console menu option in the scraper to input just the Bitcointalk URL and the Name of the coin to search that URL directly, bypassing the need for an input CSV. This will be a single scrap on that URl. 

NOTE: Enter URLs in the format https://bitcointalk.org/index.php?topic=5057721.0 for the best results.

### Search Coinmarketcap for Name/TopicUrl

There is a console menu option to enter a cryptocurrency's name and the scraper will attempt to search CoinMarketCap.com for the Announcement Topic URL (if it is available). 

Note: Misspelling the name of a coin may cause an error in the search.

### Additional Options

To aide in the scraping process of multiple URLs coming from an input CSV that may have not finished properly on its first scrape attempt, several options have been made available in these programs. Console-Menu option #3 provides a quick option to continue scraping the leftover input CSVs that were not completely scraped in the last session. 
>Example: Input CSV had 15 URLs, 5 finished, program closed. User restarts program, types in option 3, remaining 10 URLS are then scraped to complete the task.

Console-menu option #7 checks the *data/raw_data/* folder based on an input CSV to ensure that all input URLs were output into CSVs. Outputs results into *data/searchResults.csv*
>Example: AnnListCustom.csv had 13 URLs, it finished scraping. User launches program, enters option 7, types in AnnListCustom, program searchs *data/raw_data/* for all CSVs and finds that 1 URL was not scraped, outputs *data/searchResults.csv* with one line containing that 1 URL found in the search.

Console-menu option #8 uses the *data/searchResults.csv* that were made from option #7 as the input CSV for a new scraping process. 
>Example: searchResults.csv has 1 URL. User launches program, enters option 8, crawler begins scraping that 1 URL from the searchResults.csv and outputs that URL's scraping results into the appropriate output CSV.

### Menu Options

These programs contain a Console Menu when launched that offer options to accomplish the scraping task desired:

1. Scrape Topic Links from Default AnnList.csv
2. Scrape Topics based on Custom CSV
3. Load the remaining links from last CSV session
4. Enter a Specific Topic's URL
5. Search for a Cryptocurrency to scrape
6. Check a specific CSV to see if it was scraped
7. Use searchResults as new scraping task
8. Exit

# VADER Sentiment Analysis Jupyter Notebook

Included in this repository is a Jupyter Notebook named *vaderSentAnalysis.ipynb*. This Jupyter notebook contains an adaptation of a VADER Sentiment Analysis routine run alongside Textblob and language pre-processing methods to evaluate the scraped data from a Bitcointalk.org Cryptocurrency Topic.

For this Sentiment Analysis, the notebook contains methods to help refine text for analysis in a cryptocurrency and social media context. As forum posts may contain usage of emojis, crypto slang, textspeak, etc, the posts are cleaned in this notebook to prepare the analysis tool to achieve high accuracy in understanding the intentions of the poster. This implementation also utilizes a custom lexicon addition (which may be edited further) to enable cryptocurrency specific words to have a sentiment value beyond the default words that may omit understanding when calculating compound sentiment values of a post.

## Install
This Jupyter notebook is built with [python3](https://www.python.org/downloads/). Note: You may need to set *alias python=python3*. Additionally, the [Jupyter](https://jupyter.org/install) Software must be installed to view and run the notebook. 

Once you have python3 & Jupyter notebook properly installed on your machine, change to the directory of this downloaded project and run:

```
pip3 install -r requirements.txt
```

If you plan on taking advantage of spaCy, their language models may be changed as desired. Default install should be:

```
python3 -m spacy download en_core_web_sm
```

## Usage

Run the notebook from the Jupyter Notebook page in a browser by running:

```
jupyter notebook
```

Find the *vaderSentAnalysis.ipynb* file and open it.

Once the notebook is open, change the input csvName based on a CSV file located in the *data/raw_data/* folder of this repository. This input name is located in the second cell:

```
csvName = 'GTC_20190925-021514'   # Change this string value to the file you want
```

Once the input csvName is changed to the Bitcointalk Topic that is desired to run this analysis notebook on, Run All Cells in order.

## Notebook sections

The VADER Sentiment Analysis Jupyter Notebook is broken down into order of cells to achieve specific methods towards the final results and their graphical outputs.

### Imports

The notebook contains packages to analyze CSVs, utilize Textblob and VADER, take advantage of tools used by spaCy, wordcloud & matplotlib for graphical display of results.

### Input CSV

Section to define the desired input CSV. Change the name of the CSV to the specific filename for the rest of the Jupyter Notebook to understand which file you want to analyze for input.

### VADER methods & Language Pre-processing

These two sections contain methods to define the Analyzer, inject an additional wordlist with custom sentiment values that would allow more words to be added beyond the default VADER [lexicon](https://github.com/cjhutto/vaderSentiment/blob/master/vaderSentiment/vader_lexicon.txt). These additional words will make the compound sentiment values have more meaning as they now understand more words accurately in the context that VADER is evaluating.

Additional VADER methods run the input text against the lexicon for a score and rates them positive, negative or neutral based on the compound value in the addition of each word in a sentence.

For language pre-processing, this notebook takes advantage of stripping unnecessary and non-ascii characters. The words are normalized to remove post lingo, cryptocurrency-specific lingo, and clean up URLs.

Once pre-processed and sent to VADER, the posts are assigned a compound sentiment value and sorted based on positivity, negativity and neutrality. These sorted posts are prepared for output display.

### Histogram of Compound Scores

Using matplotlib, a graphical output of the frequency of compound scores from -1 (extremely negative) to 1 (extremely positive). This histogram shows that for the input CSV (which is an entire Bitcointalk.org topic), the posts for that specific URL may have higher frequencies that trend towards a specific type of sentiment.

### Pie Chart of Compound Scores

Using matplotlib, a graphical output of the ratings based on positivity, negativity and neutrality is split into three colored sections for a pie chart. The percentages of each portion is displayed to give further visual description to a Bitcointalk.org topic's sentiment.

### Wordclouds

Using the wordcloud package, the most common words are displayed for:
- Negative Posts
- Positive Posts
- Neutral Posts

Each wordcloud highlights frequency of words and displays the size of the word in relation to this. Knowing the most common words used in specific contexts helps understand how a poster may view a specific Bitcointalk.org topic.


### Topic Post Results using VADER and Textblob

In this section, the notebook displays the post's text itself along with the polarity, subjectivity provided by Textblob and compares it to the VADER compound rating.

### Is this Cryptocurrency a Scam?

Based on reports leading to acknowledgement of a scam possibility, combined with the sentiment analysis results, a plausible determination is shown. 
***NOTE***: These results should not be taken as fact, but rather as an aide to determine the possibility that a particular cryptocurrency could be showing signs of a scam attempt.

The likelihood of the cryptocurrency being a scam is based on several characteristics sorted into categories:
- **Very Unlikely**: Shows minimal negativity, not reported as scam, low use of the word *scam*
- **Unlikely**: Shows low negativity, not reported as scam, low use of the word *scam*
- **Possible**: Shows moderative negativity, moderate use of the word *scam* and may have been reported
- **Likely**: Shows above normal negativity, above normal use of the word *scam* and may have been reported
- **Very Likely**: Shows above normal negativity, above normal use of the word *scam* and was reported
- **Almost Certain**: Shows high negativity, high usage of the word scam and was reported as *scam*

The results of this analysis are shown in the Jupyter Notebook and mention the likelihood along with a note if the scam was reported on Bitcointalk.org as showing signs of a scam attempt. These results show the word count of *scam* and its ranking compared to other words in the forum topic. Based on the increasing negativity, the ranking of the usage of *scam* in comparison to other word choices and the potential reporting of a scam, this analysis places emphasis on a building negativity relative to other posts and ranks the likelihood accordingly.

### Output to HTML, MD, PDF

After the notebook has been run, the results are converted to HTML and made into a separate file available to view in the *data/processed/* directory of this repository. The file *(nameOfInputCSV).html* may be opened in a browser to view a quick display of the results of the VADER Analysis program.

There are two other converts which are currently disabled in the conversion cell (markdown & PDF export). These can be enabled at your discretion, however the PDF export requires [texlive](https://www.tug.org/texlive/) to be installed and located in PATH. NOTE: There may be CSS issues which do not show the updated outputs, please clear cache and refresh browser to find update custom.CSS file. Also, ensure that these output conversions to HTML, MD and/or PDF happen after the notebook has run and is saved. You may need to run the conversion cell again to get the output cells to show correctly in the processed files.