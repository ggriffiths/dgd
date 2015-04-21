import twitter #this will test the twitter api
import os
import sys
import string
import time
import re
import requests
import json
import urllib
import urllib2
import base64
import pymongo
from multiprocessing import Pool, Lock, Queue, Manager

def main(search_term):
    CONSUMER_KEY = 'RsORKWqt4GPomAGb0ndAVMGFt'
    CONSUMER_SECRET = 'oJG1BGj5HJ0wGROCfDIArW63KUqhbsju42XNZ9PRm6T7Hl1tgz'
    OAUTH_TOKEN = '3047116915-gixoMSHYzFiYUw72eE9smGDJMoefjV3v80Hzk3n'
    OAUTH_TOKEN_SECRET = 'ho043sAlnTaVkEOmpqdWuA6B04vRA1XhLheFOkSailGgH'
    ALCHEMY_KEY = '49d68b06acb5f1b49978b893fb138125d50bfb74' 

    # Get the Twitter OAuth
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
    twitter_api = twitter.Twitter(auth=auth)

    # Pull Tweets down from the Twitter API
    found_tweets = search(twitter_api, search_term, 50)

    # Enrich the body of the Tweets using AlchemyAPI
    enriched_tweets = enrich(ALCHEMY_KEY, found_tweets, sentiment_target = search_term)

    # Store data in MongoDB
    store(enriched_tweets)

    # Print some interesting results to the screen
    print_results()

    return

def oauth_login(): #Establishes connection for the use of twitter api #*****
    

    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
    CONSUMER_KEY, CONSUMER_SECRET)
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api


def search(twitter_api, q, max_results=200, **kw): 
    search_results = twitter_api.search.tweets(q=q, count=50, **kw)
    
    statuses = search_results['statuses']
    max_results = min(1000, max_results)
    
    for _ in range(1000): # 10*100 = 1000
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError, e: # No more results when next_results doesn't exist
            break
        kwargs = dict([ kv.split('=') 
                        for kv in next_results[1:].split("&") ])
        
        search_results = twitter_api.search.tweets(**kwargs)
        statuses += search_results['statuses']
        
        result = []
        for tweet in statuses:
            result.append([tweet['text'] , tweet['user']['location']])
            print 'ID: ', tweet['id_str'], '\n', 'Location:', tweet['user']['location'], '\nStart of tweet: \n', tweet['text'], '\nEnd of tweet. \n\n\n'

        if len(statuses) > max_results: 
            break
        
    return statuses

def enrich(credentials, tweets, sentiment_target = ''):
    # Prepare to make multiple asynchronous calls to AlchemyAPI
    apikey = credentials
    pool = Pool(processes = 10)
    mgr = Manager()
    result_queue = mgr.Queue()
    # Send each Tweet to the get_text_sentiment function
    for tweet in tweets:
        pool.apply_async(get_text_sentiment, (apikey, tweet, sentiment_target, result_queue))

    pool.close()
    pool.join()
    collection = []
    while not result_queue.empty():
        collection += [result_queue.get()]
    
    return collection

def get_text_sentiment(apikey, tweet, target, output):
    # Base AlchemyAPI URL for targeted sentiment call
    alchemy_url = "http://access.alchemyapi.com/calls/text/TextGetTextSentiment"
    
    # Parameter list, containing the data to be enriched
    parameters = {
        "apikey" : apikey,
        "text"   : tweet['text'].encode('utf-8'),
        "outputMode" : "json",
        "showSourceText" : 1
        }

    try:

        results = requests.get(url=alchemy_url, params=urllib.urlencode(parameters))
        response = results.json()

    except Exception as e:
        print "Error while calling TextGetTargetedSentiment on Tweet (ID %s)" % tweet['id']
        print "Error:", e
        return

    try:
        if 'OK' != response['status'] or 'docSentiment' not in response:
            return

        tweet['sentiment'] = response['docSentiment']['type']
        tweet['score'] = 0.
        if tweet['sentiment'] in ('positive', 'negative'):
            tweet['score'] = float(response['docSentiment']['score'])
        output.put(tweet)

    except Exception as e:
        print "D'oh! There was an error enriching Tweet (ID %s)" % tweet['id']
        print "Error:", e
        print "Request:", results.url
        print "Response:", response

    return

def store(tweets):
    # Instantiate your MongoDB client
    mongo_client = pymongo.MongoClient()
    
    # Retrieve (or create, if it doesn't exist) the twitter_db database from Mongo
    db = mongo_client.twitter_db
   
    db_tweets = db.tweets

    for tweet in tweets:
        db_id = db_tweets.insert(tweet)
 
    db_count = db_tweets.count()

    return

def print_results():

    print ''
    print '###############'
    print '#    Stats    #'
    print '###############'
    print ''   
    
    db = pymongo.MongoClient().twitter_db
    tweets = db.tweets

    num_positive_tweets = tweets.find({"sentiment" : "positive"}).count()
    num_negative_tweets = tweets.find({"sentiment" : "negative"}).count()
    num_neutral_tweets = tweets.find({"sentiment" : "neutral"}).count()
    num_tweets = tweets.find().count()

    if num_tweets != sum((num_positive_tweets, num_negative_tweets, num_neutral_tweets)):
        print "Counting problem!"
        print "Number of tweets (%d) doesn't add up (%d, %d, %d)" % (num_tweets, 
                                                                     num_positive_tweets, 
                                                                     num_negative_tweets, 
                                                                     num_neutral_tweets)
        sys.exit()
    if num_tweets != 0:
        print "SENTIMENT BREAKDOWN"
        print "Number (%%) of positive tweets: %d (%.2f%%)" % (num_positive_tweets, 100*float(num_positive_tweets) / num_tweets)
        print "Number (%%) of negative tweets: %d (%.2f%%)" % (num_negative_tweets, 100*float(num_negative_tweets) / num_tweets)
        print "Number (%%) of neutral tweets: %d (%.2f%%)" % (num_neutral_tweets, 100*float(num_neutral_tweets) / num_tweets)
        print ""

    return

if __name__ == "__main__":

    if not len(sys.argv) == 2:
        print "ERROR: invalid number of command line arguments"
        print "SYNTAX: python recipe.py <SEARCH_TERM>"
        print "\t<SEARCH_TERM> : the string to be used when searching for Tweets"
        sys.exit()

    else:
        main(sys.argv[1])

