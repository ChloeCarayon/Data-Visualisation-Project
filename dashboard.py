# Run this app with `python dashboard.py` and
# visit http://127.0.0.1:8050/ in your web browser

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

## Load dataset
df = pd.read_csv("data/ufo.csv")

## Preprocessing
df['datetime_map'] = df.datetime.map(lambda x: int(x.split('-')[2].split(" ")[0]))

df["duration_cut"] = pd.cut(x=df['duration'], bins=[0, 60, 600, 900, 1800, 3600, 7200, 10800])

df['datetime'] = pd.to_datetime(df['datetime'])

df['year'] = df.datetime.dt.year
df['month'] = df.datetime.dt.month
df['day'] = df.datetime.dt.day



colors = {
    'background': '#E5EFF4',
    'text': '#516D90',
}

year_comments = df.groupby('year')['comments'].count()

form_count = df.form.value_counts().index

type_labels = ["Count", "Duration", "Form", "Date"]
type_values = ["count", "duration", "form", "date"]


## Application layout
app = dash.Dash()

app.layout = html.Div([
    html.H1("UFO Sightings"),
    html.Div([
        dcc.Graph(id='map'),
    ], style={'width': '49%', 'display': 'inline-block'}),

    html.Div([
        dcc.Dropdown(
            id='type',
            options=[{'label': i, 'value': j} for i, j in zip(type_labels, type_values)],
            value='count'
        ),
        dcc.Graph(id="graph")
    ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),

    html.Div([
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
    ], style={'width': '49%', 'padding': '0px 20px 20px 20px'})
])


## Application callback
@app.callback(
    Output("map", "figure"),
    Output("graph", "figure"),
    Input("type", "value"),
    Input("select", "value")
)
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

    duration_comments = dff.groupby('duration_cut')['comments'].count()
    new_index = ['0-1min', '1-10mins', '10-15mins', '15-30mins',
                '30mins-1h','1h-2h','2h-3h']
    duration_comments.index = new_index
    form_count = dff.groupby('form')['comments'].count()
    form_count = form_count[form_count >= 10]

    month_comments = dff.groupby('month')['comments'].count()
    new_index = ['jan', 'feb', 'mar', 'apr',
                'may','jun','jul','aug','sep','oct','nov','dec']
    month_comments.index = new_index
    day_comments = dff.groupby('day')['comments'].count()


    fig1 = go.Figure(go.Densitymapbox(lat=dff.latitude, lon=dff.longitude, z=dff.datetime_map, radius=10))
    fig1.update_layout(mapbox_style="stamen-terrain",
                       mapbox_center_lon=180,
                       margin={"r": 10, "t": 10, "l": 10, "b": 10})

    if graph_type == "count":
        fig2 = px.histogram(dff, x="year", color="form")
    elif graph_type == "duration":
        fig2 = px.bar(x=duration_comments, color=duration_comments.index, title="Time duration of ufo")
    elif graph_type == "form":
        fig2 = px.pie(values=form_count, names=form_count.index)
    else:
        fig2 = make_subplots(rows=2, cols=1)

        fig2.add_trace(
            go.Bar(x=day_comments.index, y=day_comments, name="days"),
            row=1, col=1
        )

        fig2.add_trace(
            go.Bar(x=month_comments.index, y=month_comments, name="months"),
            row=2, col=1
        )
    return [fig1, fig2]


if __name__ == '__main__':
    app.run_server(debug=True)