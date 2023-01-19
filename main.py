import warnings
import os
import warnings
import pandas as pd
from pandas import ExcelWriter

'''
Framework to parse parameters and data 
sheet_name format as 
Cohort PI 
Cohort UW
PI/UW is classified as Proxy Insurance and underwriting 
Each class of Cohort has the same set of input parameters that is structured in config file. 
Each cohort will have the same output financial statement parameters, which will be combine at the end. 
Output will have P-L statement, Cash Flow (with investment sheet and working capital),  and Balance sheet.  
'''

def get_data(filepath, sheetname):
    df = pd.read_excel(filepath, sheet_name=sheetname, skiprows=1)
    colnames = df['Variable']
    df = df.filter(like="Value", axis=1).transpose()
    df.columns = colnames
    df.index = df['months since start']

    return df


if __name__ == '__main__':
    path_dir = 'data/input/data.xlsx'
    sheet_name = "Cohort PI 000-"
    df_test = get_data(path_dir, sheet_name)
    print(df_test)
    # print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
