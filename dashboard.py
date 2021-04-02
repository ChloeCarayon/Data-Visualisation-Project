# Run this app with `python dashboard.py` and
# visit http://127.0.0.1:8050/ in your web browser

# ------------------
# CARAYON - TAILLIEU
# ------------------

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from nltk import word_tokenize
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
from collections import Counter
import random
import plotly as plotly
import plotly.figure_factory as ff


## Load dataset
df = pd.read_csv("data/ufo.csv")

## Selector labels and values
type_labels = ["Count", "Duration", "Shape", "Word cloud"]
type_values = ["count", "duration", "shape", "wordcloud"]

## Text to display
md_text = '''With this dashboard, you can visualize some insights about UFO sightings. Check out the [dataset](https://www.kaggle.com/NUFORC/ufo-sightings) on Kaggle.\n
You can filter the data based on the country and select the graph you want to see.'''


## Date
month_comments = df.groupby('month')['comments'].count()
new_index_months = ['jan', 'feb', 'mar', 'apr',
                    'may', 'jun', 'jul', 'aug',
                    'sep', 'oct', 'nov', 'dec']

norSeason = df[df['hemisphere'] == "Northern Hemisphere"]["season"]
souSeason = df[df['hemisphere'] == "Southern Hemisphere"]["season"]

dataset_figure = ff.create_table(df[:15].drop(['comments', 'year', 'month','day','hour', 'duration_cut','season', 'hemisphere'], axis=1))

# Functions for WordCloud
def tokenise(text):
    return [word.lower() for word in word_tokenize(text) if word not in stop_words and word.isalpha()]

df['comments_token'] = df['comments'].apply(str).map(tokenise)


external_stylesheets = ['style.css']

## Application layout
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1("UFO Sightings: What are the best conditions to observe UFO signs?"),
    html.Div([
        dcc.Markdown(md_text)
    ]),
    dcc.Tabs(id='tabs', value='tab0', children=[
        dcc.Tab(label='Dataset of UFO sign', value='tab0'),
        dcc.Tab(label='Where and how most UFO appear ? ', value='tab1'),
        dcc.Tab(label='Is there a popular time where UFO appear ? ', value='tab2'),
    ]),
    html.Div(id='tabs_content'),

], style={'font-family': 'Garamond'})


