import warnings
import os
import pandas as pd
from pandas import ExcelWriter

import config
from conceptCode import *



if __name__ == '__main__':
    path = config.file_path
    simu = Simulation(path)
    # simu.run_for_one_future_month()
    # print(simu.afairi.output_latest_number_customer())
    print(simu.output_full_report())