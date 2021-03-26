#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 12:26:54 2021

@author: dpetrovykh
"""

import numpy as np
import pandas as pd

try:
    from FIAR_Saves import SAVE_FOLDER
except:
    print("Failed to import from FIAR_Saves")

PLAYERS = ['black','red']
DF_TEMP = pd.DataFrame({'marker':[],
                           'x':[],
                           'y':[],
                           'player':[]})
PLAYER2MARKER = {'red':'r',
                     'black':'b'}
MAX_MOVE_REACH = 5

class RepeatMove(Exception):
    def __init__(self, message=None):
        super(RepeatMove, self).__init__()
        self.message = message

class OutOfBounds(Exception):
    def __init__(self, message=None):
        super(OutOfBounds, self).__init__()
        self.message = message
        

class FIAR():
    '''
    TIC-TAC-TOE Five In A Row game. Contains all functionality for manually playing a game with the right commands.
    '''
    def __init__(self, df=None, first_player = 'black'):
        '''
        Test documentation for FIAR __init__()
        '''
        if type(df)==pd.DataFrame:
            # Calculate next player
            self.next_player = df['player'].iloc[-1]
            self.switch_player()
            # Calculate next_move marker value
            self.next_move = df['marker'].iloc[-1]+1
            self.df = df.copy(deep=True)            
        else: #No dataframe provided, a new game.
            assert first_player in PLAYERS
            self.next_player = first_player
            self.next_move = 1
            self.df = DF_TEMP.copy(deep=True)
        ## Calculate neccessary edge dimensions
        self.game_edges = self.marker_bounds()
    
    def __iter__(self):
        '''
        allows iteration through every game state which led up to the current one.

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        dfs = self.df_states()
        return (FIAR(df=df) for df in dfs)                              
    
    @property
    def width(self):
        return int(self.game_edges['right'] - self.game_edges['left']+1)
    
    @property
    def height(self):
        return int(self.game_edges['top'] - self.game_edges['bottom']+1)

    def move(self, x, y,player='next'):
        '''
        High-level function for performing a move
        '''
        if player != 'next':
            assert player in PLAYERS
            self.next_player = player
        ## Verify Legality of move
        self.check_move_allowed((x,y))
        ## Consequences of Move
        #record the move
        self.record_move(self.next_move, x, y, self.next_player)
        ## Calculate new board dimensions
        self.game_edges = self.marker_bounds()
        #increment next_move value
        self.next_move +=1
        #switch next_player
        self.switch_player()
    
    def to_csv(self,filename, folder=SAVE_FOLDER):
        '''
        Saves the game's dataframe as a csv. Supplied name must lack all extensions.

        Returns
        -------
        None.

        '''
        #If an extension is provided
        if '.' in filename:
            raise ValueError('Do not provide a filename with periods.')
        address = folder+'/'+filename+'.csv'
        #print(f"SAVE_FOLDER: {SAVE_FOLDER}, filename: {filename}, ext: {ext}, address: {address}")
        self.df.to_csv(address, index=None)
        #print(f"Game saved as '{filename+'.csv'}'")
        
    @staticmethod
    def from_csv(filename,folder=SAVE_FOLDER):
        '''
        Loads a saved game and returns the game object. 
        Inputs:
        -------
            filename (str): name of save. Should not contain file extension.

        Returns
        -------
        The new game object generated from old data

        '''
        address = folder+'/'+filename+'.csv'
        df = pd.read_csv(address)[['marker','x','y','player']]
        game= FIAR(df=df)
        return game

    def record_move(self, marker, x, y, player):
        new_row = DF_TEMP.copy(deep=True)
        new_row.marker = [marker]
        new_row.x = [x]
        new_row.y = [y]
        new_row.player = [player]
        self.df = pd.concat([self.df, new_row], ignore_index=True)    
    
    def undo(self):
        '''
        Undoes the previous move, removing it from the record and redrawing the plot.

        Returns
        -------
        None.

        '''
        if self.num_moves>0:
            self.df = self.df.iloc[0:-1,:]
            self.switch_player()
            self.next_move -=1
        else:
            raise IndexError("Not enough moves to undo")
        
    def df_states(self):
        '''
        Returns a generator which yields a dataframe for each state of the game, starting with the completion of the first move.

        Yields
        ------
        df pandas.DataFrame
            Record of all moves made in the game up to that point.

        '''
        for row in range(1,self.df.shape[0]+1):
            yield self.df[:row]
    
    def df_rows(self):
        '''
        Returns a generator which yields a row from the dataframe representing each move.

        Yields
        ------
        df pandas.DataFrame
            A row representing a single move in the game.

        '''
        for rowi in range(self.df.shape[0]):
            yield self.df.iloc[rowi,:] 
    
    def marker_bounds(self):
        '''
        Finds the furthest distance that markers extend in all 4 directions in the x-y plane, and returns a tuple of their integer values. Gives a minimum of 0 for right and top and maximum of 0 for left and bottom

        Returns
        -------
        bounds : dict {str:int}
            tuple of furthest tile to which markers have reach in (right, top, left, bottom) directions. Accesible with str keys, "right", "top", etc

        '''
        top = int(max([*self.df['y'],0]))
        bottom = int(min([*self.df['y'],0]))
        right = int(max([*self.df['x'],0]))
        left = int(min([*self.df['x'],0]))
        return {'right':right,
                'top':top,
                'left':left,
                'bottom':bottom}    
    
    def board_locs(self):
        '''
        Returns a list of all locations on the board

        Returns
        -------
        points : list of (x,y) int tuples.
            Every point on the board, occupied or otherwise.

        '''    
        bounds = self.marker_bounds()
        return [(int(x),int(y)) for x in np.arange(bounds['left'],bounds['right']+1) for y in np.arange(bounds['bottom'],bounds['top']+1)]

    def taken_locs(self):
        '''
        Returns a list of all occupied locations on the board

        Returns
        -------
        taken_locs : list of (x,y) int tuples
            Every point on the board that is occupied

        '''
        nplist = list(self.df[['x','y']].values)
        taken_locs = [(int(x),int(y)) for x,y in nplist]
        return taken_locs

    def switch_player(self):
        if self.next_player == 'black':
           self.next_player = 'red'
        elif self.next_player == 'red':
            self.next_player = 'black'
    
    @property
    def previous_player(self):
        return {'red':'black',
                'black':'red'}[self.next_player]
        
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
    
    def check_move_allowed(self, coords):
        '''
        Checks whether the move in (x,y) cordinates is allowed.

        Parameters
        ----------
        coords : int tuple
            (x,y) location of proposed move

        Side-Effects
        ------------
        May raise an OutOfBounds exception or RepeatMove exception.

        Returns
        -------
        None

        '''
        direction  = {'right':1,
                      'left':-1,
                      'top':1,
                      'bottom':-1}
        x,y = coords
        ## move is an integer position
        if x%1!=0 or y%1!=0:
            raise ValueError("Both x and y must in integer values")
        ## Location is empty
        if coords in self.taken_locs():
            raise RepeatMove(f'The location ({x},{y}) has already been taken')
        # Move is close enough to other points
        allowed_move_bound = {key:value+MAX_MOVE_REACH*direction[key] for key, value in self.marker_bounds().items()}
        within_bounds = not bool(x>allowed_move_bound['right'] or x<allowed_move_bound['left'] or y>allowed_move_bound['top'] or y<allowed_move_bound['left'])
        if not within_bounds:
            raise OutOfBounds(f"The location ({x},{y}) is beyond the scope of the board.")  

    def set_next_player(self, player):
        ''' Sets the next player
        '''
        assert player in PLAYERS
        self.next_player = player
    
    @property
    def num_moves(self):
        '''
        The number of moves that have been made in the game..

        Returns
        -------
        int.

        '''
        return self.df.shape[0]