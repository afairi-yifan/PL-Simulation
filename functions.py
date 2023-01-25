'''
Function file for simulation
Input three kinds of files, including the Global input file,
Cohort PI G# and Cohort UW G# files, which includes all different variables for specific group.
'''
import pandas as pd
import numpy as np
import config

FORECAST_CYCLE = 12
BUFFER_MONTH = 3
INIT_LIA_TIME = 1
TOTAL_NUMB_MONTH = 120

def get_global_data(filepath):
    df = pd.read_excel(filepath, sheet_name=config.global_sheet_name)
    index_name = df['Index']
    df.index = index_name
    df = df.drop('Index', axis=1)
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

    def give_outputs_variables(self):
        df = self.createDataFrameworkSuffix()
        outputs = list(df.loc[df['Input/Output'] == 'var', 'Variable'])
        return outputs

    def load_list_outputs_variables(self):
        df = self.createDataFrameworkSuffix()
        outputs1 = list(df.loc[df['Index'] == 'pl', 'Variable'])
        outputs2 = list(df.loc[df['Index'] == 1, 'Variable'])
        outputs3 = list(df.loc[df['Index'] == 2, 'Variable'])
        return [outputs1, outputs2, outputs3]


    # Separate the input and output variables into different dataframe
    def dataframe_from_excel(self):
        dataframe = self.createDataFrameworkSuffix()
        outputs = self.give_outputs_variables()
        index_names = dataframe['Variable']
        dataframe = dataframe.filter(like="Value", axis=1)
        dataframe.index = index_names
        df_data = dataframe.loc[outputs]
        lines = np.arange(-12, TOTAL_NUMB_MONTH + FORECAST_CYCLE + 1, 1)
        df_data.columns = lines
        df_input = df_data.transpose()
        return df_input

class Simulation:
    '''
    update the individual cohorts (with special step size)
    shift the cohorts with coefficients or step size
    Then add all of them together for the final.

    Parameters:
    steps: means that each step is one month
    full_run: mean that update the whole sheet up to 10 years
    '''
    def __init__(self):
        self.last_month = 120
        self.report_list = []


    def run(self):
        '''
        This run designs as given the global input and a sample of input parameters, then we can have the output.
        :return:
        '''
        data_dic = get_global_data(config.file_path)
        for item in data_dic:
            if isinstance(item, int):
                print(item)
            else:
                pass
        return self.report_cashflow, self.report_pl, self.report_balancesheet

    # def make_report(self):
    #     # Print out all the data and store it to the Pandas dataframe



