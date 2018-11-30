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

def get_artist_twitter_id(name_to_look_for):
    """
    Get artist twitter ID (request) with string name as input
    """
    # Search request
    r2 = requests.get(url = 'https://api.twitter.com/1.1/users/search.json?q='+ name_to_look_for, auth=oauth)
    r2 = r2.json()
    artist_id = ''
    for result in r2:
        if result['verified'] == True:
            artist_id = result['id_str']
        break
    print(result)
    print(result['listed_count'])
    return artist_id, result['statuses_count']

if __name__ == "__main__":
    if not OAUTH_TOKEN:
        token, secret = setup_oauth()
        print ("OAUTH_TOKEN: " + token)
        print ("OAUTH_TOKEN_SECRET: " + secret)
    else:
        col_names = ['artiste', 'followers' , 'fav' , 'retweet', 'nbre tweet']
        results_df = pd.DataFrame(columns=col_names)
        oauth = get_oauth()
        artists = ['rihanna', 'jain']
        for art in artists:
            artist_id, tweet_count = get_artist_twitter_id(art)
            print(artist_id)
            r = requests.get(url="https://api.twitter.com/1.1/statuses/user_timeline.json?user_id=" + artist_id + "&count=200&include_rts=false", auth=oauth)
            timeline = r.json()
            print(len(timeline))
            followers_number = timeline[0]['user']['followers_count']
            tweet_total = 1
            retweet_number = []
            favorite_number = []
            date = []
            for tweet in timeline:
                # About a post
                date.append(tweet['created_at'])
                retweet_number.append(tweet['retweet_count'])
                favorite_number.append(tweet['favorite_count'])
            retweet_total = sum(retweet_number)
            favorite_total = sum(favorite_number)
            art_results = pd.DataFrame([[str(art), followers_number, favorite_total, retweet_total, tweet_count]], columns=col_names)
            results_df = results_df.append(art_results, ignore_index = True)

