import json
from urllib.request import urlopen

import pandas as pd
import plotly.express as px

from oceanic.utils import us_codes, geodata, color_map






covid_status = pd.read_csv("data/audits/covid_status.csv")
us_covid_status = covid_status[covid_status["covid_id"].isin(us_codes)]
us_covid_status['region_codes'] = us_covid_status["covid_id"].apply(lambda x: us_codes[x])
status_corr = us_covid_status[['2010', '4002', 'date', 'region_codes']]
scale_mapper = {k:float(v) for k,v in zip(color_map, range(5))}
status_corr.replace({"2010": scale_mapper, "4002": scale_mapper}, inplace=True)

def testt(a):
    ac = a.copy()
    ac = ac.sort_values(by='date')
    ac = ac[['2010', '4002']].corr(method='spearman')
    return ac

x = status_corr.groupby(by='region_codes').apply(testt)
print()
