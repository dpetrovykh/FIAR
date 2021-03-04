#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 11:13:41 2021

@author: dpetrovykh
"""
from FIAR import FIAR

#Create a new game
game = FIAR()
game.display_all()
#Start making moves
game.move(0,0)
game.move(1,1)
game.move(0,2)
game.move(0,1)
game.move(-1,1)
game.move(2,1)
game.move(-2,0)
# game.move(1,3)
# game.move(-4,-2)
# game.move(1,0)
# game.move(-1,0)
# game.move(-3,0)
# game.move(0,-1)
# game.move(1,2)
# game.move(1,-1)
# game.move(3,1)
# game.move(4,1)
# for x,y in [(2,0),
#             (2,2),
#             (3,0),
#             (-2,1),
#             (-2,-1),
#             (-2,-2),
#             (-1,3),
#             (0,4)]:
#     game.move(x,y)
# game.update_PoTs_dict()
# # print(f" Cell_dict: {game.cell_dict_gen()}")
# cell_dict = game.cell_dict_gen()
# playable_points = game.playable_points()
# point_eval = FIAR.point_evaluater(game, FIAR.evaluate_point_sum)
