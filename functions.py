'''
Function file for simulation
Input three kinds of files, including the Global input file,
Cohort PI G# and Cohort UW G# files, which includes all different variables for specific group.
'''
import pandas as pd
import numpy as np
import config

def get_global_data(filepath):
    df = pd.read_excel(filepath, sheet_name=config.global_sheet_name)
    index_name = df['Index']
    df.index = index_name
    dict_data = df.to_dict()
    return dict_data



class CustomData:
    def __init__(self, filepath, cohort_type, cohort_numb):
        self.cohort_type = cohort_type
        self.cohort_numb = cohort_numb
        self.filepath = filepath

    def createDataFrameworkSuffix(self):
        df = pd.read_excel(self.filepath, sheet_name=f'Cohort {self.cohort_type} {self.cohort_numb}', skiprows=1)
        df['Variable'] = df['Variable'] + '-' + df['Suffix']
        return df

    def load_inputs_outputs_variables(self):
        df = self.createDataFrameworkSuffix()
        outputs = list(df.loc[df['Input/Output'] == 'Output', 'Variable'])
        inputs = list(df.loc[df['Input/Output'] == 'Input', 'Variable'])
        return inputs, outputs

    def load_inputs_outputs_variables2(self):
        df = self.createDataFrameworkSuffix()
        outputs1 = list(df.loc[df['Index'] == 1, 'Variable'])
        outputs2 = list(df.loc[df['Index'] == 2, 'Variable'])
        outputs3 = list(df.loc[df['Index'] == 3, 'Variable'])
        return outputs1, outputs2, outputs3

    def dataframe_from_excel2(self):
        dataframe = self.createDataFrameworkSuffix()
        outputs1, outputs2, outputs3 = self.load_inputs_outputs_variables2()
        index_names = dataframe['Variable']
        dataframe = dataframe.filter(like="Value", axis=1)
        dataframe.index = index_names
        df_data = dataframe.loc[outputs1 + outputs2 + outputs3]
        lines = np.arange(-12, 121, 1)
        df_data.columns = lines
        df_input = df_data.transpose()
        return df_input

    # Separate the input and output variables into different dataframe
    def dataframe_from_excel(self):
        dataframe = self.createDataFrameworkSuffix()
        inputs, outputs = self.load_inputs_outputs_variables()
        index_names = dataframe['Variable']
        dataframe = dataframe.filter(like="Value", axis=1)
        dataframe.index = index_names
        df_data = dataframe.loc[inputs + outputs]
        lines = np.arange(-12, 121, 1)
        df_data.columns = lines
        df_input = df_data.transpose()
        return df_input


# class Simulation:
#     '''
#     update the individual cohorts (with special step size)
#     shift the cohorts with coefficients or step size
#     Then add all of them together for the thing.
#
#     Parameters:
#     steps: means that each step is one month
#     full_run: mean that update the whole sheet up to 10 years
#     '''
#     def __init__(self, steps=1, full_run=False):
#         self.steps = steps
#         self.cohort = get_global_data(config.file_path, config.global_var_name)
#         self.full_run = full_run
#
#         self.report_cashflow = pd.DataFrame()
#         self.report_pl = pd.DataFrame()
#         self.report_balancesheet = pd.DataFrame()
#
#     def update(self):
#             # TODO:Update the global sheet through each step
#
#     def run(self):
#         # Comment the full run is to run the simulation for 10 years, which is 120
#         self.steps(120)
#         return self.report_cashflow, self.report_pl, self.report_balancesheet
#
#     def make_report(self):
#         # Print out all the data and store it to the Pandas dataframe

