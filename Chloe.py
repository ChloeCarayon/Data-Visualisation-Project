
import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from dash.dependencies import Input, Output
#import plotly_wordcloud
from plotly.offline import iplot, init_notebook_mode


app = dash.Dash()

df = pd.read_csv("data/ufo.csv")

colors = {
    'background': '#E5EFF4',
    'text': '#516D90',
}

df['datetime_map'] = df.datetime.map(lambda x:  int(x.split('-')[2].split(" ")[0]))

#print(df.groupby('duration').count())

# example show form specific !

df['datetime'] = pd.to_datetime(df['datetime'])

df = df[df.datetime.dt.year >= 1960]

df['year'] = df.datetime.dt.year
df['month'] = df.datetime.dt.month
df['day'] = df.datetime.dt.day

month_comments = df.groupby('month')['comments'].count()
day_comments = df.groupby('day')['comments'].count()

                                                   # 1min   #10min #15min #30min #1h #2h #3h
df["duration_cut"] = pd.cut(x=df['duration'], bins=[0, 60, 600, 900, 1800, 3600, 7200, 10800])
duration_comments = df.groupby('duration_cut')['comments'].count()
form_count = df.groupby('form')['comments'].count()
form_count = form_count[form_count>=10]

country_comments = df.groupby('country')['comments'].count()
country_ovni = country_comments[country_comments>=25]

fig = go.Figure(go.Densitymapbox(lat=df.latitude, lon=df.longitude, z=df.datetime_map,radius=10))
fig.update_layout(mapbox_style="stamen-terrain", mapbox_center_lon=180)
fig.update_layout(margin={"r":10,"t":10,"l":10,"b":10})
fig1 = px.histogram(df, x="year", color="form")
fig2 = px.bar(x=month_comments.index, y=month_comments)
fig3 = px.bar(x=day_comments.index, y=day_comments)
fig4 = px.bar(x=duration_comments, color=duration_comments.index)
fig5 = px.pie(values=form_count, names=form_count.index, color=form_count)
fig6 = px.pie(values=country_ovni, names=country_ovni.index, color=country_ovni)

app.layout = html.Div([
    html.H3(children='Chloé CARAYON - Victor TAILLIEU', style={
        'textAlign': 'left',
        'color': colors['text']
    }),

    dcc.Graph(
        id='Map',
        figure=fig
    ),

    dcc.Graph(
        id='FormByYear',
        figure=fig1
    ),
    dcc.Graph(
        id='RepartitionByDays',
        figure=fig3
    ),

    dcc.Graph(
        id='RepartitionByMonths',
        figure=fig2
    ),

    dcc.Graph(
        id='RepartitionByDuration',
        figure=fig4
    ),

    dcc.Graph(
        id='FormsRepresentation',
        figure=fig5
    ),

    dcc.Graph(
        id='CountriesPerForm',
        figure=fig6
    ),

])

if __name__ == '__main__':
   app.run_server(debug=True)


"""



import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd
import re

## Load dataset
df = pd.read_csv("data/ufo.csv")

## Preprocesing
#df = df[["turns", "victory_status", "winner", "white_rating", "black_rating", "opening_name"]]


def shorten_opening(val):
    match = re.search("(.*):", val)
    if match is None:
        return val
    return match[1]


#df["opening_short"] = df.opening_name.map(shorten_opening)
#df["rating"] = ((df.white_rating + df.black_rating) / 2)

## Useful variables
md_text = '''
With this app, you can visualize some statistics.'''
type_labels = ["Game length", "Game termination", "Game result", "Most played openings"]
type_values = ["turns", "victory_status", "winner", "opening_name"]


## Application layout
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Chess games visualization"),
    dcc.Markdown(md_text),
    html.Div([
        dcc.Dropdown(
            id='type',
            options=[{'label': i, 'value': j} for i, j in zip(type_labels, type_values)],
            value='winner'
        ),
        dcc.Graph(id="graph"),
        dcc.Slider(
            id='level-slider',
            min=0,
            max=4,
            value=0,
            marks={  # set slider levels
                0: {'label': 'All'},
                1: {'label': 'Beginner (-1200 ELO)'},
                2: {'label': 'Intermediate (1200-1600 ELO)'},
                3: {'label': 'Advanced (1600-2000 ELO)'},
                4: {'label': 'Master (+2000 ELO)'}
            },
            step=None
        )
    ], style={"width": "75%", "margin": "auto"})
])


## Application callback
@app.callback(
    Output("graph", "figure"),
    Input("type", "value"),
    Input("level-slider", "value")
)
def update_graph(graph_type, level_value):
    # Filter players by rating according to the slider
    if level_value == 1:
        dff = df[df.rating < 1200]
    elif level_value == 2:
        dff = df[(1200 <= df.rating) & (df.rating < 1600)]
    elif level_value == 3:
        dff = df[(1600 <= df.rating) & (df.rating < 2000)]
    elif level_value == 4:
        dff = df[df.rating >= 2000]
    else:
        dff = df

    # Histogram of turns
    if graph_type == "turns":
        fig = px.histogram(x=dff[dff.turns < 180].turns, histnorm="percent", nbins=50)

        fig.update_layout(
            xaxis_title_text="Number of turns",
            yaxis_title_text="Proportion of games (%)",
            bargap=0.2
        )
    # Barplot of openings
    elif graph_type == "opening_name":
        opening_count = dff.opening_short.value_counts()

        fig = px.bar(x=opening_count.index[:10],
                     y=opening_count[:10] / opening_count.sum() * 100)

        fig.update_layout(
            xaxis_title_text="Opening name",
            yaxis_title_text="Proportion of games (%)"
        )
    # Pie plots
    else:
        count = dff[graph_type].value_counts()
        fig = px.pie(names=count.index, values=count)
        fig.update_traces(textinfo='percent+label')

    return fig


if __name__ == '__main__':
    app.run_server()
"""