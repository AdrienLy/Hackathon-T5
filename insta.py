# coding: utf-8
import re
import sys
import json
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from multiprocessing import Pool

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






df = pd.read_csv('top_artist_billboard_2010-2019')
print(df.columns)
df['Artists'] = df['Artists'].str.replace(' ','')
df['Artists'] = df['Artists'].str.lower()



def test(df):
    df['followers'], df['posts'] = zip(*df['Artists'].apply(lambda x: insta(x)))
    return df

#Split data
df1 = df.iloc[0:602,:]
df2 = df.iloc[602:1204,:]
df3 = df.iloc[1204:1806,:]
df4 = df.iloc[1806:,:]
list = []
list.append(df1)
list.append(df2)
list.append(df3)
list.append(df4)
p = Pool(4)
df_r = pd.concat(p.map(test, list), axis=0, ignore_index=True)

df_r.to_csv('followers_top_artist_billboard.csv', sep=';', index=False)
