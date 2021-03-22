
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
