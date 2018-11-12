import re
import pandas as pd
import os
import openpyxl
import collections as co
import numpy

def list_all_certain_format_filename(file_path,file_format):
    absolute_filename=[os.path.join(file_path,relative_filename) for relative_filename in os.listdir(file_path)
                       if os.path.isfile(os.path.join(file_path,relative_filename))
                       if os.path.splitext(relative_filename)[1] in file_format]
    return absolute_filename

def go_split(s, symbol):
    symbol = "[" + symbol + "]+"
    result = re.split(symbol, s)
    return result

def check_first_intention(intention_list):
    if 1 in intention_list:
        intention_index_1=intention_list.index(1)
    else:
        intention_index_1=999
    if 2 in intention_list:
        intention_index_2=intention_list.index(2)
    else:
        intention_index_2=999
    if intention_index_1<intention_index_2:
        first_intention=1
    else:
        first_intention=2
    return first_intention

def preprocess_str_list_data(data_df,particular_columns):
    data_pre_list = [data_df.iat[i, particular_columns] for i in range(len(data_df))]
    data_list = [eval(data) for data in data_pre_list ]
    return data_list

if __name__ == "__main__":
    project_path = os.path.abspath(".")
    values = co.OrderedDict()
    file_path = dict([("results_path", os.path.join(project_path, "results/"))])
    file_format = [".xlsx"]
    certain_format_file_name = list_all_certain_format_filename(file_path["results_path"], file_format)
    for i in range(len(certain_format_file_name)):
        data_frame_list =pd.read_excel(certain_format_file_name[i])
        data = pd.DataFrame(data_frame_list)
        intention_data_list = preprocess_str_list_data(data,16)
        first_intention=[check_first_intention(trajectory) for trajectory in intention_data_list]
        data["first_intention"]=first_intention
        pd.DataFrame(data).to_excel(certain_format_file_name[i], sheet_name='Sheet1', index=False, header=True)
