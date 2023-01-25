'''
class Simulation:

    initialize:
        --Afairi = new Company()

    run_simulation_for_future_month
        -- Afairi.update_next_month

    run_simulation_for_ten_yrs

    output_finial_report
        export to excel file

class Company:

    initialize:
        initialize first month
            -- c_1 = new cohort()
        create list of cohorts

    update_next_month()
        if cohort_x.startingmonth == currentmonth
            -- c_x = new cohort()
            -- group of cohort add c_x
        update group of cohort for next month()

    update group of cohort for next month:
        for cohort in group of cohort:
            cohort.update_future_month
        monthly financial report = combine of individual financial report

    combine of individual financial report:
        return the monthly fin report

    output financial statement:
        customers get updated from all cohorts
            return the total customer number of the group

        profit_&_loss statement get updated
            return the p & l statement of the combine cohort group

        pocket/balance_sheet get updated
            -- company debt
            -- investment
            return the balance_sheet statement of the combine cohort group

        cashflow get updated
        return the cashflow statement of the combine cohort group

        output_financial_report for the current month


class Cohort:

    initialize the cohort
        --everthingAt&BeforeStartingMonth
        --update first month values
            including things related to the first month

    update_future_month
        update p&l
        update balance sheet
        update cashflow

    output cohort financial report
'''
import pandas as pd
from data_getter import *

LIFE_SPAN = 120 #TODO: update the life span

#############
# Simulation
#############
class Simulation:
    '''
    Input file contains two kinds of files, global data and distinct input data file.
    '''
    def __init__(self, input_path):
        self.current_month = 0
        self.input_path = input_path
        global_data, list_input_para_files = self.init_data()
        self.afairi = Company(global_data, list_input_para_files)
        self.update_current_month()

    def update_current_month(self):
        self.current_month += 1
        self.afairi.current_month += 1

    def init_data(self):
        # TODO: initialize dataset input functions
        data = get_global_data(self.input_path)
        list_files = get_list_input_data_files(data, config.file_path)
        list_vars = load_list_outputs_variables()
        return data, list_files, list_vars

    def run_for_this_month(self):
        self.afairi.run_for_this_month()
        self.update_current_month()

    def run_for_whole_time_span(self):
        for _ in range(LIFE_SPAN):
            self.run_for_this_month()

    def output_full_report(self):
        self.nice_print_report_format()
        return self.afairi.output_latest_financial_report()

    def output_to_excel(self):
        #TODO: export to excel output file.
        return None

    def nice_print_report_format(self):
        print('Current simulation month is: ', self.current_month)
        print('\n-----------')
        print('This financial report is \n')



class Company:
    def __init__(self, global_data, list_input_para_files):
        c_1 = Cohort(global_data[1], list_input_para_files[1].copy()) # TODO:starting data input
        self.cohort_group = [c_1]
        self.global_data = global_data
        self.list_input_para_files = list_input_para_files
        # self.investing_account = Investment()
        self.current_month = 0
        self.financial_report = pd.DataFrame()

    def run_for_this_month(self):
        assert self.current_month == self.cohort_group[0].current_month, f'The Company and cohort level month is not consistent.'
        self.assert_all_cohort_current_month_consistent()
        for cohort_numb in self.global_data:
            if self.global_data[cohort_numb]['start_month'] == self.current_month:
                # TODO: data input
                new_cohort = Cohort(self.global_data[cohort_numb], self.list_input_para_files[cohort_numb].copy())
                self.cohort_group.append(new_cohort)
        self.update_group_cohorts_next_month()
        return None

    def assert_all_cohort_current_month_consistent(self):
        #TODO: assert cohort month in group
        return None


    def update_group_cohorts_next_month(self):
        for idx in range(len(self.cohort_group)):
            self.update_individual_cohort_one_month(self.cohort_group[idx])
        self.combine_update_full_report()

    def combine_update_full_report(self):
        # TODO: to combine individual cohort report to a full one.
        for cohort in self.cohort_group:
            self.financial_report += cohort.output_financial_report()

    def update_individual_cohort_one_month(self, cohort):
        cohort.update_one_month()
        cohort.starting_month = self.current_month

    def output_latest_financial_report(self):
        return self.financial_report.copy()

    def output_latest_number_customer(self):
        return f'There are {self.financial_report.loc[self.current_month]} customers at the month {self.current_month}.'

    def output_individual_report(self):
        lt_report = []
        for ch in self.cohort_group:
            lt_report.append(ch.output_financial_report())
        return lt_report

    def update_investment_from_outside(self):
        #self.investing_account. update # TODO: update this account to receive investment from the outside.
        return pd.DataFrame()



class Cohort:
    def __init__(self, global_para, input_data):
        # PARAS:
        self.gb_para = global_para
        self.starting_month = global_para['start_month']
        self.input_data = input_data.copy()
        self.financial_report = pd.DataFrame()
        # TODO: update everything before the starting month
        # TODO: update the starting month, then self.current_month = 1
        self.init_canvas_before_starting()
        self.init_starting_month()
        ## To make the cohort month and upper structure month consistent
        self.current_month = self.starting_month + 1

    def init_canvas_before_starting(self):

        # take the cohort -- g1 as canvas and update data from there
        # draw the canvas




    def init_starting_month(self):
        #update all the constant on the starting month
        #update all the non-constant on the starting month
        #update all the values before the starting month
        #attach all the data back to the financial report   self.update_financial_report

    def update_financial_report(self):
        return None

    def update_one_month(self):
        # update p&l section
        # update the balance sheet section after one yr
        # update the cash flow section after one yr

    def output_financial_report(self):
        return self.financial_report.copy()



'''
class Investment:
    def __init__(self):
        self.investment = pd.DataFrame()

    def init_from_company_report(self, report):

        return None

    def update_every_month_from_report(self, report):
        return None
'''
