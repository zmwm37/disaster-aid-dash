"""
Quasi-API to connect to American Community Survey (ACS).

(la)Monty Python
Wesley Janson
March 2022

Code relies on CensusData library, which uses Census API to pull
data and returns it as a Pandas dataframe.
CensusData information: https://pypi.org/project/CensusData/
"""
import pandas as pd
import re
import censusdata
from backend.api import API
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.precision', 2)

class ACSapi(API):
    '''
    Class built to pull ACS data.
    '''
    table_dict = {"detail": ['B01003_001E','B05012_003E','B06011_001E'],
                "dp": ['DP05_0038PE','DP03_0005PE','DP03_0074PE','DP03_0096PE',
                    'DP04_0003PE','DP04_0005E','DP04_0047PE','DP04_0089E','DP04_0134E']}

    def __init__(self, states, years):
        '''
		Constructor.

        Parameters:
			-states: list of states to filter on
			-years: list of years to filter on
		'''
        self.states = states
        self.years = years
        self.detail_df = None
        self.dp_df = None


    def get_data(self):
        '''
        Class method that uses CensusData library to pull American Community Survey
            data using an API. It downloads the two separate tables, outputs them as
            pandas dataframes.

        The two tables correspond to relevant variables pulled from the Detail
            Tables (detail) and the Data Profiles (dp), respectively. More information
            can be found in the links below:

        Detail: https://data.census.gov/cedsci/all?d=ACS%201-Year%20Estimates%20Detailed%20Tables
        DP: https://www.census.gov/acs/www/data/data-tables-and-tools/data-profiles/
        '''
        for table,cols in self.table_dict.items():
            for year in self.years:
                if table == "detail":
                    detail_year = censusdata.download('acs1', year,
                                    censusdata.censusgeo([('county', '*')]), cols)
                    detail_year['year'] = year
                    self.detail_df = pd.concat([self.detail_df,detail_year])

                elif table == "dp":
                    dp_year = censusdata.download('acs1', year,
                                    censusdata.censusgeo([('county', '*')]),
                                   cols, tabletype='profile')
                    self.dp_df = pd.concat([self.dp_df,dp_year])


    def clean_data(self):
        '''
        Class method that initially calls the "get_data" method that pulls ACS
            data, merges and then cleans the merged pandas dataframe. It removes any
            NA or null values, removes missing observations, and creates relevant
            variables from the index. The last step is to filter by the input "states" list.
        '''

        self.get_data()
        self.detail_df = self.make_state_county(self.detail_df)
        self.dp_df = self.make_state_county(self.dp_df)

        final_df = pd.merge(self.detail_df, self.dp_df, on = ['state_fips','county_fips'], how = 'inner')
        final_df = final_df.rename(columns={"B01003_001E":"population",
                "B05012_003E":"foreign_born","B06011_001E":"median_income",
                "DP05_0038PE":"black_afam","DP03_0005PE":"unemp_rate",
                "DP03_0074PE":"snap_benefits", "DP03_0096PE":"health_insurance_rate",
                "DP04_0003PE":"vacant_housing_rate", "DP04_0005E":"rental_vacancy_rate",
                "DP04_0047PE":"renter_occupied_rate","DP04_0089E":"median_home_price",
                "DP04_0134E":"median_rent"})

        for col in final_df:
            final_df = final_df[final_df[col] != -999999999.0]

        final_df["foreign_born"] = 100*(final_df["foreign_born"]/final_df["population"])

        final_df = final_df.loc[final_df['state_fips'].isin(self.states)]

        return final_df

    def make_state_county(self,data):
        '''
        Class method to generate state and county FIPS code from ACS index.
        '''
        state_list = []
        county_list = []
        for row in data.index:
            row = str(row)
            _, state, county = re.findall('[0-9]+', row)
            state_list.append(state)
            county_list.append(county)

        data['state_fips'] = state_list
        data['county_fips'] = county_list

        return data


def make_acs_api_call(states,years):
    '''
    Functions that makes the call to run ACS class, and return final dataframe.
    '''
    df_create = ACSapi(states,years)
    dataframe = df_create.clean_data()
    return dataframe