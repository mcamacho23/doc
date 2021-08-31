import json
from urllib.request import urlopen

import pandas as pd
import plotly.express as px
from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from oceanic.utils import us_codes, event_codes, event_codes_options, color_map, geodata


app = dash.Dash(__name__)

# ---------- Import and clean data (importing csv into pandas)
covid_status = pd.read_csv("data/audits/covid_status.csv", parse_dates=['timestamp'])
us_covid_status = covid_status[covid_status["covid_id"].isin(us_codes)]
us_covid_status['region_codes'] = us_covid_status["covid_id"].apply(lambda x: us_codes[x])
us_df = us_covid_status.sort_values(by='timestamp')
# geodata_us = {'type': 'FeatureCollection', 'features': [x for x in geodata['features'] if int(x['id']) in us_df['region_id'].unique()]}

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    html.H1("US covid measurements - color code", style={'text-align': 'center'}),
    html.Br(),
    dcc.Dropdown(id='dropdown', options=event_codes_options, searchable=False, value='2010', style={'width': "40%"}),
    dcc.Graph(id='event', figure={}, style={'width': '90vh', 'height': '60vh'}),
])


@app.callback(
    [Output(component_id='event', component_property='figure')],
    [Input(component_id='dropdown', component_property='value')])
def update_graph(dropdown_value):
    fig = make_choropleth_fig(dropdown_value)
    return fig,


def make_choropleth_fig(dropdown_value):
    fig = px.choropleth(
        data_frame=us_df,
        locationmode='USA-states',
        # geojson=geodata_us,
        locations='region_codes',
        scope="usa",
        color=dropdown_value,
        hover_data=['region_codes'],
        animation_frame="date",
        title=event_codes[dropdown_value],
        color_discrete_map=color_map,
        # featureidkey="id",
    )
    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 30
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 5
    fig.layout.xaxis['fixedrange'] = True
    fig.layout.yaxis['fixedrange'] = True
    return fig

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
