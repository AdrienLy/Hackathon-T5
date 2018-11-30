import requests
from io import StringIO
import pandas as pd
from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup

def get_spotify_token():
    r = requests.post('https://accounts.spotify.com/api/token/', data = {'grant_type':'client_credentials'}, headers={"Authorization": "Basic ZDNhMTBkYjU0MTkxNGY5OGI4OTJjMzFmOWMyYjU0Y2I6ZDUxYTBjNzgzZDdhNDFiOTg2MGIzMGQ0NDdlYjliMzk="})
    return r.json()["access_token"]

def get_audio_analysis(song_id):
    token = get_spotify_token()
    r = requests.get(f"https://api.spotify.com/v1/audio-analysis/{song_id}", headers={"Authorization": f"Bearer {token}"})
    return r

def get_all_audio_analysis(song_ids):
    for song_id in song_ids:
        r = get_audio_analysis(song_id)

def get_spotify_top_200_dates():
    d1 = date(2017, 1, 1)  # start date
    d2 = date(2018, 11, 28)  # end date

    delta = d2 - d1         # timedelta

    dates = []
    for i in range(delta.days + 1):
        d = d1 + timedelta(i)
        dates.append(d.__str__())

    return dates

def get_dates():
    html_doc = requests.get("https://spotifycharts.com/").text
    soup = BeautifulSoup(html_doc, 'html.parser')
    lis = soup.select(".responsive-select")[2].select("li")
    dates = []
    for li in lis:
        date = li.text
        date = datetime.strptime(date, "%m/%d/%Y").__str__()[0:10]
        dates.append(date)
    return dates

def get_spotify_top_200_on_date(date):
    print(date)
    r = requests.get(f"https://spotifycharts.com/regional/global/daily/{date}/download")

    return pd.read_csv(StringIO(r.text), sep=",")

def get_spotify_top_200_history():
    dates = get_dates()
    dfs = []
    for date in dates:
        df = get_spotify_top_200_on_date(date)
        dfs.append(df)
    new_df = pd.concat(dfs)
    new_df.to_csv("billboard_spotify.csv")
    return new_df

def get_track_ids():
    track_url_col = "Unnamed: 4"
    _df = pd.read_csv("billboard_spotify.csv")
    df = _df[_df[track_url_col] != "URL"]
    track_df = df[track_url_col]
    return track_df.str.replace('https://open.spotify.com/track/', '')

def fetch_song_audio_features(token, df, start, end):
    ids = df[start:end].to_csv(index=False).replace('\n', ',')[:-1]
    r = requests.get(f"https://api.spotify.com/v1/audio-features/?ids={ids}"[:-1], headers={"Authorization": f"Bearer {token}"})
    return r.json()["audio_features"]

def make_audio_features_df(input_df):
    token = get_spotify_token()
    dfs = []
    for r in input_df.index[0:15000:50]:
        print(r)
        input_df = get_track_ids()
        a = fetch_song_audio_features(token, input_df, r, r+50)
        partial_df = pd.DataFrame(a[:-1])
        dfs.append(partial_df)
    df = pd.concat(dfs)
    df = df.reset_index()
    df = df.drop(columns=['index'])
    return df

def fetch_tracks(token, df, start, end):
    ids = df[start:end].to_csv(index=False).replace('\n', ',')[:-1]
    r = requests.get(f"https://api.spotify.com/v1/tracks/?ids={ids}"[:-1], headers={"Authorization": f"Bearer {token}"})
    return r.json()["tracks"]

def make_tracks_df(input_df):
    token = get_spotify_token()
    dfs = []
    for r in input_df.index[0:15000:50]:
        print(r)
        input_df = get_track_ids()
        a = fetch_tracks(token, input_df, r, r+50)
        partial_df = pd.DataFrame(a[:-1])
        dfs.append(partial_df)
    df = pd.concat(dfs)
    df = df.reset_index()
    df = df.drop(columns=['index'])
    return df

df = get_track_ids()
#X_audio_features = make_audio_features_df(df)
X_tracks = make_tracks_df(df)
