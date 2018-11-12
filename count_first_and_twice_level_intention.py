import pandas as pd
import os
import openpyxl
import collections as co
import numpy


def dict_to_string(values={}, sep="_", prefix="", postfix=""):
    signature = prefix
    for (key, value) in values.items():
        signature = sep.join((signature, str(key), str(value)))

    signature = signature + postfix
    signature = signature.lstrip(sep)
    return signature


def count_certain_number_in_list(list_to_manipulate, certain_number):
    count = 0
    number_index_initial = 0
    index_list=[]
    for number in list_to_manipulate:
        if certain_number == number:
            count = count + 1
            index_list.append(certain_number)

    return count,index_list

def two_grid_distance(grid_1,grid_2):
    grid_distance_x = abs(grid_2[0] - grid_1[0])
    grid_distance_y = abs(grid_2[1] - grid_1[1])
    distance = grid_distance_y+grid_distance_x
    return distance

def count_first_order_intention(pacman_trajectory,bean1_position,bean2_position,action_list,noise_point):
    intention_list=[]
    for i in range(len(pacman_trajectory)-1):
        pacman_bean1_distance=two_grid_distance(pacman_trajectory[i+1],bean1_position)
        pacman_bean2_distance=two_grid_distance(pacman_trajectory[i+1],bean2_position)
        if pacman_bean1_distance<pacman_bean2_distance:
            intention=1
        elif pacman_bean1_distance>pacman_bean2_distance:
            intention=2
        else:
            intention=0
        intention_list.append(intention)
    for noise in noise_point:
        position=[pacman_trajectory[noise-1][0]+action_list[noise-1][0],
                  pacman_trajectory[noise - 1][1] + action_list[noise - 1][1]]
        pacman_bean1_distance = two_grid_distance(position, bean1_position)
        pacman_bean2_distance = two_grid_distance(position, bean2_position)
        if pacman_bean1_distance < pacman_bean2_distance:
            intention = 1
        elif pacman_bean1_distance > pacman_bean2_distance:
            intention = 2
        else:
            intention = 0
        intention_list[noise]=intention
    return intention_list



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

def count_total_order_intention(first_order_intention_list,second_order_intention_list):
    total_intention_list=[]
    for i in range(len(first_order_intention_list)):
        if second_order_intention_list[i]==0:
            total_intention_list.append(first_order_intention_list[i])
        else:
            total_intention_list.append(second_order_intention_list[i])
    return total_intention_list


def main():
    project_path = os.path.abspath(".")
    values=co.OrderedDict()
    # values["participant_name"] = input("participant_name:")
    # values["noise_probability"] = input("noise_probability:")
    # values["data_number"] = input("data_number:")
    file_path = dict([("results_path", os.path.join(project_path, "results/")),
                      ("indicator_output_path",os.path.join(project_path, "data_analysis/5_indicator.csv"))])
    file_format = [".xlsx"]
    n_step=20
    certain_format_file_name = list_all_certain_format_filename(file_path["results_path"], file_format)
    for i in range(len(certain_format_file_name)):
        data_frame_list =pd.read_excel(certain_format_file_name[i])
        data = pd.DataFrame(data_frame_list)
        dimension_data=data.shape
        intention_data_list = preprocess_str_list_data(data,16)
        pacman_trajectory_list=preprocess_str_list_data(data,12)
        noise_list=preprocess_str_list_data(data,11)
        action_list=preprocess_str_list_data(data,22)
        first_order_intention=[count_first_order_intention(pacman_trajectory_list[i],[data.iat[i,6],data.iat[i,7]],\
            [data.iat[i,8],data.iat[i,9]],action_list[i],noise_list[i]) for i in range(dimension_data[0])]
        total_order_intention=[count_total_order_intention(first_order_intention[i],intention_data_list[i])
                               for i in range(len(first_order_intention))]







if __name__ == "__main__":
    main()