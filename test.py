import pandas as pd



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
        self.current_row['Retention ratio monthly-P&L'] = self.current_row['Retention ratio yearly-P&L' ]* *( 1 /12)

    def update_quantity(self):
        if (self.month_since_start_pl == self.startmonth):
            self.current_row['Quantity-P&L'] = self.start_quantity
        else:
            assert not np.isnan(self.current_row['Retention ratio monthly-P&L'])
            self.current_row['Quantity-P&L'] = self.last_row['Quantity-P&L'] * self.current_row
                ['Retention ratio monthly-P&L']

    def update_monthly_premium(self):
        if (self.month_since_start_pl - self.startmonth) % 12 == 0 and self.month_since_start_pl != self.startmonth:
            self.premium *= self.price_increase_ratio
        self.current_row['Premium per month-P&L'] = self.premium

    def update_premiumVolume_netRev(self):
        self.current_row['Premium, Volume-P&L'] = self.current_row['Premium per month-P&L'] * self.current_row
            ['Quantity-P&L']
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
                                                                  self.current_row['Loss-P&L'] - self.current_row
                                                                      ['Expenses-P&L']
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
