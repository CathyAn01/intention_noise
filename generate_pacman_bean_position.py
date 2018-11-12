
import openpyxl
import os
import numpy as np
import pygame as pg
import collections as co
import random
import pandas as pd
from pygame.locals import *
import time
import xlrd




def two_points_distance(point1,center):
    distance_difference = np.linalg.norm(np.array(point1) - np.array(center))
    return distance_difference



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

def Count_certain_number_in_list(list_to_manipulate, certain_number):
    count = 0
    number_index_initial = 0
    for number in list_to_manipulate:
        if certain_number == number:
            count = count + 1

    return count

def dict_to_string(values={}, sep="_", prefix="", postfix=""):
    signature = prefix
    for (key, value) in values.items():
        signature=sep.join((signature, str(key), str(value)))

    signature = signature+postfix
    signature = signature.lstrip(sep)
    return signature

def set_random_point(dimension,speed_pixel_per_second):
    while True:
        point=[round((random.randint(3,dimension-4)+0.5)*speed_pixel_per_second),
               round((random.randint(3,dimension-4) + 0.5) * speed_pixel_per_second)]
        if point[0]!=0 and point[1]!=0:
            break

    return point

def detect_within_screen(point,screen_area):
    if point != None:
        flag1=screen_area[0]<=point[0] and screen_area[1] >= point[0]
        flag2=screen_area[0]<=point[1] and screen_area[1] >= point[1]
        within_area_flag=flag1 and flag2
    else:
        within_area_flag = False
    return within_area_flag


