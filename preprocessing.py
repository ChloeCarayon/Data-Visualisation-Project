# -*- coding: utf-8 -*-
"""
---
Authors : Chloé CARAYON - Victor TAILLIEU
Date : 24/03/2021

# DASHBOARD PROJECT
---

# Preprocessing part

## Import
"""

import pandas as pd
from tqdm import tqdm
import re
from geopy.geocoders import Nominatim

import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
nltk.download("stopwords")
nltk.download('punkt')

"""## Load data"""

df = pd.read_csv("data/scrubbed.csv")

df

"""## Preprocessing"""

df.columns

"""### Columns cleaning"""

df.rename(columns={'shape': 'form',
                   "duration (seconds)": "duration",
                   "date posted": "date_posted",
                   "longitude ": "longitude"}, inplace=True)
df.drop("duration (hours/min)", axis=1, inplace=True)

"""### Handle missing values"""

df.isnull().sum()

"""### Clean duration and latitude columns"""

tqdm.pandas()


def clean_number(text):
    replacements = {
        r"`": "",
        r"q": ""
    }

    for exp in replacements:
        text = re.sub(exp, replacements[exp], str(text))

    return pd.to_numeric(text)


df["duration"] = df.duration.progress_map(clean_number)
df["latitude"] = df.latitude.progress_map(clean_number)

"""### Replace missing countries and states based on coordinates"""

geolocator = Nominatim(user_agent="geoapiExercises")


def location(lat, lon, state=True):
    lat = str(lat)
    lon = str(lon)
    try:
        location = geolocator.reverse(lat + "," + lon)
        address = location.raw['address']
        if state:
            return address.get('state', '')
        else:
            return address.get('country_code', '')
    except:
        address = ""
    return address


geolocator = Nominatim(user_agent="geoapiExercises")

df['state'] = df.progress_apply(lambda x: location(x['latitude'], x['longitude']) if pd.isnull(x['state']) else x['state'], axis=1)

df['country'] = df.progress_apply(lambda x: location(x['latitude'], x['longitude'], False) if pd.isnull(x['country']) else x['country'], axis=1)

"""### Replace missing forms by unknown """

df.form.fillna("unknown", inplace=True)
df.comments.fillna("", inplace=True)

print("Number of missing values:", df.isnull().sum())

"""### Text preprocessing"""

df['comments'].values


def preprocessing(text):
    words = word_tokenize(text)
    words = [word for word in words if word not in stopwords.words("english")]
    words = [word for word in words if word.isalpha()]
    return ' '.join(words)


df['comments'] = df['comments'].map(preprocessing)

df['comments'].values

df

"""### Numbers preprocessing

#### Datetime format
"""


def clean_datetime(text):
    replacements = {
        r"24:": "00:",
    }

    for exp in replacements:
        text = re.sub(exp, replacements[exp], str(text))

    return pd.to_datetime(text, format='%m/%d/%Y %H:%M')


df.datetime = df.datetime.progress_map(clean_datetime)
df.date_posted = pd.to_datetime(df.date_posted, format='%m/%d/%Y')

"""#### Split in year, month, day and hour"""

df['year'] = df.datetime.dt.year
df['month'] = df.datetime.dt.month
df['day'] = df.datetime.dt.day
df['hour'] = df.datetime.dt.hour

"""#### Create categories for duration, season and hemisphere"""

df["duration_cut"] = pd.cut(x=df['duration'], bins=[0, 60, 600, 900, 1800, 3600, 7200, 10800], labels=[0, 1, 2, 3, 4, 5, 6])

df["season"] = pd.cut(x=df['month'], bins=[0, 5, 7, 10, 12], labels=["winter", "spring", "summer", "fall"])
df["hemisphere"] = pd.cut(x=df['latitude'], bins=[-100, 0, 100], labels=["Southern Hemisphere", "Northern Hemisphere"])

"""## Save preprocessed dataset"""

df.to_csv('data/ufo.csv', index=False)
