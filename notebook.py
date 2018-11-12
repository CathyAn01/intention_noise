import pickle
import os
import xlrd
import random
import openpyxl
import numpy as np
import collections as co
from pygame.locals import *
import time
import xlrd

def go_split(s, symbol):
    # 拼接正则表达式
    symbol = "[" + symbol + "]+"
    # 一次性分割字符串
    result = re.split(symbol, s)
    # 去除空字符
    #return [x for x in result if x]
    return result

def detect_within_screen(point,screen_area):
    if point != None:
        flag1=point[0]<=screen_area[0] and 0 <= point[0]
        flag2=point[1]<=screen_area[1] and 0 <=point[1]
        within_area_flag=flag1 and flag2
    else:
        within_area_flag = False
    return within_area_flag

def Read_position_file(position_file_path):
    data = xlrd.open_workbook(position_file_path)
    position_data = data.sheet_by_name('Sheet')
    return position_data

def grid_to_position(grid,grid_per_distance):
    position=[round((grid[0]+0.5)*grid_per_distance),round((grid[1]+0.5)*grid_per_distance)]
    return position

def position_to_grid(position,grid_per_distance):
    grid= [round(position[0]/grid_per_distance-0.5),round((position[1])/grid_per_distance-0.5)]
    return grid

def two_grid_distance(grid_1,grid_2):
    grid_distance_x = abs(grid_2[0] - grid_1[0])
    grid_distance_y = abs(grid_2[1] - grid_1[1])
    distance = grid_distance_y+grid_distance_x
    return distance

def count_certain_number_in_list(list_to_manipulate, certain_number):
    count = 0
    index_list=[]
    for i in range(len(list_to_manipulate)):
        if certain_number == list_to_manipulate[i]:
            count = count + 1
            index_list.append(i)

    return count,index_list

def dict_to_string(values={}, sep="_", prefix="", postfix=""):
    signature = prefix
    for (key, value) in values.items():
        signature=sep.join((signature, str(key), str(value)))

    signature = signature+postfix
    signature = signature.lstrip(sep)
    return signature


class Writer(object):

    """Docstring for Writer. """

    def __init__(self, path, header,replace=False):
        """TODO: to be defined1.

        @param path TODO
        @param mode TODO

        """
        self._path = path
        self.header=header
        self.index = 0
        self.data_workbook=openpyxl.Workbook()
        self.data_worksheet = self.data_workbook.active



    def __call__(self, kwargs):
        table_title=self.header
        if self.index==0:
            for col in range(len(table_title)):
                c = col + 1
                self.data_worksheet.cell(row=1, column=c).value = table_title[col]
        self.index = self.index + 1
        self.data_worksheet.append(kwargs)
        self.data_workbook.save(filename=self._path)


class Experiment(object):
    """Docstring for Experiment. """

    def __init__(self,design_values, name="expt", sub_num=-999, sub_init="test", **constants):
        """TODO: to be defined1.

        @param name TODO
        @param sub_num TODO
        @param sub_init TODO
        @param **constants TODO

        """
        self._name = name
        self._sub_num = sub_num
        self._sub_init = sub_init
        self._constants = constants
        self._values = co.OrderedDict()
        self._values['A'] = self._name
        self._values['B'] = self._sub_num
        self._values['C'] = self._sub_init
        self._design_values=design_values
        self._values.update(self._constants)

    def get_expt_signature(self, sep="_", prefix="expt", postfix=""):
        return dict_to_string(self._values, sep, prefix, postfix)

    def __call__(self, trial=None,  writer=None):
        for index in self._design_values:
            # here is critial: each d must be passed to the trial callable
            result = trial(index)
            to_writer_dic = self._values.copy()
            to_writer_dic ["D"]=self._design_values[index]
            to_writer_dic.update(result)
            writer(to_writer_dic)




