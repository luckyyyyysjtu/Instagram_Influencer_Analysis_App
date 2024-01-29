#!/usr/bin/env python
# coding: utf-8
#File Name: twitter.py
#C1_Group3
#Name: Xinyi Yang, Yuetian Sun, Yi Guo, Man Luo, Yining Lu
#Andrew ID: xinyiy2, yuetians, yiguo, manluo, yininglu
#imported by: driver.py

"""
This package aims to provide users an overview of what is popular on Twitter 
based on certain keywords. If users input a certain industry, the function will 
return a list of most popular tweets based on the hashtag suggestions. 
In addition, if users choose to input a keyword of his or her interest, 
the function will return the most popular tweets based on the specific keyword
of choice. In addition, a wordCloud will be presented based on the frequency
of words mentioned in these popular tweets. Users are able to directly extract 
most relevant related words based on the wordClouds. 

"""



import textblob
import wordcloud
import tweepy
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import nltk
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import wordnet as wn
#nltk.download('omw-1.4')
#nltk.download('wordnet')
import spacy
import en_core_web_sm
from spacy import displacy
from wordcloud import WordCloud
from tabulate import tabulate

lemmatizer = WordNetLemmatizer()
plt.style.use('fivethirtyeight')

def enterKeyWord(keyWords):
    
    access_token = "1569478264686809088-Yd6qvxBMYVzraeJEK3U1T7keRWHjAB"
    access_token_secret = "1FFYp0tsUN00y3HdSNPyFkmJOeVdfT0n0o73ebJwOcvUL"
    
    api_key = "THPNs612Gy1SOEBa8J4iFbymS"
    api_key_secret = "ENZKtKwL6I6ul1UT8d97H5vmqS5BWBDLveWuy6DvxjdyfuQ66d"
    
    
    #authentification
    auth = tweepy.OAuthHandler(
       api_key, api_key_secret,
       access_token, access_token_secret)
    api = tweepy.API(auth)
    
    
    def printtweetdata(n, ith_tweet):
            print()
            print(f"Tweet {n}:")
            print(f"Username:{ith_tweet[0]}")
            print(f"Description:{ith_tweet[1]}")
            print(f"Location:{ith_tweet[2]}")
            print(f"Following Count:{ith_tweet[3]}")
            print(f"Follower Count:{ith_tweet[4]}")
            print(f"Total Tweets:{ith_tweet[5]}")
            print(f"Retweet Count:{ith_tweet[6]}")
            print(f"Tweet Text:{ith_tweet[7]}")
            print(f"Hashtags Used:{ith_tweet[8]}")
    
    
    #scrape data from Twitter 
    def scrape(words, date_since, numtweet):
     
            # Creating DataFrame using pandas
            db = pd.DataFrame(columns=['username',
                                       'description',
                                       'location',
                                       'following',
                                       'followers',
                                       'totaltweets',
                                       'retweetcount',
                                       'text',
                                       'hashtags'])
    
            tweets = tweepy.Cursor(api.search_tweets,
                                   words, lang="en",
                                   since_id=date_since,
                                   tweet_mode='extended').items(numtweet)
     
    
            list_tweets = [tweet for tweet in tweets]
     
            # Counter to maintain Tweet Count
            i = 1
     
            # we will iterate over each tweet in the
            # list for extracting information about each tweet
            for tweet in list_tweets:
                    print("#############################################")
                    username = tweet.user.screen_name
                    description = tweet.user.description
                    location = tweet.user.location
                    following = tweet.user.friends_count
                    followers = tweet.user.followers_count
                    totaltweets = tweet.user.statuses_count
                    retweetcount = tweet.retweet_count
                    hashtags = tweet.entities['hashtags']
     
                    # Retweets can be distinguished by
                    # a retweeted_status attribute,
                    # in case it is an invalid reference,
                    # except block will be executed
                    try:
                            text = tweet.retweeted_status.full_text
                    except AttributeError:
                            text = tweet.full_text
                    hashtext = list()
                    for j in range(0, len(hashtags)):
                            hashtext.append(hashtags[j]['text'])
     
                    # Here we are appending all the
                    # extracted information in the DataFrame
                    ith_tweet = [username, description,
                                 location, following,
                                 followers, totaltweets,
                                 retweetcount, text, hashtext]
                    db.loc[len(db)] = ith_tweet
     
                    # Function call to print tweet data on screen
                    # only print top 10 tweets
                    if i < 11:
                        printtweetdata(i, ith_tweet)
                    
                    i = i+1
            
            filename = f'Twitter_{keyWords}.csv'
            db.to_csv(filename,index=False,encoding='utf_8_sig')
    
            return db
    
   
    words = keyWords
    #Results will show starting from the date below 
    date_since = '2010-01-01'
     
    # number of tweets you want to extract in one run
    numtweet = 200
    df = scrape(words, date_since, numtweet)
    print('Scraping has completed!')
    
    
    #Show Scraped Tweets Sorted by number of retweetcount
    df = df.sort_values(by='retweetcount', ascending=False)
    df = df[df['retweetcount'] > 0]
    df = df.reset_index()


    # from spacy.lang.en.examples import sentences 
    nlp = spacy.load("en_core_web_sm")
    nouns = []
    
    for twt in df['text']:
        doc = nlp(twt)
        for token in doc:
            if token.pos_ == "NOUN":
                nouns.append(token.orth_)
    
    final = [item for item in nouns if len(item) > 1 and len(item)<10]
    
    

    lemmatized_output = ' '.join([lemmatizer.lemmatize(item) for item in final])
        
    stop_words =[words]
    
    wordcloud = WordCloud(stopwords = stop_words, width = 1000, height = 500,collocations=False).generate(lemmatized_output)
    plt.figure(figsize=(15,8))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig("your_file_name"+".png", bbox_inches='tight')
    plt.show()
    plt.close()