@app.callback(Output('tabs_content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab0':
        return tab0content()
    elif tab == 'tab1':
        return tab1content()
    elif tab == 'tab2':
        return tab2content()


def tab0content():
    return( html.Div([
        html.H2(children='Preprocessed Dataset', style={
            'textAlign': 'left',
            'color': '#516D90'
        }),
        dcc.Graph(
            id='dataset',
            figure= dataset_figure
        )]))

def tab1content():
    return(
        html.Div([
        html.H2(children='Map', style={
            'textAlign': 'left',
            'color': '#516D90'
        }),
        dcc.Graph(id='map'),
    ], style={'width': '49%', 'display': 'inline-block'}),  # display map on the left half
        html.Div([
        html.H2(children='Graphs', style={
            'textAlign': 'left',
            'color': '#516D90'
        }),
        # graph selector
        dcc.Dropdown(
            id='type',
            options=[{'label': i, 'value': j} for i, j in zip(type_labels, type_values)],
            value='count'
        ),
        dcc.Graph(id="graph")
    ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),  # display graph on the right half

    html.Div([
        # Countries selector
        dcc.Dropdown(
            id='select',
            options=[
                {"label": "United States", "value": "us"},
                {"label": "Canada", "value": "ca"},
                {"label": "United Kingdom", "value": "gb"},
                {"label": "Other countries", "value": "other"}
            ],
            value="us",
            multi=True
        )
    ], style={'width': '49%', 'padding': '0px 20px 20px 20px'})  # display countries selector on the left half)
    )

@app.callback(
    Output("map", "figure"),
    Output("graph", "figure"),
    Input("type", "value"),
    Input("select", "value"))

def update_graph(graph_type, select_values):
    # Filter observations by country
    dff = df
    if "other" not in select_values:
        dff = dff[dff.country.isin(["us", "ca", "gb"])]
    if "us" not in select_values:
        dff = dff[dff.country != "us"]
    if "ca" not in select_values:
        dff = dff[dff.country != "ca"]
    if "gb" not in select_values:
        dff = dff[dff.country != "gb"]

    ## Duration
    duration_comments = dff.groupby('duration_cut')['comments'].count()
    new_index_duration = ['0-1min', '1-10mins', '10-15mins',
                          '15-30mins', '30mins-1h', '1h-2h', '2h-3h']

    ## Shape
    form_count = dff.groupby('form')['comments'].count()
    form_count = form_count[form_count >= 10]


    # Word cloud
    df_comments = dff.comments_token.tolist()
    count_C = Counter(x for l in df_comments for x in l)
    comments_count = dict(count_C)
    comments_nb = pd.Series(comments_count)
    comments_nb.sort_values(ascending=False, inplace=True)
    # take most important words
    size_half = int(comments_nb.size / 70)
    comments_nb = comments_nb[:size_half]

    max_min = (comments_nb.iloc[1] - comments_nb.iloc[-1])
    min = comments_nb.iloc[-1]

    ## Figures implementation
    # Map
    fig1 = go.Figure(go.Densitymapbox(lat=dff.latitude, lon=dff.longitude, radius=5))
    fig1.update_layout(mapbox_style="stamen-terrain",
                       mapbox_center_lon=180,
                       margin={"r": 10, "t": 10, "l": 10, "b": 10})

    # Graph
    if graph_type == "count":
        fig2 = px.histogram(dff, x="year", color="form",
                            title="Numbers of apparitions by year")
    elif graph_type == "duration":
        fig2 = px.bar(x=duration_comments, y=new_index_duration,
                      title="Time duration of apparition",
                      labels={"x": "Proportion", "y": "Duration"})
    elif graph_type == "shape":
        fig2 = px.pie(values=form_count, names=form_count.index,
                      title="Proportion of ufo shapes")
    else:
        # center and reduce
        comments_nb = comments_nb.apply(lambda x: int((x - min) / (max_min) * 30))
        comments_nb = comments_nb[comments_nb > 0]  # drop words of weight 0
        words = comments_nb.index
        colors = [plotly.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for i in range(comments_nb.size)]
        weights = comments_nb.values
        data = go.Scatter(x=[random.random() for _ in range(comments_nb.size)],
                          y=[random.random() for _ in range(comments_nb.size)],
                          mode='text',
                          text=words,
                          marker={'opacity': 0.3},
                          textfont={'size': weights,
                                    'color': colors})

        layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                            'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                            'title': "WordCloud on comments",
                            })
        fig2 = go.Figure(data=[data], layout=layout)

    return [fig1, fig2]


def tab2content():
    fig1 = go.Figure()
    fig1.add_trace(
       go.Histogram( x=souSeason, histnorm='percent', name='Southern Hemisphere'))
    fig1.add_trace(
        go.Histogram( x=norSeason, histnorm='percent', name='Northern Hemisphere'))
    fig1.update_layout(
        title_text="Season and Hemisphere UFO signs in percent", xaxis_title_text='Season', yaxis_title_text='Percent', bargap=0.2, bargroupgap=0.1 )

    return(
        html.Div([
            dcc.RadioItems(
                id='radio',
                options=[{'label': 'Northern Hemisphere', 'value': 'north'},
                         {'label': 'Southern Hemisphere', 'value': 'south'}, ],
                value='north',
                labelStyle={'display': 'inline-block'}
            ),
        ], style={'width': '49%', 'float': 'left', 'padding': '40px 0px 0px 40px'}),
        html.Div([
            dcc.Graph(id='datesTimes'),
        ], style={'width': '49%', 'float': 'left'}),

        html.Div([
        dcc.Graph(id="SeasonsHemisp", figure=fig1)
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block',  'padding': '100px 0px 0px 0px'}),
    )


@app.callback(
    Output("datesTimes", "figure"),
    Input("radio", "value"))

def update_graph_hemisphere(select_values):
    dff = df
    if "north" not in select_values:
        dff = dff[dff['hemisphere'] == "Northern Hemisphere"]
    else:
        dff = dff[dff['hemisphere'] == "Southern Hemisphere"]

    day_comments = dff.groupby('day')['comments'].count()
    hour_comments = dff.groupby('hour')['comments'].count()
    month_comments = dff.groupby('month')['comments'].count()

    fig = make_subplots(rows=3, cols=1, subplot_titles=("Repartition by hour", "Repartition by day", "Repartition by month" ))
    fig.add_trace(
        go.Bar(x=hour_comments.index, y=hour_comments, name="hour"),
        row=1, col=1)

    fig.add_trace(
        go.Bar(x=day_comments.index, y=day_comments, name="day"),
        row=2, col=1)

    fig.add_trace(
        go.Bar(x=month_comments.index, y=month_comments, name="month"),
        row=3, col=1)
    fig.update_layout(height=600)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
