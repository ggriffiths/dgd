import twitter #this will test the twitter api

def oauth_login(): #Establishes connection for the use of twitter api #*****
    CONSUMER_KEY = 'RsORKWqt4GPomAGb0ndAVMGFt'
    CONSUMER_SECRET = 'oJG1BGj5HJ0wGROCfDIArW63KUqhbsju42XNZ9PRm6T7Hl1tgz'
    OAUTH_TOKEN = '3047116915-gixoMSHYzFiYUw72eE9smGDJMoefjV3v80Hzk3n'
    OAUTH_TOKEN_SECRET = 'ho043sAlnTaVkEOmpqdWuA6B04vRA1XhLheFOkSailGgH'

    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
    CONSUMER_KEY, CONSUMER_SECRET)
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api


def search(api, word, count = 5): #will search for the word
    ###
    # search, in order to work it requires:
    # api - an oauth connection varible
    # word - the word that is being searched
    # count - and the number of tweets to be searched, default 5
    # Note: you can only make 450 app auth calls within 15 mins
    # Returns list of lists [[tweet content, location]]
    ###
    search = api.search.tweets(q=word, count=count)
    tweets = search['statuses']
    result = []
    for tweet in tweets:
        result.append([tweet['text'] , tweet['user']['location']])
        print 'ID: ', tweet['id_str'], '\n', 'Location:', tweet['user']['location'], '\nStart of tweet: \n', tweet['text'], '\nEnd of tweet. \n\n\n'
    return result
                
def run(): #Testing purposes
    twitter_api = oauth_login()
    #print twitter_api.search.tweets(q='hello', count=1)
    result = search(twitter_api, 'party')
    print result
