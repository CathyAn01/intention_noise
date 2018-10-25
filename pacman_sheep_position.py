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


def Read_position_file(position_file_path):
    data = xlrd.open_workbook(position_file_path)
    position_data = data.sheet_by_name('Sheet')
    return position_data

def two_points_distance(point1,center):
    distance_difference = np.linalg.norm(np.array(point1) - np.array(center))
    return distance_difference

def set_random_grid(dimension):
    grid=[random.randint(0,dimension-1),
          random.randint(0, dimension - 1)]
    return grid

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
        flag1=point[0]<screen_area[0] and 0 < point[0]
        flag2=point[1]<screen_area[1] and 0 < point[1]
        within_area_flag=flag1 and flag2
    else:
        within_area_flag = False
    return within_area_flag


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
        self._values['name'] = self._name
        self._values['subNum'] = self._sub_num
        self._values['subInit'] = self._sub_init
        self._design_values=design_values
        self._values.update(self._constants)

    def get_expt_signature(self, sep="_", prefix="expt", postfix=""):
        return dict_to_string(self._values, sep, prefix, postfix)

    def __call__(self, trial_number,trial=None,  writer=None):
        for index in range(trial_number):
            # here is critial: each d must be passed to the trial callable
            result = trial(index)
            to_writer_dic = self._values.copy()
            to_writer_dic ["condition"]=self._design_values[index]
            to_writer_dic.update(result)
            writer(to_writer_dic)




