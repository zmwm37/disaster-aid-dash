"""
(la)Monty Python
Ali Klemencic
March 2022

Module to download data from ACS and FEMA
and combine into a single dataframe.
"""

import pandas as pd
from backend.fema_api import FEMAapi
from backend.acs_api import ACSapi


def write_data_to_csv(dataframe, filename):
    """
    Writes data to a csv.

    :param dataframe: Pandas dataframe
    :param filename: (str) name of file to write to
    """
    dataframe.to_csv(filename, index=False)


def get_data(states, years):
    """
    Calls the FEMA and ACS API functions to get data
    from each based on the given states and years.

    :param states: (lst) states to include
    :param years: (lst) years to include

    :return: Pandas dataframe of the combined FEMA
            and ACS data for the given years
    """
    fema_df = make_fema_api_call(states, years)
    acs_df = make_acs_api_call(states, years)

    merged_df = pd.merge(acs_df, fema_df, how="left",
                        left_on=["county_fips", "state_fips", "year"],
                        right_on=["county_fips", "state_fips", "year"])

    merged_df['aid_per_capita'] = merged_df['aid_requested'] / merged_df['population']

    merged_df = merged_df[merged_df['disaster_number'].notna()]
    merged_df = merged_df.fillna(0)

    return merged_df


def make_fema_api_call(states, years):
    """
    Creates an instance of the FEMAapi class
    to get data for given states and years.

    :param states: (lst) states to include
    :param years: (lst) years to include

    :return: Pandas dataframe of resulting FEMA data
    """
    fema_api_call = FEMAapi(states, years)
    dataframes = fema_api_call.get_data()
    fema_api_call.clean_data(dataframes)
    return fema_api_call.data


def make_acs_api_call(states, years):
    """
    Creates an instance of the ACSapi class
    to get data for given states and years.

    :param states: (lst) states to include
    :param years: (lst) years to include

    :return: Pandas dataframe of resulting ACS data
    """
    acs_api_call = ACSapi(states, years)
    dataframe = acs_api_call.clean_data()
    return dataframe
