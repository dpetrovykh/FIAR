#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 12:26:54 2021

@author: dpetrovykh
"""

import matplotlib.pyplot as plt
plt.ioff()
import numpy as np
import pandas as pd
from IPython.display import display
from sys import exit
import os
from pynput.keyboard import Listener, Key
import types
from collections import namedtuple
import itertools as it
import math

DEBUGGING = True

GRIDCOLOR = 'black'
GRID_MARKER_SPACING = int(3)
FIGSIZE = 0.5
TILE_ALPHA = 0.6
TILE_COLOR = 'yellow'
X1DCOMP = -0.2
Y1DCOMP = -0.2
X2DCOMP = -0.35
Y2DCOMP = -0.2
TEXTSIZE = 14
PLAYERS = ['black','red']
DISPLAYS = ['other','Jupyter']
DF_TEMP = pd.DataFrame({'marker':[],
                           'x':[],
                           'y':[],
                           'player':[]})
MIN_EDGE_GAP = 3
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
                SOFT_THREAT: {'size':15,
                              'alpha':0.3},
                HARD_THREAT: {'size':20,
                              'alpha':0.5}
                }
T_MARKER = {SOFT_POWER:'o',
            HARD_POWER:'*'}
T_MARKERDICT = {
                SOFT_POWER: {'size':17,
                       'alpha':0.3},
                HARD_POWER: {'size':16,
                       'alpha':0.5,}
                }            
LINEKWARGS = {
              SOFT_POWER: {'alpha':0.3,
                     'linestyle':'dotted',
                     'linewidth':3},
              HARD_POWER: {'alpha':0.2,
                     'linestyle':'-',
                     'linewidth':4},
              SOFT_THREAT: {'alpha': 0.2,
                     'linestyle':'-',
                     'linewidth':10},
              HARD_THREAT: {'alpha': 0.3,
                     'linestyle':'-',
                     'linewidth':20},
              }
SPOT_MARKER  = {'red':'>',
                'black':'<'}
SPOT_MARKERDICT = {'size': 10,
               'alpha': 1}
SPT_X_CORR = -0.05
SPT_Y_CORR = -0.05

HPOT_MARKER  = {'red':'=',
                'black':'|'}
HPOT_MARKERDICT = {'size': 10,
               'alpha': 1}

## Evaluator Constants

EVAL_CONSTANTS = namedtuple('Eval_Constants','HT_fins ST_fins HP_trigs SP_trigs SPot_trigs boosts HT_defs ST_defs SP_defs HP_defs')
EvKs = EVAL_CONSTANTS(HT_fins= 1000,
                                ST_fins = 50,
                                HP_trigs = 0.1,
                                SP_trigs = 1,
                                SPot_trigs = 1,
                                boosts = 1,
                                HT_defs = 100,
                                ST_defs = 10,
                                SP_defs = 0.5,
                                HP_defs = 0.5)

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

    def __str__(self):
        return f"coords      = {self.coords}\nrating      = {self.rating}\nHT_finish     = {self.HT_finish}\nST_finish     = {self.ST_finish}\nHP_triggers   = {self.HP_triggers}\nSP_triggers   = {self.SP_triggers}\nSPot_triggers = {self.SPot_triggers}\nboosters      = {self.boosters}\nHT_defusers   = {self.HT_defusers}\nST_defusers   = {self.ST_defusers}\nSP_defusers   = {self.SP_defusers}\nHP_defusers   = {self.HP_defusers}"
        
class RepeatMove(Exception):
    pass

class OutOfBounds(Exception):
    pass

class FIAR():
    '''
    Documentation for FIAR class
    '''
    def __init__(self, size=5, df=None, first_player = 'black', display='Jupyter', view_index = 'last'):
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
            self.PoTs = []
            
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
            self.PoTs = []
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
        game = FIAR(size=1)
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
                print(f"victory set to: {victory}")
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
                    coords = FIAR.game_decider(game, FIAR.evaluator_sum)
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
        self.update_PoTs()
        self.update_PoTs_dict()
        # print("Powers Or Threats:")
        # for PoT in self.PoTs:
        #     print(PoT)
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
        #print(f"original cell_dict: {cell_dict}")
        ## Limit entries in cell dict
        limited_cell_dict = {key:val for key, val in cell_dict.items() if key in game.playable_points()}
        ## Apply evaluator to cell_dict
        limited_cell_dict = evaluator(limited_cell_dict)
        #print(f"eval'd, limited cell_dict: {limited_cell_dict}")
        ## Choose cell with maximum value
        max_cell = max(limited_cell_dict.values(), key = lambda cell: cell.rating)
        print(f"max cell: {max_cell}")
        ## return location of cell with maximum value
        return max_cell.coords
    
    @staticmethod
    def evaluator_sum(cell_dict):
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
            rating = (cell.HT_finish*EvKs.HT_fins + 
                      cell.ST_finish*EvKs.ST_fins + 
                      cell.HP_triggers*EvKs.HP_trigs + 
                      cell.SP_triggers*EvKs.SP_trigs +
                      cell.SPot_triggers*EvKs.SPot_trigs + 
                      cell.boosters*EvKs.boosts + 
                      cell.HT_defusers*EvKs.HT_defs + 
                      cell.ST_defusers*EvKs.ST_defs + 
                      cell.SP_defusers*EvKs.SP_defs + 
                      cell.HP_defusers*EvKs.HP_defs) 
            print(f"{location} rated as: {rating}")
            cell_dict[location].rating = rating
        return cell_dict
            
    def playable_points(self):
        '''
        Returns a list of points which the next player's moves are tactically limited to. The default is to return the entire play area, but this is shrunk by enemy threats.
        
        Returns
        -------
        points : list of x,y coordinate tuples
            Move locations that don't guarantee a loss if possible.'

        '''
        enemy = self.previous_player
        # If there are hard threats against the next player
        if self.PoTs_dict[enemy][HARD_THREAT]:
            ## The only valid move locations are defusers of hard threats.
            points = []
            for HT in self.PoTs_dict[enemy][HARD_THREAT]:
                points.extend(HT.defuser_locs)
            return [(int(x),int(y)) for x,y in set(points)]
        # elif there are soft threats against the next player
        elif self.PoTs_dict[enemy][SOFT_THREAT]:
            # The only valid move locations are defusers of soft threats or triggers of hard powers.
            points = []
            for ST in self.PoTs_dict[enemy][SOFT_THREAT]:
                points.extend(ST.defuser_locs)
            for HP in self.PoTs_dict[self.next_player][HARD_POWER]:
                points.extend(HP.trigger_locs)
            return [(int(x),int(y)) for x,y in set(points)]
        # Else if there are no threats against the current player
        else:
            return self.empty_locs()
                
    
    def draw_board(self):
        '''
        Creates a new figure and axes and draws the board on them.
        figure and axes saved in self.fig and self.ax

        Returns
        -------
        None.

        '''
        plt.rcParams['figure.figsize'] = (self.width*FIGSIZE, self.height*FIGSIZE)
        #Draws the Board
        self.fig, self.ax = plt.subplots()
        # Control size of figure
        self.ax.set_xlim(self.left_edge, self.right_edge)
        self.ax.set_ylim(self.bottom_edge, self.top_edge)
        # set aspect ration to maintain square grid
        #aspect_ratio = (self.right_edge-self.left_edge-1)/(self.top_edge-self.bottom_edge-1)
        #self.ax.set_aspect(aspect_ratio)
        #self.ax.set_aspect(1)
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
                    rect = plt.Rectangle((x,y),1,1, alpha=TILE_ALPHA, color = TILE_COLOR)
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
        plt.close(self.fig)

    def draw_PoTs(self):
        #For each PoT
        for PoT in self.PoTs:
            #print(f"PoTtype: {PoTtype}")
            PoTtype = type(PoT)
            print(f"PoT: {PoT}")
            color = COLOR_DICT[PoT.player]
            #if PoT is a power:
            if PoTtype in [SOFT_POWER,HARD_POWER]:
                #draw appropriate marker for SP or HP
                for x,y in PoT.trigger_locs:
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
                    self.ax.text(x+X1DCOMP,y+Y1DCOMP,D_MARKER[PoTtype], color=color, fontdict = D_MARKERDICT[PoTtype])
            elif PoTtype == SPOT_TEMPLATE:
                if DEBUGGING:
                    # print("draw_PoTs detected a spot")
                    # print(f"Spot: {PoT}")
                    ## Draw trigger locations for SPots
                    # print(f"PoT.trigger_locs: {PoT.trigger_locs}")
                    # print(f"list(zip(*PoT.trigger_locs)): {list(zip(*PoT.trigger_locs))}")
                    for x, y in PoT.trigger_locs:
                        self.ax.text(x+SPT_X_CORR,y+SPT_Y_CORR,SPOT_MARKER[color], color = color, fontdict = SPOT_MARKERDICT)
            elif PoTtype == HPOT_TEMPLATE:
                if DEBUGGING:
                    for x,y in PoT.booster_locs:
                        self.ax.text(x+SPT_X_CORR,y+SPT_Y_CORR,HPOT_MARKER[color], color = color, fontdict = HPOT_MARKERDICT)
                
                
    
    def display_all(self):
        '''
        Helper method which draws the board, the markers, and renders the image.

        Returns
        -------
        None.

        '''
        global overlay
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
        '''
        Runs through the game's df and generates a matrix of string characters that represent the markers on each tile.

        Returns
        -------
        None.

        '''
        matrix = np.ones((self.height,self.width), dtype=str)
        matrix[:,:] = EMPTY_CHAR
        for rowi in range(self.df.shape[0]):
            x,y,player = self.df[['x','y','player']].iloc[rowi,:]
            i,j = self.xy_to_ij((x,y))
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
                    #print(f"queue6: {queue6}, head_loc: {head_loc}, tail_dir: {tail_dir}")
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
                                marker_locs = [(head_loc[0]-tail_dir[0]*rel_loc, head_loc[1]-tail_dir[1]*rel_loc) for rel_loc in pattern.rel_markers]
                                #print(f"marker_locs: {marker_locs}")
                                trigger_locs = [(head_loc[0]-tail_dir[0]*rel_loc, head_loc[1]-tail_dir[1]*rel_loc) for rel_loc in pattern.rel_triggers]
                                defuser_locs = [(head_loc[0]-tail_dir[0]*rel_loc, head_loc[1]-tail_dir[1]*rel_loc) for rel_loc in pattern.rel_defusers]
                                booster_locs = [(head_loc[0]-tail_dir[0]*rel_loc, head_loc[1]-tail_dir[1]*rel_loc) for rel_loc in pattern.rel_boosters]
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
        # if DEBUGGING:
        #     print("Powers Or Threats:")
        #     for PoT in self.PoTs:
        #         if type(PoT) != SPOT_TEMPLATE:
        #             print(PoT)
        #     print("Spots:")
        #     for PoT in self.PoTs:
        #         if type(PoT) == SPOT_TEMPLATE:
        #             print(PoT)
        
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
                queue6 =['']*length
                for n in range(num_steps):
                    i,j = starting_loc + dir_*n
                    queue6.pop(0)
                    queue6.append(self.matrix[i,j])
                    x,y= self.ij_to_xy((i,j))
                    #print(f"Head_loc (i:{i},j:{j})->(x:{x},y:{y})")
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
        return min(step_limits.values())
                

        
    
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
        for loc in self.empty_locs():
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
        points = []
        for x in np.arange(self.left_edge+0.5, self.right_edge+0.5):
            for y in np.arange(self.bottom_edge+0.5, self.top_edge+0.5):
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
    # def scan_through_matrix(self):
    #     ## Vertical Scanning
    #     #print('Vertical Scanning')
    #     self.SPs = []
    #     self.HPs = []
    #     self.STs = []
    #     self.HTs = []
    #     ## CHECKING FOR THREATS
    #     for j in range(self.width):
    #         queue5 = ['_']*5
    #         queue6 = ['_']*6
    #         for i in range(self.height):
    #             ##Update both queues
    #             queue5.pop(0)
    #             queue5.append(self.matrix[i,j])
    #             queue6.pop(0)
    #             queue6.append(self.matrix[i,j])
    #             # print(queue5)
    #             self.check_victory(queue5)
    #             print(queue6)
    #             print(f"Head Loc: {self.ij_to_xy((i,j))}")
    #             #self.check_SP(queue6,np.array(self.ij_to_xy((i,j))), (0,1))
    #     ## Horizontal Scanning
    #     # print('Horizontal Scanning')
    #     for i in range(self.height):
    #         queue5 = ['_']*5
    #         queue6 = ['_']*6
    #         for j in range(self.width):
    #             ##Update both queues
    #             queue5.pop(0)
    #             queue5.append(self.matrix[i,j])
    #             queue6.pop(0)
    #             queue6.append(self.matrix[i,j])
    #             # print(queue5)
    #             self.check_victory(queue5)
    #             print(queue6)
    #             print(f"Head Loc: {self.ij_to_xy((i,j))}")
    #             #self.check_SP(queue6,np.array(self.ij_to_xy((i,j))), (-1,0))     
    #     ##Negative-slope Diagonal Scanning
    #     #Generate list of starting points
    #     # print('Down-Right Scanning')
    #     left_side_points = zip(list(range(self.height-1,0,-1)),[0]*self.height) 
    #     top_side_points = zip([0]*self.width,list(range(0,self.width)))
    #     start_points = list(left_side_points)
    #     start_points.extend(top_side_points)
    #     for i_0,j_0 in start_points:
    #         queue5 = ['_']*5
    #         queue6 = ['_']*6
    #         N = min(self.height-i_0, self.width-j_0)
    #         # print(f'N = {N}')
    #         for n in range(N):
    #             ##Update both queues
    #             i = i_0+n
    #             j = j_0+n
    #             queue5.pop(0)
    #             queue5.append(self.matrix[i, j])
    #             queue6.pop(0)
    #             queue6.append(self.matrix[i, j])
    #             # print(queue5)
    #             self.check_victory(queue5)
    #             print(queue6)
    #             print(f"Head Loc: {self.ij_to_xy((i,j))}")
    #             #self.check_SP(queue6,np.array(self.ij_to_xy((i,j))), (-1,1))     
    #     ##Positive-sloped Diagonal Scanning
    #     #Generate list of starting points
    #     # print('Down-Left Scanning')
    #     right_points = zip(list(range(self.height-1,0,-1)),[self.width-1]*self.height)
    #     top_points = zip([0]*self.width,list(range(self.width-1,-1,-1)))
    #     start_points = list(right_points) #copy the list
    #     start_points.extend(top_points)
    #     for i_0,j_0 in start_points:
    #         queue5 = ['_']*5
    #         queue6 = ['_']*6
    #         N = min(self.height-i_0, j_0+1)
    #         # print(f'N = {N}')
    #         for n in range(N):
    #             i = i_0+n
    #             j = j_0-n
    #             queue5.pop(0)
    #             queue5.append(self.matrix[i, j])
    #             queue6.pop(0)
    #             queue6.append(self.matrix[i, j])
    #             # print(queue5)
    #             self.check_victory(queue5)
    #             print(queue6)
    #             print(f"Head Loc: {self.ij_to_xy((i,j))}")
    #             #self.check_SP(queue6,np.array(self.ij_to_xy((i,j))), (1,1))  
                
                
    #     ## CHECKING FOR POWERS
    #     for j in range(self.width):
    #         queue5 = ['_']*5
    #         queue6 = ['_']*6
    #         for i in range(self.height):
    #             ##Update both queues
    #             queue5.pop(0)
    #             queue5.append(self.matrix[i,j])
    #             queue6.pop(0)
    #             queue6.append(self.matrix[i,j])
    #             # print(queue5)
    #             print(queue6)
    #             head_loc = np.array(self.ij_to_xy((i,j)))
    #             print(f"Head Loc: {head_loc}")
    #             self.check_SP(queue6,head_loc, (0,1))
    #             self.check_HP(queue5,head_loc, (0,1))   
    #     ## Horizontal Scanning
    #     # print('Horizontal Scanning')
    #     for i in range(self.height):
    #         queue5 = ['_']*5
    #         queue6 = ['_']*6
    #         for j in range(self.width):
    #             ##Update both queues
    #             queue5.pop(0)
    #             queue5.append(self.matrix[i,j])
    #             queue6.pop(0)
    #             queue6.append(self.matrix[i,j])
    #             # print(queue5)
    #             print(queue6)
    #             head_loc = np.array(self.ij_to_xy((i,j)))
    #             print(f"Head Loc: {head_loc}")
    #             self.check_SP(queue6,head_loc, (-1,0))     
    #             self.check_HP(queue5,head_loc, (-1,0))     
    #     ##Negative-slope Diagonal Scanning
    #     #Generate list of starting points
    #     # print('Down-Right Scanning')
    #     left_side_points = zip(list(range(self.height-1,0,-1)),[0]*self.height) 
    #     top_side_points = zip([0]*self.width,list(range(0,self.width)))
    #     start_points = list(left_side_points)
    #     start_points.extend(top_side_points)
    #     for i_0,j_0 in start_points:
    #         queue5 = ['_']*5
    #         queue6 = ['_']*6
    #         N = min(self.height-i_0, self.width-j_0)
    #         # print(f'N = {N}')
    #         for n in range(N):
    #             ##Update both queues
    #             i = i_0+n
    #             j = j_0+n
    #             queue5.pop(0)
    #             queue5.append(self.matrix[i, j])
    #             queue6.pop(0)
    #             queue6.append(self.matrix[i, j])
    #             # print(queue5)
    #             print(queue6)
    #             head_loc = np.array(self.ij_to_xy((i,j)))
    #             print(f"Head Loc: {head_loc}")
    #             self.check_SP(queue6,head_loc, (-1,1)) 
    #             self.check_HP(queue5,head_loc, (-1,1))
    #     ##Positive-sloped Diagonal Scanning
    #     #Generate list of starting points
    #     # print('Down-Left Scanning')
    #     right_points = zip(list(range(self.height-1,0,-1)),[self.width-1]*self.height)
    #     top_points = zip([0]*self.width,list(range(self.width-1,-1,-1)))
    #     start_points = list(right_points) #copy the list
    #     start_points.extend(top_points)
    #     for i_0,j_0 in start_points:
    #         queue5 = ['_']*5
    #         queue6 = ['_']*6
    #         N = min(self.height-i_0, j_0+1)
    #         # print(f'N = {N}')
    #         for n in range(N):
    #             i = i_0+n
    #             j = j_0-n
    #             queue5.pop(0)
    #             queue5.append(self.matrix[i, j])
    #             queue6.pop(0)
    #             queue6.append(self.matrix[i, j])
    #             # print(queue5)
    #             print(queue6)
    #             head_loc = np.array(self.ij_to_xy((i,j)))
    #             print(f"Head Loc: {head_loc}")
    #             self.check_SP(queue6,head_loc, (1,1))
    #             self.check_HP(queue5,head_loc, (1,1))
    #     print(f"All Soft Powers: {self.SPs}")
    #     print(f"All Hard Powers: {self.HPs}")

    # def check_HP(self,queue, head_loc, tail_dir):
    #     '''
        

    #     Parameters
    #     ----------
    #     queue : list of str characters
    #         DESCRIPTION. A list of string characters representing a scanned line in the game matrix.

    #     Returns
    #     -------
    #     None.

    #     '''            
    #     # if queue == ['+','+','+','b','+','+']:
    #     #     print('Found a simple pattern')
    #     #For each HP pattern:
    #     #print(f"HP_Temps: {HP_Temps}")
    #     for pattern in HP_Temps:
    #         #print(f'Looking at pattern: {pattern}')
    #         #print(f"checking for pattern '{pattern.name}'")
    #         #If the queue matches the pattern:
    #         if queue == pattern.match_pat:
    #             print(f"Match found with pattern '{pattern.name}'")
    #             #Considered a success
    #             print(f"Head loc: {head_loc}, tail_dir: {tail_dir}, rel_markers: {pattern.rel_markers}")
    #             marker_locs = [(head_loc[0]-tail_dir[0]*rel_loc, head_loc[1]-tail_dir[1]*rel_loc) for rel_loc in pattern.rel_markers]
    #             print(f"marker_locs: {marker_locs}")
    #             trigger_locs = [(head_loc[0]-tail_dir[0]*rel_loc, head_loc[1]-tail_dir[1]*rel_loc) for rel_loc in pattern.rel_triggers]
    #             print(f"trigger_locs: {trigger_locs}")
    #             #If a HP with the same marker coords already exists:
    #             match_none = True #assume that hp is unique among all
    #             for hp in self.HPs:
    #                 match=True #Assume the hp in storage and new hp have the same marker_locs
    #                 for loc in hp.marker_locs:
    #                     if loc not in marker_locs:
    #                         #At least one set of marker locations doesn't match those of the sp we are inspecting
    #                         match = False
    #                 if match: #if the new old power are one and the same
    #                     match_none = False
    #                     print(f"New hp matches old hp with pattern '{hp.name}'")
    #                     #if the new HP has triggers that the old HP didnt:
    #                     for trigger_loc in trigger_locs:
    #                         if trigger_loc not in hp.trigger_locs:
    #                             #add those triggers to the old HP
    #                             hp.trigger_locs.append(trigger_loc)
    #                             print(f"Added trigger location '({trigger_loc})'")
    #                     #Also add the pattern.name to the list of pattern names.
    #                     hp.name.append(pattern.name)
    #             #If a ST or HT with the same markers already exists
    #             for threat in it.chain(self.STs, self.HTs):
    #                 match = True #assume that all HP markers belong to the current threat
    #                 for loc in marker_locs: #marker locations of potential new HP
    #                     if loc not in threat.marker_locs: #if not found in threat being inspected
    #                         match=False
    #                 if match:
    #                     match_none = False
    #                     print(f"New hp matches old threat with pattern '{threat.name}'")
                
    #             if match_none:
    #                 #No match, AKA, this is a new hp        
    #                 #Create new HP with marker and trigger locations
    #                 hp = PoT_TEMPLATE([pattern.name], pattern.player, marker_locs, trigger_locs)
    #                 self.HPs.append(hp)
    #                 print(f"Created new hard power: {hp}")
        
    
    
    # def check_SP(self,queue, head_loc, tail_dir):
    #     '''
        

    #     Parameters
    #     ----------
    #     queue : list of str characters
    #         DESCRIPTION. A list of string characters representing a scanned line in the game matrix.

    #     Returns
    #     -------
    #     None.

    #     '''            
    #     # if queue == ['+','+','+','b','+','+']:
    #     #     print('Found a simple pattern')
    #     #For each SP pattern:
    #     #print(f"SP_Temps: {SP_Temps}")
    #     for pattern in SP_Temps:
    #         #print(f'Looking at pattern: {pattern}')
    #         #print(f"checking for pattern '{pattern.name}'")
    #         #If the queue matches the pattern:
    #         if queue == pattern.match_pat:
    #             print(f"Match found with pattern '{pattern.name}'")
    #             #Considered a success
    #             print(f"Head loc: {head_loc}, tail_dir: {tail_dir}, rel_markers: {pattern.rel_markers}")
    #             marker_locs = [(head_loc[0]-tail_dir[0]*rel_loc, head_loc[1]-tail_dir[1]*rel_loc) for rel_loc in pattern.rel_markers]
    #             print(f"marker_locs: {marker_locs}")
    #             trigger_locs = [(head_loc[0]-tail_dir[0]*rel_loc, head_loc[1]-tail_dir[1]*rel_loc) for rel_loc in pattern.rel_triggers]
    #             print(f"trigger_locs: {trigger_locs}")
    #             #If a SP with the same marker coords already exists:
    #             match_none = True
    #             for sp in self.SPs:
    #                 match=True #Assume the sp in storage and new sp have the same marker_locs
    #                 for loc in sp.marker_locs:
    #                     if loc not in marker_locs:
    #                         #At least one set of marker locations doesn't match those of the sp we are inspecting
    #                         match = False
    #                 if match: #if the new old power are one and the same
    #                     match_none = False
    #                     print(f"New sp matches old sp with pattern '{sp.name}'")
    #                     #if the new SP has triggers that the old SP didnt:
    #                     for trigger_loc in trigger_locs:
    #                         if trigger_loc not in sp.trigger_locs:
    #                             #add those triggers to the old SP
    #                             sp.trigger_locs.append(trigger_loc)
    #                             print(f"Added trigger location '({trigger_loc})'")
    #                     #Also add the pattern.name to the list of pattern names.
    #                     sp.name.append(pattern.name)
    #             #If a ST or HT with the same markers already exists
    #             for threat in it.chain(self.STs, self.HTs):
    #                 match = True #assume that all SP markers belong to the current threat
    #                 for loc in marker_locs: #marker locations of potential new HP
    #                     if loc not in threat.marker_locs: #if not found in threat being inspected
    #                         match=False
    #                 if match:
    #                     match_none = False
    #                     print(f"New sp matches old threat with pattern '{threat.name}'")
    #             if match_none:
    #                 #No match, AKA, this is a new sp        
    #                 #Create new SP with marker and trigger locations
    #                 sp = PoT_TEMPLATE([pattern.name], pattern.player, marker_locs, trigger_locs)
    #                 self.SPs.append(sp)
    #                 print(f"Created new soft power: {sp}")
                    
    # def check_ST(self,queue, head_loc, tail_dir):
    #     '''
        

    #     Parameters
    #     ----------
    #     queue : list of str characters
    #         DESCRIPTION. A list of string characters representing a scanned line in the game matrix.

    #     Returns
    #     -------
    #     None.

    #     '''            
    #     # if queue == ['+','+','+','b','+','+']:
    #     #     print('Found a simple pattern')
    #     #For each ST pattern:
    #     #print(f"ST_Temps: {ST_Temps}")
    #     for pattern in ST_Temps:
    #         #print(f'Looking at pattern: {pattern}')
    #         #print(f"checking for pattern '{pattern.name}'")
    #         #If the queue matches the pattern:
    #         if queue == pattern.match_pat:
    #             print(f"Match found with pattern '{pattern.name}'")
    #             #Considered a success
    #             print(f"Head loc: {head_loc}, tail_dir: {tail_dir}, rel_markers: {pattern.rel_markers}")
    #             marker_locs = [(head_loc[0]-tail_dir[0]*rel_loc, head_loc[1]-tail_dir[1]*rel_loc) for rel_loc in pattern.rel_markers]
    #             print(f"marker_locs: {marker_locs}")
    #             trigger_locs = [(head_loc[0]-tail_dir[0]*rel_loc, head_loc[1]-tail_dir[1]*rel_loc) for rel_loc in pattern.rel_triggers]
    #             print(f"trigger_locs: {trigger_locs}")
    #             #If a ST with the same marker coords already exists:
    #             match_none = True
    #             for st in self.STs:
    #                 match=True #Assume the st in storage and new st have the same marker_locs
    #                 for loc in st.marker_locs:
    #                     if loc not in marker_locs:
    #                         #At least one set of marker locations doesn't match those of the st we are inspecting
    #                         match = False
    #                 if match: #if the new old power are one and the same
    #                     match_none = False
    #                     print(f"New st matches old st with pattern '{st.name}'")
    #                     #if the new ST has triggers that the old ST didnt:
    #                     for trigger_loc in trigger_locs:
    #                         if trigger_loc not in st.trigger_locs:
    #                             #add those triggers to the old SP
    #                             st.trigger_locs.append(trigger_loc)
    #                             print(f"Added trigger location '({trigger_loc})'")
    #                     #Also add the pattern.name to the list of pattern names.
    #                     st.name.append(pattern.name)
    #             #If a HT with the same markers already exists
    #             for threat in self.HTs:
    #                 match = True #assume that all HT markers belong to the current threat
    #                 for loc in marker_locs: #marker locations of potential new ST
    #                     if loc not in threat.marker_locs: #if not found in threat being inspected
    #                         match=False
    #                 if match:
    #                     match_none = False
    #                     print(f"New st matches old hard threat with pattern '{threat.name}'")
                
                
    #             if match_none:
    #                 #No match, AKA, this is a new sp        
    #                 #Create new SP with marker and trigger locations
    #                 st = PoT_TEMPLATE([pattern.name], pattern.player, marker_locs, trigger_locs)
    #                 self.STs.append(st)
    #                 print(f"Created new soft power: {st}")