class Trial():
    def __init__(self, screen_trait,background_trait,bean_trait,pacman_trait,image_path,time,\
                 center_position,pacman_grid,bean_grid,\
                 action_space,event_space,speed_pixel_per_second,\
                 noise_probability,font_information,score_information,count_step,**constants):
        self.screen_area=[screen_trait["width"],screen_trait["height"]]
        self.background_trait=background_trait
        self.screen = pg.display.set_mode(self.screen_area)
        self.screen_rect = self.screen.get_rect()
        self.screen_color = screen_trait['color']
        self.noise_probability=noise_probability
        self.fixation_image = pg.image.load(image_path["fixation_path"])
        self.fixation=pg.transform.scale(self.fixation_image,(80,80))
        self.fixation_rect = self.fixation.get_rect()
        self.fixation_rect.center=center_position
        self.rest_image = pg.image.load(image_path["rest_path"])
        self.rest=pg.transform.scale(self.rest_image,(300,200))
        self.rest_rect = self.fixation.get_rect()
        self.rest_rect.center=center_position
        self.introduction_image = pg.image.load(image_path["introduction_path"])
        self.introduction=pg.transform.scale(self.introduction_image,self.screen_area)
        self.introduction_rect = self.introduction.get_rect()
        self.introduction_rect.center=center_position
        self.bean_color = bean_trait["color"]
        self.bean_size = bean_trait["size"]
        self.pacman_color=pacman_trait["color"]
        self.pacman_size = pacman_trait["size"]
        self.action_space = action_space
        self.event_space=event_space
        self.pacman_grid= pacman_grid
        self.bean_grid = bean_grid
        self.constants = constants
        self.bean_initial_disappear_time=time["bean_initial_disappear_time_s"]
        self.feedback_time=time["feedback_time_ms"]
        self.fixation_time = time["fixation_time_ms"]
        self.blank_screen_time=time["blank_screen_time_ms"]
        self.font_information=font_information
        self.score_information=score_information
        self.font=pg.font.SysFont(font_information["type"],font_information["size"])
        self.text_color=font_information["color"]
        self.text_size=font_information["size"]
        self.text_type = font_information["type"]
        self.initial_score=self.score_information["initial_score"]
        self.score_position=self.score_information["position"]
        self.rest_time=time["rest_time_trial"]
        self.count_step=count_step
        self.speed_pixel_per_second=speed_pixel_per_second
        self.result = {}

    def set_preview(self):
        self.screen.fill(self.screen_color)
        start_points_horizontal=[[0,(i+1)*self.screen_area[0]/self.background_trait["dimension"]]
                                 for i in range(self.background_trait["dimension"])]
        end_points_horizontal=[[self.screen_area[0],(i+1)*self.screen_area[0]/self.background_trait["dimension"]]
                               for i in range(self.background_trait["dimension"])]
        start_points_vertical=[[(i+1)*self.screen_area[1]/self.background_trait["dimension"],0]
                               for i in range(self.background_trait["dimension"])]
        end_points_vertical = [[(i + 1) * self.screen_area[1] / self.background_trait["dimension"], self.screen_area[1]] for i in
                                 range(self.background_trait["dimension"])]
        for i in range(self.background_trait["dimension"]):
            pg.draw.line(self.screen, self.background_trait["color"], start_points_horizontal[i], end_points_horizontal[i],
                         self.background_trait["width"])
            pg.draw.line(self.screen, self.background_trait["color"], start_points_vertical[i], end_points_vertical[i],
                         self.background_trait["width"])


    def draw_fixation(self,trial_index):
        self.set_preview()
        pg.display.flip()
        pg.time.delay(self.blank_screen_time)
        while trial_index % self.rest_time ==0 and trial_index != 0:
            self.screen.blit(self.rest, self.rest_rect)
            pg.display.flip()
            pg.event.set_allowed([KEYDOWN, KEYUP])
            event=pg.event.wait()
            if event.type==pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    break
        while trial_index ==0:
            self.screen.blit(self.introduction, self.introduction_rect)
            pg.display.flip()
            pg.event.set_allowed([KEYDOWN, KEYUP])
            event=pg.event.wait()
            if event.type==pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    break
        self.set_preview()
        self.screen.blit(self.fixation, self.fixation_rect)
        pg.display.flip()
        pg.time.delay(self.fixation_time)
        self.set_preview()
        pg.display.flip()
        pg.time.delay(self.blank_screen_time)

    def check_intention(self,pacman_trajectory_list,aimed_position,bean_1_position,bean_2_position):
        pacman_displacement=np.array(aimed_position)-\
                            np.array(pacman_trajectory_list[-1])
        pacman_bean1_initial_vector=np.array(bean_1_position)-np.array(pacman_trajectory_list[-1])
        pacman_bean2_initial_vector = np.array(bean_2_position)-np.array(pacman_trajectory_list[-1])
        normalise_pacman_bean1_initial_vector=pacman_bean1_initial_vector/\
                                              np.sqrt(pacman_bean1_initial_vector.dot(pacman_bean1_initial_vector))
        normalise_pacman_bean2_initial_vector=pacman_bean2_initial_vector/\
                                              np.sqrt(pacman_bean2_initial_vector.dot(pacman_bean2_initial_vector))
        intention_bean1=pacman_displacement.dot(normalise_pacman_bean1_initial_vector)
        intention_bean2=pacman_displacement.dot(normalise_pacman_bean2_initial_vector)
        if intention_bean1>intention_bean2:
            intention=1
        elif intention_bean1<intention_bean2:
            intention=2
        else:
            intention=0
        return intention


    def update_screen(self, pacman_position, bean1_position,bean2_position):
        self.set_preview()
        pg.draw.circle(self.screen, self.pacman_color, [round(pacman_position[0]),round(pacman_position[1])], self.pacman_size)
        pg.draw.circle(self.screen, self.bean_color, bean1_position, self.bean_size)
        pg.draw.circle(self.screen, self.bean_color, bean2_position, self.bean_size)
        pg.display.flip()

    def check_events(self, event, pacman_position,pacman_trajectory,target1_position,
                     target2_position,event_space,step_count):
        center_initial=pacman_position
        new_step_count=step_count
        if event.type == pg.KEYDOWN and event.key in self.event_space:
            new_step_count=step_count+1
            aimed_position=[x + y for (x, y) in list(zip(pacman_position, self.action_space[event.key]))]
            intention=self.check_intention(pacman_trajectory,aimed_position,target1_position,target2_position)
            if intention !=0 and random.random() < self.noise_probability["intention"]:
                center=self.move_to_anti_intention_bean(center_initial,intention,target1_position,target2_position)
            else:
                center = aimed_position
        else:
            center=center_initial
        if detect_within_screen(center, self.screen_area):
            pacman_position=center
        else:
            pacman_position=center_initial

        return pacman_position,new_step_count

    def move_to_anti_intention_bean(self,pacman_position, intention, target1_position, target2_position):
        if intention==0:
            if random.random<0.8:
                new_position=pacman_position
            else:
                all_event_center = [[pacman_position[0] + self.action_space[per_event][0], pacman_position[1] + \
                                     self.action_space[per_event][1]
                                     ] for per_event in self.event_space]
                new_position=all_event_center[random.randint(0,len(all_event_center))]
        else:
            all_event_center= [[pacman_position[0]+self.action_space[per_event][0],pacman_position[1]+\
                               self.action_space[per_event][1]
                ]for per_event in self.event_space]
            if intention==1:
                all_possible_distance=[[two_points_distance(all_event_center[i],target2_position),all_event_center[i]]
                                   for i in range(len(all_event_center))]
                all_possible_distance_ordered=sorted(all_possible_distance,key=lambda x:x[0])
                new_position=all_possible_distance_ordered[random.randint(0,1)][1]
            else:
                all_possible_distance=[[two_points_distance(all_event_center[i],target1_position),all_event_center[i]]
                                   for i in range(len(all_event_center))]
                all_possible_distance_ordered=sorted(all_possible_distance,key=lambda x:x[0])
                new_position=all_possible_distance_ordered[random.randint(0,1)][1]

        position=[round(new_position[0]),round(new_position[1])]
        return position

    def update_trajectory(self,event, trajectory_list,pacman_position):
        if event.type == pg.KEYDOWN and event.key in self.event_space:
            trajectory_list.append(pacman_position)
        return trajectory_list

    def update_response_time(self,event,response_current_time_list):
        if event.type == pg.KEYDOWN and event.key in self.event_space:
            now=time.time()
            response_current_time_list.append(now)
        return response_current_time_list

    def check_end_condition(self, event, pacman_position, bean1_position,bean2_position):
        if event.type == pg.QUIT:
            end_condition1 = True
        else:
            end_condition1 = False

        end_condition2_1 = self.check_eaten(pacman_position,bean1_position)
        end_condition2_2 = self.check_eaten(pacman_position,bean2_position)
        end = end_condition1 or end_condition2_1 or end_condition2_2
        if end_condition1:
            exit_condition = "QUIT"
        elif end_condition2_1:
            exit_condition = "bean_1_eaten"
        elif end_condition2_2:
            exit_condition = "bean_2_eaten"
        else:
            exit_condition=False
        return end,exit_condition



    def give_feedback(self,pacman_position, bean1_position, bean2_position, exit_condition):
        self.set_preview()
        pg.draw.circle(self.screen, self.pacman_color, [round(pacman_position[0]),round(pacman_position[1])], self.pacman_size)
        if exit_condition=="bean_1_eaten":
            pg.draw.circle(self.screen, [255,215,0], bean1_position, self.bean_size)
        else:
            pg.draw.circle(self.screen, self.bean_color, bean1_position, self.bean_size)

        if exit_condition=="bean_2_eaten":
            pg.draw.circle(self.screen, [255, 215, 0], bean2_position, self.bean_size)
        else:
            pg.draw.circle(self.screen, self.bean_color, bean2_position, self.bean_size)
        pg.display.flip()
        pg.time.delay(self.feedback_time)
        self.set_preview()
        pg.display.flip()
        pg.time.delay(self.blank_screen_time)
        pg.display.flip()
        pg.time.delay(self.feedback_time)
        self.set_preview()
        pg.display.flip()

    def set_bean_disappear_probability(self, bean_disappear_flag,disappear_time,initial_time):
        bean_disappear_update_flag=bean_disappear_flag
        for i in range(len(bean_disappear_flag)):
            if bean_disappear_flag[i] == False:
                bean_disappear_update_flag[i]=random.random() < self.bean_disappear_probability
                if bean_disappear_update_flag:
                    disappear_time['bean_'+str(i+1)+'_disappear_time'] = time.time()-initial_time

        return bean_disappear_update_flag,disappear_time

    def check_eaten(self,pacman_position,bean_position):
        if two_points_distance(pacman_position,bean_position)<self.pacman_size :
            check_eaten=True
        else:
            check_eaten=False
        return check_eaten

    def __call__(self, trial_index):
        print(self.pacman_grid[trial_index])
        print(self.bean_grid[trial_index][0])
        print(self.bean_grid[trial_index][1])
        pacman_position = grid_to_position(self.pacman_grid[trial_index], self.speed_pixel_per_second)
        bean1_position = grid_to_position(self.bean_grid[trial_index][0], self.speed_pixel_per_second)
        bean2_position = grid_to_position(self.bean_grid[trial_index][1], self.speed_pixel_per_second)
        score=self.initial_score
        event_space=self.event_space
        pacman_trajectory_list=[self.pacman_grid[trial_index]]
        bean_disappear_flag=[False,False]
        self.draw_fixation(trial_index)
        exit_flag = False
        initial_trial_time = time.time()
        response_current_time_list = [initial_trial_time]
        pg.event.set_allowed([KEYDOWN, KEYUP])
        step_count=0
        while not exit_flag:
            self.update_screen(pacman_position, bean1_position, bean2_position)
            for event in pg.event.get():
                pacman_position,step_count = self.check_events(event, pacman_position,pacman_trajectory_list,
                                                               bean1_position,bean2_position
                                                           ,event_space,step_count)
                pacman_trajectory_list=self.update_trajectory(event,pacman_trajectory_list,pacman_position)
                response_current_time_list=self.update_response_time(event,response_current_time_list)
                exit_flag,exit_condition = self.check_end_condition(event, pacman_position, bean1_position, bean2_position)

        pg.event.set_blocked([KEYDOWN, KEYUP])
        reaction_time=[response_current_time_list[i+1]-response_current_time_list[i] for i in range(len(response_current_time_list)-1)]
        self.give_feedback(pacman_position, bean1_position, bean2_position, exit_condition)
        end_trial_time=time.time()
        self.result["total_trial_time"] = end_trial_time - initial_trial_time
        self.result["pacman_initial_position"]=str(self.pacman_grid[trial_index])
        self.result["bean_1_initial_position"] = str(self.bean_grid[trial_index][0])
        self.result["bean_2_initial_position"] = str(self.bean_grid[trial_index][1])
        self.result["end_condition_reason"] = exit_condition
        self.result["pacman_trajectory"] = str(pacman_trajectory_list)
        self.result["reaction_time"]=str(reaction_time)
        return self.result

