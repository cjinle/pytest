#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

UNKNOWN = 0x0
MINE = 0x9
MARKED = 0xa
BAD_MARK = 0xb
EMPTY = 0xc
DETONATED = 0xd


class Mine:
    width = 10
    height = 10
    numMines = 2
    markedMines = 0
    badMarkedMines = 0
    field = []

    def __init__(self):
        self.field = [0] * (self.width * self.height)

    def get_idx(self, x, y):
        return x + y * self.width

    def get_xy(self, idx):
        return (idx % self.width, int(idx/self.width))

    def get_mine(self, x, y):
        idx = self.get_idx(x, y)
        if idx >= (self.width * self.height):
            return UNKNOWN
        return self.field[idx] & 0xf

    def set_mine(self, x, y, mine_type):
        self.field[self.get_idx(x, y)] = mine_type
        return

    def random_mine(self):
        minesToSet = self.numMines
        while minesToSet > 0:
            randX = int(random.random()*100000000) % self.width
            randY = int(random.random()*100000000) % self.height
            if self.get_mine(randX, randY) != MINE:
                self.set_mine(randX, randY, MINE)
                minesToSet -= 1

    def random_mine2(self):
        tmplist = list(range(len(self.field)-1))
        random.shuffle(tmplist)
        minesToSet = self.numMines
        while minesToSet > 0:
            x, y = self.get_xy(tmplist.pop())
            if self.get_mine(x, y) != MINE:
                self.set_mine(x, y, MINE)
                minesToSet -= 1

    def reready(self):
        self.random_mine()

    def incr_number(self, x, y, num):
        if self.get_mine(x, y) in (MINE, MARKED, DETONATED):
            num += 1
        return num

    def calc_number(self, x, y):
        mine_type = self.get_mine(x, y)
        if mine_type != UNKNOWN:
            return mine_type
            
        total = 0
        if y-1 >= 0:
            if x-1 >= 0:
                total = self.incr_number(x-1, y-1, total)
            total = self.incr_number(x, y-1, total)
            if x+1 < self.width:
                total = self.incr_number(x+1, y-1, total)

        if x-1 >= 0:
            total = self.incr_number(x-1, y, total)

        if x+1 < self.width:
            total = self.incr_number(x+1, y, total)

        if y+1 < self.height:
            if x-1 >= 0:
                total = self.incr_number(x-1, y+1, total)
            total = self.incr_number(x, y+1, total)
            if x+1 < self.width:
                total = self.incr_number(x+1, y+1, total)

        return total

    def get_children(self, x, y):
        ret = []
        if y-1 >= 0:
            if x-1 >= 0:
                if self.get_mine(x-1, y-1) == UNKNOWN:
                    ret.append(self.get_idx(x-1, y-1))
            if self.get_mine(x, y-1) == UNKNOWN:
                ret.append(self.get_idx(x, y-1))
            if x+1 < self.width:
                if self.get_mine(x+1, y-1) == UNKNOWN:
                    ret.append(self.get_idx(x+1, y-1))
        if x-1 >= 0:
            if self.get_mine(x-1, y) == UNKNOWN:
                ret.append(self.get_idx(x-1, y))
        if x+1 < self.width:
            if self.get_mine(x+1, y) == UNKNOWN:
                ret.append(self.get_idx(x+1, y))
        if y+1 < self.height:
            if x-1 >= 0:
                if self.get_mine(x-1, y+1) == UNKNOWN:
                    ret.append(self.get_idx(x-1, y+1))
            if self.get_mine(x, y+1) == UNKNOWN:
                ret.append(self.get_idx(x, y+1))
            if x+1 < self.width:
                if self.get_mine(x+1, y+1) == UNKNOWN:
                    ret.append(self.get_idx(x+1, y+1)) 
        return ret

    def clear(self, x, y):
        mark = [self.get_idx(x, y)]
        while len(mark) > 0:
            idx = mark.pop()
            x, y = self.get_xy(idx)
            total = self.calc_number(x, y)
            print("total: {0}".format(total))
            mine_type = total
            if total == 0:
                mine_type = EMPTY
                for child in self.get_children(x, y):
                    if child not in mark: mark.append(child)
                    print(child)
            self.set_mine(x, y, mine_type)
    

    def output(self):
        print('+', '-'*3*self.width, '+', sep='')
        for x in range(self.height):
            print('|', end='')
            for y in range(self.width):
                # num = self.calc_number(x, y)
                print(self.output_format(self.get_mine(x, y)), end='')
            print('|')
        print('+', '-'*3*self.width, '+', sep='')

    def output_format(self, mine_type):
        if mine_type == UNKNOWN:
            return ' - '
        if mine_type == EMPTY:
            return '   '
        elif mine_type == MINE:
            return ' \033[31mo\033[0m '
        else:
            return " {0} ".format(mine_type)



if __name__ == '__main__':
    mine = Mine()
    mine.reready()
    while True:
        param = input("input > ")
        arr = param.split(' ')
        if len(arr) > 1:
            print(arr)
            mine.clear(int(arr[0]), int(arr[1]))
        mine.output()