class Trial():
    def __init__(self,dimension, pacman_grid,bean_grid,star_grid,\
                 action_space,speed_pixel_per_second,policy, \
                 foolish_wolf_standard,noise_probability,**constants):

        self.screen_area=[dimension-1,dimension-1]
        self.noise_probability=noise_probability
        self.action_space = action_space
        self.pacman_grid= pacman_grid
        self.bean_grid = bean_grid
        self.star_grid=star_grid
        self.constants = constants
        self.policy=policy
        self.speed_pixel_per_second=speed_pixel_per_second
        self.foolish_wolf_standard=foolish_wolf_standard
        self.result = {}




    def check_intention(self,pacman_trajectory_list,aimed_grid,bean_1_grid,bean_2_grid):
        pacman_bean1_aimed_displacement=two_grid_distance(aimed_grid,bean_1_grid)
        pacman_bean2_aimed_displacement=two_grid_distance(aimed_grid,bean_2_grid)
        pacman_bean1_initial_displacement=two_grid_distance(bean_1_grid,pacman_trajectory_list[-1])
        pacman_bean2_initial_displacement = two_grid_distance(bean_2_grid,pacman_trajectory_list[-1])
        intention_bean1= pacman_bean1_initial_displacement-pacman_bean1_aimed_displacement
        intention_bean2= pacman_bean2_initial_displacement-pacman_bean2_aimed_displacement
        if intention_bean1>intention_bean2:
            intention=1
        elif intention_bean1<intention_bean2:
            intention=2
        else:
            intention=0
        return intention

    def find_next_step(self,pacman_grid,pacman_trajectory_list,
                     bean1_grid, bean2_grid, step_count,noise_point_list,intention_list):

        grid_initial=pacman_grid
        new_step_count=step_count
        new_noise_point_list=noise_point_list
        this_grid_policy=self.policy[(pacman_grid,(bean1_grid,bean2_grid))]
        probability=[this_grid_policy[self.action_space[i]] for i in range (len(this_grid_policy))]
        action_space=[str(a)  for a in self.action_space]
        action = np.random.choice(action_space, 1, p=probability).tolist()
        action=eval(action[0])
        aimed_grid = tuple([x + y for (x, y) in list(zip(pacman_grid,action))])
        new_step_count=step_count
        if aimed_grid !=pacman_trajectory_list[-1]:
            new_step_count=step_count+1
        intention=self.check_intention(pacman_trajectory_list,aimed_grid,bean1_grid,bean2_grid)
        intention_list.append(intention)
        if random.random() < self.noise_probability["intention"]:
            new_noise_point_list.append(new_step_count)
            new_pacman_grid=self.add_noise(grid_initial, action)
        else:
            new_pacman_grid = aimed_grid
        if detect_within_screen(new_pacman_grid, self.screen_area):
            new_pacman_grid=new_pacman_grid

        else:
            new_pacman_grid=grid_initial

        new_pacman_position=grid_to_position(new_pacman_grid,self.speed_pixel_per_second)
        return new_pacman_position,new_pacman_grid,new_step_count,new_noise_point_list,intention_list

    def add_noise(self,pacman_grid, action):
        action_space = [str(a) for a in self.action_space]
        print(action_space)
        action_space.remove(str(action))
        noise_action = np.random.choice(action_space).tolist()
        noise_action = eval(noise_action)
        print(noise_action)
        noise_grid = tuple([x + y for (x, y) in list(zip(pacman_grid, noise_action))])

        return noise_grid


    def check_end_condition(self,pacman_grid, bean1_grid,bean2_grid,step_count):
        if step_count>self.foolish_wolf_standard["maximal_step"]:
            end_condition1=True
        else:
            end_condition1=False

        end_condition2_1 = self.check_eaten(pacman_grid,bean1_grid)
        end_condition2_2 = self.check_eaten(pacman_grid,bean2_grid)
        end =  end_condition1 or end_condition2_1 or end_condition2_2
        if end_condition1:
            exit_condition="foolish_wolf"
        elif end_condition2_1:
            exit_condition = "bean_1_eaten"
        elif end_condition2_2:
            exit_condition = "bean_2_eaten"
        else:
            exit_condition=False

        return end,exit_condition


    def set_bean_disappear_probability(self, bean_disappear_flag,disappear_time,initial_time):
        bean_disappear_update_flag=bean_disappear_flag
        for i in range(len(bean_disappear_flag)):
            if bean_disappear_flag[i] == False:
                bean_disappear_update_flag[i]=random.random() < self.bean_disappear_probability
                if bean_disappear_update_flag:
                    disappear_time['bean_'+str(i+1)+'_disappear_time'] = time.time()-initial_time

        return bean_disappear_update_flag,disappear_time

    def check_eaten(self,pacman_grid,bean_grid):
        if two_grid_distance(pacman_grid,bean_grid)==0 :
            check_eaten=True
        else:
            check_eaten=False
        return check_eaten

    def update_trajectory(self, trajectory_list,pacman_position,bean1_grid,bean2_grid):
        if pacman_position!=trajectory_list[-1]:
            trajectory_list.append(pacman_position)

        return trajectory_list

    def check_first_intention(self, intention_list):
        if 1 in intention_list:
            intention_index_1=intention_list.index(1)
        else:
            intention_index_1=999
        if 2 in intention_list:
            intention_index_2=intention.index(2)
        else:
            intention_index_2=999
        if intention_index_1<intention_index_2:
            first_intention=1
        else:
            first_intention=2
        return first_intention

    def check_last_intention(self,exit_condition):
        if exit_condition == "bean_1_eaten":
            last_intention = 1
        elif exit_condition == "bean_2_eaten":
            last_intention = 2
        else:
            last_intention = 0
        return last_intention

    def __call__(self, trial_index):
        pacman_grid= self.pacman_grid[trial_index]
        bean1_grid =self.bean_grid[trial_index][0]
        bean2_grid = self.bean_grid[trial_index][1]
        pacman_trajectory_list=[pacman_grid]
        exit_flag = False
        step_count=0
        noise_point_list=[]
        intention_list=[]
        while not exit_flag:
            pacman_position,pacman_grid,step_count,noise_point_list,intention_list =\
                self.find_next_step( pacman_grid,pacman_trajectory_list,
                                     bean1_grid,bean2_grid,step_count,
                                     noise_point_list,intention_list)
            pacman_trajectory_list = self.update_trajectory( pacman_trajectory_list,
                                                             pacman_grid,bean1_grid,bean2_grid)
            exit_flag,exit_condition = self.check_end_condition( pacman_grid, bean1_grid, bean2_grid,step_count)

        first_intention=self.check_first_intention(intention_list)
        last_intention=self.check_last_intention(exit_condition)


        self.result["E"] = self.pacman_grid[trial_index][0]
        self.result["F"] = self.pacman_grid[trial_index][1]
        self.result["G"] = self.bean_grid[trial_index][0][0]
        self.result["H"] = self.bean_grid[trial_index][0][1]
        self.result["I"] = self.bean_grid[trial_index][1][0]
        self.result["J"] = self.bean_grid[trial_index][1][1]
        self.result["K"] = exit_condition
        self.result["L"]=str(noise_point_list)
        self.result["M"] = str(pacman_trajectory_list)
        self.result["N"] = len(pacman_trajectory_list)-1
        self.result["O"] = first_intention
        self.result["P"] = last_intention
        self.result["Q"]=str(intention_list)
        self.result["R"] = self.star_grid[trial_index][0]
        self.result["S"] = self.star_grid[trial_index][1]
        return self.result


def main():
    project_path = os.path.abspath(".")
    file_path = dict([("fixation_path",os.path.join(project_path, "images/fixation.png")),
                     ("rest_path",os.path.join(project_path, "images/rest.png")),
                     ("introduction_path" ,os.path.join(project_path, "images/introduction.png")),
                     ("results_path",os.path.join(project_path,"results/")),
                     ("sheep_wolf_position_path", os.path.join(project_path, "images/position_index.xlsx")),
                      ("machine_policy_path",os.path.join(project_path, "machine_policy/noise0.2sheep_states_two_policy.pkl"))])
    noise_probability = {"intention": 0.3}
    picklefile = open(file_path["machine_policy_path"], 'rb')
    policy = pickle.load(picklefile, encoding='iso-8859-1')
    print(policy[((11,11),((15,12),(6,11)))])



if __name__ == "__main__":
    main()