class Cohort:
    '''
    1. Separate the input and output variables from the input data file. Ok
    2. Create functions for each of the output variables.
    3. (test) Update step by step and check for the result
    4. (test) Update all cohort
    Variables:

    attributes:

    '''
    def __init__(self, input_df, global_data=None):
        # Data input file
        self.data = input_df.copy()
        self.gb_var = global_data
        # Parameters
        self.coh_type = global_data['Cohort_Type']
        self.coh_group = global_data['Cohort_Group']
        self.start_quantity = global_data['start_quantity']
        self.month_since_start_pl = global_data['start_month']
        self.startmonth = global_data['start_month']
        self.inflation = global_data['inflation']
        self.premium = global_data['premium']
        self.price_increase_ratio = global_data['price_increase_ratio']
        self.acquisition_ratio = global_data['acquisition_ratio']
        # Data to be update
        self.current_row = self.data.loc[self.month_since_start_pl]
        self.last_row = self.data.loc[self.month_since_start_pl - 1]
        self.pl_update_times = 0
        self.computed = {}

    def __repr__(self):
        return f'Cohort (Group: {self.coh_group}, Type: {self.coh_type}, Start Month: {self.startmonth}, ' \
               f'Quantity: {self.start_quantity})'

    def __str__(self):
        data = str(self.gb_var)
        return f'Cohort' + data

    def update(self):
        self.computed = dict.fromkeys(self.data.columns, 0)

    # Profit and loss update
    '''
        Price increase is coded as 5% increase every year after the first month. 
    '''
    def update_retention_ratio(self):
        assert not np.isnan(self.current_row['Retention ratio yearly-P&L'])
        self.current_row['Retention ratio monthly-P&L'] = self.current_row['Retention ratio yearly-P&L']**(1/12)

    def update_quantity(self):
        if (self.month_since_start_pl == self.startmonth):
            self.current_row['Quantity-P&L'] = self.start_quantity
        else:
            assert not np.isnan(self.current_row['Retention ratio monthly-P&L'])
            self.current_row['Quantity-P&L'] = self.last_row['Quantity-P&L'] * self.current_row['Retention ratio monthly-P&L']

    def update_monthly_premium(self):
        if (self.month_since_start_pl - self.startmonth) % 12 == 0 and self.month_since_start_pl != self.startmonth:
            self.premium *= self.price_increase_ratio
        self.current_row['Premium per month-P&L'] = self.premium

    def update_premiumVolume_netRev(self):
        self.current_row['Premium, Volume-P&L'] = self.current_row['Premium per month-P&L'] * self.current_row['Quantity-P&L']
        self.current_row['Net revenue-P&L'] = self.current_row['Premium, Volume-P&L']

    def check_risk_expense_ratio(self, ratio):
        if np.isnan(self.current_row[ratio]):
            self.current_row[ratio] = self.last_row[ratio]
        else:
            pass

    def update_loss_expenses(self):
        self.current_row['Loss-P&L'] = self.current_row['Risk ratio-P&L'] * self.current_row['Net revenue-P&L']
        self.current_row['Expenses-P&L'] = self.current_row['Expense Ratio-P&L'] * self.current_row['Net revenue-P&L']
        self.computed['Loss-P&L'] += 1
        self.computed['Expenses-P&L'] += 1


    def update_two_netIncome(self):
        self.current_row['Net income pre-acquisition cost-P&L'] = self.current_row['Net revenue-P&L'] - \
                                                                  self.current_row['Loss-P&L'] - self.current_row['Expenses-P&L']
        if self.month_since_start_pl == self.startmonth:
            acquisi = self.acquisition_ratio * self.current_row['Net revenue-P&L'] * 12
            self.current_row['Acquisition Costs-P&L'] = acquisi
            self.current_row['Net income-P&L'] = self.current_row['Net income pre-acquisition cost-P&L'] - acquisi
        else:
            self.current_row['Net income-P&L'] = self.current_row['Net income pre-acquisition cost-P&L']

    def row_update(self):
        self.current_row = self.data.loc[self.month_since_start_pl]
        self.last_row = self.data.loc[self.month_since_start_pl - 1]

    def update_PL(self, step):
        '''Update the P&L section'''
        self.pl_update_times = step
        while step > 0:
            self.update_retention_ratio()
            self.update_quantity()
            self.update_monthly_premium()
            self.update_premiumVolume_netRev()
            self.check_risk_expense_ratio('Risk ratio-P&L')
            self.check_risk_expense_ratio('Expense Ratio-P&L')
            self.update_loss_expenses()
            self.update_two_netIncome()

            step -= 1
            self.month_since_start_pl += 1
            self.row_update()

    
    '''
        Update the Liability related cells 
    '''
    def assert_12month_advancement(self, original, sum_input):
        assert self.computed[original] - self.computed[sum_input] >= 12, f'Need at least 12 months advancement to ' \
                                                                         f'update {sum_input} from {original}!'

    def update_liability(self):
        assert self.pl_update_times >= 12, f'Need at least 12 months advancement to update liability!'








    def report_monthly(self):
        return self.current_row.copy()

    def report_data(self):
        return self.data.copy()

# class CohortPI(Cohort):
#
#
# class CohortUW(Cohort):


