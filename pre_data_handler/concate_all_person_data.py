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


def main():
    project_path = os.path.abspath(".")
    values=co.OrderedDict()
    # values["participant_name"] = input("participant_name:")
    # values["noise_probability"] = input("noise_probability:")
    # values["data_number"] = input("data_number:")
    file_path = dict([("results_equal_path", os.path.join(project_path, "results/person_equal.csv")),
                      ("results_unequal_path", os.path.join(project_path, "results/person_unequal.csv")),
                      ("results_path",os.path.join(project_path, "results/")),
                      ("indicator_output_path",os.path.join(project_path, "data_analysis/indicator.csv"))])

    file_format = [".xlsx"]
    certain_format_file_name = list_all_certain_format_filename(file_path["results_path"], file_format)
    data_frame_list=[pd.DataFrame(pd.read_excel(file)) for file in certain_format_file_name]
    data=pd.concat(data_frame_list)
    dimension_data=data.shape
    data_equal=data[data["condition"]=="text:'equal_distance'"]
    data_unequal=data[data["condition"]=="text:'unequal_distance'"]
    data_equal.to_csv(file_path["results_equal_path"],index=False)
    data_unequal.to_csv(file_path["results_unequal_path"],index=False)


if __name__ == "__main__":
    main()