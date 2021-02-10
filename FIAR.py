#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 12:26:54 2021

@author: dpetrovykh
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display

GRIDCOLOR = 'black'
TILE_ALPHA = 0.2
X1DCOMP = -0.3
Y1DCOMP = -0.2
X2DCOMP = -0.5
Y2DCOMP = -0.3
TEXTSIZE = 14
PLAYERS = ['black','red']
DISPLAYS = ['other','Jupyter']
DF_TEMP = pd.DataFrame({'marker':[],
                           'x':[],
                           'y':[],
                           'player':[]})

class FIAR():
    def __init__(self,height=13, width=13, size=None, first_player = 'black', display='Jupyter'):
        assert display in DISPLAYS
        self.display = display
        #Verify size or (height and width) are odd
        if size:
            assert size%2==1
            self.height = size
            self.width = size
        else:
            assert width%2==1 and height%2==1 
            self.height = height
            self.width = width
        assert first_player in PLAYERS
        self.next_player = first_player
        self.next_move = 1
        self.df = DF_TEMP.copy(deep=True)
        self.draw_board()

        
    
    def draw_board(self):
        #Draws the Board
        self.fig, self.ax = plt.subplots()
        # Control size of figure
        self.ax.set_xlim(-self.width/2, self.width/2)
        self.ax.set_ylim(-self.height/2, self.height/2)
        self.ax.set_aspect(1)
        
        ## Hide original Axes and labels
        for side in['top','right','left','bottom']:
            self.ax.spines[side].set_visible(False)
        self.ax.tick_params(axis='both',
                       which='both',
                       bottom=False,
                       top=False,
                       labelbottom=False,
                       labelleft=False,
                       left=False,
                       right=False)
        ## Drawing the grid lines
        for x in np.arange(-self.width/2,self.width/2+1):
            self.ax.axvline(x, color = GRIDCOLOR)
        for y in np.arange(-self.height/2,self.height/2+1):
            self.ax.axhline(y, color = GRIDCOLOR)
        
        ## Drawing the grid squares
        for x in np.arange(-self.width/2, self.width/2):
            for y in np.arange(-self.height/2, self.height/2):
                if (np.abs(x+0.5)+np.abs(y+0.5))%2==1:
                    rect = plt.Rectangle((x,y),1,1, alpha=TILE_ALPHA, color = 'black')
                    self.ax.add_artist(rect)
    
    def draw_number(self, num , x, y, color):
        '''
        Manual method of drawing a number to the figure
        '''
        if len(str(int(num)))==1:
            self.ax.text(x+X1DCOMP,
                         y+Y1DCOMP,
                         str(int(num)),
                         color=color,
                         size = TEXTSIZE)
        elif len(str(int(num)))==2:
            self.ax.text(x+X2DCOMP,
                         y+Y2DCOMP,
                         str(int(num)),
                         color=color,
                         size = TEXTSIZE)
        else:
            raise Exception("There's been a terrible error")
    def render(self):
        '''
        Refreshes the game. Display method depends on 'display' setting.
        '''
        if self.display == 'regular':
            self.show()
        elif self.display == 'Jupyter':
            self.JNshow()
        else:
            raise Exception("display value invalid")
    
    def show(self):
        '''
        Regular method for drawing the figure
        '''
        self.fig.show()
        
    def JNshow(self):
        '''
        Jupyter-Notebook-specific display method
        '''
        display(self.fig)
        
    def move(self, x, y,player='next'):
        '''
        High-level function for performing a move
        '''
        if player != 'next':
            assert player in PLAYERS
            self.next_player = player
        ## Verify Legality of move
        # Move is in  repeat location
        if self.loc_taken([x,y]):
            raise ValueError(f'The location ({x},{y}) has already been taken')
        # Move is beyond the current board.
        if abs(x)>self.width//2 or abs(y)>self.width//2:
            raise ValueError(f"The location ({x},{y}) is beyond the scope of the board.")
        ## Consequences of Move
        #record the move
        self.record_move(self.next_move, x, y, self.next_player)
        #Draw the move
        self.draw_number(self.next_move, x, y, self.next_player)
        #increment next_move value
        self.next_move +=1
        #switch next_player
        self.switch_player()
        self.render()

    def set_next_player(self, player):
        ''' Sets the next player
        '''
        assert player in PLAYERS
        self.next_player = player
        
    def record_move(self, marker, x, y, player):
        new_row = DF_TEMP.copy(deep=True)
        new_row.marker = [marker]
        new_row.x = [x]
        new_row.y = [y]
        new_row.player = [player]
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        
    def draw_markers(self):
        '''
        Draws all of the markers present in this game's log.'

        Returns
        -------
        None.

        '''
        for rowi in range(self.df.shape[0]):
            row = self.df.iloc[rowi,:] 
            marker = row.marker
            x = row.x
            y = row.y
            player = row.player
            #display(marker,x,y,player)
            #print(marker,x,y,player)
            self.draw_number(marker,x,y,player)
    
    def check_move(self):
        '''
        Need some way to verify that a move has not been made before.
        '''
        pass
    
    def undo(self):
        '''
        Undoes the previous move, removing it from the record and redrawing the plot.

        Returns
        -------
        None.

        '''
        self.df = self.df.iloc[0:-1,:]
        self.draw_board()
        self.draw_markers()
        self.switch_player()
        self.next_move -=1
        
    def switch_player(self):
        if self.next_player == 'black':
           self.next_player = 'red'
        elif self.next_player == 'red':
            self.next_player = 'black'
        
    def loc_taken(self, loc):
        '''
        Verifies the membership of a point in the game data

        Parameters
        ----------
        loc : tuple of ints.
            DESCRIPTION. The x and y location of a point which we would like to verify.

        Returns
        -------
        None.

        '''
        return loc in self.df[['x','y']].values.tolist()
    
    def d_to_edge(self,edge):
        '''calculates the minimum distance from every point to a given edge
        '''
        ## Redefine variables based on supplied 'edge'
        prop_dict = {'right':('x',np.max,'width',1),
                     'left':('x',np.min,'width',-1),
                     'top':('y',np.max,'height',1),
                     'bottom':('y',np.min,'height',-1)}
        axis, max_or_min, dim, pol = prop_dict[edge]
        #print(axis, max_or_min, dim, pol)
        edge_loc = (eval('self.'+dim)//2)*pol
        #print(edge_loc)
        ## Calculate gap
        return abs(edge_loc -max_or_min(self.df[axis]))