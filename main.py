import warnings
import os
import pandas as pd
from pandas import ExcelWriter

import config
from functions import *
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
    #Test case 1
    data = CustomData(config.file_path, 'UW', 'G1')
    data_dic = get_global_data(config.file_path)
    df = data.dataframe_from_excel()
    list_var = data.load_list_outputs_variables()
    c1 = Cohort(df, list_var, data_dic[1])
    # print(str(c1))
    c1.update(120)
    outout = c1.ret_final_report().transpose()
    print(outout)
    #
    with ExcelWriter(f'{config.save_path}') as writer:
        outout.to_excel(writer, sheet_name='Simulation forth test')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
