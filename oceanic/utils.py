from datetime import datetime
import geojson
import plotly.express as px

###################################### Mappings ######################################
# Maps Smartvel covid_id with postal codes for US states. Useful to map regions to geo maps.
us_codes = {155: "AL", 179: "AK", 171: "AZ", 134: "AR", 143: "CA", 167: "CO", 156: "CT", 136: "DE", 185: "DC",
            137: "FL", 138: "GA", 184: "HI", 172: "ID", 158: "IL",
            159: "IN", 157: "IA", 144: "KS", 180: "KY", 145: "LA", 160: "ME", 146: "MD", 181: "MA", 161: "MI",
            162: "MN", 148: "MS", 147: "MO", 173: "MT", 163: "NE",
            169: "NV", 164: "NH", 165: "NJ", 168: "NM", 166: "NY", 149: "NC", 174: "ND", 139: "OH", 150: "OK",
            175: "OR", 182: "PA", 140: "RI", 151: "SC", 176: "SD",
            152: "TN", 153: "TX", 170: "UT", 141: "VT", 183: "VA", 177: "WA", 154: "WV", 142: "WI", 178: "WY"
            }
# Maps restriction id with their latest descriptive names. It helps to normalize restriction names.
event_codes = {"2010": "Quarantine", "2011": "Negative COVID-19 Test Result", "2999": "Forms or Health Insurance",
               "3001": "Non-essential Shops Open",
               "3002": "Tourist Accommodations Open", "3003": "Restaurants Open", "3004": "Bars and Cafes Open",
               "3006": "Museums and Heritage Sites Open",
               "4002": "Face Coverings", "4003": "Social Distancing", "2998": "Health Insurance"}
# event codes in dropdown format. Useful to populate a dropdown.
event_codes_options = [{'label': v, 'value': k} for k, v in event_codes.items()]
# color_map maps event statuses (red, yellow, ...) with their color in  plotly choropleth
color_map = {"black": "#111111", "grey": "#444444", "green": "#008800", "yellow": "#FFFF00","red": "#FF0000"}
months = ['February', 'March', 'April', 'May', 'June', 'July']
with open('data/simple_borders.json') as f:
    geodata = [{'geometry':{'type': 'MultiPolygon', 'coordinates': v['coordinates']}, 'id': k, 'type': 'Feature'} for k,v in geojson.load(f).items()]
    geodata = {'type': 'FeatureCollection', 'features': geodata}

###################################### Functions ######################################
def format_dates_str(x):
    return datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'). \
        replace(minute=00, hour=12, second=00, microsecond=00). \
        strftime("%Y%m%d")

def format_dates_dt(x):
    return x.strftime("%Y%m%d")

def pivot_event(df, columns, index, values):
    return df \
        .pivot_table(index=index, columns=columns, values=values, aggfunc='count')\
        .fillna(0)[color_map]/51     # divide by the number of states to get average days per state

def make_choropleth_fig(df, column):
    fig = px.choropleth(
        data_frame=df,
        locationmode='USA-states',
        # geojson=geodata_us,
        locations='region_codes',
        scope="usa",
        color=column,
        hover_data=['region_codes'],
        animation_frame="date",
        title=event_codes[column],
        color_discrete_map=color_map,
        category_orders={column: ['red', 'yellow', 'green', 'grey', 'black']},
        # featureidkey="id",
    )
    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 30
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 5
    fig.layout.dragmode = False
    return fig