#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 12:26:54 2021

@author: dpetrovykh
"""

import matplotlib.pyplot as plt
plt.ion()
## TODO
## Make sure that ion() and ioff() when neccessary.
import numpy as np
import pandas as pd
from IPython.display import display
from sys import exit
import sys
import os
from pynput.keyboard import Listener, Key
import types
from collections import namedtuple
import itertools as it
import math
import random

##Debugging constants that trigger print statements
SHOW_PoTs = False
SHOW_SPots = False
SHOW_HPots = False
PRINT_CELL_CHOICE = True
SHOW_Evals = False
SHOW_QUEUES= False
## Debugging constants that trigger overlay elements to be displayed
DRAW_SPOTS = False
DRAW_HPOTS = False

## Constants
G_SCALE = 4 # global scaler
GRID_DICT = {'color': 'blue',
             'alpha': 0.2,
             'linewidth':0.5*G_SCALE}
GRID_MARKER_SPACING = int(3)
FIGSIZE = 0.5*G_SCALE
# TILE_ALPHA = 0.2
# TILE_COLOR = 'yellow'
TILE_DICT = {'alpha':0.2,
             'color':'yellow'}
GRID_MARKER = '+'
GRID_MARKER_KWARGS = {'color':'grey',
                      'markersize': 10*G_SCALE}
X1DCOMP = 0 #-0.2
Y1DCOMP = -0.1 #-0.2
X2DCOMP = 0 #-0.35
Y2DCOMP = -0.1 #-0.2
PLAYERS = ['black','red']
DISPLAYS = ['regular','Jupyter']
DF_TEMP = pd.DataFrame({'marker':[],
                           'x':[],
                           'y':[],
                           'player':[]})
MIN_EDGE_GAP = 2
MAX_MOVE_REACH = 5
NUM_DICT = {'size':17*G_SCALE,
            'alpha':1,
            'horizontalalignment':'center',
            'verticalalignment':'center',
            'fontstyle':'normal'}


EMPTY_CHAR = '+'
PLAYER2MARKER = {'red':'r',
                     'black':'b'}
BLACK_VICTORY = ['b']*5
RED_VICTORY = ['r']*5
SAVE_FOLDER = 'saves'
RECORDS_FOLDER = 'records'
TEST_FOLDER = 'test_saves'
YESSES = ['y','yes','yup']
NOS = ['n','no','nope']
RAW_SPs = [
    ['SP1','efftte'],
    ['SP1r','ettffe'],
    ['SP2','eftfte'],
    ['SP2r','etftfe'],
    ['SP3','efttfe'],
    ['SP4','etffte']]
RAW_HPs = [
    ['HP1','ttfff'],
    ['HP1r','ffftt'],
    ['HP2','tftff'],
    ['HP2r','fftft'],
    ['HP3','tfftf'],
    ['HP3r', 'ftfft'],
    ['HP4','tffft'],
    ['HP5','fttff'],
    ['HP5r','ffttf'],
    ['HP6','ftftf']]
RAW_STs = [
    ['ST1','dfffde'],
    ['ST1r','edfffd'],
    ['ST2','dffdfd'],
    ['ST2r','dfdffd']
    ]
RAW_HTs = [
    ['HT1','dffff'],
    ['HT1r','ffffd'],
    ['HT2','fdfff'],
    ['HT2r','fffdf'],
    ['HT3','ffdff']
    ]
RAW_Spots = [
    ['Spot1','efttte'],
    ['Spot1r','etttfe'],
    ['Spot2','etftte'],
    ['Spot2r','ettfte']
    ]
RAW_Hpots = [
    ['Hpot1','bbbff'],
    ['Hpot1r','ffbbb'],
    ['Hpot2','bbfbf'],
    ['Hpot2r','fbfbb'],
    ['Hpot3','bbffb'],
    ['Hpot3r','bffbb'],
    ['Hpot4','bfbbf'],
    ['Hpot4r','fbbfb'],
    ['Hpot5','bfbfb'],
    ['Hpot6','fbbbf']]

PATTERN_TEMPLATE = namedtuple('Pattern','name player match_pat rel_markers rel_triggers rel_defusers rel_boosters')
PoT_TEMPLATE = namedtuple('PoT','names player marker_locs trigger_locs')
SPOT_TEMPLATE = namedtuple('SPot','names player marker_locs trigger_locs')
HPOT_TEMPLATE = namedtuple('HPot','names player marker_locs booster_locs')
SOFT_POWER = namedtuple('SoftPower','names player marker_locs trigger_locs booster_locs defuser_locs')
HARD_POWER = namedtuple('HardPower','names player marker_locs trigger_locs defuser_locs')
SOFT_THREAT = namedtuple('SoftThreat','names player marker_locs defuser_locs')
HARD_THREAT = namedtuple('HardThreat','names player marker_locs defuser_locs')

IJ_TO_XY_R = [[0,1],[-1,0]] #Matrix for transforming unit vectors from ij to xy coords
XY_TO_IJ_R = [[0,-1],[1,0]] #Matrix for transforming unit vectors from xy to ij coords.

## PoT Plotting Constants
COLOR_DICT = {'red':'red',
                 'black':'black'}
D_MARKER = {SOFT_THREAT:'s',
            HARD_THREAT:'s'}
D_MARKERDICT = {
                SOFT_THREAT: {'size':15*G_SCALE,
                              'alpha':0.3,
                              'horizontalalignment':'center',
                              'verticalalignment':'center',},
                HARD_THREAT: {'size':20*G_SCALE,
                              'alpha':0.5,
                              'horizontalalignment':'center',
                              'verticalalignment':'center',}
                }
T_MARKER = {SOFT_POWER:'o',
            HARD_POWER:'*'}
T_MARKERDICT = {
                SOFT_POWER: {'size':17*G_SCALE,
                             'alpha':0.3,
                             'horizontalalignment':'center',
                             'verticalalignment':'center'},
                HARD_POWER: {'size':16*G_SCALE,
                             'alpha':0.5,
                             'horizontalalignment':'center',
                             'verticalalignment':'center'}
                }            
LINEKWARGS = {
              SOFT_POWER: {'alpha':0.3,
                     'linestyle':'dotted',
                     'linewidth':3*G_SCALE},
              HARD_POWER: {'alpha':0.2,
                     'linestyle':'-',
                     'linewidth':4*G_SCALE},
              SOFT_THREAT: {'alpha': 0.2,
                     'linestyle':'-',
                     'linewidth':10*G_SCALE},
              HARD_THREAT: {'alpha': 0.3,
                     'linestyle':'-',
                     'linewidth':20*G_SCALE},
              }
SPOT_MARKER  = {'red':'>',
                'black':'<'}
SPOT_MARKERDICT = {'size': 10*G_SCALE,
               'alpha': 1,
               'horizontalalignment':'center',
               'verticalalignment':'center'}
SPT_X_CORR = -0.05
SPT_Y_CORR = -0.05

HPOT_MARKER  = {'red':'=',
                'black':'|'}
HPOT_MARKERDICT = {'size': 10*G_SCALE,
                   'alpha': 1,
                   'horizontalalignment':'center',
                   'verticalalignment':'center'}

## Evaluator Constants

EVAL_CONSTANTS = namedtuple('Eval_Constants','HT_fins ST_fins HP_trigs SP_trigs SPot_trigs boosts HT_defs ST_defs SP_defs HP_defs SPot_blocks')
Ev_sum_Ks = EVAL_CONSTANTS(HT_fins= 1000,
                        ST_fins = 50,
                        HP_trigs = 1,
                        SP_trigs = 1.25,
                        SPot_trigs = 1,
                        boosts = 0.5,
                        HT_defs = 100,
                        ST_defs = 10,
                        SP_defs = 0.75,
                        HP_defs = 0.75,
                        SPot_blocks = 0.01)
                        # Mult_HP_trigs = 25,
                        # Mult_SP_trigs = 5,
                        # EN_mult_SP_trigs = 5,
                        # EN_mult_HP_trigs = 7.5)

# Ev_funcs = EVAL_CONSTANTS(HT_fins = lambda cnt: cnt*Ev_sum_Ks.HT_fins,
#                           ST_fins = lambda cnt: cnt*Ev_sum_Ks.ST_fins,
#                           #HP_SP_trigs =  lambda cnt: cnt*100000,
#                           SPot_trigs = lambda cnt: cnt*Ev_sum_Ks.SPot_trigs,
#                           boosts = lambda cnt: cnt*Ev_sum_Ks.boosts,
#                           HT_defs = lambda cnt: cnt*Ev_sum_Ks.HT_defs,
#                           ST_defs = lambda cnt: cnt*Ev_sum_Ks.ST_defs,
#                           SP_defs = lambda cnt: cnt*Ev_sum_Ks.SP_defs,
#                           HP_defs = lambda cnt: cnt*Ev_sum_Ks.HP_defs,
#                           SPot_blocks= lambda cnt: cnt*Ev_sum_Ks.SPot_blocks)
                          
                          
##Globals
view_index = 0 #index of latest row which is to be displayed.
overlay_toggle = it.cycle([False, True])
overlay = next(overlay_toggle)
victory = False
ai_color = None

def pattern_processing(raw_patterns, player):
    list_ = [] #Empty list to be returned
    for name, pattern in raw_patterns:
        matching_pattern = []
        rel_triggers = []
        rel_markers = []
        rel_defusers = []
        rel_boosters = []
        for index, char in enumerate(pattern):
            rel_loc = index-(len(pattern)-1)
            if char == 'e':
                matching_pattern.append(EMPTY_CHAR)
                #if this is a soft power
                if name[0:2] == 'SP':
                    #Then the empty spots that are not triggers are boosters.
                    rel_boosters.append(rel_loc)
                    # Then the empty spots are also defusers
                    rel_defusers.append(rel_loc)
            elif char == 't':
                matching_pattern.append(EMPTY_CHAR)
                rel_triggers.append(rel_loc)
                if name[0:2] in ['SP','HP']:
                    rel_defusers.append(rel_loc)
            elif char == 'f':
                matching_pattern.append(PLAYER2MARKER[player])
                rel_markers.append(rel_loc)
            elif char == 'd':
                matching_pattern.append(EMPTY_CHAR)
                rel_defusers.append(rel_loc)
            elif char == 'b':
                matching_pattern.append(EMPTY_CHAR)
                rel_boosters.append(rel_loc)
        list_.append(PATTERN_TEMPLATE(name,player, matching_pattern, rel_markers, rel_triggers, rel_defusers, rel_boosters))
    return list_
        
## Constants Requiring Processing
## HPotentail
Red_HPot_Temps = pattern_processing(RAW_Hpots, 'red')
Black_HPot_Temps = pattern_processing(RAW_Hpots, 'black')
HPot_Temps = list(Red_HPot_Temps)
HPot_Temps.extend(Black_HPot_Temps)
## SPotential
Red_SPot_Temps = pattern_processing(RAW_Spots, 'red')
Black_SPot_Temps = pattern_processing(RAW_Spots, 'black')
SPot_Temps = list(Red_SPot_Temps)
SPot_Temps.extend(Black_SPot_Temps)
#print(f"SPot_Temps: {SPot_Temps}")
##Soft Powers
Red_SP_Temps = pattern_processing(RAW_SPs, 'red')
Black_SP_Temps = pattern_processing(RAW_SPs, 'black')
SP_Temps = list(Red_SP_Temps)
SP_Temps.extend(Black_SP_Temps)
#print(SP_Temps)
##Hard Powers
Red_HP_Temps = pattern_processing(RAW_HPs, 'red')
Black_HP_Temps = pattern_processing(RAW_HPs, 'black')
HP_Temps = list(Red_HP_Temps)
HP_Temps.extend(Black_HP_Temps)
##Soft Threats
Red_ST_Temps = pattern_processing(RAW_STs,'red')
Black_ST_Temps = pattern_processing(RAW_STs, 'black')
ST_Temps = list(Red_ST_Temps)
ST_Temps.extend(Black_ST_Temps)
# print(ST_Temps)
##Hard Threats
Red_HT_Temps = pattern_processing(RAW_HTs, 'red')
Black_HT_Temps = pattern_processing(RAW_HTs, 'black')
HT_Temps = list(Red_HT_Temps)
HT_Temps.extend(Black_HT_Temps)
#print(HT_Temps)

class Cell():
    def __init__(self,coords):
        self.coords      = coords
        self.rating      = None
        ## Good for us
        self.HT_finish     = 0
        self.ST_finish     = 0
        self.HP_triggers   = 0
        self.SP_triggers   = 0
        self.SPot_triggers = 0
        self.boosters      = 0
        ## Bad for them
        self.HT_defusers   = 0
        self.ST_defusers   = 0
        self.SP_defusers   = 0
        self.HP_defusers   = 0
        self.EN_SPot_triggers = 0

    def __str__(self):
        return f"""coords      = {self.coords}
    rating      = {self.rating}
    HT_finish     = {self.HT_finish} * {Ev_sum_Ks.HT_fins}
    ST_finish     = {self.ST_finish} * {Ev_sum_Ks.ST_fins}
    HP_triggers   = {self.HP_triggers} * {Ev_sum_Ks.HP_trigs}
    SP_triggers   = {self.SP_triggers} * {Ev_sum_Ks.SP_trigs}
    SPot_triggers = {self.SPot_triggers} * {Ev_sum_Ks.SPot_trigs}
    boosters      = {self.boosters} * {Ev_sum_Ks.boosts}
    HT_defusers   = {self.HT_defusers} * {Ev_sum_Ks.HT_defs}
    ST_defusers   = {self.ST_defusers} * {Ev_sum_Ks.ST_defs}
    SP_defusers   = {self.SP_defusers} * {Ev_sum_Ks.SP_defs}
    HP_defusers   = {self.HP_defusers} * {Ev_sum_Ks.HP_defs}
    EN_SPot_triggers={self.EN_SPot_triggers} * {Ev_sum_Ks.SPot_blocks}"""
        
class RepeatMove(Exception):
    pass

class OutOfBounds(Exception):
    pass

class FIAR():
    '''
    TIC-TAC-TOE Five In A Row game. Contains all functionality for manually playing a game with the right commands.
    '''
    def __init__(self, df=None, first_player = 'black', display='regular', view_index = 'last'):
        '''
        Test documentation for FIAR __init__()
        '''
        assert display in DISPLAYS
        self.display = display
        if type(df)==pd.DataFrame:
            # Calculate next player
            self.next_player = df['player'].iloc[-1]
            self.switch_player()
            # Calculate next_move
            self.next_move = df['marker'].iloc[-1]+1
            self.df = df.copy(deep=True)
            self.PoTs = []
            
        else: #No dataframe provided, a new game.
            assert first_player in PLAYERS
            self.next_player = first_player
            self.next_move = 1
            self.df = DF_TEMP.copy(deep=True)
            self.PoTs = []
        ## Calculate neccessary edge dimensions
        self.disp_edges = self.display_bounds()    
        self.game_edges = self.point_bounds()
        #print(self.game_edges)
        self.update_matrix()
        self.update_PoTs()
        self.update_PoTs_dict()
        # print("Powers Or Threats:")
        # for PoT in self.PoTs:
        #     print(PoT)
    
    def __iter__(self):
        dfs = self.df_states()
        return (FIAR(df=df) for df in dfs)
    
    @staticmethod
    def run():
        '''
        The highest-level run

        Returns
        -------
        None.

        '''
        #print(SP_Temps)
        try:
        #Welcome players to the game
            print("Welcome to Tic-Tac-Toe Five-in-a-Row!")
            ##Ask if playing new or saved game
            mode = FIAR.input_handler(choices=[(['new','new game'],'new'),
                                               (['load','save','load save','load game','cont','continue'],'load'),
                                               (['view'],'view')],
                                      prompt="Would you like to play a 'new' game, 'load' a save, or 'view' a save?\n",
                                      mods=[str.lower, str.strip])
            #If new:
            if mode == 'new':
                FIAR.new_game()
            #If saved:
            elif mode == 'load':
                #Perform selection of a saved game
                game = FIAR.game_selector()
                FIAR.run_game(game)
            elif mode == 'view':
                ##Select a folder
                folder  = FIAR.input_handler(choices =[(['r','records','record','history'],'records'),
                                                       (['s','saves','save'],'saves')],
                                             prompt = "Would you like to view a 'save' game or 'record' game?\n",
                                             mods=[str.lower, str.strip])
                folder = {'saves':SAVE_FOLDER,
                          'records':RECORDS_FOLDER}[folder]
                ## Select a game to view
                game = FIAR.game_selector(folder=folder)
                ## Launch viewer with selected game.
                FIAR.game_viewer(game)                
            print("NotAnError: Out of 'run'way")
        except SystemExit:
            print('System Exit')
            #os._exit(1)

    @staticmethod
    def new_game():
        '''
        Runs a NEW game through a terminal interface

        Returns
        -------
        None.

        '''
        #create the game
        global overlay
        global ai_color
        game = FIAR()
        game.draw_board()
        game.render()        
        ai_game = FIAR.input_handler(choices = [(['comp','computer','1p','ai','one player', 'single player', 'single'],True),
                                                (['two player','2p', 'two_player','versus','vs','player'],False)], 
                                     prompt="Would you like to play 'versus' mode or 'AI' mode?",
                                     mods=[str.lower,str.strip])
        if ai_game: #if we are playing an AI
            print('Welcome to Thunderdome!\n')
            ## Determine colors for player and ai.
            player_color = FIAR.input_handler(choices =[(['black','b'],'black'),
                                                        (['red','r'],'red')],
                                              prompt = "Would you like to play as 'black' or 'red'?")
            ai_color = {'red':'black',
                        'black':'red'}[player_color]
            
        print("New Game:\n")
        ## Receive input of player
        first_player = FIAR.input_handler(choices=[(['b','black'],'black'),
                                                   (['r','red'], 'red')],
                                          prompt= "Is the first player 'black' or 'red'?\n",
                                          failure_prompt="    {} is not an option.",
                                          mods = [str.lower, str.strip])
        game.set_next_player(first_player)
        ## Receive input about whether to show overlay
        user_overlay = FIAR.input_handler(choices = [(YESSES,True),
                                                     (NOS,False)],
                                          prompt= "Would you like the strategic overlay to be turned on during your game?",
                                          mods = [str.lower, str.strip])
        if user_overlay:
            overlay = True
        print("It is recommended to make '0,0' your first move. Special commands include: 'undo', 'quit', 'save'")
        #print(first_player)
        FIAR.game_loop(game)

    @staticmethod
    def game_selector(folder = SAVE_FOLDER):
        saves = FIAR.list_saves(folder)
        chosen_save = FIAR.input_handler(choices=[[saves,'input']], 
                                         prompt = f"The available games are: {saves}\nPlease input a valid game name: ")
        game = FIAR.from_csv(chosen_save, folder=folder)
        return game
    
    @staticmethod
    def run_game(game):
        '''
        Serves the same purpose as run() but takes a game as an input. Lacks setup inputs
        '''
        print('Welcome back!')
        game.draw_board()
        game.draw_markers()
        game.render()
        FIAR.game_loop(game)    
    
    @staticmethod
    def game_loop(game):
        global ai_game
        global victory
        ##Main game loop
        while True:
            #print("Checking Victory Condition")
            if victory:
                #print(f"Victory Detected for {victory}")
                print(f"{victory.capitalize()} wins! Congratulations!")
                victory = False
                #print(f"victory set to: {victory}")
                filename = FIAR.save_name_input()
                if filename: #If the user saved the game after completing
                    game.to_csv(filename, folder=RECORDS_FOLDER)
                    view = FIAR.input_handler(choices=[(['yes','y','yeah','fuck yeah'],'yes'),
                                                       (['no','n','nope'],'no')],
                                              prompt="Would you like to recap this game in the Viewer? (y/n)\n",
                                              mods = [str.lower,str.strip])
                    if view:#If the user wants to open the game in the viewer
                        game = FIAR.from_csv(filename, folder=RECORDS_FOLDER)
                        FIAR.game_viewer(game)
                exit()
            else:## Game is not over
                ## IF this is an ai_game and it is the ai's turn.
                if ai_color == game.next_player:
                    print("AI is making a move...")
                    ## the AI makes a move.
                    coords = FIAR.game_decider(game, FIAR.evaluate_point_sum)
                    game.move(*coords)
                    print("...AI move complete.")
                else: #It is either a regular game or it is the human's turn
                    x = None
                    y = None
        
                    ## Ask for inputs
                    coords = input(f"Enter 'x,y' coordinates for {game.next_player}'s next move: ")
                    #UNDO Special input
                    #print("got here 123")
                    if coords == 'undo':
                        game.undo()
                    ## QUIT special input    
                    elif coords.lower() in ['quit','exit','end']:
                        print(f'The game has been ended by the {game.next_player} player')
                        game.to_csv('autosave')
                        exit()
                    ## SAVE special input
                    elif coords.lower()=='save':
                        filename = FIAR.save_name_input()
                        game.to_csv(filename)
                        print(f"Game saved as '{filename}'")
                        continue_ = FIAR.input_handler(choices = [(YESSES,True),(NOS,False)],
                                                       prompt = "Would you like to continue the game you just saved? (y/n)\n",
                                                       mods=[str.lower,str.strip])
                        if continue_: #==True
                            FIAR.run_game(game)
                        else:
                            exit()
                    ## Regular move input
                    else:
                        try:
                            ## Interpret supplied coordinates as an integer pair
                            x,y = coords.split(',')
                            x = int(x.strip())
                            y = int(y.strip())
                        except: #Provided coords not interpretable as integer pair
                            print("Input for coordinates not recognized as valid.") 
                            continue
                        try:
                            ## Make a move using the supplied integer pair
                            game.move(x,y)
                            game.to_csv('autosave')
                            # print("autosave...complete.")
                        except OutOfBounds:
                            print("The prescribed move is out-of-bounds")
                        except RepeatMove:
                            print("That spot has already been taken")   

   
                            

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
        # Move is in  repeat location
        if self.loc_taken([x,y]):
            raise RepeatMove(f'The location ({x},{y}) has already been taken')
        # Move is beyond the current board.
        if not self.move_allowed((x,y)):
            raise OutOfBounds(f"The location ({x},{y}) is beyond the scope of the board.")
        ## Consequences of Move
        #record the move
        self.record_move(self.next_move, x, y, self.next_player)
        ## Calculate new board dimensions
        self.disp_edges = self.display_bounds()
        self.game_edges = self.point_bounds()
        self.update_matrix()
        self.update_PoTs()
        self.update_PoTs_dict()
        #increment next_move value
        self.next_move +=1
        #switch next_player
        self.switch_player()
        self.display_all()
        #self.render()
    
    @staticmethod
    def game_viewer(game):
        print("---------------------------------------------------------------")
        print("Game Viewer:\n    Use the left-and-right or up-and-down arrow keys to step through the game.\n    Press 'space' to exit or 'enter' to continue play from the current view.\n    Press 'o' to toggle the Power/Threat overlay.")
        #type checking
        assert type(game) == FIAR
        #print(f"game_viewer received a {type(game)}")
        #print(game)
        #displaying the game
        game.display_all()
        #set view_index
        global view_index
        view_index = game.df.shape[0]
        #Listening to keys
        with Listener(on_press = game.view_press) as listener:
            listener.join()
            
    def view_press(self, key):
        global view_index
        global overlay
        if key in [Key.right,Key.up]:
            if view_index< self.df.shape[0]:
                view_index +=1
            ## move forward in time on the current game if possible
                new_game = FIAR(df=self.df.iloc[:view_index,:])
                new_game.display_all()
            else:
                print("This is the latest view of the game.")
            #print("up or right")
        elif key in [Key.left,Key.down]:
            ## move backwards in time on the current game if possible
            if view_index>1:
                view_index-=1
                new_game = FIAR(df= self.df.iloc[:view_index,:])
                new_game.display_all()
            else:
                print("We cannot go any further back in this game.")
            #print("left or down")
        elif key in [Key.space, Key.backspace, Key.esc]:
            print(f"Exiting viewer using: {key}")
            exit()
        elif key == Key.enter:
            # print("Pressing 'enter' again will load this game for play and exit the viewer")
            new_game = FIAR(df= self.df.iloc[:view_index,:])
            FIAR.run_game(new_game)
        elif getattr(key, 'char', None)=='o':
            ## toggle the overlay
            # print('Detected press of "o"')
            overlay = next(overlay_toggle)
            # print(f"Overlay: {overlay}")
            new_game = FIAR(df=self.df.iloc[:view_index,:])
            new_game.display_all()     
        # print(f"key:{key},type:{type(key)}")
        # print(f"str(key): {str(key)}")
            
    @staticmethod
    def save_name_input():
        while True:
            filename = input('Please provide a save name for this game: \n')
            if len(filename.split()) >1:
                print("Please don't use special characters")
            elif filename in FIAR.list_saves():
                ## Check if willing to overwrite existing save
                overwrite = FIAR.input_handler(choices=[(YESSES,True),
                                                     (NOS, False)],
                                            prompt = f"The specified name '{filename}' is already taken. Would you like to overwrite the save? (y/n)\n")
                if overwrite: #==True
                    return filename
                else:
                    #Ask for another name
                    pass
            elif filename.lower() in ['none','no','n']:
                return None
            else:#Save name is okay and not taken
                return filename            
    
    @staticmethod
    def list_saves(folder = SAVE_FOLDER):
        ## Generate list of all .csv's,presumably all valid games.
        files = os.listdir(folder)
        saves = []
        for file in files:
            try:
                name, ext = file.split('.')
                if ext == 'csv':
                    saves.append(name)
            except:
                pass
        return saves
    
    def to_csv(self,filename, folder = SAVE_FOLDER):
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
    

    
    @staticmethod
    def input_handler(choices, prompt, failure_prompt=None, mods = None):
        while True:
            input_ = input(prompt)
            if mods:
                for mod in mods:
                    input_ = mod(input_)
            for check, result in choices:
                # If check is a function
                if type(check) == types.FunctionType:
                    # Check to see if the function returns True
                    if check(input_):
                        # if a special value has been given for the intended return value.
                        if result == "input":
                            return input_
                        # If a normal value has been given for the intended return value
                        else:
                            return result
                    #check function does not return True
                    else:
                        #move on to next check 
                        pass
                #assume check is something iterable, like a list.
                else:
                    #If the user input is in the provided 'list'
                    if input_ in check:
                        # if a special value has been given for the intended return value.
                        if result == "input":
                            return input_
                        # If a normal value has been given for the intended return value
                        else:
                            return result
            if failure_prompt:
                if "{}" in failure_prompt:
                    print(failure_prompt.format(input_))
                else:
                    print(failure_prompt)
    
    def update_PoTs_dict(self):
        PoTs_dict = {
                'red':{SPOT_TEMPLATE:[],
                       HPOT_TEMPLATE:[],
                    SOFT_POWER:[],
                    HARD_POWER:[],
                    SOFT_THREAT:[],
                    HARD_THREAT:[]},
                'black':{SPOT_TEMPLATE:[],
                         HPOT_TEMPLATE:[],
                     SOFT_POWER:[],
                     HARD_POWER:[],
                     SOFT_THREAT:[],
                     HARD_THREAT:[]}
                }
        for PoT in self.PoTs:
            PoTs_dict[PoT.player][type(PoT)].append(PoT)    
        self.PoTs_dict = PoTs_dict
    
    @staticmethod
    def point_evaluater(game, evaluator):
        cell_dict = game.cell_dict_gen()
        def evaluate_point(x,y): 
            cell = cell_dict[(x,y)]
            cell.rating = evaluator(cell)
            print(cell)
        return evaluate_point        
    
    @staticmethod
    def game_decider(game, evaluator):
        '''
        Accepts a FIAR game, applies an evaluator to its cells, and returns a reccomended move

        Parameters
        ----------
        game : FIAR
            A FIAR game.

        Returns
        -------
        location : (x,y) int tuple
            Coordinates of recommended move

        '''
        ## Generate cell_dict
        cell_dict = game.cell_dict_gen()
        # print(f"cell_dict_keys: {cell_dict.keys()}")
        #print(f"original cell_dict: {cell_dict}")
        ## Limit entries in cell dict
            #limited_cell_dict = {key:val for key, val in cell_dict.items() if key in game.playable_points()}
        ## Apply evaluator to cell_dict
        cell_dict = FIAR.evaluate_cell_dict(cell_dict, evaluator)
        #print(f"eval'd, limited cell_dict: {limited_cell_dict}")
        ## Choose cell with maximum value
        
        ## From internet
        cells = cell_dict.values()
        maxRating = max(cells, key = lambda cell: cell.rating).rating
        chosen_cell = None
        if maxRating > Ev_sum_Ks.SPot_blocks:
            max_cells = [cell for cell in cells if cell.rating ==maxRating]
            chosen_cell = random.choice(max_cells)
        elif maxRating ==0:
            chosen_cell = cell_dict[(0,0)]
        else: #0>x>'Ev_sum_Ks.SPot_blocks
            ## find a cell close to previous cell
            print("game_decider: There are no good choices!")
            random_taken = random.choice(game.taken_locs())
            chosen = False
            while chosen == False:
                location = (random_taken[0]+random.randint(-2,2),
                            random_taken[1]+random.randint(-2,2))
                if location not in game.taken_locs():
                    chosen = True
                    chosen_cell = cell_dict[location]
        if PRINT_CELL_CHOICE:
            print(f"chosen_cell: {chosen_cell}")
        
        ## return location of cell with maximum value
        return chosen_cell.coords
    
    @staticmethod
    def eval_HPs_SPs(HP_count, SP_count):
        '''
        Evaluates the point rating that the Soft Power count and Hard Power count contribute to the total cell rating. Considers the importance of special cases where there are multiple of some or each.

        Parameters
        ----------
        HP_count : int
            Number of friendly hard power triggers at this cell location
        SP_count : int
            Number of friendly soft power triggers at this cell location

        Returns
        -------
        HP_rating : float
            Point value attributed to friendly Hard Power triggers
        SP_rating : float
            Point value attributed to friendly Soft Power triggers

        '''
        if HP_count >1:
            HP_rating = 25
            SP_rating = SP_count*Ev_sum_Ks.SP_trigs
        elif HP_count==1 and SP_count >0:
            SP_rating = 12.5
            HP_rating = 12.5
        elif SP_count >1:
            HP_rating = HP_count*Ev_sum_Ks.HP_trigs
            SP_rating = 5
        else:
            HP_rating = HP_count*Ev_sum_Ks.HP_trigs
            SP_rating = SP_count*Ev_sum_Ks.SP_trigs
        return HP_rating, SP_rating
            
    # @staticmethod
    # def evaluate_point_piecewise(cell):
    #     return (Ev_funcs.HT_fins(cell.HT_finish) + 
    #             Ev_funcs.ST_fins(cell.ST_finish) +
    #             Ev_funcs.HP_SP_trigs(cell.HP_triggers, cell.SP_triggers) + 
    #             Ev_funcs.SPot_trigs(cell.SPot_triggers) + 
    #             Ev_funcs.boosts(cell.boosters) + 
    #             Ev_funcs.HT_defs(cell.HT_defusers) +
    #             Ev_funcs.ST_defs(cell.ST_defusers) +
    #             Ev_funcs.SP_defs(cell.SP_defusers) +
    #             Ev_funcs.HP_defs(cell.HP_defusers) + 
    #             Ev_funcs.SPot_blocks(cell.EN_SPot_triggers))
    
    @staticmethod
    def evaluate_point_sum(cell):
        return (cell.HT_finish*Ev_sum_Ks.HT_fins + 
                      cell.ST_finish*Ev_sum_Ks.ST_fins + 
                      cell.HP_triggers*Ev_sum_Ks.HP_trigs + 
                      cell.SP_triggers*Ev_sum_Ks.SP_trigs +
                      cell.SPot_triggers*Ev_sum_Ks.SPot_trigs + 
                      cell.boosters*Ev_sum_Ks.boosts + 
                      cell.HT_defusers*Ev_sum_Ks.HT_defs + 
                      cell.ST_defusers*Ev_sum_Ks.ST_defs + 
                      cell.SP_defusers*Ev_sum_Ks.SP_defs + 
                      cell.HP_defusers*Ev_sum_Ks.HP_defs +
                      cell.EN_SPot_triggers*Ev_sum_Ks.SPot_blocks) 
    
    @staticmethod
    def evaluate_cell_dict(cell_dict, evaluator):
        '''
        Scans every cell in a cell_dict and populates the 'rating' field. 
        
        SideEffects:
        ----------
        cell_dict:
                Adds a value for the 'rating' field
        
        Parameters
        ----------
        cell_dict : {(x,y):Cell}.
            keys are coordinate tuples of positions on board
            Cell objects with populated fields except for 'rating'

        Returns
        -------
        evald_cell_dict : {(x,y):Cell}.
            keys are coordinate tuples of positions on board
            Cell objects with all populated fields, including 'rating'

        '''
        for location, cell in cell_dict.items():
            rating = evaluator(cell)
            if SHOW_Evals:
                print(f"{location} rated as: {rating}")
            cell_dict[location].rating = rating
        return cell_dict                
    
    def draw_board(self):
        '''
        Creates a new figure and axes and draws the board on them.
        figure and axes saved in self.fig and self.ax

        Returns
        -------
        None.

        '''
        plt.rcParams['figure.figsize'] = (self.disp_width*FIGSIZE, self.disp_height*FIGSIZE)
        # print(f"disp_width: {self.disp_width}")
        # print(f"disp_height: {self.disp_height}")
        lEdge = self.disp_edges['left']
        rEdge = self.disp_edges['right']
        tEdge = self.disp_edges['top']
        bEdge = self.disp_edges['bottom']
        #Draws the Board
        self.fig, self.ax = plt.subplots()
        # Control size of figure
        self.ax.set_xlim(lEdge, rEdge)
        self.ax.set_ylim(bEdge, tEdge)
        # print(f"xlims: ({lEdge},{rEdge})")
        # print(f"ylims: ({bEdge},{tEdge})")
        
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
        for x in np.arange(lEdge, rEdge+1):
            # self.ax.axvline(x, color = GRIDCOLOR, linewidth = 1, alpha = 0.5)
            # print(f"drawing vline @ x={x}")
            self.ax.axvline(x, **GRID_DICT)
        for y in np.arange(bEdge,tEdge+1):
            # print(f"drawing hline @ y={y}")
            self.ax.axhline(y, **GRID_DICT)
        
        ## Drawing the grid squares
        for x in np.arange(lEdge, rEdge):
            for y in np.arange(bEdge, tEdge):
                if (np.abs(x+0.5)+np.abs(y+0.5))%2==1:
                    rect = plt.Rectangle((x,y),1,1, **TILE_DICT)
                    self.ax.add_artist(rect)
                    
    ## Draw the grid markers denoting distance
        neg_x_dir = int(abs(self.game_edges['left'])//GRID_MARKER_SPACING)
        pos_x_dir = int(abs(self.game_edges['right'])//GRID_MARKER_SPACING)
        pos_y_dir = int(abs(self.game_edges['top'])//GRID_MARKER_SPACING)
        neg_y_dir = int(abs(self.game_edges['bottom'])//GRID_MARKER_SPACING)
        # print(f"neg_x_dir: {neg_x_dir}")
        # print(f"pos_x_dir: {pos_x_dir}")
        xs = list(range(neg_x_dir,pos_x_dir+GRID_MARKER_SPACING,GRID_MARKER_SPACING))
        ys = list(range(neg_y_dir,pos_y_dir+GRID_MARKER_SPACING, GRID_MARKER_SPACING))
        for x in xs:
            for y in ys:
                self.ax.plot([x-0.05],[y],GRID_MARKER,**GRID_MARKER_KWARGS)
                
        # draw it
    def draw_markers(self):
        '''
        Draws all of the markers present in this game's log.'

        Returns
        -------
        None.

        '''
        for rowi in range(self.num_moves):
            row = self.df.iloc[rowi,:] 
            marker = row.marker
            x = row.x
            y = row.y
            player = row.player
            #display(marker,x,y,player)
            #print(marker,x,y,player)
            self.draw_number(marker,x,y,player)
            
    def draw_number(self, num , x, y, color):
        '''
        Manual method of drawing a number to the figure
        '''
        if len(str(int(num)))==1:
            self.ax.text(x+X1DCOMP,
                         y+Y1DCOMP,
                         str(int(num)),
                         color=color,
                         fontdict=NUM_DICT)
        elif len(str(int(num)))==2:
            self.ax.text(x+X2DCOMP,
                         y+Y2DCOMP,
                         str(int(num)),
                         color=color,
                         fontdict=NUM_DICT)
        else:
            raise Exception("There's been a terrible error")
        plt.close(self.fig)

    def draw_PoTs(self):
        #For each PoT
        for PoT in self.PoTs:
            #print(f"PoTtype: {PoTtype}")
            PoTtype = type(PoT)
            #print(f"PoT: {PoT}")
            color = COLOR_DICT[PoT.player]
            #if PoT is a power:
            if PoTtype in [SOFT_POWER,HARD_POWER]:
                #draw appropriate marker for SP or HP
                for x,y in PoT.trigger_locs:
                    if self.on_figure((x,y)):
                        self.ax.text(x+X1DCOMP,y+Y1DCOMP,T_MARKER[PoTtype], color=color, fontdict = T_MARKERDICT[PoTtype])
                #Calculate line end points
                all_points = list(PoT.trigger_locs)
                all_points.extend(PoT.marker_locs)
                p1,p2 = FIAR.extreme_points(all_points)
                #draw appropriate line for SP or HP
                x1,y1 = p1
                x2,y2 = p2
                self.ax.plot((x1,x2),(y1,y2),color=color, **LINEKWARGS[PoTtype])
            #if PoT is a ST or HT
            elif PoTtype in [SOFT_THREAT, HARD_THREAT]:              
                ## Get all points connecting marker locations
                p1,p2 = FIAR.extreme_points(PoT.marker_locs)
                x1,y1 = p1
                x2,y2 = p2
                #Draw thick lines representing threats
                self.ax.plot((x1,x2),(y1,y2),color=color, **LINEKWARGS[PoTtype])
                ## Draw defuser Locations
                for x,y in PoT.defuser_locs:
                    if self.on_figure((x,y)):
                        self.ax.text(x+X1DCOMP,y+Y1DCOMP,D_MARKER[PoTtype], color=color, fontdict = D_MARKERDICT[PoTtype])
            elif PoTtype == SPOT_TEMPLATE:
                if DRAW_SPOTS:
                    # print("draw_PoTs detected a spot")
                    # print(f"Spot: {PoT}")
                    ## Draw trigger locations for SPots
                    # print(f"PoT.trigger_locs: {PoT.trigger_locs}")
                    # print(f"list(zip(*PoT.trigger_locs)): {list(zip(*PoT.trigger_locs))}")
                    for x, y in PoT.trigger_locs:
                        if self.on_figure((x,y)):
                            self.ax.text(x+SPT_X_CORR,y+SPT_Y_CORR,SPOT_MARKER[color], color = color, fontdict = SPOT_MARKERDICT)
            elif PoTtype == HPOT_TEMPLATE:
                if DRAW_HPOTS:
                    for x,y in PoT.booster_locs:
                        if self.on_figure((x,y)):
                            self.ax.text(x+SPT_X_CORR,y+SPT_Y_CORR,HPOT_MARKER[color], color = color, fontdict = HPOT_MARKERDICT)
                
                
    
    def display_all(self):
        '''
        Helper method which draws the board, the markers, and renders the image.

        Returns
        -------
        None.

        '''
        global overlay
        # Linux
        if sys.platform.startswith('linux'):
            os.system('clear')
        # Windows
        elif sys.platform.startswith('win32'):
            os.system('cls')
        # if self.fig:
        #     plt.close(self.fig)
        self.draw_board()
        self.draw_markers()
        if overlay:
            # print("display_all sees overlay== True")
            self.draw_PoTs()
        else:
            pass
            # print(f"display_all sees overlay== {overlay}")
        self.render()
    
    def render(self):
        '''
        Refreshes the game. Display method depends on 'display' setting.
        '''
        print(f"render. self.display = {self.display}")
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
        print("attempting fig.show()")
        self.fig.show()
        
    def JNshow(self):
        '''
        Jupyter-Notebook-specific display method
        '''
        print("Attempting to display(self.fig)")
        display(self.fig)
        
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
        self.df = self.df.iloc[0:-1,:]
        self.draw_board()
        self.draw_markers()
        self.render()
        self.switch_player()
        self.next_move -=1
        
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
    
    # def d_to_edge(self,edge):
    #     '''calculates the minimum distance from every point to a given edge
    #     '''
    #     ## Redefine variables based on supplied 'edge'
    #     prop_dict = {'right':('x',np.max,self.right_edge-0.5),
    #                  'left':('x',np.min,self.left_edge+0.5),
    #                  'top':('y',np.max,self.top_edge-0.5),
    #                  'bottom':('y',np.min,self.bottom_edge+0.5)}
    #     axis, max_or_min, edge_loc = prop_dict[edge]
    #     #print(axis, max_or_min, edge_loc)
    #     ## Calculate gap
    #     return abs(edge_loc -max_or_min(self.df[axis]))
    
    def point_bounds(self):
        '''
        Finds the furthest distance that markers extend in all 4 directions, and returns a tuple of their integer values. Gives a minimum of 1 for right and top and maximum of -1 for left and bottom

        Returns
        -------
        bounds : dict {str:int}
            tuple of furthest tile to which markers have reach in (right, top, left, bottom) directions. Accesible with str keys, "right", "top", etc

        '''
        top = int(max([*self.df['y'],1], default = 1))
        bottom = int(min([*self.df['y'],-1], default = 1))
        right = int(max([*self.df['x'],1], default = 1))
        left = int(min([*self.df['x'],-1], default = 1))
        return {'right':right,
                'top':top,
                'left':left,
                'bottom':bottom}
    
    def display_bounds(self, padding = MIN_EDGE_GAP):
        '''
        Calculate edges of displayed area. 

        Parameters
        ----------
        padding : int, optional
            The number of empty tiles which should be displayed to each side of the outermost pieces. The default is MIN_EDGE_GAP.

        Returns
        -------
        bounds : dict {str:float}
            Defines the bounds of the figure to be displayed for the (right, top, left, bottom) sides. Accesible with str keys, "right", "top", etc

        '''
        point_bounds = self.point_bounds()
        right = point_bounds['right'] + padding+0.5
        top = point_bounds['top'] + padding+0.5
        left = point_bounds['left'] - padding-0.5
        bottom = point_bounds['bottom'] - padding -0.5
        return {'right':right,
                'top':top,
                'left':left,
                'bottom':bottom}
     
    def on_figure(self, loc):
        '''
        Determines whether a given point fits within the currently-displayed window.

        Parameters
        ----------
        loc : tuple of numbers
            An (x,y) coordinate location

        Returns
        -------
        on_figure : bool
            Whether or not the loc is within the display bounds.

        '''
        x,y = loc
        on_figure = True
        if x>self.disp_edges['right'] or x<self.disp_edges['left']:
            on_figure = False
        if y>self.disp_edges['top'] or y<self.disp_edges['bottom']:
            on_figure = False
        return on_figure
    
    
    def update_matrix(self):
        '''
        Runs through the game's df and generates a matrix of string characters that represent the markers on each tile.

        Returns
        -------
        None.

        '''
        matrix = np.ones((self.height,self.width), dtype=str)
        #print(f"width: {self.width}, height: {self.height}")
        matrix[:,:] = EMPTY_CHAR
        for rowi in range(self.df.shape[0]):
            x,y,player = self.df[['x','y','player']].iloc[rowi,:]
            i,j = self.xy_to_ij((x,y))
            #print(f" x,y: {x,y} to ij: {i,j}")
            matrix[i,j]= PLAYER2MARKER[player]
        self.matrix = matrix
    
    # def check_victory(self, queue):
    #     if queue == RED_VICTORY:
    #         ## END THE GAME
    #         print('Red Wins! Congratulations!')
    #         filename = FIAR.save_name_input()
    #         self.to_csv(filename, folder=RECORDS_FOLDER)
    #         exit()
    #     elif queue == BLACK_VICTORY:
    #         ## END THE GAME
    #         print('Black wins! Congratulations!')
    #         filename = FIAR.save_name_input()
    #         self.to_csv(filename, folder=RECORDS_FOLDER)
    #         exit()    

    def update_PoTs(self):
        global victory
        victory_detected = False
        ## create all queues
        all_queues = self.queues_gen()
        all_PoTs = []
        for scan_queues in all_queues:
            ##Context of a single scanning direction
            for line_queues in scan_queues:
                ## Context of queues generated from the same starting location
                ## Scan this line of queues and return powers/threats
                line_SPs = []
                line_HPs = []
                line_STs = []
                line_HTs = []
                line_Spots = []
                line_Hpots = []
                ## for each type of power and threat
                for queue6, head_loc, tail_dir in line_queues:
                    if SHOW_QUEUES:
                        print(f"queue6: {queue6}, head_loc: {head_loc}, tail_dir: {tail_dir}")
                    ## Context of a single queue.
                    queue5 = list(queue6[1:])
                    ## Scan queue for powers and threats
                    if queue5 == RED_VICTORY:
                        #print("Red victory detected")
                        victory = 'red'
                        victory_detected = True
                    elif queue5 == BLACK_VICTORY:
                        victory = 'black'
                        victory_detected = True
                        #print("Black victory detected")
                    for line_storage, PATTERNS, queue in[[line_SPs, SP_Temps,queue6],
                                                         [line_HPs, HP_Temps, queue5],
                                                         [line_STs, ST_Temps, queue6 ],
                                                         [line_HTs, HT_Temps, queue5],
                                                         [line_Spots, SPot_Temps, queue6],
                                                         [line_Hpots, HPot_Temps, queue5]]:                        
                        for pattern in PATTERNS:
                            ## Context of a single queue being compaed to a single pattern
                            if queue == pattern.match_pat:
                                ## Context of a match having been found.
                                marker_locs = [(int(head_loc[0]-tail_dir[0]*rel_loc),int( head_loc[1]-tail_dir[1]*rel_loc)) for rel_loc in pattern.rel_markers]
                                #print(f"marker_locs: {marker_locs}")
                                trigger_locs = [(int(head_loc[0]-tail_dir[0]*rel_loc), int(head_loc[1]-tail_dir[1]*rel_loc)) for rel_loc in pattern.rel_triggers]
                                defuser_locs = [(int(head_loc[0]-tail_dir[0]*rel_loc), int(head_loc[1]-tail_dir[1]*rel_loc)) for rel_loc in pattern.rel_defusers]
                                booster_locs = [(int(head_loc[0]-tail_dir[0]*rel_loc), int(head_loc[1]-tail_dir[1]*rel_loc)) for rel_loc in pattern.rel_boosters]
                                PoTtype = pattern.name[0:2]
                                #print(f"PoTtype: {PoTtype}")
                                PoT_Template = {'SP':SOFT_POWER,
                                                'HP':HARD_POWER,
                                                'ST':SOFT_THREAT,
                                                'HT':HARD_THREAT,
                                                'Sp':SPOT_TEMPLATE,
                                                'Hp':HPOT_TEMPLATE}[PoTtype]
                                PoT = None
                                if PoTtype == 'SP':
                                    PoT = PoT_Template([pattern.name], pattern.player, marker_locs, trigger_locs, booster_locs, defuser_locs)
                                elif PoTtype == 'Hp':
                                    PoT = PoT_Template([pattern.name], pattern.player, marker_locs, booster_locs)
                                elif PoTtype =='Sp':
                                    PoT = PoT_Template([pattern.name], pattern.player, marker_locs, trigger_locs)
                                elif PoTtype =='HP':
                                    PoT = PoT_Template([pattern.name], pattern.player, marker_locs, trigger_locs, defuser_locs)
                                elif PoTtype in ['ST','HT']:
                                    PoT = PoT_Template([pattern.name], pattern.player, marker_locs, defuser_locs)
                                else:
                                    raise Exception('Shouldnt be here')
                                line_storage.append(PoT)
                                #print(f"Match found: {PoT}")
                ## Collapse nonunique pattern matches within each type of power and threat
                line_SPs = self.collapse_PoTs(line_SPs)
                line_HPs = self.collapse_PoTs(line_HPs)
                line_STs = self.collapse_PoTs(line_STs)
                line_HTs = self.collapse_PoTs(line_HTs)
                line_Spots = self.collapse_PoTs(line_Spots)
                line_Hpots= self.collapse_PoTs(line_Hpots)
                ## compare PoTs heirarchically to eliminate duplicates.
                line_master_PoTs = list(line_HTs)
                line_master_PoTs.extend(self.nonrepeat_PoTs(line_master_PoTs, line_STs))
                line_master_PoTs.extend(self.nonrepeat_PoTs(line_master_PoTs, line_HPs))
                line_master_PoTs.extend(self.nonrepeat_PoTs(line_master_PoTs, line_SPs))  
                line_master_PoTs.extend(self.nonrepeat_PoTs(line_master_PoTs, line_Hpots))                
                line_master_PoTs.extend(self.nonrepeat_PoTs(line_master_PoTs, line_Spots))
                all_PoTs.extend(line_master_PoTs)
        self.PoTs = all_PoTs
        if SHOW_PoTs:
            print("Powers Or Threats:")
            for PoT in self.PoTs:
                if type(PoT) not in [SPOT_TEMPLATE,HPOT_TEMPLATE]:
                    print(PoT)
        if SHOW_SPots:
            print("SPots:")
            for PoT in self.PoTs:
                if type(PoT) == SPOT_TEMPLATE:
                    print(PoT)
        if SHOW_HPots:
            print("HPots:")
            for PoT in self.PoTs:
                if type(PoT) == HPOT_TEMPLATE:
                    print(PoT)
        
        if not victory_detected:
            victory = False
            
    def nonrepeat_PoTs(self,master_list, list_):
        '''
        returns a list of PoTs in list_ whose marker locations are not contained by any one PoT in master_list 

        Parameters
        ----------
        master_list : list of PoTs
            list of
        added_list : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        unique_PoTs = []
        for PoT in list_:
            match_none = True #Assume that current PoT is unique
            for master_PoT in master_list:
                match = True #Assume that current master PoT is a match
                ## Check if PoT marker locations are a subset of master_PoT's marker locations.
                for loc in PoT.marker_locs:
                    if loc not in master_PoT.marker_locs:
                        match = False
                if match:
                    match_none = False
                    #print(f"PoT eliminated for non-uniqueness: {PoT}. Matched {master_PoT}")
            if match_none:
                unique_PoTs.append(PoT)
                #print(f"PoT found to be unique: {PoT}")
        return unique_PoTs
    
    def collapse_PoTs(self,line_PoTs):
        '''Takes a list of Powers or Threats (PoTs) and returns a list of "collapsed" ones, where any PoTs with matching marker locations are combined'''
        collapsed_PoTs = [] #list of PoTs with unique marker locations.
        for PoT in line_PoTs:
            match_none = True #Assume that current match has no collapsed matches with the same marker locations.
            ## Check if the PoT matches any collapsed ones
            for col_PoT in collapsed_PoTs:
                match = True #assume that the PoT and col_PoT match each other
                for loc in col_PoT.marker_locs:
                    if loc not in PoT.marker_locs:
                        match = False
                if match: #If marker locations are shared
                    match_none = False
                    ##Combine all triggers. Perform an OR on the sets.
                    for trigger_loc in getattr(PoT,'trigger_locs',[]):
                        if trigger_loc not in getattr(col_PoT,'trigger_locs', []):
                            col_PoT.trigger_locs.append(trigger_loc)
                    ## Combine all boosters. Perform an OR on the sets.
                    for booster_loc in getattr(PoT,'booster_locs',[]):
                        if booster_loc not in getattr(col_PoT,'booster_locs', []):
                            col_PoT.booster_locs.append(booster_loc)
                    ## Find defusers in common. Perform an AND on the sets.
                    defuser_locs = []
                    for defuser_loc in getattr(col_PoT,'defuser_locs',[]):
                        if defuser_loc in getattr(PoT, 'defuser_locs',[]):
                            defuser_locs.append(defuser_loc)
                    if defuser_locs:
                        # Empty list
                        for _ in range(len(col_PoT.defuser_locs)):
                            col_PoT.defuser_locs.pop()
                        # Extend list with new contents
                        col_PoT.defuser_locs.extend(defuser_locs)
                    col_PoT.names.extend(PoT.names)
            if match_none: #This is a unique PoT
                collapsed_PoTs.append(PoT)
        return collapsed_PoTs
 
    def queues_gen(self, length=6):
        '''
        Returns a list of all queues of interest, along with their head location, and tail direction. Linearly scans through the matrix attribute of a FIAR game and generates the queues of length 'queue_length' along the downward, right-ward, down-and-to-the-left, and down-and-to-the-right directions.

        Returns
        -------
        3-tuple of (queue,head_location, tail_direction)
            - queue (list of individual string characters: Each character represents the content of a scanned position in the
            - head_location (2-tuple of ints): The location of the head of the queue in the x,y convention pertaining to the game coordinates, not matrix coordinates..
            - tail_direction (2-tuple of ints): The unit vector describing the direction from which the queue is coming from in (x,y) notation.        

'''
        # Define the scans done in all directions
        scan_inputs = [
                 [np.array([1,0]),['top']],
                 [np.array([1,1]),['left','top']],
                 [np.array([0,1]),['left']],
                 [np.array([1,-1]),['right','top']]
                 ]
        all_queues = []
        for dir_, start_sides in scan_inputs:
            # Convert tail_dir to xy, because it is yielded
            tail_dir = self.rot_ij_to_xy(-dir_)
            #print(f"head_dir,ij: {dir_}, tail_dir,xy: {tail_dir}")
            scan_queues = [] #queues all with the same scanning direction.
            for starting_loc in self.merged_edge_coords(start_sides):
                #print(f"starting_loc: {starting_loc}")
                line_queues = [] #queues all with the same starting location   
                starting_loc = np.array(starting_loc)
                num_steps = self.num_steps(starting_loc,dir_)
                queue6 =[EMPTY_CHAR]*length
                for n in range(num_steps):
                    i,j = starting_loc + dir_*n
                    queue6.pop(0)
                    # If indexing into negative position
                    if i<0 or j<0:
                        queue6.append(EMPTY_CHAR)
                    # If indexing into normal, positive position
                    else:
                        try:    
                            queue6.append(self.matrix[i,j])
                        except IndexError: #In case index is out of bounds.
                            queue6.append(EMPTY_CHAR)
                    x,y= self.ij_to_xy((i,j))
                    # if (x,y) == (-6,-3):
                    #     print(f"Head_loc (i:{i},j:{j})->(x:{x},y:{y})") 
                    #     print(f"starting_loc")
                    #     print("----------------------------------------")
                    head_loc = (x,y)
                    #print(f"queue6: {queue6}")
                    line_queues.append([list(queue6), head_loc, tail_dir])
                scan_queues.append(list(line_queues))
            all_queues.append(list(scan_queues))
        return all_queues
    
   
    
    def num_steps(self, start_loc, dir_):
        """
        Calculates the number of queues that must be generated if starting at start_loc and moving in dir.

        Parameters
        ----------
        start_loc : tuple of ints
            i,j coordinates describing starting location for scan.
        dir_ : tuple of ints
            i,j coordinates defining unit vector along which queue will advance.

        Returns
        -------
        Num_steps: The total number of queues that will be generated as a result of moving from the start_loc in direction dir_.

        """
        step_limits = {}
        ## Iterate once for i-direction and once for j-direction
        for max_dim, axis, loc, u_vec in zip((self.height, self.width),
                                             ('i','j'),
                                             start_loc, 
                                             dir_):
            if u_vec == 1:
                step_limits[axis] = max_dim-loc
            elif u_vec == -1:
                step_limits[axis] = loc+1
            elif u_vec == 0:
                step_limits[axis] = math.inf
        return min(step_limits.values())+4
                

        
    
    def edge_coords(self,side):
        '''
        Generates a list of coordinates for the points along an edge of a matrix.

        Returns
        -------
        coords : list of int pairs.
            Define the centers of the tiles which make up the edge of a matrix. Uses i,j notation

        '''
        assert side in ['right','left','top','bottom']
        ## 
        vert_list = list(range(0,self.height))
        horz_list = list(range(0,self.width))
        if side=='left':
            i = list(vert_list)
            j = [0]*self.height
        elif side=='right':
            i = list(vert_list)
            j = [self.width-1]*self.height
        elif side == 'top':
            i = [0]*self.width
            j = list(horz_list)
        elif side == 'bottom':
            i = [self.height-1]*self.width
            j = list(horz_list)
        #return coords
        return list(zip(i,j))   

    def merged_edge_coords(self, edges):
        '''
        Generates a set of coordinates of locations along the edge of the game's matrix.

        Parameters
        ----------
        edges : list of strings
            Each element describes a direction whos points are to be combined (EX: 'top','bottom','right','left')

        Returns
        -------
        locs
            set of ij coordinate pairs describing locations along the outside of the game's matrix.

        '''
        locs = []
        for edge in edges:
            locs.extend(self.edge_coords(edge))
        return set(locs)       

    def cell_dict_gen(self):
        cell_dict = {}
        for loc in self.playable_locs():
            cell_dict[loc] = Cell(loc)
        friend = self.next_player
        enemy = self.previous_player
        for PoT in self.PoTs:
            ptype = type(PoT)
            if PoT.player == friend:
                if ptype == HARD_THREAT:
                    ## add hard threat defusers to the Cell at the proper location.
                    for def_loc in PoT.defuser_locs:
                        cell_dict[def_loc].HT_finish+=1
                elif ptype == SOFT_THREAT:
                    ## Add hard threat defusers
                    for def_loc in PoT.defuser_locs:
                        cell_dict[def_loc].ST_finish +=1
                elif ptype == HARD_POWER:
                    ## Add hard power triggers
                    for trig_loc in PoT.trigger_locs:
                        cell_dict[trig_loc].HP_triggers +=1
                elif ptype == SOFT_POWER:
                    ## Add soft power triggers
                    for trig_loc in PoT.trigger_locs:
                        cell_dict[trig_loc].SP_triggers +=1
                    for bstr_loc in PoT.booster_locs:
                        cell_dict[bstr_loc].boosters +=1
                elif ptype == SPOT_TEMPLATE:
                    ## Add SPot triggers
                    for trig_loc in PoT.trigger_locs:
                        cell_dict[trig_loc].SPot_triggers +=1
                elif ptype == HPOT_TEMPLATE:
                    ## Add HPot template
                    for bstr_loc in PoT.booster_locs:
                        cell_dict[bstr_loc].boosters +=1
            elif PoT.player == enemy:
                if ptype == HARD_THREAT:
                    ## add hard threat defusers
                    for def_loc in PoT.defuser_locs:
                        cell_dict[def_loc].HT_defusers += 1
                elif ptype == SOFT_THREAT:
                    ## add soft threat defusers
                    for def_loc in PoT.defuser_locs:
                        cell_dict[def_loc].ST_defusers += 1
                elif ptype == SOFT_POWER:
                    ## add soft power defusers
                    for def_loc in PoT.defuser_locs:
                        cell_dict[def_loc].SP_defusers += 1
                elif ptype == HARD_POWER:
                    ## add hard power defusers
                    for def_loc in PoT.defuser_locs:
                        cell_dict[def_loc].HP_defusers += 1
                elif ptype == SPOT_TEMPLATE:
                    ## Add SPot triggers
                    for trig_loc in PoT.trigger_locs:
                        cell_dict[trig_loc].EN_SPot_triggers +=1
            else:
                raise Exception(f"'{PoT.player}' is not supposed to be an option.")
        # print(f"cell_dict: {cell_dict}")
        # print(f"playable_points: {self.playable_points()}")
        # limited_cell_dict = {key:val for key, val in cell_dict.items() if key in self.playable_points()}
        return cell_dict

    def board_locs(self):
        '''
        Returns a list of all locations on the board

        Returns
        -------
        points : list of (x,y) int tuples.
            Every point on the board, occupied or otherwise.

        '''    
        bounds = self.point_bounds()
        return [(int(x),int(y)) for x in np.arange(bounds['left'],bounds['right']+1) for y in np.arange(bounds['bottom'],bounds['top']+1)]
    
    def playable_locs(self, scan_reach = int(4)):
        '''
        returns a list of empty points within scan_reach of previously-played points

        Returns
        -------
        points: list of (x,y) int tuples.
            Empty points within scan_reach of previous points

        '''
        points = []
        for x in range(self.game_edges['left']-scan_reach, self.game_edges['right']+scan_reach+1):
            for y in range(self.game_edges['bottom']-scan_reach,self.game_edges['top']+scan_reach+1):
                points.append((int(x),int(y)))
        return points
        
    
    def empty_locs(self):
        '''
        Returns a list of all empty spaces on the board.

        Returns
        -------
        empty_locs : list of (x,y) int tuples
            Every point on the board that is unoccupied.

        '''
        all_points = self.board_locs()
        taken_points = self.taken_locs()
        empty_locs = []
        for point in all_points:
            if point not in taken_points:
                empty_locs.append(point)
        return empty_locs

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
    
    def move_allowed(self, coords):
        '''
        Checks whether the move in (x,y) cordinates is allowed.

        Parameters
        ----------
        coords : int tuple
            (x,y) location of proposed move

        Returns
        -------
        allowed : bool
            True or False of whether move is acceptable

        '''
        x,y = coords
        allowed_move_bound = {key:value+MAX_MOVE_REACH*value/abs(value) for key, value in self.point_bounds().items()}
        allowed = not bool(x>allowed_move_bound['right'] or x<allowed_move_bound['left'] or y>allowed_move_bound['top'] or y<allowed_move_bound['left'])
        return allowed
    
    @staticmethod
    def extreme_points(points):
        '''
        Finds the end points in a line of points

        Parameters
        ----------
        points : list of (x,y) tuples.
            Points on a common line

        Returns
        -------
        extremes : tuple of (x,y) tuples
            The points on the ends of the lien shared by the 'points'

        '''
        inspect_x = lambda point: point[0]
        inspect_y = lambda point: point[1]
        min_x = min(points,key=inspect_x)
        max_x = max(points,key=inspect_x)
        if not max_x[0] == min_x[0]:
            return (min_x, max_x)
        else: #Must be vertically aligned.
            min_y = min(points, key=inspect_y)
            max_y = max(points, key=inspect_y)
            return (min_y, max_y)
    
    @staticmethod
    def fill_line(points):
        '''
        Finds any points along a line of points that are between the two extremes and missing.
        Returns a complete tuple of points.

        Parameters
        ----------
        points : list of (x,y) tuples.
            Points on a common line

        Returns
        -------
        filled_points : tuple of (x,y) tuples
            The points making up the body of the line between the two extremes

        '''
        ## Calculate the end points
        p1,p2 = np.array(FIAR.extreme_points(points))
        x1,y1 = p1
        x2,y2 = p2
        ## Calculate the directional vector from one extreme point to another
        vector = p2-p1
        dir_vect = vector/abs(vector)
        dir_vect = dir_vect.astype(int)
        ## Generate all the points from one extreme point to another stepping along the unit vector
        n_points = max(abs(y2-y1),abs(x2-x1))+1
        return tuple([tuple(p1+dir_vect*n) for n in range(n_points)])
    
    @property
    def width(self):
        return int(self.game_edges['right'] - self.game_edges['left']+1)
    
    @property
    def height(self):
        return int(self.game_edges['top'] - self.game_edges['bottom']+1)
    
    @property
    def disp_height(self):
        return int(self.disp_edges['top']-self.disp_edges['bottom'])
    
    @property
    def disp_width(self):
        return int(self.disp_edges['right'] - self.disp_edges['left'])
    
    def xy_to_ij(self, xy):
        '''
        Transforms a coordinate pair from the game coordinate system to the matrix coordinate system
        '''
        x,y = xy
        return int(self.game_edges['top']-y), int(x-self.game_edges['left'])
    
    def ij_to_xy(self, ij):
        '''
        Transforms a coordinate pair from the matrix coordinate system to the game coordinate system.
        '''
        i,j = ij
        return j+self.game_edges['left'], self.game_edges['top']-i

    def rot_ij_to_xy(self,ij):
        '''
        rotates a unit vector in ij coords into xy coords

        Parameters
        ----------
        ij : array
            Describes unit vector in ij coords

        Returns
        -------
        xy : array
            Describes unit vector in xy coords

        '''
        return np.dot(IJ_TO_XY_R, ij)
    
    def rot_xy_to_ij(self, xy):
        '''
        Rotates a unit vector from xy to ij space

        Parameters
        ----------
        xy : array
            Describes unit vector in xy space

        Returns
        -------
        ij : array
            Describes unit vector in ij space

        '''
        return np.dot(XY_TO_IJ_R, xy)

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