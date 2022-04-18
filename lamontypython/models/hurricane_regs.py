"""
Regression class that performs specified 
regressions.

(la)Monty Python
Wesley Janson
March 2022
"""
import statsmodels.api as sm
from linearmodels.panel import PanelOLS
from statsmodels.stats.outliers_influence import variance_inflation_factor
from patsy import dmatrices
import numpy as np
import pandas as pd
from backend import datasets

class DisasterRegs():
    '''
    Class for running natural disaster regressions.
    '''

    variable_dict = {'const':'Intercept term',
                'population':'County-level population.',
                'foreign_born':'Percentage of county population born outside U.S.',
                'black_afam':'Percentage of county population Black/African American.',
                'median_income':'Median household income (in nominal dollars).',
                'snap_benefits':'Percentage of county households on SNAP benefits in the last 12 months.',
                'unemp_rate':'County unemployment rate for prime-age workers.',
                'health_insurance_rate':'Percentage of county population with health insurance coverage.',
                'vacant_housing_rate':'Percentage of housing units vacant at time of survey.',
                'rental_vacancy_rate':'Percentage of rental units vacant at time of survey.',
                'median_rent':'Median gross rent at county level (in nominal dollars).',
                'median_home_price':'Median home price at county level (in nominal dollars).'}


    def __init__(self, states, year,reg_type = None):
        '''
		Constructor.

        Parameters:
			-states: list of states to filter on corresponding
            to specific hurricane.
            -year: year hurricane occurred.
            -reg_type: regression type to run.
		'''
        self.states = states
        self.year = year
        self.reg_type = reg_type


    def pull_data(self):
        '''
        Method that will pull data using API abstract class.
        '''
        self.dataframe = datasets.get_data(self.states,self.year)
        return self.dataframe
    

    def pooled_ols(self,dataset):
        '''
        Method to run simple pooled OLS regression.

        Input:
            -dataset: pandas dataframe to be read in and analyzed.
        '''
        y = pd.DataFrame(dataset, columns=['aid_requested'])
        exog_vars = self.vif_detection(pd.DataFrame(dataset, columns=['foreign_born','black_afam','median_income','snap_benefits','unemp_rate',
        'health_insurance_rate','vacant_housing_rate','rental_vacancy_rate','median_rent','median_home_price','population']),y)
        X = sm.add_constant(exog_vars)
        var_table = self.var_table(X)
        pooled_reg = sm.OLS(y,X).fit()

        return self.output_to_df(pooled_reg,"pooled"),y.merge(exog_vars, left_index=True, right_index=True),var_table


    def panel_ols(self,dataset):
        '''
        Method running Fixed Effect regression. The state is set to be the panel variable, 
        with the year being the time variable.

        Input:
            -dataset: pandas dataframe to be read in and analyzed.
        '''
        dataset['year'] = pd.to_datetime(dataset.year, format='%Y')
        dataset.astype({'state_fips': 'int32'}).dtypes
        dataset = dataset.set_index(['state_fips','year'])

        y = pd.DataFrame(dataset, columns=['aid_requested'])
        exog_vars = self.vif_detection(pd.DataFrame(dataset, columns=['foreign_born','black_afam','median_income','snap_benefits','unemp_rate',
        'health_insurance_rate','vacant_housing_rate','rental_vacancy_rate','median_rent','median_home_price','population']),y)
        X = sm.add_constant(exog_vars)
        var_table = self.var_table(X)
        
        fe_reg = PanelOLS(y, sm.add_constant(exog_vars), entity_effects=True, time_effects=False).fit(cov_type='robust') 

        return self.output_to_df(fe_reg,"fe"),y.merge(exog_vars, left_index=True, right_index=True),var_table


    def output_to_df(self,reg_output,reg_type):
        '''
        Method taking regression summary table and saves in clean pandas df.
            For readability, the numbers in the table are rounded to thousandths
            decimal place.

        Input:
            -reg_output: regression output table to be converted.
            -reg_type: type of regression to be run.
        '''
        coefs = reg_output.params
        pvals = reg_output.pvalues
        if reg_type=="pooled":
            std_err = reg_output.bse
            tvals = reg_output.tvalues            
        else:
            std_err = reg_output.std_errors
            tvals = reg_output.tstats
        
        out_df = pd.DataFrame({"Coefficient Estimate":coefs, "Standard Error":std_err,
                            "T-Stat":tvals, "P-Value":pvals})
        out_df.reset_index()

        return out_df.round(decimals=3)


    def vif_detection(self,exog_vars,dep_var):
        '''
        Method computing Variance Inflation Factors (VIF) on prospective exogenous variables for regression. 
        5 (inclusive) is used as the cutoff for multicollinearity. This function eliminiates the variable with 
        the highest VIF, and reruns the regression until the highest VIF is below the threshold.

        Input:
            -exog_vars (pandas df): pandas dataframe of potential exogenous variables for regression.
            -dep_var (pandas series): pandas dataframe of dependent variable in regression.
        '''
        max_vif = float('inf')
        while max_vif > 5:
            reg_string = dep_var.columns[0] + ' ~ ' + '+'.join(exog_vars.columns)
            _, X = dmatrices(reg_string, data=self.dataframe, return_type='dataframe')
            vif = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
            max_vif = max(vif[1:])
            if max_vif > 5:
                max_col = vif.index(max_vif)
                exog_vars = exog_vars.drop(exog_vars.columns[max_col-1], axis=1)

        return exog_vars


    def var_table(self,exog_vars):
        '''
        Method to take exogenous variables used in regression and create corresponding
        variable description table to be displayed on UI page.

        Input:
            -exog_vars: list of exogenous variables that will be added to variable
                description table.
        '''
        desc_list=[]
        for var in exog_vars.columns:
            desc_list.append(self.variable_dict[var])

        return pd.DataFrame({"Independent Variable":exog_vars.columns, "Description":desc_list})