class Generate_bean_grid():
    def __init__(self,dimension):
        self.dimension=dimension

    def __call__(self,min_grid_distance):
        while True:
            bean1_grid=set_random_grid(self.dimension)
            bean2_grid=set_random_grid(self.dimension)
            bean_distance=two_grid_distance(bean1_grid,bean2_grid)
            if bean_distance>min_grid_distance and bean_distance%2==0:
                break
        return [bean1_grid,bean2_grid]

class Generate_pacman_grid():
    def __init__(self,bean_grid,dimension):
        self.bean_grid=bean_grid
        self.dimension=dimension

    def __call__(self,trial_index):
        bean_distance=two_grid_distance(self.bean_grid[trial_index][1],self.bean_grid[trial_index][0])
        delta_x=abs(self.bean_grid[trial_index][1][1]-self.bean_grid[trial_index][0][1])
        delta_y=abs(self.bean_grid[trial_index][0][0]-self.bean_grid[trial_index][1][0])
        if delta_y!=0:
            gradient=(self.bean_grid[trial_index][0][1]-self.bean_grid[trial_index][1][1])/(self.bean_grid[trial_index][0][0]-self.bean_grid[trial_index][1][0])
            if gradient <0:
                left_down_grid_index=[self.bean_grid[trial_index][0][0],self.bean_grid[trial_index][1][0]].\
                    index(max([self.bean_grid[trial_index][0][0],self.bean_grid[trial_index][1][0]]))
                right_up_grid_index=not left_down_grid_index
                if bean_distance/2<delta_x:
                    min_mid_point1=[self.bean_grid[trial_index][left_down_grid_index][0],
                                    self.bean_grid[trial_index][left_down_grid_index][1]+bean_distance/2]
                    min_mid_point2 = [self.bean_grid[trial_index][right_up_grid_index][0],
                                      self.bean_grid[trial_index][right_up_grid_index][1] - bean_distance / 2]
                    if random.random()<0.5:
                        pacman_grid=[random.randint(min_mid_point1[0],self.dimension-1),min_mid_point1[1]]
                    else:
                        pacman_grid = [random.randint(0,min_mid_point2[0]), min_mid_point2[1]]

                else:
                    min_mid_point1=[self.bean_grid[trial_index][left_down_grid_index][0]-(bean_distance/2-delta_x),
                                    self.bean_grid[trial_index][right_up_grid_index][1]]
                    min_mid_point2 = [self.bean_grid[trial_index][right_up_grid_index][0] + (bean_distance / 2 - delta_x),
                                      self.bean_grid[trial_index][left_down_grid_index][1]]
                    if random.random()<0.5:
                        pacman_grid=[min_mid_point1[0],random.randint(min_mid_point1[1],self.dimension-1)]
                    else:
                        pacman_grid = [min_mid_point2[0],random.randint(0,min_mid_point2[1])]

            else:
                left_up_grid_index = [self.bean_grid[trial_index][0][0], self.bean_grid[trial_index][1][0]]. \
                    index(min([self.bean_grid[trial_index][0][0], self.bean_grid[trial_index][1][0]]))
                right_down_grid_index = not left_up_grid_index
                if bean_distance/2<delta_x:
                    min_mid_point1 = [self.bean_grid[trial_index][left_up_grid_index][0] ,
                                      self.bean_grid[trial_index][left_up_grid_index][1]+bean_distance/2]
                    min_mid_point2 = [self.bean_grid[trial_index][right_down_grid_index][0],
                                      self.bean_grid[trial_index][right_down_grid_index][1]-bean_distance/2]
                    if random.random()<0.5:
                        pacman_grid=[random.randint(0,min_mid_point1[0]),min_mid_point1[1]]
                    else:
                        pacman_grid = [random.randint(min_mid_point2[0],self.dimension-1),min_mid_point2[1]]

                else:
                    min_mid_point1=[self.bean_grid[trial_index][left_up_grid_index][0]+bean_distance/2-delta_x,
                                    self.bean_grid[trial_index][right_down_grid_index][1]]
                    min_mid_point2 = [self.bean_grid[trial_index][right_down_grid_index][0]-(bean_distance/2-delta_x),
                                      self.bean_grid[trial_index][left_up_grid_index][1] ]
                    if random.random()<0.5:
                        pacman_grid=[min_mid_point1[0],random.randint(min_mid_point1[1],self.dimension-1)]
                    else:
                        pacman_grid = [min_mid_point2[0], random.randint(0,min_mid_point2[1])]
        else:
            left_grid_index = [self.bean_grid[trial_index][0][1], self.bean_grid[trial_index][1][1]]. \
                index(min([self.bean_grid[trial_index][0][1], self.bean_grid[trial_index][1][1]]))
            right_grid_index = not left_grid_index
            mid_point = [self.bean_grid[trial_index][left_grid_index][0],
                              self.bean_grid[trial_index][left_grid_index][1] + bean_distance / 2]
            if random.random()<0.5:
                pacman_grid = [random.randint(0,mid_point[0]), mid_point[1]]
            else:
                pacman_grid=[random.randint(mid_point[0],self.dimension-1), mid_point[1]]
        if two_grid_distance(pacman_grid,self.bean_grid[trial_index][0])==\
            two_grid_distance(pacman_grid,self.bean_grid[trial_index][0]):
            return pacman_grid
        else :
            return 0

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
    file_path=dict([("fixation_path",os.path.join(project_path, "images/fixation.png")),
                     ("rest_path",os.path.join(project_path, "images/rest.png")),
                     ("introduction_path" ,os.path.join(project_path, "images/introduction.png")),
                     ("positive_feedback_path",os.path.join(project_path, "images/positive_feedback.png")),
                     ("negative_feedback_path",os.path.join(project_path, "images/negative_feedback.png")),
                     ("results_path",os.path.join(project_path,"results/")),
                     ("sheep_position_path", os.path.join(project_path, "sheep_position.xlsx")),
                    ("position_path", os.path.join(project_path, "position_index.xlsx"))])
    event_space=[pg.K_UP, pg.K_DOWN,pg.K_LEFT,pg.K_RIGHT]
    speed_pixel_per_second = 30
    dimension=21
    action_space = {pg.K_UP: (0, -speed_pixel_per_second), pg.K_DOWN: (0, speed_pixel_per_second ),
                    pg.K_LEFT: (-speed_pixel_per_second , 0), pg.K_RIGHT: (speed_pixel_per_second , 0)
                    }
    noise_probability={"intention":0.1}
    screen_trait = dict([("color", [230,230,230]), ("width", speed_pixel_per_second*dimension),
                         ("height", speed_pixel_per_second*dimension)])
    background_trait=dict([("color", [0, 0, 0]), ("width", 1), ("dimension",21)])
    center_position=(screen_trait["width"]/2,screen_trait["height"]/2)
    trialnumber=60
    min_grid_distance=2
    bean_trait = dict([("color", [0, 0, 0]), ("size",10),
                       ("bean_disappear_probability", 1)])
    pacman_trait = dict([("color", [255, 48, 48]), ("size", 10)])
    time = dict([("bean_initial_disappear_time_s", 1), ("fixation_time_ms", 1300), ("feedback_time_ms", 1000),
                 ("blank_screen_time_ms",1000),("rest_time_trial",trialnumber/2 )])
    condition_ratio = {'absolute_equal_distance':2, "unequal_distance": 2}
    condition=['absolute_equal_distance','unequal_distance']
    font_information=dict([("color", [30,30,30]), ("size", 30),("type", "arial")])
    score_information=dict([("position", [4/5*screen_trait["width"],5/6*screen_trait["height"]]), ("initial_score", 0)])
    count_step=[0,1]
    pg.event.set_allowed([pg.QUIT,pg.KEYDOWN])
    pg.event.set_blocked([pg.MOUSEBUTTONUP,pg.MOUSEMOTION,pg.MOUSEBUTTONDOWN])
    bean_position = Read_position_file(file_path["sheep_position_path"])
    trial_number = bean_position.nrows - 1
    bean_grid = [[[bean_position.cell(i + 1, 0).value,
                   bean_position.cell(i + 1, 1).value],
                  [bean_position.cell(i + 1, 2).value,
                   bean_position.cell(i + 1, 3).value]
                  ] for i in range(trial_number)]
    print(bean_grid)
    generate_pacman_grid = Generate_pacman_grid(bean_grid, dimension)
    pacman_grid = [generate_pacman_grid(i) for i in range(trialnumber)]
    position_header=("sheep1_grid_y","sheep1_grid_x",
                     "sheep2_grid_y","sheep2_grid_x")
    data_workbook = openpyxl.Workbook()
    data_worksheet = data_workbook.active
    table_title = position_header
    position={}
    for index in range(len(bean_grid)):
        if index == 0:
            for col in range(len(table_title)):
                c = col + 1
                data_worksheet.cell(row=1, column=c).value = table_title[col]
        position["A"]=pacman_grid[index][0]
        position["B"] = pacman_grid[index][1]
        position["C"]=bean_grid[index][0][0]
        position["D"] = bean_grid[index][0][1]
        position["E"] = bean_grid[index][1][0]
        position["F"] = bean_grid[index][1][1]
        print(position)
        data_worksheet.append(position)
        data_workbook.save(filename=file_path["position_path"])



if __name__=="__main__":
    main()




