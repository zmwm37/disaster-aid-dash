"""
(la)Monty Python
Aditya Retnanto
March 2022

Script to clean data to match scope of the project,
this file is not run but
"ibtracs.ALL.list.v04r00.csv" from NOAA dataset
and
"countypres_2000-2020.csv" can be obtained from MIT Eletion data
"""
import pandas as pd

def clean_fips(df):
    """
    Appends 0 to certian state dataframe 
    :param dataframe: Election Dataframe
    """
    states = ['AL', 'AR', 'AK','AZ','CA', 'CO', 'CT']
    for state in states:
        df.loc[df['state_po'] == state, ['county_fips']] = '0' + df.loc[df['state_po'] == state, ['county_fips']]
    return df

def hurricane_subset(df):
    """
    Creates hurricane subset for analysis
    :param dataframe: Hurricane Dataframe
    """
    harvey_data = df.loc[(df['NAME'] == 'HARVEY') & (df['SEASON'] == 2017)]
    irma_data = df.loc[(df['NAME'] == 'IRMA') & (df['SEASON'] == 2017)]
    michael_data = df.loc[(df['NAME'] == 'MICHAEL') & (df['SEASON'] == 2018)]
    subset = [harvey_data, irma_data, michael_data]
    subset_df = pd.concat(subset)
    subset_df.to_csv("hurricane_path.csv", index = False)

county = pd.read_csv("countypres_2000-2020.csv", dtype={"county_fips": str})
winning_candidate_idx = county.groupby(['county_fips','year'], sort=False)['candidatevotes'].transform(max) == county['candidatevotes']
winner = county[winning_candidate_idx]
winner = clean_fips(winner)
winner.to_csv("county_president_winner.csv", index = False)
hurricane_data = pd.read_csv("ibtracs.ALL.list.v04r00.csv")
hurricane_subset(hurricane_data)
