import pandas as pd
from math import gcd

from pathlib import Path

class SuitabilityScore:

    def __init__(self, drivers_file = '', addresses_file = ''):

        self.suitability_score = 0
        self.ADDRESS_EVEN_MULTIPLIER = 1.5
        self.COMMON_FACTORS_MULTIPLIER = 1.5

        self.consonants = [*"bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ"]
        self.vowels = [*"aeiouAEIOU"]

        self.drivers = self.to_dataframe(drivers_file, 'driver')
        self.addresses = self.to_dataframe(addresses_file, 'address')
        self.master_dataframe = pd.DataFrame()

    def to_dataframe(self, file, column_name):
        try:
            with open(file) as file:
                data = []
                for line in file:
                    data.append(line.rstrip())
        except IOError:
            return []
        return pd.DataFrame(data, columns=[column_name])

    def get_suitability_score(self):
        return self.suitability_score

    def precalculate_data(self):
        self.count_consonants(self.drivers, 'driver')
        self.count_vowels(self.drivers, 'driver')
        self.count_consonants(self.addresses, 'address')
        self.count_vowels(self.addresses, 'address')
        self.drivers['driver_name_length'] = self.drivers['driver'].str.len()
        self.addresses['address_name_length'] = self.addresses['address'].str.len()
        self.addresses['address_length_is_even'] = self.addresses['address'].str.len() % 2 == 0
        self.drivers['driver_name_length_is_even'] = self.drivers['driver'].str.len() % 2 == 0

    def count_consonants(self, df, column_name):
        df['consonants'] = df.apply(lambda x: ''.join([c for c in x[column_name] if c in self.consonants]).__len__(), axis=1)

    def count_vowels(self, df, column_name):
        df['vowels'] = df.apply(lambda x: ''.join([c for c in x[column_name] if c in self.vowels]).__len__(), axis=1)

    def sort_even_streets(self):
        self.addresses = self.addresses.sort_values(by='address_length_is_even', ascending=False, ignore_index=True)

    def sort_drivers(self):
        self.drivers = self.drivers.sort_values(by=['driver_name_length_is_even', 'consonants'], ascending=[False, True], ignore_index=True)

    def merge_dataframes(self):
        # we will assume there is an equal number of records in both files
        # we rename both indexes as 'idx' since we need a common column before merging
        self.addresses.index.name = 'idx'
        self.drivers.index.name = 'idx'
        self.master_dataframe = self.addresses.merge(self.drivers, how='left', on='idx', suffixes=('_in_address', '_in_driver'))

    def calculate_ss(self, row):
        ss = 0
        if (row['address_length_is_even']):
            ss = row['vowels_in_driver'] * self.ADDRESS_EVEN_MULTIPLIER
        else:
            ss = row['consonants_in_driver']
        if (row['address_length_is_even'] and row['driver_name_length_is_even']):
            # if both numbers are even, then it's guaranteed that 2 will be a common factor
            ss = ss * self.COMMON_FACTORS_MULTIPLIER
        elif(gcd(row['address_name_length'], row['driver_name_length']) > 1):
            ss = ss * self.COMMON_FACTORS_MULTIPLIER
        return ss

    def apply_algorithm(self):
        self.master_dataframe['ss'] = self.master_dataframe.apply(self.calculate_ss, axis=1)

    def process_datasets(self):

        # we will need to precalculate some data
        self.precalculate_data()

        # - odd destination streets lengths are better paired with drivers names with the most consonants
        #     sort drivers by number of consonants in their names
        # - even destination streets lengths are better paired with drivers names with the most vowels
        #     currently we're not trying to optimize this, we prefer to focus on consonants
        #     since there will be more more of them on average
        # - streets and drivers lengths with common factors get bonus SuitabilityScore, so:
        #     we should pair strings with even lengths, since any two even numbers will have 2 as a common factor

        self.sort_even_streets()
        self.sort_drivers()

        # - do the matching, this step can be done only once
        self.merge_dataframes()

        self.apply_algorithm()

        self.suitability_score = self.master_dataframe['ss'].sum()

        return self.suitability_score

    def export_csv(self, file_name='master.csv'):
        filepath = Path(file_name)
        self.master_dataframe.to_csv(filepath)
