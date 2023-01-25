import pandas as pd
import numpy as np
import config

class CustomData:
    def __init__(self, filepath, sheetname):
        self.sheetname = sheetname
        self.filepath = filepath
    def createDataFrameworkSuffix(self):
        df = pd.read_excel(self.filepath, sheet_name=self.sheetname, skiprows=1)
        df['Variable'] = df['Variable'] + '-' + df['Suffix']
        return df
    def give_outputs_variables(self):
        df = self.createDataFrameworkSuffix()
        outputs = list(df.loc[df['Var'] == 'var', 'Variable'])
        return outputs
    def load_list_outputs_variables(self):
        df = self.createDataFrameworkSuffix()
        outputs1 = list(df.loc[df['Suffix'] == 'P&L', 'Variable'])
        outputs2 = list(df.loc[df['Input/Output'] == 'in', 'Variable'])
        outputs3 = list(df.loc[df['Input/Output'] == 'out', 'Variable'])
        return [outputs1, outputs2, outputs3]
    def dataframe_from_excel(self):
        dataframe = self.createDataFrameworkSuffix()
        outputs = self.give_outputs_variables()
        index_names = dataframe['Variable']
        dataframe = dataframe.filter(like="Value", axis=1)
        dataframe.index = index_names
        df_data = dataframe.loc[outputs]
        lines = np.arange(-12, 133, 1)
        df_data.columns = lines
        df_input = df_data.transpose()
        return df_input

def get_list_input_data_files(glob_data, file_path):
    list_title , list_data = [], [0]
    for item in glob_data:
        list_title.append(f'Cohort {glob_data[item]["Cohort_Type"]} {glob_data[item]["Cohort_Group"]}')
    for title in list_title:
        data_getter = CustomData(file_path, sheetname=title)
        list_data.append(data_getter.dataframe_from_excel())
    return list_data

def get_global_data(filepath):
    df = pd.read_excel(filepath, sheet_name=config.global_sheet_name)
    index_name = df['Index']
    df.index = index_name
    df = df.drop('Index', axis=1)
    dict_data = df.to_dict()
    return dict_data

