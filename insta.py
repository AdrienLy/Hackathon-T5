# coding: utf-8
import re
import sys
import json
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

header =   {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 Firefox/62.0'}

def insta(pseudo):
    r = requests.get(f"https://www.instagram.com/{pseudo}", headers=header)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content)
        scripts = soup.find_all('script', type="text/javascript",\
                                text=re.compile('window._sharedData'))
        stringified_json = scripts[0].get_text()\
                                     .replace('window._sharedData = ', '')[:-1]
        test = json.loads(stringified_json)['entry_data']['ProfilePage'][0]
        df = pd.DataFrame(test['graphql']['user'])
        df = pd.DataFrame(df[['username', 'edge_followed_by',\
                              'edge_owner_to_timeline_media']])
        df = df. drop(['edges', 'page_info'], axis=0)
        print(pseudo, df.loc['count', 'edge_followed_by'], df.loc['count', 'edge_owner_to_timeline_media'])
        return float(df.loc['count', 'edge_followed_by']), float(df.loc['count', 'edge_owner_to_timeline_media'])
    return np.NaN, np.NaN

# print(insta("beyonce"))

df = pd.read_csv('chart_UK_top40_nospace.csv')
print(df.columns)
df['Artistes'] = df['Artistes'].str.lower()
df['followers'], df['posts'] = zip(*df['Artistes'].apply(lambda x: insta(x)))
df.to_csv('follow.csv', sep=';', index=False)
print(df)
