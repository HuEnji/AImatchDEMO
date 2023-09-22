import random
from collections import deque
import pygame
# from blocks import *
import numpy


NUM_CHANNELS = 5
NUM_ACTIONS = 9

EMPTY = 0
OBSTACLE = 1
ENEMY = 2
ALLIANCE = 3
SOLDOER = 4

class SnakeStateTransition:
    actions = { # 坐标变换
        0:(0, 0), # 不动
        1:(1, 0), # 东
        2:(1, -1), # 东南
        3:(0, -1), # 南
        4:(-1, -1), # 西南
        5:(-1, 0), # 西
        6:(-1, 1), # 西北
        7:(0, 1), # 北
        8:(1, 1), # 东北
    }

    def __init__(self, pos, field):
        self.pos = pos
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.field = field.copy()
        self.field_height, self.field_width = len(field), len(field[0])
    

    def get_state(self):
        return numpy.eye(NUM_CHANNELS)[numpy.array(self.field)]

    # def get_length(self):
    #     # return len(self.snake) + 1
    #     return self.points

    def find_enemy(self, name):
        res = []
        # for i in range(self.field_height):
        #     for j in range(self.field_width):
        #         if self.field[i][j] == name:
        #             res.append([i,j])
        pos = numpy.where(numpy.array(self.field) == name)
        for p in zip(pos[0], pos[1]):
            res.append(p)
        return res

    def move_forward(self, action):
        # action: 0-8
        old_pos = self.pos
        # 新的位置
        hx = old_pos[0] + SnakeStateTransition.actions[action][0]
        hy = old_pos[1] + SnakeStateTransition.actions[action][1]
        if hx < 0 or hx >= self.field_height or hy < 0 or hy >= self.field_width \
                or self.field[hx][hy] != EMPTY:
            hx = old_pos[0]
            hy = old_pos[1]
            
            return -20, True

        # 前进，更新地图
        self.field[old_pos[0]][old_pos[1]] = EMPTY
        self.field[hx][hy] = SOLDOER
        self.pos = hx, hy

        enemy_pos = self.find_enemy(ENEMY)
        # 计算能打到的人
        hit_cnt = 0
        for enemy in enemy_pos:
            if abs(enemy[0]-self.pos_x) <= 1 and abs(enemy[1]-self.pos_y) <= 1:
                hit_cnt += 1
                self.field[enemy[0]][enemy[1]] = OBSTACLE

        if hit_cnt != 0:
            if hit_cnt == len(enemy_pos):
                return 10000, True
            return 20*hit_cnt, False

        # 没打到，但是靠近了
        distance1 = self.closest_point(old_pos, enemy_pos)
        distance2 = self.closest_point(self.pos, enemy_pos)
        if distance1 > distance2:
            return 5, False
        else:
            return -10, False

    def closest_point(self, point, points):
        '''
        计算某个点和某个list中所有点的曼哈顿距离，并返回距离最小的点和距离
        '''
        closest_distance = float('inf')
        for p in points:
            d = self.manhattan_distance(point, p)
            if d < closest_distance:
                closest_distance = d
        return closest_distance

    def manhattan_distance(self, point1, point2):
        '''
        计算两个点之间的曼哈顿距离
        '''
        x1, y1 = point1
        x2, y2 = point2
        return abs(x1 - x2) + abs(y1 - y2)



class Snake:

    actions = { # 坐标变换
        0:(0, 0), # 不动
        1:(1, 0), # 东
        2:(1, -1), # 东南
        3:(0, -1), # 南
        4:(-1, -1), # 西南
        5:(-1, 0), # 西
        6:(-1, 1), # 西北
        7:(0, 1), # 北
        8:(1, 1), # 东北
    }

    def __init__(self, field_size = 21):
        self.field_size = field_size
        self.field_height, self.field_width = field_size, field_size
        self.field = [[EMPTY]*field_size for _ in range(field_size)]
        # print(self.field)
        self.team_num = 10
        # self.feed_pos = []
        # print("self.points : ", self.points)
        self._generate_obstacles()
        self.init_characters()
        self.tot_reward = 0

    def init_characters(self):
        enemy_cnt = 0
        while enemy_cnt < self.team_num:
            pos_x, pos_y = numpy.random.randint(self.field_size, size = 2)
            if self.field[pos_x][pos_y] == EMPTY:
                self.field[pos_x][pos_y] = ENEMY
                enemy_cnt += 1

        alliance_cnt = 0
        while alliance_cnt < self.team_num - 1:
            pos_x, pos_y = numpy.random.randint(self.field_size, size = 2)
            if self.field[pos_x][pos_y] == EMPTY:
                self.field[pos_x][pos_y] = ALLIANCE
                alliance_cnt += 1

        while True:
            pos_x, pos_y = numpy.random.randint(self.field_size, size = 2)
            if self.field[pos_x][pos_y] == EMPTY:
                self.field[pos_x][pos_y] = SOLDOER
                # init soldier
                self.soldier = SnakeStateTransition([pos_x, pos_y], self.field)
                break

    def _generate_obstacles(self):
        obstacles_num = numpy.random.randint(0, 50)
        obs_cnt = 0
        while obs_cnt < obstacles_num:
            pos_x, pos_y = numpy.random.randint(self.field_size, size = 2)
            if self.field[pos_x][pos_y] == EMPTY:
                self.field[pos_x][pos_y] = OBSTACLE
                obs_cnt += 1


    def step(self, action):
        reward, done = self.soldier.move_forward(action)
        self.tot_reward += reward
        return self.soldier.get_state(), reward, done

    # def get_length(self):
    #     return self.state_transition.get_length()

    def quit(self):
        pass

    def render(self, fps):
        print(numpy.array(self.soldier.field))

    def reset(self):
        self.__init__(field_size = 21)
        return numpy.eye(NUM_CHANNELS)[numpy.array(self.field)]
    # def save_image(self, save_path):
    #     pygame.image.save(self.screen, save_path)

# snake = Snake()
# print(snake.field)
# res = numpy.where(numpy.array(snake.field) == ENEMY)
# print(res[0])
# print(res[1])
# z = zip(res[0],res[1])
# for i in z:
#     print(i)