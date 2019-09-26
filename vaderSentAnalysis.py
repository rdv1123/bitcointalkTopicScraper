# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'

#%%
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob.base import BaseSentimentAnalyzer
from textblob.sentiments import NaiveBayesAnalyzer, PatternAnalyzer
from textblob.classifiers import NaiveBayesClassifier
import os
from textblob import TextBlob
import textblob
import pandas as pd
from operator import methodcaller
from operator import attrgetter
import nltk
pd.options.display.max_colwidth = 500


#%%
# os.chdir('/Users/matthewson/Dropbox (UFL)/Projects/Scams/from Matthew/sentiment analysis')
data = pd.read_csv('diamond_sample.csv')
data['Time'] = pd.to_datetime(data.Time)
data.head()


#%%
# nltk.download('movie_reviews')
# do this once: grab the trained model from the web
# nltk.download('vader_lexicon')
Analyzer = SentimentIntensityAnalyzer()
Analyzer.lexicon

#%% [markdown]
# # Comparison among analyzers 
# 1. NaiveBayesAnalyzer using movie_reviews from nltk (TextBlob default, performs worst)
# 2. PatternAnalyzer from pattern
# 3. NativeBayseAnalyzer using vader_lexicon 

#%%
# from operator import attrgetter
# Reffering from https://textblob.readthedocs.io/en/dev/advanced_usage.html
blob1 = TextBlob('This project I think is amazing')
blob2 = TextBlob('This project I think is amazing',
                 analyzer=NaiveBayesAnalyzer())  # aww it sucks...
blob3 = TextBlob('This project I think is amazing', analyzer=PatternAnalyzer())
blob4 = Analyzer.polarity_scores('This project I think is amazing')
print(blob1.sentiment, '\n', blob2.sentiment,
      '\n', blob3.sentiment, '\n', blob4)
# TextBlob uses PatternAnalyzer as a default analyzer.

#%% [markdown]
# # Scam test

#%%
blob1 = TextBlob('this is a scam.')
blob2 = Analyzer.polarity_scores('this is a scam')
print(f'{blob1.sentiment} <--- TextBlob sentiment result, does not catch scam',
      '\n', f'{blob2} <--- VADER sentiment result')
# VADER Works better.


#%% [markdown]
# # About the scoring system VADER (Valence Aware Dictionary and sEntiment Reasoner):
# 
# DESCRIPTION: <br>
# Empirically validated by multiple independent human judges, VADER incorporates a "gold-standard"<br>
#  sentiment lexicon that is especially attuned to microblog-like contexts.
# 
# The VADER sentiment lexicon is sensitive both the polarity and the intensity of sentiments <br>
# expressed in social media contexts, and is also generally applicable to sentiment analysis in <br>
# other domains.
# 
#     Sentiment ratings from 10 independent human raters 
#     (all pre-screened, trained, and quality checked for optimal inter-rater reliability). 
#     Over 9,000 token features were rated on a scale from "[–4] Extremely Negative" to 
#     "[4] Extremely Positive", with allowance for "[0] Neutral (or Neither, N/A)". 
#     We kept every lexical feature that had a non-zero mean rating, and whose standard deviation
#     was less than 2.5 as determined by the aggregate of those ten independent raters. 
#     This left us with just over 7,500 lexical features with validated valence scores that
#     indicated both the sentiment polarity (positive/negative), and the sentiment intensity on
#     a scale from –4 to +4. For example, the word "okay" has a positive valence of 0.9, 
#     "good" is 1.9, and "great" is 3.1, whereas "horrible" is –2.5, the frowning emoticon :( 
#     is –2.2, and "sucks" and it's slang derivative "sux" are both –1.5.
# 
# The compound score is computed by summing the valence scores of each word in the lexicon,
# adjusted according to the rules, and then normalized to be between -1 (most extreme negative)
# and +1 (most extreme positive). This is the most useful metric if you want a single 
# unidimensional measure of sentiment for a given sentence.
# Calling it a 'normalized, weighted composite score' is accurate.
# 
# It is also useful for researchers who would like to set standardized thresholds for 
# classifying sentences as either positive, neutral, or negative. Typical threshold values
# (used in the literature cited on this page) are:
# 
#     positive sentiment: compound score >= 0.05
#     neutral sentiment: (compound score > -0.05) and (compound score < 0.05)
#     negative sentiment: compound score <= -0.05
# 
# The pos, neu, and neg scores are ratios for proportions of text that fall in each category <br>
# (so these should all add up to be 1... or close to it with float operation).<br>
# These are the most useful metrics if you want multidimensional measures of sentiment for a given<br>
#  sentence.
# 
#%% [markdown]
# https://stackoverflow.com/questions/40481348/is-it-possible-to-edit-nltks-vader-sentiment-lexicon
# https://stackoverflow.com/questions/54831079/cannot-update-vader-lexicon
# 
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# new_words = {
#     'foo': 2.0,
#     'bar': -3.4,
# }
# 
# SIA = SentimentIntensityAnalyzer()
# 
# SIA.lexicon.update(new_words)
# If you wish to remove words, use the '.pop' function:
# 
# SIA = SentimentIntensityAnalyzer()
# 
# SIA.lexicon.pop('no')

#%%


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


data['Blob'] = data.Body.apply(TextBlob)
data['Polarity'] = data.Blob.apply(attrgetter('sentiment.polarity'))
data['Subjectivity'] = data.Blob.apply(attrgetter('sentiment.subjectivity'))
data['Assessment'] = data.Body.apply(assessments)
# data['Detect_lang'] = data.Blob.apply(
#     methodcaller('detect_language'))  # powered by google API
# data['Translated'] = data.Body.apply(translated)
data['Vader_sentiment'] = data.Body.apply(Analyzer.polarity_scores)
data['Vader_compound'] = data['Vader_sentiment'].apply(lambda x: x['compound'])

#%% [markdown]
# # Comparison of the results

#%%
data[['Body', 'Polarity', 'Vader_compound', 'Subjectivity',
      'Vader_sentiment']]


#%% [markdown]
# # Updating the dictionary

#%%
# Before updating word 'enough'
print(Analyzer.polarity_scores('not so good'))
print(Analyzer.polarity_scores('not good'))
print(Analyzer.polarity_scores('good'))
print(Analyzer.polarity_scores('enough'))
print(Analyzer.polarity_scores('not enough'))


#%%
new_words = {'enough': 2}  # give positive score on enough
Analyzer.lexicon.update(new_words)

print(Analyzer.polarity_scores('not so good'))
print(Analyzer.polarity_scores('not good'))
print(Analyzer.polarity_scores('good'))
print(Analyzer.polarity_scores('enough'))
print(Analyzer.polarity_scores('not enough'))


#%%

os.system('jupyter nbconvert --to html demo4.ipynb')


#%%



