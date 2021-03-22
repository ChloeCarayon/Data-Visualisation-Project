
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

df["duration_cut"] = pd.cut(x=df['duration'], bins=[0, 60, 600, 900, 1800, 3600, 7200, 10800])

#print(df.groupby('duration').count())

# example show form specific !
df = df[df.form == 'cone']

df['datetime'] = pd.to_datetime(df['datetime'])

df['year'] = df.datetime.dt.year
df['month'] = df.datetime.dt.month
df['day'] = df.datetime.dt.day

year_comments = df.groupby('year')['comments'].count()

form_count = df.form.value_counts().index

fig = go.Figure(go.Densitymapbox(lat=df.latitude, lon=df.longitude, z=df.datetime_map, radius=10))
fig.update_layout(mapbox_style="stamen-terrain", mapbox_center_lon=180)
fig.update_layout(margin={"r":10,"t":10,"l":10,"b":10})
fig1 = px.histogram(df, x="year", color="form")
fig2 = px.histogram(df, x="duration", color="form")
#fig3 = px.pie(df, values='form_count', names='form_count.index')

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
        id='Repartition',
        figure=fig1
    ),

    dcc.Graph(
        id='Repartition2',
        figure=fig2
    ),



])

if __name__ == '__main__':
   app.run_server(debug=True)

