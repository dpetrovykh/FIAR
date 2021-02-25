#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 11:13:41 2021

@author: dpetrovykh
"""
from FIAR import FIAR

#Create a new game
game = FIAR()
game.draw_board()
#Start making moves
game.move(0,0)
game.move(1,1)
game.move(0,2)
game.move(0,1)
game.move(-1,1)
game.move(2,1)
game.move(-2,0)
game.move(1,3)
game.move(-4,-2)
game.move(1,0)
