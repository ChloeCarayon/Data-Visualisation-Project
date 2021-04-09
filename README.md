# Data visualisation project

Project at EFREI in Data Visualization course by Chloé CARAYON and Victor TAILLIEU.

## Project Objective

With this dashboard, you can visualize some insights about UFO sightings.
Check out the [dataset](https://www.kaggle.com/NUFORC/ufo-sightings) on Kaggle.

## Prerequisites

This application requires Python 3.8. Check your python version using:
````
$ python --version
Python 3.8.6
````

To install the requirements, you can use:
```
$ pip install -r requirements.txt
```

## Quickstart

Run the dashboard with:
```
$ python dashboard.py
```
Once started, open your browser at:

http://127.0.0.1:8050/

## Project Structure

This project is divided into two parts:
- Preprocessing
- Dashboard

`preprocessing.py` was used to preprocess the original dataset `scrubbed.csv`. The obtained cleaned dataset `ufo.csv` is the one used by the dashboard.
