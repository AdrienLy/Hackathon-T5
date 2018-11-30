#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 10:58:33 2018

@author: margaux
"""
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import requests
from requests_oauthlib import OAuth1
from urllib.parse import parse_qs
import os
import pandas as pd
from datetime import datetime
import re

REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize?oauth_token="
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']

OAUTH_TOKEN = os.environ['OAUTH_TOKEN']
OAUTH_TOKEN_SECRET = os.environ['OAUTH_TOKEN_SECRET']

def setup_oauth():
    """Authorize your app via identifier."""
    # Request token
    oauth = OAuth1(CONSUMER_KEY, client_secret=CONSUMER_SECRET)
    r = requests.post(url=REQUEST_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)

    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]

    # Authorize
    authorize_url = AUTHORIZE_URL + resource_owner_key
    print ('Please go here and authorize: ' + authorize_url)

    verifier = raw_input('Please input the verifier: ')
    oauth = OAuth1(CONSUMER_KEY,
                   client_secret=CONSUMER_SECRET,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=verifier)

    # Finally, Obtain the Access Token
    r = requests.post(url=ACCESS_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)
    token = credentials.get('oauth_token')[0]
    secret = credentials.get('oauth_token_secret')[0]

    return token, secret


def get_oauth():
    oauth = OAuth1(CONSUMER_KEY,
                client_secret=CONSUMER_SECRET,
                resource_owner_key=OAUTH_TOKEN,
                resource_owner_secret=OAUTH_TOKEN_SECRET)
    return oauth

def DiffChars(str1, str2):
    tmp = []
    for ch in str1:
        if ch not in tmp:
            tmp.append(ch)
        else:
            pass
    return len(tmp)
    
def get_artist_twitter_id(name_to_look_for):
    """
    Get artist twitter ID (request) with string name as input
    """
    # Search request
    name = re.sub("\W"," ", name_to_look_for)
    r2 = requests.get(url = 'https://api.twitter.com/1.1/users/search.json?q='+ name, auth=oauth)
    if r2.status_code != 200:
        return '',0
    else:
        if len(r2.json()) < 2:  
            return '',0
        else:
            r2 = r2.json()[0:2]
            artist_id = ''
            for result in r2:
                if result['verified'] == True:
                    artist_id = result['id_str']
                    return artist_id, result['statuses_count']
                break
            return '',0
    
if __name__ == "__main__":
    
    date_format = '%a %b %d %H:%M:%S +0000 %Y'
    
    if not OAUTH_TOKEN:
        token, secret = setup_oauth()
        print ("OAUTH_TOKEN: " + token)
        print ("OAUTH_TOKEN_SECRET: " + secret)
    else:
        col_names = ['artiste','has_tweet', 'followers' , 'fav' , 'retweet', 'nbre tweet', 'tweet_freq']
        results_df = pd.DataFrame(columns=col_names)
        oauth = get_oauth()
        artists = pd.read_csv('top_artist_billboard_2015-2019', header=None)[0]
        for art in artists:
            artist_id, tweet_count = get_artist_twitter_id(art)
            if artist_id != '':
                r = requests.get(url="https://api.twitter.com/1.1/statuses/user_timeline.json?user_id=" + artist_id + "&count=200&include_rts=false", auth=oauth)
                timeline = r.json()
                if len(timeline) > 0:
                    followers_number = timeline[0]['user']['followers_count']
                    tweet_total = 1
                    retweet_number = []
                    favorite_number = []
                    date = []
                    for tweet in timeline:
                        # About a post
                        date.append(datetime.strptime(tweet['created_at'], date_format))
                        retweet_number.append(tweet['retweet_count'])
                        favorite_number.append(tweet['favorite_count'])
                    date_df = pd.DataFrame(date)
                    date_df[0] =  pd.to_datetime(date_df[0])
                    diff_date = date_df[0][-1:] - date_df[0][0]
                    moyenne_hebd = len(timeline) * 7 / abs(diff_date.iloc[0].days)
                    retweet_total = sum(retweet_number)
                    favorite_total = sum(favorite_number)
                    has_twitter_account = True
                    art_results = pd.DataFrame([[str(art), has_twitter_account, followers_number, favorite_total, retweet_total, tweet_count, moyenne_hebd]], columns=col_names)
                else:
                    art_results = pd.DataFrame([[str(art), False, 0, 0, 0, 0, 0]], columns=col_names)
            else:
                art_results = pd.DataFrame([[str(art), False, 0, 0, 0, 0, 0]], columns=col_names)
            results_df = results_df.append(art_results, ignore_index = True)

    y = pd.read_csv('top_artist_billboard_2015-2019', header = None )[1]
    df_concat = pd.concat([results_df, y], axis = 1)  
    df_concat.to_csv('twitter_data.csv')
    
    df_concat2 = df_concat.drop([0, 2], axis = 0)
    df_concat2['fav moyen'] = df_concat2['fav'] / (df_concat2['nbre tweet'] + 1)
    df_concat2.plot(y = 'followers', x = 1, style = 'o')
    df_concat2.plot(y = 'nbre tweet', x = 1, style = 'o')
    df_concat2.plot(y = 'retweet', x = 1, style = 'o')
    df_concat2 = df_concat2.loc[df_concat2['has_tweet'] == True]
    df_concat2.plot(y = 'retweet', x = 1, style = 'o')
    df_concat2.plot(y = 'tweet_freq', x = 1, style = 'o')
    df_concat2.plot.bar(x= 1, y='has_tweet')

    # TO COPY PASTE INTO NOTEBOOK
    import matplotlib.pyplot as plt
    df_concat = pd.read_csv('twitter_data.csv')

    df_concat2 = df_concat2.loc[df_concat2['has_tweet'] == True]
    
    plt.figure()
    df_concat2.plot(y = 'retweet', x = 1, style = 'o')
    plt.title('Nombre de mois dans le top 200 en fonction du nombre de retweets')

    plt.figure()
    df_concat2.plot(y = 'tweet_freq', x = 1, style = 'o')
    plt.title('Nombre de mois dans le top 200 en fonction de la fréquence de tweet')

    plt.figure()
    df_concat2.plot(y = 'followers', x = 1, style = 'o')
    plt.title('Nombre de mois dans le top 200 en fonction du nombre de followers')

