#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 11:13:41 2021

@author: dpetrovykh
"""
from FIAR import FIAR
from IPython.display import display

#Create a new game
game = FIAR()
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
#Check that move verifier works
try:
    assert game.loc_taken([-2,2]) #Should pass
    assert not game.loc_taken([9,9]) #Should fail
except:
    raise Exception('You fucked up')

#Check that Repeat moves are forbidden
try: 
    game.move(-2,1)
except ValueError:
    print("PASS: Repeat move not allowed")

#Check that out-of-bounds moves are not allowed
try:
    game.move(15,15)
except ValueError:
    print('PASS: Out-of-bounds move not allowed.')
    
# Check that the distance measurements work properly
try:
    for edge, dist in [['left',3],
                       ['right',4],
                       ['bottom',5],
                       ['top',4]]:
        assert game.d_to_edge(edge)==dist
    print('PASS: d_to_edge()')
except:
    print('FAIL: d_to_edge()')