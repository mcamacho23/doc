
#################################################
#               Oceanic Source Study            #
#################################################

import json
import numpy as np
import pandas as pd
import glob
from itertools import product

from oceanic.utils import format_dates_str


class AuditDataSet():
    audit_columns = ['audit_id', 'covid_id', 'timestamp', 'region_id']
    taxonomy_columns = ['2010', '2011', '2998', '2999', '3001', '3002', '3003', '3004', '3006', '4002', '4003']
    columns = audit_columns + taxonomy_columns
    (audit_id, covid_id, timestamp, region_id) = range(4)
    checkpoint_path = 'data/audits/checkpoint.csv'

    def __init__(self):
        self.covid_status = None

    def _load_audit_files(self, path):
        filenames = glob.glob(path)
        data = []
        for i, fname in enumerate(filenames):
            f = open(fname)
            audit = json.load(f)
            print(f"processing file {i} of {len(filenames)}")
            for a in audit:
                au_row = [None] * len(self.audit_columns)
                au_row[self.audit_id] = a['id']
                au_row[self.covid_id] = a['covid_id']
                au_row[self.timestamp] = a['timestamp']
                au_row[self.region_id] = a['new_data']['region_id']
                if not a['new_data']['extra']:
                    continue
                extra = {x['id']: x for x in a['new_data']['extra']['en']}
                tax_row = [extra.get(int(x), {}).get('colour') for x in self.taxonomy_columns]
                data.append(au_row + tax_row)
        return pd.DataFrame(data, columns=self.columns)

    def load_audits(self, path=None, from_checkpoint=True, to_checkpoint=False):
        if from_checkpoint:
            self.covid_status = pd.read_csv(self.checkpoint_path)
        else:
            self.covid_status = self._load_audit_files(path)
            if to_checkpoint:
                self.covid_status.to_csv(self.checkpoint_path, index=False)

    def normalize_and_ffill(self):
        covid_status = self.covid_status
        # Create a string date per day
        covid_status['date'] = covid_status['timestamp'].apply(lambda x: format_dates_str(x))
        covid_status = covid_status.drop_duplicates(subset=['date', 'covid_id', 'region_id'],
                                                    keep='last')  # We keep last entry of the day
        # Our final table has to have all regions all days and take region_id away
        dates = covid_status['date'].unique()
        regions = covid_status['covid_id'].unique()
        all_regions_dates = pd.DataFrame(product(dates, regions), columns=['date', 'covid_id'])
        covid_status = pd.merge(all_regions_dates, covid_status, how='left', left_on=['date', 'covid_id'],
                                right_on=['date', 'covid_id']).drop("region_id", axis=1)
        # We fill gaps with no updates with last update. Logs only get updated when new information comes in
        covid_status = covid_status.groupby(by=['covid_id'], as_index=False).apply(lambda group: group.ffill())
        # We assign color black to unknown values
        covid_status[self.taxonomy_columns] = covid_status[self.taxonomy_columns].replace(np.nan, "black")
        self.covid_status = covid_status

    def to_csv(self, path):
        self.covid_status.to_csv(path, index=False)

    def enrich(self):
        # Enrich data with complete region_id, region codes and region level
        covid_region_codes = pd.read_json("data/covid_region_codes.json").T
        self.covid_status = pd.merge(self.covid_status, covid_region_codes, left_on='covid_id', right_index=True)


audit = AuditDataSet()
# audit.load_audits(from_checkpoint=True)
audit.load_audits('data/audits/*_covid.json', from_checkpoint=False, to_checkpoint=True)
audit.normalize_and_ffill()
audit.enrich()
audit.to_csv('data/audits/covid_status.csv')
