'''
Function file for simulation
Input three kinds of files, including the Global input file,
Cohort PI G# and Cohort UW G# files, which includes all different variables for specific group.
'''
import pandas as pd
import numpy as np
import config

def get_global_data(filepath, sheetname):
            # TODO:Input the global data from sheet Global Input


def createDataFrameworkSuffix(filepath, cohort_type, cohort_numb):
    df = pd.read_excel(filepath, sheet_name=f'Cohort {cohort_type} {cohort_numb}', skiprows=1)
    df['Variable'] =  df['Variable'] + '-' + df['suffix']
    return df

def load_inputs_outputs_variables(dataframe):
    df = dataframe
    outputs = list(df.loc[df['Input/Output'] == 'Output', 'Variable'])
    inputs = list(df.loc[df['Input/Output'] == 'Input', 'Variable'])
    return inputs, outputs

# Separate the input and output variables into different dataframe
def dataframe_input_output(dataframe, inputs, outputs):
    index_names = dataframe['Variable']
    dataframe = dataframe.filter(like="Value", axis=1)
    dataframe.index = index_names
    df_input = dataframe.loc[inputs]
    df_outputs = dataframe.loc[outputs]
    lines = [str(x) for x in np.arange(-12, 121, 1)]
    df_input.columns = lines
    df_outputs.columns = lines
    return df_input, df_outputs


class Simulation:
    '''
    update the individual cohorts (with special step size)
    shift the cohorts with coefficients or step size
    Then add all of them together for the thing.

    Parameters:
    steps: means that each step is one month
    full_run: mean that update the whole sheet up to 10 years
    '''
    def __init__(self, steps=1, full_run=False):
        self.steps = steps
        self.cohort = get_global_data(config.file_path, config.global_var_name)
        self.full_run = full_run

        self.report_cashflow = pd.DataFrame()
        self.report_pl = pd.DataFrame()
        self.report_balancesheet = pd.DataFrame()

    def update(self):
        # TODO:Update the global sheet through each step

    def run(self):
        # Comment the full run is to run the simulation for 10 years, which is 120
        self.steps(120)
        return self.report_cashflow, self.report_pl, self.report_balancesheet

    def make_report(self):
        # Print out all the data and store it to the Pandas dataframe

class Cohort:
    '''
    1. Separate the input and output variables from the input data file. Ok
    2. Create functions for each of the output variables.
    3. (test) Update step by step and check for the result
    4. (test) Update all cohort
    Variables:

    attributes:

    '''
    def __init__(self, input_df, global_data):
        # Data input file
        self.data = input_df.copy()
        # Parameters
        self.coh_type = global_data.cohort_type
        self.coh_group = global_data.cohort_group
        self.start_quantity = global_data.start_quantity
        self.month_since_start = global_data.start_month
        self.startmonth = global_data.start_month
        self.current_row = self.data.loc[self.month_since_start]
        self.last_row = self.data.loc[self.month_since_start-1]

    def __repr__(self):
        return f'Cohort (Group: {self.coh_group}, Type: {self.coh_type}, Start Month: {self.start_month}, ' \
               f'Quantity: {self.start_quantity})'

    # Profit and loss update
    def update_retention_ratio(self):
        assert not np.isnan(self.current_row['Retention ratio yearly-P&L'])
        self.current_row['Retention ratio monthly-P&L'] = self.current_row['Retention ratio yearly-P&L']**(1/12)

    def update_quantity(self):
        if (self.month_since_start == self.startmonth):
            self.current_row['Qupantity-P&L'] = self.start_quantity
        else:
            assert not np.isnan(self.current_row['Retention ratio monthly-P&L'])
            self.current_row['Quantity-P&L'] = self.last_row['Quantity-P&L'] * self.current_row['Retention ratio monthly-P&L']






    def update_PL(self):
        '''Update the P&L section'''
        update_quantity()


class CohortPI(Cohort):


class CohortUW(Cohort):