class Generate_position(object):
    """Docstring for Experiment. """

    def __init__(self,design_values,dimension,min_grid_distance,min_isometric_distance):
        self.design_values=design_values
        self.dimension=dimension
        self.min_grid_distance=min_grid_distance
        self.min_isometric_distance=min_isometric_distance
        self.screen_area_grid=[0,self.dimension-1]

    def generate_pacman_grid(self, bean_grid):
        bean_distance = two_grid_distance(bean_grid[1], bean_grid[0])
        delta_x = abs(bean_grid[1][1] - bean_grid[0][1])
        delta_y = abs(bean_grid[0][0] - bean_grid[1][0])
        while True:
            if delta_y != 0:
                gradient = (bean_grid[0][1] - bean_grid[1][1]) / (
                        bean_grid[0][0] - bean_grid[1][0])
                if gradient < 0:
                    left_down_grid_index = [bean_grid[0][0], bean_grid[1][0]]. \
                        index(max([bean_grid[0][0], bean_grid[1][0]]))
                    right_up_grid_index = not left_down_grid_index
                    if bean_distance / 2 < delta_x:
                        min_mid_point1 = [bean_grid[left_down_grid_index][0],
                                          bean_grid[left_down_grid_index][1] + bean_distance / 2]
                        min_mid_point2 = [bean_grid[right_up_grid_index][0],
                                          bean_grid[right_up_grid_index][1] - bean_distance / 2]
                        if random.random() < 0.5:
                            pacman_grid = [random.randint(
                                min_mid_point1[0] + self.min_isometric_distance, self.dimension - 1)
                                , min_mid_point1[1]]
                            star_grid = min_mid_point1
                        else:
                            pacman_grid = [random.randint(0,
                                                          min_mid_point2[0] - self.min_isometric_distance),
                                           min_mid_point2[1]]
                            star_grid = min_mid_point2

                    else:
                        min_mid_point1 = [
                            bean_grid[left_down_grid_index][0] - (bean_distance / 2 - delta_x),
                            bean_grid[right_up_grid_index][1]]
                        min_mid_point2 = [
                            bean_grid[right_up_grid_index][0] + (bean_distance / 2 - delta_x),
                            bean_grid[left_down_grid_index][1]]
                        if random.random() < 0.5:
                            pacman_grid = [min_mid_point1[0],
                                           random.randint(min_mid_point1[1] + self.min_isometric_distance,
                                                          self.dimension - 1)]
                            star_grid = min_mid_point1
                        else:
                            pacman_grid = [min_mid_point2[0],
                                           random.randint(0, min_mid_point2[1] - self.min_isometric_distance)]
                            star_grid = min_mid_point2

                else:
                    left_up_grid_index = [bean_grid[0][0], bean_grid[1][0]]. \
                        index(min([bean_grid[0][0], bean_grid[1][0]]))
                    right_down_grid_index = not left_up_grid_index
                    if bean_distance / 2 < delta_x:
                        min_mid_point1 = [bean_grid[left_up_grid_index][0],
                                          bean_grid[left_up_grid_index][1] + bean_distance / 2]
                        min_mid_point2 = [bean_grid[right_down_grid_index][0],
                                          bean_grid[right_down_grid_index][1] - bean_distance / 2]
                        if random.random() < 0.5:
                            pacman_grid = [random.randint(0, min_mid_point1[0] - self.min_isometric_distance),
                                           min_mid_point1[1]]
                            star_grid = min_mid_point1
                        else:
                            pacman_grid = [
                                random.randint(min_mid_point2[0] + self.min_isometric_distance, self.dimension - 1),
                                min_mid_point2[1]]
                            star_grid = min_mid_point2

                    else:
                        min_mid_point1 = [
                            bean_grid[left_up_grid_index][0] + bean_distance / 2 - delta_x,
                            bean_grid[right_down_grid_index][1]]
                        min_mid_point2 = [
                            bean_grid[right_down_grid_index][0] - (bean_distance / 2 - delta_x),
                            bean_grid[left_up_grid_index][1]]
                        if random.random() < 0.5:
                            pacman_grid = [min_mid_point1[0],
                                           random.randint(min_mid_point1[1] + self.min_isometric_distance,
                                                          self.dimension - 1)]
                            star_grid = min_mid_point1
                        else:
                            pacman_grid = [min_mid_point2[0],
                                           random.randint(0, min_mid_point2[1] - self.min_isometric_distance)]
                            star_grid = min_mid_point2
            else:
                left_grid_index = [bean_grid[0][1], bean_grid[1][1]]. \
                    index(min([bean_grid[0][1], bean_grid[1][1]]))
                right_grid_index = not left_grid_index
                mid_point = [bean_grid[left_grid_index][0],
                             bean_grid[left_grid_index][1] + bean_distance / 2]
                if random.random() < 0.5:
                    pacman_grid = [random.randint(0, mid_point[0] - self.min_isometric_distance), mid_point[1]]
                else:
                    pacman_grid = [random.randint(mid_point[0] + self.min_isometric_distance, self.dimension - 1),
                                   mid_point[1]]
                star_grid = mid_point
            if detect_within_screen(pacman_grid, [0, self.dimension - 1]):
                break
            else:
                print("wrong")
                break
        return [pacman_grid, star_grid]


    def generate_bean_position(self,min_grid_distance):
        while True:
            bean1_grid=[random.randint(0+self.min_isometric_distance,
                                       self.dimension - 1-self.min_isometric_distance),
                    random.randint(0+self.min_isometric_distance,
                                       self.dimension - 1-self.min_isometric_distance)]
            bean2_grid=[random.randint(0+self.min_isometric_distance,
                                       self.dimension - 1-self.min_isometric_distance),
                    random.randint(0+self.min_isometric_distance,
                                       self.dimension - 1-self.min_isometric_distance)]
            bean_distance=two_grid_distance(bean1_grid,bean2_grid)
            if bean_distance>min_grid_distance and bean_distance%2==0:
                break
        return [bean1_grid,bean2_grid]

    def generate_unequal_distance_pacman(self,pacman_grid,star_grid):
        relative_position=[pacman_grid[0]==star_grid[0],pacman_grid[1]==star_grid[1]]
        while True:
            if relative_position==[1,0] :
                new_pacman_grid=[pacman_grid[0]+random.choice([-1,1]),pacman_grid[1]]
            elif relative_position==[0,1]:
                new_pacman_grid=[pacman_grid[0],pacman_grid[1]+random.choice([-1,1])]
            elif relative_position==[1,1]:
                print("mid_point==initial_point")
                new_pacman_grid=pacman_grid
            else:
                print("wrong initial_point")
                new_pacman_grid=pacman_grid
            if detect_within_screen(new_pacman_grid, self.screen_area_grid):
                break
            else:
                print("wrong")
                break
        return new_pacman_grid

    def __call__(self, writer_1,writer_2):
        for index in self.design_values:
            # here is critial: each d must be passed to the trial callable
            position=co.OrderedDict()
            position_1=co.OrderedDict()
            position_2=co.OrderedDict()
            bean_grid=self.generate_bean_position(self.min_grid_distance)
            equal_pacman_grid,star_grid=self.generate_pacman_grid(bean_grid)
            unequal_pacman_grid=self.generate_unequal_distance_pacman(equal_pacman_grid,star_grid)
            position["C"] = bean_grid[0][0]
            position["D"] = bean_grid[0][1]
            position["E"] = bean_grid[1][0]
            position["F"] = bean_grid[1][1]
            position["G"] = star_grid[0]
            position["H"] = star_grid[1]
            if index==0:
                position_1["A"]=unequal_pacman_grid[0]
                position_2["A"]=equal_pacman_grid[0]
                position_1["B"] = unequal_pacman_grid[1]
                position_2["B"] = equal_pacman_grid[1]
                position_1["I"] = "unequal"
                position_2["I"] = "equal"
            else:
                position_1["A"] = equal_pacman_grid[0]
                position_2["A"] = unequal_pacman_grid[0]
                position_1["B"] = equal_pacman_grid[1]
                position_2["B"] = unequal_pacman_grid[1]
                position_1["I"] = "equal"
                position_2["I"] = "unequal"
            position_1.update(position)
            position_2.update(position)
            writer_1(position_1)
            writer_2(position_2)


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

def main():
    pg.init()
    project_path = os.path.abspath(".")
    file_path=dict([("results_path",os.path.join(project_path,"results/"))])
    trial_number=60
    min_grid_distance=2
    min_isometric_distance=3
    dimension=21
    position_header=( "person_grid_y","person_grid_x",
                     "sheep1_grid_y","sheep1_grid_x",
                     "sheep2_grid_y","sheep2_grid_x",
                     "star_grid_y","star_grid_x")
    design_value = [0, 1] * int(trial_number / 2)
    random.shuffle(design_value)
    path_1 = os.path.join(file_path["results_path"], "equal_position_index_1.xlsx")
    path_2 = os.path.join(file_path["results_path"], "equal_position_index_2.xlsx")
    writer_1 = Writer(path_1, position_header, replace=False)
    writer_2 = Writer(path_2, position_header, replace=False)
    generate_position=Generate_position(design_value,dimension,min_grid_distance,min_isometric_distance)
    generate_position(writer_1,writer_2)








if __name__=="__main__":
    main()







