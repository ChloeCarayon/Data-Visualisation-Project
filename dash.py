# -*- coding: utf-8 -*-

import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from dash.dependencies import Input, Output

app = dash.Dash()

df = pd.read_csv("ufo.csv")
df.datetime = df.datetime.map(lambda x:  int(x.split('-')[2].split(" ")[0]))

colors = {
    'background': '#E5EFF4',
    'text': '#516D90',
}

#fig0 = ff.create_table(df[:20])

#fig1 = px.histogram(df, x="total_bill", color="sex")

#fig2 = px.bar(df, x="sex", y="total_bill", color="smoker", barmode="group")


#fig4 = px.scatter(df, x="total_bill", y="tip", color="sex", facet_col="smoker")
#fig5 = px.box(df, y="tip", x="smoker", color="sex")
#fig6 = px.box(df, x="day", y="total_bill", color="smoker")
#fig7 = px.pie(df, values='tip', names='day')
#fig8 = px.scatter(df, x="total_bill", y="tip", color="day", facet_col="time")


#df = df.query("country =='us'")
df = df[df.city == 'san marcos']

fig = go.Figure(go.Densitymapbox(lat=df.latitude, lon=df.longitude, z=df.datetime, radius=10))
fig.update_layout(mapbox_style="stamen-terrain", mapbox_center_lon=180)
fig.update_layout(margin={"r":10,"t":10,"l":10,"b":10})
#fig.show()

#fig1 = px.choropleth(lat=df.latitude, lon=df.longitude )


app.layout = html.Div([
    html.H3(children='Chloé CARAYON - Victor TAILLIEU', style={
        'textAlign': 'left',
        'color': colors['text']
    }),

    dcc.Graph(
        id='dataset',
        figure=fig
    ),


])


# legends
#




if __name__ == '__main__':
   app.run_server(debug=True)