class Cohort:
    '''
    Initialize the constant variables then copy the whole data set before start_month to the final_report
    update the p&l 12 months in advance
    update other data variables in parallel with p&l variables

    parameter:
        coh_type
        coh_group
    attributes:
        acquisition_ratio
    '''
    def __init__(self, input_df, var_list, global_data=None):
        # Data input file
        self.data = input_df.copy()
        self.gb_var = global_data
        self.var_pl = var_list[0] + ['Regulatory requirement absolute-InvestSide']
        self.var_input = var_list[1]
        self.var_output = var_list[2]
        # Parameters
        self.coh_type = global_data['Cohort_Type']
        self.coh_group = global_data['Cohort_Group']
        self.start_quantity = global_data['start_quantity']
        self.startmonth = global_data['start_month']
        self.month_since_start_pl = self.startmonth
        self.month_since_start_lia = self.startmonth
        self.month_since_start_rest = self.startmonth
        self.month_since_start_2loop = self.startmonth
        self.inflation = global_data['inflation']
        self.premium = global_data['premium']
        self.price_increase_ratio = global_data['price_increase_ratio']
        self.acquisition_ratio = global_data['acquisition_ratio']
        self.starting_val_wcr = 0
        # Data to be update
        self.current_row = self.data.loc[self.startmonth].copy()
        self.current_row_to_replace = self.data.loc[self.startmonth].copy()
        self.current_row_rest = self.data.loc[self.startmonth].copy()
        self.current_row_2loop = self.data.loc[self.startmonth].copy()
        self.computed = {}
        self.final_report = pd.DataFrame()

        # month zero
        self.data.loc[self.startmonth, 'Quantity-P&L'] = self.start_quantity
        # all month
        self.init_constant_var_for_all_month()
        # Month after the start
        self.init_var_month_after_startmonth()
        # Month before the start
        # TODO: input variables and cash flow variables are all zeros

        # Copy all columns before the start month
        self.final_report = pd.concat([self.final_report, self.data.loc[:(self.startmonth - 1)]], axis=0)
        assert len(self.final_report.columns) == len(self.data.columns), f'The number of the columns is not aligned with the original.'
        # Initialize P&L for 12 months in advance and update liability, 2 investing and asset sections.
        self.init_whole_chart()


    def init_constant_var_for_all_month(self):
        ratio_list = ['Retention ratio yearly-P&L', 'Risk ratio-P&L', 'Profit share ratio MGA-P&L', 'Expense Ratio-P&L',
                      'Regulatory requirement ratio-InvestSide', 'Research and Development1-InvestSide',
                      'Business-expansion (market entry cost)1-InvestSide', 'Interest rate-FinanceSide',
                      'Loss ratio-PreviousII', 'Expense in advance ratio-PreviousII', 'Profit share ratio MGA-P&L']
        for ratio in ratio_list:
            self.update_fixed_ratio(ratio)
        self.data.loc[:, 'Retention ratio monthly-P&L'] = self.data['Retention ratio yearly-P&L'][self.startmonth] ** (
                    1 / 12)
        self.update_workingcapital_ratio()

    def init_var_month_after_startmonth(self):
        self.update_premium()
        self.update_netRev_startmonth()
        self.update_acquisition_cost()
        working_cap_variables = ['Working capital acquisition1-InvestSide', 'Working capital expenses1-InvestSide',
                                 'Working capital loss1-InvestSide']
        self.data.loc[self.startmonth:, working_cap_variables] = 0


    def init_whole_chart(self):
        self.computed = dict.fromkeys(self.data.columns, 0)
        for _ in range(FORECAST_CYCLE + BUFFER_MONTH):
            self.loop_section_pl()
        self.loop_section_liability()
        # Update two investing sections
        self.init_two_investing_sections()
        # Update the asset section
        self.update_asset()

    def init_two_investing_and_asset_sections(self):
        first_month_row = self.final_report.loc[self.startmonth]
        self.assert_start_month_value_valid('Loss requirement 12 months-Liability')
        self.final_report.loc[self.startmonth, 'Loss in advance-real-PreviousII'] = first_month_row['Loss requirement 12 months-Liability']
        self.assert_start_month_value_valid('Expense capital requirement absolute-Liability')
        self.final_report.loc[self.startmonth, 'Expenses in advance-PreviousII'] = first_month_row['Expense capital requirement absolute-Liability']
        self.final_report.loc[self.startmonth - 12, 'Working capital loss1-InvestSide'] = -first_month_row['Loss requirement 12 months-Liability']
        self.final_report.loc[self.startmonth - 6, 'Working capital expenses1-InvestSide'] = -first_month_row['Expense capital requirement absolute-Liability']
        self.final_report.loc[self.startmonth - 3, 'Working capital acquisition1-InvestSide'] = -first_month_row['Acquisition Costs in advance-PreviousII']
        self.assert_start_month_value_valid('Loss requirement 12 months-Liability')
        self.assert_start_month_value_valid('Expenses in advance-PreviousII')
        self.assert_start_month_value_valid('Acquisition Costs in advance-PreviousII')
        self.final_report.loc[:self.startmonth, 'Risk loss 12 months-Assets'] = self.final_report.loc[self.startmonth, 'Loss requirement 12 months-Liability']
        self.final_report.loc[(self.startmonth - 6):(self.startmonth - 1), 'Expenses 12 months-Assets'] = - \
        self.final_report.loc[self.startmonth, 'Expenses in advance-PreviousII']
        self.final_report.loc[(self.startmonth - 3):(self.startmonth - 1), 'Acquisition 12 months-Assets'] = - \
        self.final_report.loc[self.startmonth, 'Acquisition Costs in advance-PreviousII']
        self.final_report.loc[self.startmonth:, 'Acquisition 12 months-Assets'] = 0


    # def update_asset(self):
    #     self.final_report.loc[self.month_since_start_lia, 'Risk loss 12 months-Assets'] = self.final_report.loc[self.month_since_start_lia, 'Loss requirement 12 months-Liability']
    #     self.final_report.loc[self.month_since_start_lia, 'Expenses 12 months-Assets'] = 0

    def __repr__(self):
        return f'Cohort (Group: {self.coh_group}, Type: {self.coh_type}, Start Month: {self.startmonth}, ' \
               f'Quantity: {self.start_quantity})'

    def __str__(self):
        data = str(self.gb_var)
        return f'Cohort' + data

    def assert_start_month_value_valid(self, para):
        assert not np.isnan(self.data.loc[self.startmonth, para]), f'The {para} at {self.startmonth} has no valid value.'

    def update_fixed_ratio(self, ratio):
        self.assert_start_month_value_valid(ratio)
        fixed_ratio = self.data.loc[self.startmonth, ratio]
        self.data.loc[:, ratio] = fixed_ratio

    def update_workingcapital_ratio(self):
        starting_val_wcr = self.startmonth + 12
        self.data.loc[self.startmonth:starting_val_wcr, 'Working capital financing ratio-FinanceSide'] = 0
        self.data.loc[starting_val_wcr:, 'Working capital financing ratio-FinanceSide'] = 0.5

    def update_premium(self):
        price_increase_circle = 12
        for i in self.data.index:
            if i < self.startmonth:
                continue
            if (i - self.startmonth) % price_increase_circle == 0 and i != self.startmonth:
                self.premium *= self.inflation
            self.data.loc[i, 'Premium per month-P&L'] = self.premium

    def update_netRev_startmonth(self):
        self.assert_start_month_value_valid('Quantity-P&L')
        self.assert_start_month_value_valid('Premium per month-P&L')
        st_premium = self.data.loc[self.startmonth, 'Premium per month-P&L']
        self.data.loc[self.startmonth, 'Net revenue-P&L'] = self.start_quantity * st_premium

    def update_acquisition_cost(self):
        self.assert_start_month_value_valid('Net revenue-P&L')
        net_rev = self.data.loc[self.startmonth, 'Net revenue-P&L']
        acqu1 = self.acquisition_ratio * net_rev
        self.data.loc[self.startmonth, 'Acquisition Costs-P&L'] = acqu1
        self.data.loc[self.startmonth + 1, 'Acquisition Costs-P&L'] = 0
        self.assert_start_month_value_valid('Acquisition in advance ratio-PreviousII')
        acq_adv_ratio = self.data.loc[self.startmonth, 'Acquisition in advance ratio-PreviousII']
        acqu2 = acqu1 * acq_adv_ratio
        self.data.loc[self.startmonth, 'Acquisition Costs in advance-PreviousII'] = acqu2
        self.data.loc[self.startmonth, 'Acquisition-NowCast'] = acqu1 - acqu2


    # Update the p & l section
    def loop_section_pl(self):
        if self.month_since_start_pl <= (TOTAL_NUMB_MONTH + FORECAST_CYCLE):
            self.current_row = self.data.loc[self.month_since_start_pl].copy()
            for col_name in self.var_pl:
                assert len(self.var_pl) == 11, f'The number of function is not aligned with the variables'
                self.update_p_l_append_report(col_name)
            # Update month and final_report
            print(self.month_since_start_pl)
            row_to_concat = pd.DataFrame(self.current_row).transpose()
            self.final_report = pd.concat([self.final_report, row_to_concat], axis=0)
            assert len(self.final_report.columns) == len(self.data.columns), f'The columns are not aligned, final report has {len(self.final_report.columns)}.'
            self.month_since_start_pl += 1
        else:
            pass

    def assert_value(self, para, row, month):
        assert not np.isnan(row.loc[para]), f'{para} at this month {month} is not valid.'

    def assert_this_month_two_value(self, name1, name2):
        # if month < self.month_since_start_pl:
        assert not np.isnan(self.current_row.loc[name1]), f'{name1} at {self.month_since_start_pl} is not valid'
        assert not np.isnan(self.current_row.loc[name2]), f'{name2} at {self.month_since_start_pl} is not valid'

    def update_p_l_append_report(self, col_name):
        '''
        update P&L function always append to the report dataframe, while update other graph is replacement.
        :return: none
        '''
        assert len(self.final_report.index) - 12 == self.month_since_start_pl, f'Month is wrong. Final report index has {len(self.final_report.index)} and month is {self.month_since_start_pl}'
        if col_name in self.var_input:
            pass
        elif col_name == 'Quantity-P&L':
            if self.month_since_start_pl == self.startmonth:
                self.current_row['Quantity-P&L'] = self.start_quantity
            else:
                pre_ratio = self.final_report.loc[self.month_since_start_pl - 1, 'Retention ratio monthly-P&L']
                pre_quantity = self.final_report.loc[self.month_since_start_pl - 1, 'Quantity-P&L']
                assert not np.isnan(pre_ratio), f'Quantity-P&L at {self.month_since_start_pl} is not valid'
                assert not np.isnan(pre_quantity), f'Retention ratio monthly-P&L at {self.month_since_start_pl} is not valid'
                self.current_row['Quantity-P&L'] = pre_quantity * pre_ratio
                self.computed['Quantity-P&L'] += 1
        elif col_name == 'Premium, Volume-P&L':
            self.assert_this_month_two_value('Quantity-P&L', 'Premium per month-P&L')
            self.current_row['Premium, Volume-P&L'] = self.current_row['Premium per month-P&L'] * self.current_row['Quantity-P&L']
            self.computed['Premium, Volume-P&L'] += 1
        elif col_name == 'Net revenue-P&L':
            self.assert_value('Premium, Volume-P&L', self.current_row, self.month_since_start_pl)
            self.current_row['Net revenue-P&L'] = self.current_row['Premium, Volume-P&L']
            self.computed['Net revenue-P&L'] += 1
        elif col_name == 'Loss-P&L':
            self.assert_this_month_two_value('Net revenue-P&L', 'Risk ratio-P&L')
            self.current_row['Loss-P&L'] = self.current_row['Net revenue-P&L'] * self.current_row['Risk ratio-P&L']
            self.computed['Loss-P&L'] += 1
        elif col_name == 'Profit share MGA-P&L':
            self.assert_value('Profit share ratio MGA-P&L', self.current_row, self.month_since_start_pl)
            self.assert_this_month_two_value('Net revenue-P&L', 'Loss-P&L')
            ratio = self.current_row['Profit share ratio MGA-P&L']
            self.current_row['Profit share MGA-P&L'] = (self.current_row['Net revenue-P&L'] - self.current_row['Loss-P&L']) * ratio
            self.computed['Profit share MGA-P&L'] += 1
        elif col_name == 'Expenses-P&L':
            self.assert_this_month_two_value('Net revenue-P&L', 'Expense Ratio-P&L')
            self.current_row['Expenses-P&L'] = self.current_row['Net revenue-P&L'] * self.current_row['Expense Ratio-P&L']
            self.computed['Expenses-P&L'] += 1
        elif col_name == 'Net income pre-acquisition cost-P&L':
            self.current_row['Net income pre-acquisition cost-P&L'] = self.current_row['Profit share MGA-P&L'] - self.current_row['Expenses-P&L']
            self.computed['Net income pre-acquisition cost-P&L'] += 1
        elif col_name == 'Net income-P&L':
            if self.month_since_start_pl == self.startmonth:
                self.assert_value('Acquisition Costs-P&L', self.current_row, self.month_since_start_pl)
                self.current_row['Net income-P&L'] = self.current_row['Net income pre-acquisition cost-P&L'] - self.current_row['Acquisition Costs-P&L']
            else:
                self.current_row['Net income-P&L'] = self.current_row['Net income pre-acquisition cost-P&L']
            self.computed['Net income-P&L'] += 1
        elif col_name == 'Regulatory requirement absolute-InvestSide':
            self.assert_value('Loss-P&L', self.current_row, self.month_since_start_pl)
            if self.month_since_start_pl == self.startmonth:
                ratio = self.current_row['Regulatory requirement ratio-InvestSide']
                self.final_report.loc[:self.startmonth, 'Regulatory requirement absolute-InvestSide'] = ratio * self.current_row['Loss-P&L'] * 12
            else:
                ratio = self.current_row['Regulatory requirement ratio-InvestSide']
                self.current_row.loc['Regulatory requirement absolute-InvestSide'] = ratio * self.current_row['Loss-P&L'] * 12

    # Update the Liability section
    def loop_section_liability(self):
        self.current_row_to_replace = self.data.loc[self.month_since_start_lia].copy()
        for col_name in self.var_output:
            self.update_liability(col_name)
        self.final_report.loc[self.month_since_start_lia] = self.current_row_to_replace
        self.month_since_start_lia += 1


    def assert_12month_advancement(self, original, sum_input):
        assert self.computed[original] - self.computed[sum_input] >= 12, f'Need at least 12 months advancement to ' \
                                                                         f'update {sum_input} from {original}!'

    def update_liability(self, col_name):
        if col_name == 'Forecast Loss 12 months-Liability':
            self.assert_12month_advancement('Loss-P&L', 'Forecast Loss 12 months-Liability')
            sum = self.final_report.loc[self.month_since_start_lia:(self.month_since_start_lia + FORECAST_CYCLE), 'Loss-P&L'].sum()
            self.current_row_to_replace.loc['Forecast Loss 12 months-Liability'] = sum
            self.computed['Forecast Loss 12 months-Liability'] += 1
        elif col_name == 'Loss requirement 12 months-Liability':
            self.assert_value('Loss ratio-PreviousII', self.current_row_to_replace,  self.month_since_start_lia)
            self.current_row_to_replace.loc['Loss requirement 12 months-Liability'] = self.current_row_to_replace['Forecast Loss 12 months-Liability'] * (1 - self.current_row_to_replace['Loss ratio-PreviousII'])
            self.computed['Loss requirement 12 months-Liability'] += 1
        elif col_name == 'Forecast Expense 12 months-Liability':
            self.assert_12month_advancement('Expenses-P&L', 'Forecast Expense 12 months-Liability')
            self.current_row_to_replace.loc['Forecast Expense 12 months-Liability'] = self.final_report.loc[self.month_since_start_lia:(self.month_since_start_lia + FORECAST_CYCLE),'Expenses-P&L'].sum()
            self.computed['Forecast Expense 12 months-Liability'] += 1
        elif col_name == 'Expense capital requirement absolute-Liability':
            self.assert_value('Expense in advance ratio-PreviousII', self.current_row_to_replace, self.month_since_start_lia)
            self.current_row_to_replace.loc['Expense capital requirement absolute-Liability'] = self.current_row_to_replace['Forecast Expense 12 months-Liability'] * (1 - self.current_row_to_replace['Expense in advance ratio-PreviousII'])
            self.computed['Expense capital requirement absolute-Liability'] += 1
        elif col_name == 'Risk loss 12 months-Assets':
            self.assert_value('Loss requirement 12 months-Liability', self.current_row_to_replace, self.month_since_start_lia)
            self.current_row_to_replace['Risk loss 12 months-Assets'] = self.current_row_to_replace['Loss requirement 12 months-Liability']
        elif col_name == 'Expenses 12 months-Assets':
            if self.final_report.loc[self.month_since_start_lia - 1, 'Expenses 12 months-Assets'] < self.current_row_to_replace['Expenses-P&L']):
                self.current_row_to_replace['Expenses 12 months-Assets'] = 0
            else:
                self.current_row_to_replace['Expenses 12 months-Assets'] =


    # Update the Rest of the chart
    def loop_section_rest(self):
        self.current_row_rest = self.final_report.loc[self.month_since_start_rest].copy()
        for col_name in self.var_output:
            self.update_the_rest(col_name)
        self.final_report.loc[self.month_since_start_rest] = self.current_row_rest
        self.month_since_start_rest += 1

    def update_the_rest(self, col_name):
        if col_name == 'Loss requirement absolute-NowCast':
            self.assert_value('Loss requirement 12 months-Liability', self.current_row_rest,  self.month_since_start_rest)
            self.current_row_rest['Loss requirement absolute-NowCast'] = self.current_row_rest['Loss requirement 12 months-Liability']
            self.computed['Loss requirement absolute-NowCast'] += 1
        elif col_name == 'Expense capital requirement absolute-NowCast':
            self.assert_value('Expense capital requirement absolute-Liability', self.current_row_rest, self.month_since_start_rest)
            self.current_row_rest['Expense capital requirement absolute-NowCast'] = self.current_row_rest['Expense capital requirement absolute-Liability']
            self.computed['Expense capital requirement absolute-NowCast'] += 1
        elif col_name == 'Expenses-NowCast' or 'Expenses from continuous operations-CashFlow':
            self.assert_value('Expenses-P&L', self.current_row_rest, self.month_since_start_rest)
            self.current_row_rest['Expenses-NowCast'] = self.current_row_rest['Expenses-P&L']
            self.current_row_rest['Expenses from continuous operations-CashFlow'] = self.current_row_rest['Expenses-P&L']
            self.computed['Expenses-NowCast'] += 1
            self.computed['Expenses from continuous operations-CashFlow'] += 1
        elif col_name == 'Revenue-CashFlow':
            self.assert_value('Net revenue-P&L', self.current_row_rest, self.month_since_start_rest)
            self.current_row_rest['Revenue-CashFlow'] = self.current_row_rest['Net revenue-P&L']
            self.computed['Revenue-CashFlow'] += 1

    def assert_next_values(self, para, para_later):
        assert self.computed[para] - self.computed[para_later] >= 1, f'The next month value {para} is yet not valid.'

    def loop_twice_before_this(self):
        self.current_row_2loop = self.final_report.loc[self.month_since_start_2loop].copy()
        for col_name in self.var_output:
            self.two_update_before_this_values(col_name)
        self.final_report.loc[self.month_since_start_2loop] = self.current_row_2loop
        self.month_since_start_2loop += 1

    def two_update_before_this_values(self, col_name):
        if col_name == 'Loss-NowCast':
            self.assert_next_values('Loss requirement absolute-NowCast', 'Loss-NowCast')
            next = self.final_report.loc[self.month_since_start_2loop + 1]
            self.current_row_2loop['Loss-NowCast'] = self.current_row_2loop['Loss-P&L'] + next - self.current_row_2loop['Loss requirement absolute-NowCast']
            self.computed['Loss-NowCast'] += 1
        elif col_name == 'Net income-NowCast':
            self.current_row_2loop['Net income-NowCast'] = self.current_row_2loop['Net revenue-P&L'] - self.current_row_2loop['Loss-NowCast'] - self.current_row['Expenses-NowCast']
            self.computed['Net income-NowCast'] += 1
        elif col_name == 'Loss from contious operations-CashFlow':
            self.current_row_2loop['Loss from contious operations-CashFlow'] = self.current_row_2loop['Loss-NowCast']
            self.computed['Loss from contious operations-CashFlow'] += 1
        elif col_name == 'Earnings-CashFlow':
            self.current_row_2loop['Earnings-CashFlow'] = self.current_row_2loop['Revenue-CashFlow'] - self.current_row_2loop['Loss from contious operations-CashFlow'] - self.current_row_2loop['Expenses from continuous operations-CashFlow']
            self.computed['Earnings-CashFlow'] += 1
        elif col_name == 'Change from non-cash to cash-OperateSide':
            self.assert_next_values('Loss requirement 12 months-Liability', 'Change from non-cash to cash-OperateSide')
            next = self.final_report.loc[self.month_since_start_2loop + 1]
            self.current_row_2loop['Change from non-cash to cash-OperateSide'] = self.current_row_2loop['Loss requirement 12 months-Liability'] - next
            self.computed['Change from non-cash to cash-OperateSide'] += 1
        elif col_name == 'Cash from operating activities-OperateSide':
            self.current_row_2loop['Cash from operating activities-OperateSide'] = self.current_row_2loop['Earnings-CashFlow']


    # update the whole chart in one go
    def update(self, step):
        for _ in range(step):
            self.loop_section_pl()
            self.loop_section_liability()
            self.update_asset()
            self.loop_section_rest()
            if step % 2 == 0:
                self.loop_twice_before_this()
            else:
                continue
        assert self.month_since_start_lia - self.startmonth == step + INIT_LIA_TIME, f'Update liability month is {self.month_since_start_lia}, the starting month is {self.startmonth}'

        if (self.month_since_start_lia - self.startmonth) >= 24:
            loss = self.final_report.loc[self.starting_val_wcr, 'Loss requirement 12 months-Liability']
            capital = loss * self.current_row['Working capital financing ratio-FinanceSide']
            self.final_report.loc[self.month_since_start_lia, 'Working capital financing-FinanceSide'] = capital
            interest = capital * self.current_row['Interest rate-FinanceSide']
            self.final_report.loc[self.month_since_start_lia, 'Interest payment-FinanceSide'] = interest
            self.final_report.loc[self.month_since_start_lia, 'Cash from investing activities-FinanceSide'] = interest


    def ret_final_report(self):
        complete_10_yr_report = self.final_report.loc[:120]
        return complete_10_yr_report.copy()

# class CohortPI(Cohort):
#
#
# class CohortUW(Cohort):


