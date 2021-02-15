#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 11:13:41 2021

@author: dpetrovykh
"""
from FIAR import FIAR, RepeatMove, OutOfBounds
from IPython.display import display

#Create a new game
game = FIAR(size=13)
game.draw_board()
#Start making moves
game.move(0,0)
game.move(1,1)
game.move(2,2)
game.move(-1,-1)
# print(game.df)
# d_to_edgeprint(f"(1,-1) is taken: {game.loc_taken((1,-1))}")
game.move(1,-1)
game.move(-1,1)
game.move(0,2)
game.move(0,1)
game.move(2,1)
game.move(-3,1)
game.move(-2,1)
game.move(-2,0)
game.undo()
game.move(-2,2)
game.move(5,3)
#Check that move verifier works
try:
    assert game.loc_taken([-2,2]) #Should pass
    assert not game.loc_taken([9,9]) #Should fail
except:
    raise Exception('You fucked up')

#Check that Repeat moves are forbidden
try: 
    game.move(-2,1)
    print('FAIL: Repeat move not allowed')
except RepeatMove:
    print("PASS: Repeat move not allowed")

#Check that out-of-bounds moves are not allowed
try:
    game.move(15,15)
    print('FAIL: Out-of-bounds move not allowed')
except OutOfBounds:
    print('PASS: Out-of-bounds move not allowed.')
    
#Check that non-int moves are not allowed
try:
    game.move(6.3,5)
    print('FAIL: non-int value checking')
except ValueError:
    print('PASS: non-int value checking')
    
# Check that the distance measurements work properly
try:
    for edge, dist in [['left',3],
                       ['right',2],
                       ['bottom',5],
                       ['top',3]]:
        calc_dist = game.d_to_edge(edge) 
        #print(f"edge: {edge}, dist: {dist}, calc_dist: {calc_dist}")
        assert calc_dist==dist
    print('PASS: d_to_edge()')
except:
    print('FAIL: d_to_edge()')
    
## Continue game to completion
game.move(-1,0)
game.move(4,0)
game.move(-1,-2)
game.move(3,0)
game.move(-1,-3)