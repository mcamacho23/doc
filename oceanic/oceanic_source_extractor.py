
#################################################
#               Oceanic Source Study            #
#################################################
# This is not finished. It has a more completed version in oceanic_source_study by Pedro
import json
from pathlib import Path
import numpy as np
import pandas as pd
import os
import sys


feeds_on = pd.read_json('data/scrapes/feeds_on.json').T.rename(columns={0: 'feed_code', 1: 'crontab'}).set_index('feed_code')
if feeds_on.index.duplicated().any():
    print("Warning: feed crontab table may have duplicates")
oceanic_sources = pd.read_json('data/scrapes/oceanic_sources.json')
if len(oceanic_sources) != len(feeds_on):
    print("Warning: feeds_on and oceanic_sources have a different number or entries")
feed_df = pd.concat([oceanic_sources, feeds_on])
feed_df = feed_df[feed_df["output_var"].notna()]        # Why these dups?

feed_df['output_var'].apply(dict.keys).apply(list).explode().value_counts()
# Posibles valores 'event', 'store', 'common' y 'data' ¿Qué significan?
event = feed_df['output_var'].str.get('event')

######################### Region Coverage #########################

# First we get all feeds without country_code and retrieve all regions from steps code
def clean_and_flat(l):
    l = [item for sublist in l for item in sublist]
    return [x for x in l if x]

def filter_cc(d, values):
    d = d.get('param',{})
    if d.get('output_var') == 'event.country_code':
        list_of_regions = [x['rdict'].values() if values else x['rdict'] for x in d.get('operations') or [] if
                           x['operation_type'] == "replace"]
        return clean_and_flat(list_of_regions)

def get_codes(d, values):
    codes = [y for x in d if (y := filter_cc(x, values)) is not None]
    return clean_and_flat(codes)

no_country_feeds = feed_df[event.str.get('country_code').apply(len) < 2]['steps'].apply(get_codes, args=(True,))

# Now we go with the remaining feeds
coverage = event.str.get('country_code').replace('', np.nan)
coverage = coverage.groupby(event.index).apply(lambda x: x.dropna().to_list()).rename('coverage')
coverage.loc[coverage.apply(len) == 0] = no_country_feeds

# Last we get the legend for all regions
legends = feed_df[event.str.get('country_code').apply(len) < 2]['steps'].apply(get_codes, args=(False,))
legends = pd.merge(no_country_feeds, legends, left_index=True, right_index=True)

def test(a):
    print()

legend = legends.apply(lambda x: {key:value for (key, value) in zip(x['steps_x'],x['steps_y'])}, axis=1)
print()

