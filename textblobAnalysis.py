"""
Author: Ronald DeLuca
Perform sentiment analysis on CryptoCurrency ICO Announcements using Textblob
"""

# The main package to help us with our text analysis
from textblob import TextBlob
import textblob
import pandas as pd
import csv  # For reading input files in CSV format
import re   # For doing cool regular expressions
import operator  # For sorting dictionaries
import numpy as np  # For plotting results
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from operator import methodcaller
from operator import attrgetter

# Intialize an empty list to hold all of our posts
posts = []

# A helper function that gives a user menu to choose what 
# the user wants to search for in their analysis
def let_user_pick(options):
    print("Welcome to CryptoAnalysis - Textblob Sentiment Analysis")
    print("Please choose an option:")
    for idx, element in enumerate(options):
        print("{}) {}".format(idx+1,element))
    i = input("Enter number: ")
    try:
        if 0 < int(i) <= len(options):
            return int(i)
    except:
        pass
    return None

# A helper function that removes all the non ASCII characters
# from the given string. Retuns a string with only ASCII characters.
def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

def assessments(str):
    blob = TextBlob(str)
    return blob.sentiment_assessments.assessments


def translated(series):
    blob = TextBlob(series)
    try:
        trans = blob.translate(to='en')
        return trans.raw
    except textblob.exceptions.NotTranslated:
        return ''

# LOAD AND CLEAN DATA
# Load in the input file and process each row at a time.
# We assume that the file has 16 columns:
# 0. The post Id.
# 1. The post Author.
# 2. The post UserId number.
# 3. The User's Merit.
# 4. The User's Activity.
# 5. The User's Position.
# 6. The TopicURL.
# 7. The time PostedAt.
# 8. The TaskId of the process that wrote the data record.
# 9. The PostNumber on the topic thread. (May appear different due to deleted posts)
# 10. The time the record was RetrievedAt.
# 11. The Status of the record retrieval.
# 12. The Body text of the post.
# 13. The TopicAuthor who created the whole topic.
# 14. The TopicTitle that hosts all related posts in the topic.
# 15. The IsScamHeaderPresent boolean which signals if the red scam text is present on topic.
#
# We create a data structure for each post:
# Id:       The ID of the post
# Body:     The original, unpreprocessed string of characters
# clean:    The preprocessed string of characters
# TextBlob: The TextBlob object, created from the 'clean' string

