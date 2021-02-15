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
from sys import exit

GRIDCOLOR = 'black'
GRID_MARKER_SPACING = int(3)
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
MIN_EDGE_GAP = 2
EMPTY_CHAR = '+'
PLAYER_CHARS = {'red':'r',
                     'black':'b'}
BLACK_VICTORY = ['b']*5
RED_VICTORY = ['r']*5
SAVE_FOLDER = 'saves'

class RepeatMove(Exception):
    pass

class OutOfBounds(Exception):
    pass

class FIAR():
    '''
    Documentation for FIAR class
    '''
    def __init__(self, size=5, df=None, first_player = 'black', display='Jupyter'):
        '''
        Test documentation for FIAR __init__()
        '''
        assert display in DISPLAYS
        self.display = display
        if type(df)==pd.DataFrame:
            meg = MIN_EDGE_GAP
            ## Calculate neccessary edge dimensions
            self.right_edge = df['x'].max() +meg+0.5
            self.left_edge = df['x'].min() -meg-0.5
            self.top_edge = df['y'].max() +meg+0.5
            self.bottom_edge = df['y'].min() -meg-0.5
            # Calculate next player
            self.next_player = df['player'].iloc[-1]
            self.switch_player()
            # Calculate next_move
            self.next_move = df['marker'].iloc[-1]+1
            self.df = df.copy(deep=True)
        else: #No dataframe provided, a new game.
            #Verify size is odd and define edge locations
            assert size%2==1
            self.right_edge = size//2+0.5
            self.left_edge = -size//2+0.5
            self.top_edge = size//2+0.5
            self.bottom_edge = -size//2+0.5
            #Other vars
            assert first_player in PLAYERS
            self.next_player = first_player
            self.next_move = 1
            self.df = DF_TEMP.copy(deep=True)
        self.matrix = self.update_matrix()
    
    @staticmethod
    def run():
        '''
        The highest-level run

        Returns
        -------
        None.

        '''
        #Welcome players to the game
        print("Welcome to Tic-Tac-Toe Five-in-a-Row!")
        #Ask if playing new or saved game
        mode = None
        while mode == None:
            ret = input("Would you like to play a 'new' game or 'load' a save?\n")
            if ret in ['new','new_game','New']:
                mode = 'new'
            elif ret in ['load','save','load_save','old game']:
                mode = 'load'
        #If new:
        if mode == 'new':
            FIAR.new_game()
        #If saved:
        elif mode == 'load':
            #Display saves
            pass
            #allow selection
            filename = None
            while filename == None:
                ret = input('Please input a valid save name: ')
                ## checking input
                name, ext = [None]*2
                try: 
                    game = FIAR.from_csv(ret+'.csv')
                    FIAR.run_game(game)
                    filename = True
                except:
                    pass
            exit()
    
    @staticmethod
    def new_game():
        '''
        Runs a NEW game through a terminal interface

        Returns
        -------
        None.

        '''
        #create the game
        game = FIAR(size=1)
        game.draw_board()
        game.render()        
        print("It is recommended to make '0,0' your first move. Special commands include: 'undo', 'quit', 'save'")
        ## Receive input of player
        first_player = None
        while first_player == None:
            fp = input("Is the first player 'black' or 'red'? ")
            if fp in PLAYERS:
                first_player = fp
            else:
                print(f"\'{fp}\' is not an option")
        game.set_next_player(first_player)
        #print(first_player)
        FIAR.game_loop(game)
    
    @staticmethod
    def list_saves():
        pass
    
    def to_csv(self,filename = None):
        '''
        Saves the game's dataframe as a csv

        Returns
        -------
        None.

        '''
        name,ext = [None]*2
        #Assume it has 'csv' extension
        try:
            name, ext = filename.split('.')    
            if ext != 'csv':
                print(f"'{ext}' extension changed to '.csv'")
                ext = 'csv'
        # Case where name has no exception
        except ValueError: 
            name = filename
            ext = 'csv'
        filename = SAVE_FOLDER+'/'+name+'.'+ext
        self.df.to_csv(filename, index=None)
    
    @staticmethod
    def from_csv(filename = None):
        '''
        Loads a saved game an returns the game object

        Returns
        -------
        The new game object generated from old data

        '''
        filename = SAVE_FOLDER+'/'+filename
        df = pd.read_csv(filename)[['marker','x','y','player']]
        game= FIAR(df=df)
        return game
    
    @staticmethod
    def run_game(game):
        '''
        Serves the same purpose as run() but takes a game as an input. Lacks setup inputs
        '''
        print('Welcome!')
        game.draw_board()
        game.draw_markers()
        game.render()
        FIAR.game_loop(game)
    
    @staticmethod
    def game_loop(game):
        ##Main game loopzXC
        while True:
            x = None
            y = None
            move_made = False
            while move_made ==False:
                #iterate through moves
                coords = input(f"Enter 'x,y' coordinates for {game.next_player}'s next move: ")
                if coords == 'undo':
                    game.undo()
                elif coords.lower() in ['quit','exit','end']:
                    print(f'The game has been ended by the {game.next_player} player')
                    exit()
                elif coords.lower()=='save':
                    #print('Saving the game has not yet been implemented')
                    while True:
                        ret = input('Please provide a save name for this game: \n')
                        if len(ret.split()) >1:
                            print("Please don't use special characters")
                        else:
                            game.to_csv(ret.lower().strip()+'.csv')
                            exit()
                else:
                    try:
                        x,y = coords.split(',')
                        x = int(x.strip())
                        y = int(y.strip())
                        move_made = True
                    except:
                        print("Input for coordinates not recognized as valid.")
            try:
                game.move(x,y)
            except OutOfBounds:
                print("The prescribed move is out-of-bounds")
            except RepeatMove:
                print("That spot has already been taken")
    
    def draw_board(self):
        #Draws the Board
        self.fig, self.ax = plt.subplots()
        # Control size of figure
        self.ax.set_xlim(self.left_edge, self.right_edge)
        self.ax.set_ylim(self.bottom_edge, self.top_edge)
        # set aspect ration to maintain square grid
        #aspect_ratio = (self.right_edge-self.left_edge-1)/(self.top_edge-self.bottom_edge-1)
        #self.ax.set_aspect(aspect_ratio)
        self.ax.set_aspect(1)
        #print(f"aspect ratio: {aspect_ratio}")
        
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
        for x in np.arange(self.left_edge,self.right_edge+1):
            self.ax.axvline(x, color = GRIDCOLOR)
        for y in np.arange(self.bottom_edge,self.top_edge+1):
            self.ax.axhline(y, color = GRIDCOLOR)
        
        ## Drawing the grid squares
        for x in np.arange(self.left_edge, self.right_edge):
            for y in np.arange(self.bottom_edge, self.top_edge):
                if (np.abs(x+0.5)+np.abs(y+0.5))%2==1:
                    rect = plt.Rectangle((x,y),1,1, alpha=TILE_ALPHA, color = 'black')
                    self.ax.add_artist(rect)
                    
        ## Draw the grid markers
        
        # Go through each point with specified spacing that fits within the playing field
        neg_x_dir = 0
        while True:
            if neg_x_dir - GRID_MARKER_SPACING>self.left_edge:
                neg_x_dir += -GRID_MARKER_SPACING
            else:
                break
        pos_x_dir=0
        while True:
            if pos_x_dir + GRID_MARKER_SPACING<self.right_edge:
                pos_x_dir += GRID_MARKER_SPACING
            else:
                break
        neg_y_dir = 0
        while True:
            if neg_y_dir-GRID_MARKER_SPACING>self.bottom_edge:
                neg_y_dir += -GRID_MARKER_SPACING
            else:
                break
        pos_y_dir = 0
        while True:
            if pos_y_dir-GRID_MARKER_SPACING <self.top_edge:
                pos_y_dir += GRID_MARKER_SPACING
            else:
                break
        xs = list(range(neg_x_dir,pos_x_dir+GRID_MARKER_SPACING,GRID_MARKER_SPACING))
        ys = list(range(neg_y_dir,pos_y_dir+GRID_MARKER_SPACING, GRID_MARKER_SPACING))
        for x in xs:
            for y in ys:
                self.ax.plot([x-0.05],[y],'+',color='grey')
                
        # draw it
    
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
        #move is an integer position
        if x%1!=0 or y%1!=0:
            raise ValueError("Both x and y must in integer values")
        #TODO
        # Move is in  repeat location
        if self.loc_taken([x,y]):
            raise RepeatMove(f'The location ({x},{y}) has already been taken')
        # Move is beyond the current board.
        if x>self.right_edge or x<self.left_edge or y>self.top_edge or y<self.bottom_edge:
            raise OutOfBounds(f"The location ({x},{y}) is beyond the scope of the board.")
        ## Consequences of Move
        #record the move
        self.record_move(self.next_move, x, y, self.next_player)
        #Draw the move
        self.draw_number(self.next_move, x, y, self.next_player)
        # Check if board must be expanded on any side
        #print(f"Move: {self.next_move}")
        for direction, edge in [('left', self.left_edge),
                           ('right', self.right_edge),
                           ('top', self.top_edge),
                           ('bottom', self.bottom_edge)]:
            #if gap too small
            gap =self.d_to_edge(direction)
            #print(f"direction: {direction}, gap: {gap}")
            if gap<MIN_EDGE_GAP:
                #print(f"Not enough room in direction: {direction}")
                #print(f"old dist: {edge}")
                #expand the board
                additional_spaces = MIN_EDGE_GAP-gap
                if direction == 'left':
                    self.left_edge += -additional_spaces
                elif direction == 'right':
                    self.right_edge += additional_spaces
                elif direction == 'top':
                    self.top_edge += additional_spaces
                elif direction == 'bottom':
                    self.bottom_edge += -additional_spaces
                #print(f"new dist: {edge}")
                ## Redraw the newly enlarged board with the markers
                self.draw_board()
                self.draw_markers()
        self.update_matrix()
        self.scan_through_matrix()
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
        self.render()
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
        prop_dict = {'right':('x',np.max,self.right_edge-0.5),
                     'left':('x',np.min,self.left_edge+0.5),
                     'top':('y',np.max,self.top_edge-0.5),
                     'bottom':('y',np.min,self.bottom_edge+0.5)}
        axis, max_or_min, edge_loc = prop_dict[edge]
        #print(axis, max_or_min, edge_loc)
        ## Calculate gap
        return abs(edge_loc -max_or_min(self.df[axis]))
    
    def update_matrix(self):
        matrix = np.ones((self.height,self.width), dtype=str)
        matrix[:,:] = EMPTY_CHAR
        for rowi in range(self.df.shape[0]):
            x,y,player = self.df[['x','y','player']].iloc[rowi,:]
            i,j = self.xy_to_ij((x,y))
            matrix[i,j]= PLAYER_CHARS[player]
        self.matrix = matrix
        
    def scan_through_matrix(self):
        ## Vertical Scanning
        #print('Vertical Scanning')
        for j in range(self.width):
            queue = ['_']*5
            for i in range(self.height):
                queue.pop(0)
                queue.append(self.matrix[i,j])
                # print(queue)
                self.check_victory(queue)
        ## Horizontal Scanning
        # print('Horizontal Scanning')
        for i in range(self.height):
            queue = ['_']*5
            for j in range(self.width):
                queue.pop(0)
                queue.append(self.matrix[i,j])
                # print(queue)
                self.check_victory(queue)        
        ##Negative-slope Diagonal Scanning
        #Generate list of starting points
        # print('Down-Right Scanning')
        left_side_points = zip(list(range(self.height-1,0,-1)),[0]*self.height) 
        top_side_points = zip([0]*self.width,list(range(0,self.width)))
        start_points = list(left_side_points)
        start_points.extend(top_side_points)
        for i_0,j_0 in start_points:
            queue = ['_']*5
            N = min(self.height-i_0, self.width-j_0)
            # print(f'N = {N}')
            for n in range(N):
                queue.pop(0)
                queue.append(self.matrix[i_0+n, j_0+n])
                # print(queue)
                self.check_victory(queue)
        ##Positive-sloped Diagonal Scanning
        #Generate list of starting points
        # print('Down-Left Scanning')
        right_points = zip(list(range(self.height-1,0,-1)),[self.width-1]*self.height)
        top_points = zip([0]*self.width,list(range(self.width-1,-1,-1)))
        start_points = list(right_points) #copy the list
        start_points.extend(top_points)
        for i_0,j_0 in start_points:
            queue = ['_']*5
            N = min(self.height-i_0, j_0+1)
            # print(f'N = {N}')
            for n in range(N):
                queue.pop(0)
                queue.append(self.matrix[i_0+n, j_0-n])
                # print(queue)
                self.check_victory(queue)        
                
    def check_victory(self, queue):
        if queue == RED_VICTORY:
            ## END THE GAME
            print('Red Wins! Congratulations!')
            exit()
        elif queue == BLACK_VICTORY:
            ## END THE GAME
            print('Black wins! Congratulations!')
            exit()
            
    def end_game(self):
        pass
    
    @property
    def width(self):
        return int(self.right_edge-self.left_edge)
    
    @property
    def height(self):
        return int(self.top_edge-self.bottom_edge)
    
    def xy_to_ij(self, xy):
        '''
        Transforms a coordinate pair from the game coordinate system to the matrix coordinate system
        '''
        return int((self.top_edge-0.5)-xy[1]), int(xy[0]-(self.left_edge+0.5))
    
    def ij_to_xy(self, ij):
        '''
        Transforms a coordinate pair from the matrix coordinate system to the game coordinate system.
        '''
        return ij[1]+(self.left_edge+0.5), (self.top_edge-0.5)-ij[0]