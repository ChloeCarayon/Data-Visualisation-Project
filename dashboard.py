    # Run this app with `python dashboard.py` and
    # visit http://127.0.0.1:8050/ in your web browser

    #-----
    # CARAYON - TAILLIEU
    #-----

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


    ## Selector labels and values
    type_labels = ["Count", "Duration", "Shape", "Date"]
    type_values = ["count", "duration", "shape", "date"]


    ## Text to display
    md_text = '''With this dashboard, you can visualize some insights about UFO sightings. \n
    Check out the [dataset](https://www.kaggle.com/NUFORC/ufo-sightings) on Kaggle. \n
    This dataset contains around 80 000 and we ask ourselves what are the best conditions to observe UFO signs?'''

    ## Application layout
    app = dash.Dash()

    app.layout = html.Div([
            html.H1("UFO Sightings: What are the best conditions to observe UFO signs?"),
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
            ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),    # display graph on the right half

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
            ], style={'width': '49%', 'padding': '0px 20px 20px 20px'}),    # display countries selector on the left half

            html.Div([
                    dcc.Markdown(md_text),
            ], style={'display': 'inline-block'})
    ], style={'font-family': 'Garamond'})


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

            ## Duration
            duration_comments = dff.groupby('duration_cut')['comments'].count()
            new_index_duration = ['0-1min', '1-10mins', '10-15mins', '15-30mins',
                                    '30mins-1h','1h-2h','2h-3h']
            duration_comments.index = new_index_duration

            ## Shape
            form_count = dff.groupby('form')['comments'].count()
            form_count = form_count[form_count >= 10]

            ## Date
            month_comments = dff.groupby('month')['comments'].count()
            new_index_months = ['jan', 'feb', 'mar', 'apr',
                                    'may','jun','jul','aug','sep','oct','nov','dec']
            month_comments.index = new_index_months
            day_comments = dff.groupby('day')['comments'].count()

            ## Figures implementation
            # Map
            fig1 = go.Figure(go.Densitymapbox(lat=dff.latitude, lon=dff.longitude, radius=5))
            fig1.update_layout(mapbox_style="stamen-terrain",
                                                 mapbox_center_lon=180,
                                                 margin={"r": 10, "t": 10, "l": 10, "b": 10})

            # Graph
            if graph_type == "count":
                    fig2 = px.histogram(dff, x="year", color="form", title="Numbers of apparitions by year")
            elif graph_type == "duration":
                    fig2 = px.bar(x=duration_comments,y=new_index_duration, title="Time duration of apparition", #color = new_index_duration
                                                labels={
                                                        "x": "Proportion",
                                                        "y": "Duration"
                                                })
            elif graph_type == "shape":
                    fig2 = px.pie(values=form_count, names=form_count.index, title="Proportion of ufo shapes")
            else:
                    fig2 = make_subplots(rows=2, cols=1, subplot_titles=("Repartition by day","Repartition by month"))
                    # day and month subplots
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