while True: 
    # Delete any previous filtered results
    oldFilterFile = "data/Posts_filtered.csv"
    f = open(oldFilterFile, "w+")
    f.close()

    with open('data/Posts.csv', 'rb') as csvfile_input, open('data/Posts_filtered.csv', 'wb') as csvfile_output:
        csv_input = csv.reader((x.replace('\0', '') for x in csvfile_input), delimiter=';')
        csv_output = csv.writer(csvfile_output, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        header = ['Id', 'Author', 'UserId', 'Merit', 'Activity', 'Position', 'TopicUrl', 'PostedAt', 'TaskId', 
        'PostNumber', 'RetrievedAt', 'Status', 'Body', 'TopicAuthor', 'TopicTitle', 'IsScamHeaderPresent']
        csv_output.writerow(header)
        csv_output = csv.writer(csvfile_output, delimiter=';', quotechar='"')

        # User menu options
        options = ["Search for an ICO", "Search for a User", "Search by URL"]
        choice = let_user_pick(options)

        if choice == 1:
            # Get the ICO user wants to search for
            try: input = raw_input
            except NameError: pass
            userPromptCoin = input("Enter an ICO to check: ")

            for row in csv_input:
                if userPromptCoin in row[14]:
                    csv_output.writerow(row)

        if choice == 2:
            # Get a user
            try: input = raw_input
            except NameError: pass
            userPromptAuthor = input("Enter a username to check: ")

            for row in csv_input:
                if userPromptAuthor in row[1]:
                    csv_output.writerow(row)

        if choice == 3:
            # Get a user
            try: input = raw_input
            except NameError: pass
            userPromptURL = input("Enter a URL to check: ")

            for row in csv_input:
                if userPromptURL in row[6]:
                    csv_output.writerow(row)
        
    with open('data/Posts_filtered.csv', 'rb') as csvfile_outputFilter:
        reader = csv.reader((x.replace('\0', '') for x in csvfile_outputFilter), delimiter=';')
        reader.next()
        for row in reader:

            post= dict()
            post['Id'] = row[0]
            post['Author'] = row[1]
            post['UserId'] = int(row[2])
            post['Merit'] = int(row[3])
            post['Activity'] = int(row[4])
            post['Position'] = row[5]
            post['TopicUrl'] = row[6]
            post['PostedAt'] = row[7]
            post['TaskId'] = int(row[8])
            post['PostNumber'] = int(row[9])
            post['RetrievedAt'] = row[10]
            post['Status'] = int(row[11])
            post['Body'] = row[12]
            post['TopicAuthor'] = row[13]
            post['TopicTitle'] = row[14]
            post['isScamHeaderPresent'] = row[15]

            # Ignore reposts(quotes)
            if re.match(r'^RT.*', post['Body']):
                continue

            post['clean'] = post['Body']

            # Remove all non-ascii characters
            post['clean'] = strip_non_ascii(post['clean'])

            # Normalize case
            post['clean'] = post['clean'].lower()

            # Remove URLS.
            post['clean'] = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', post['clean'])
            post['clean'] = re.sub(r'stratum[+]tcp?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', post['clean'])

            # Remove Mistranslated Characters
            post['clean'] = re.sub('&nbsp;', '', post['clean'])
            post['clean'] = re.sub('&amp;', '', post['clean'])
            post['clean'] = re.sub('&lt;', '', post['clean'])
            post['clean'] = re.sub('&gt;', '', post['clean'])
            post['clean'] = re.sub('&#[0-9][0-9];', '', post['clean'])
            post['clean'] = re.sub('&#[0-9][0-9][0-9];', '', post['clean'])
            post['clean'] = re.sub('&#[0-9][0-9][0-9][0-9];', '', post['clean'])
            post['clean'] = re.sub('&#[0-9][0-9][0-9][0-9][0-9];', '', post['clean'])
            post['clean'] = re.sub('&#[0-9][0-9][0-9][0-9][0-9][0-9];', '', post['clean'])
            post['clean'] = re.sub('&quot;', '', post['clean'])

            # Fix classic post lingo
            post['clean'] = re.sub(r'\bthats\b', 'that is', post['clean'])
            post['clean'] = re.sub(r'\bive\b', 'i have', post['clean'])
            post['clean'] = re.sub(r'\bim\b', 'i am', post['clean'])
            post['clean'] = re.sub(r'\bya\b', 'yeah', post['clean'])
            post['clean'] = re.sub(r'\bcant\b', 'can not', post['clean'])
            post['clean'] = re.sub(r'\bwont\b', 'will not', post['clean'])
            post['clean'] = re.sub(r'\bid\b', 'i would', post['clean'])
            post['clean'] = re.sub(r'wtf', 'what the fuck', post['clean'])
            post['clean'] = re.sub(r'\bwth\b', 'what the hell', post['clean'])
            post['clean'] = re.sub(r'\br\b', 'are', post['clean'])
            post['clean'] = re.sub(r'\bu\b', 'you', post['clean'])
            post['clean'] = re.sub(r'\bk\b', 'OK', post['clean'])
            post['clean'] = re.sub(r'\bsux\b', 'sucks', post['clean'])
            post['clean'] = re.sub(r'\bno+\b', 'no', post['clean'])
            post['clean'] = re.sub(r'\bcoo+\b', 'cool', post['clean'])

            # Emoticons?
            # NOTE: Turns out that TextBlob already handles emoticons well, so the
            # following is not actually needed.
            # See http://www.datagenetics.com/blog/october52012/index.html
            # post['clean'] = re.sub(r'\b:\)\b', 'good', post['clean'])
            # post['clean'] = re.sub(r'\b:D\b', 'good', post['clean'])
            # post['clean'] = re.sub(r'\b:\(\b', 'sad', post['clean'])
            # post['clean'] = re.sub(r'\b:-\)\b', 'good', post['clean'])
            # post['clean'] = re.sub(r'\b=\)\b', 'good', post['clean'])
            # post['clean'] = re.sub(r'\b\(:\b', 'good', post['clean'])
            # post['clean'] = re.sub(r'\b:\\\b', 'annoyed', post['clean'])

            # Create textblob object
            post['TextBlob'] = TextBlob(post['clean'])

            # Correct spelling (WARNING: SLOW)
            #post['TextBlob'] = post['TextBlob'].correct()
            print(post['clean'])
            posts.append(post)
        

    # DEVELOP MODELS
    for post in posts:
        post['polarity'] = float(post['TextBlob'].sentiment.polarity)
        post['subjectivity'] = float(post['TextBlob'].sentiment.subjectivity)

        if post['polarity'] >= 0.1:
            post['sentiment'] = 'positive'
        elif post['polarity'] <= -0.1:
            post['sentiment'] = 'negative'
        else:
            post['sentiment'] = 'neutral'

    posts_sorted = sorted(posts, key=lambda k: k['polarity'])

    # EVALUATE RESULTS
    # First, print out a few example posts from each sentiment category.
    # print "\n\nTOP NEGATIVE POSTS"
    negative_posts = [d for d in posts_sorted if d['sentiment'] == 'negative']
    # for post in negative_posts[0:100]:
    #     print "Id=%s, polarity=%.2f, clean=%s" % (post['Id'], post['polarity'], post['clean'])

    # print "\n\nTOP POSITIVE POSTS"
    positive_posts = [d for d in posts_sorted if d['sentiment'] == 'positive']
    # for post in positive_posts[-100:]:
    #     print "Id=%s, polarity=%.2f, clean=%s" % (post['Id'], post['polarity'], post['clean'])

    # print "\n\nTOP NEUTRAL POSTS"
    neutral_posts = [d for d in posts_sorted if d['sentiment'] == 'neutral']
    # for post in neutral_posts[0:500]:
    #     print "Id=%s, polarity=%.2f, clean=%s" % (post['Id'], post['polarity'], post['clean'])

    data = pd.read_csv('data/Posts_filtered.csv', sep=';')
    data.head()

    data['Blob'] = data.Body.apply(TextBlob)
    data['Polarity'] = data.Blob.apply(attrgetter('sentiment.polarity'))
    data['Subjectivity'] = data.Blob.apply(attrgetter('sentiment.subjectivity'))
    data['Assessment'] = data.Body.apply(assessments)
    # data['Detect_lang'] = data.Blob.apply(methodcaller('detect_language'))  # powered by google API
    # data['Translated'] = data.Body.apply(translated)
    print (data[['Body', 'Polarity', 'Subjectivity', 'Assessment']])

    # PLOTS
    # A histogram of the scores.
    x = [d['polarity'] for d in posts_sorted]
    num_bins = 21
    n, bins, patches = plt.hist(x, num_bins, density=1, facecolor='green', alpha=0.5)
    plt.xlabel('Polarity')
    plt.ylabel('Probability')
    plt.title(r'Histogram of polarity')
    # Tweak spacing to prevent clipping of ylabel
    plt.subplots_adjust(left=0.15)
    plt.show()

    # A pie chart showing the number of posts in each sentiment category
    pos = len(positive_posts)
    neu = len(negative_posts)
    neg = len(neutral_posts)
    labels = 'Positive', 'Neutral', 'Negative'
    sizes = [pos, neu, neg]
    colors = ['yellowgreen', 'gold', 'lightcoral']
    plt.pie(sizes, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')
    plt.show()

    while True:
        answer = raw_input('Run again? (y/n): ')
        if answer in ('y', 'n'):
            break
        print 'Invalid input.'
    if answer == 'y':
        continue
    else:
        print 'Goodbye'
        break