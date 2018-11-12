import pandas as pd
import os
import openpyxl
import collections as co
import numpy
import functools


def dict_to_string(values={}, sep="_", prefix="", postfix=""):
    signature = prefix
    for (key, value) in values.items():
        signature = sep.join((signature, str(key), str(value)))

    signature = signature + postfix
    signature = signature.lstrip(sep)
    return signature

def Count_prediction_error_n_step(last_intention,intention_data_list,n_step):
    data_number=last_intention.shape[0]
    valid_data_number=0
    count_correct_prediction=0
    for i in range(data_number):
        length=len(intention_data_list[i])
        if n_step<length:
            valid_data_number=valid_data_number+1
            if intention_data_list[i][n_step]==last_intention[i]:
                count_correct_prediction=count_correct_prediction+1

    if valid_data_number !=0:
        prediction_error_n_step=count_correct_prediction/valid_data_number
    else:
        prediction_error_n_step="out_of_step"
    return prediction_error_n_step


class Writer(object):
    """Docstring for Writer. """

    def __init__(self, path, replace=False):
        """TODO: to be defined1.

        @param path TODO
        @param mode TODO

        """
        self._path = path
        self._replace = replace

    def __call__(self, kwargs,index):
        if self._replace and self._couter == 0:
            mode = "w"
        else:
            mode = "a"

        if index == 0:
            header = True
        else:
            header = False

        result_dict = {}
        result_dict.update(kwargs)
        result_df = pd.DataFrame(data=result_dict,
                                 index=[index])
        result_df.to_csv(self._path, header=header, mode=mode)


def Count_first_intention_prediction_error(data,first_intention,last_intention):
    prediction_correct_data=data[data["first_intention"]==data["last_intention"]]
    prediction_error=prediction_correct_data.shape[0]/data.shape[0]
    return prediction_error

def list_all_certain_format_filename(file_path,file_format):
    absolute_filename=[os.path.join(file_path,relative_filename) for relative_filename in os.listdir(file_path)
                       if os.path.isfile(os.path.join(file_path,relative_filename))
                       if os.path.splitext(relative_filename)[1] in file_format]
    return absolute_filename

def preprocess_str_list_data(data_df,particular_columns):
    data_pre_list = [data_df.iat[i, particular_columns] for i in range(len(data_df))]
    data_list = [eval(data) for data in data_pre_list ]
    return data_list

def count_certain_number_in_list(list_to_manipulate, certain_number):
    count = 0
    number_index_initial = 0
    index_list=[]
    for number in list_to_manipulate:
        if certain_number == number:
            count = count + 1
            index_list.append(certain_number)

    return count

def main():
    project_path = os.path.abspath(".")
    values=co.OrderedDict()
    # values["participant_name"] = input("participant_name:")
    # values["noise_probability"] = input("noise_probability:")
    # values["data_number"] = input("data_number:")
    file_path = dict([("results_path", os.path.join(project_path, "results/")),
                      ("indicator_output_path",os.path.join(project_path, "data_analysis/5_indicator.csv"))])

    file_format = [".csv"]
    n_step=20
    certain_format_file_name = list_all_certain_format_filename(file_path["results_path"], file_format)
    for i in range(len(certain_format_file_name)):
        data_frame_list =pd.read_csv(certain_format_file_name[i])
        data = pd.DataFrame(data_frame_list)
        dimension_data=data.shape
        average_step=data["step"].mean()
        prediction_error=Count_first_intention_prediction_error(data,data["first_intention"],data["last_intention"])
        intention_data_list = preprocess_str_list_data(data,16)
        total_intention_1=[count_certain_number_in_list(intention,1) for intention in intention_data_list]
        total_intention_2=[count_certain_number_in_list(intention,2) for intention in intention_data_list]
        intention_ratio=(sum(total_intention_1)+sum(total_intention_2))/dimension_data[0]/average_step
        first_intention_step_list=[intention_data_list[i].index(data.iat[i,14])+1
                                               for i in range(dimension_data[0]) if data.iat[i,14] in intention_data_list[i]]
        average_first_intention_step=numpy.mean(numpy.array(first_intention_step_list))
        first_intention_whole_step_ratio=[first_intention_step_list[i]/data["step"][i] for i in range(len(first_intention_step_list))]
        average_first_intention_whole_step_ratio=numpy.mean(numpy.array(first_intention_whole_step_ratio))
        prediction_error_n_step=[Count_prediction_error_n_step(data["last_intention"],intention_data_list,i) for i in range(n_step)]
        values["file_name"]=certain_format_file_name[i]
        values["subject"]="person"
        result = dict([("total_step",average_step), ("first_intention_prediction_ratio",prediction_error),
                        ("every_step_prediction_ratio",str(prediction_error_n_step)),
                        ("first_intention_step",average_first_intention_step),
                       ("first_intention_step/total_step", average_first_intention_whole_step_ratio),
                       ("intention_ratio",intention_ratio)])
        print(result)
        values.update(result)
        writer=Writer(file_path["indicator_output_path"])
        writer(values,i)





if __name__ == "__main__":
    main()