#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 15:10:08 2021

@author: dpetrovykh
"""
import types
import os
from FIAR import FIAR

SAVE_FOLDER = 'saves'
RECORDS_FOLDER = 'records'
TEST_FOLDER = 'test_saves'
YESSES = ['y','yes','yup']
NOS = ['n','no','nope']


class FIAR_Interface():
    def __init__(self):
        print("Welcome to Tic-Tac-Toe Five-in-a-Row!")
        self.game = None
        self.victory = False
        self.new_state(MainMenu)
    
    def new_state(self, newstate):
        self.__class__ = newstate
        self.run()
        
    def run(self):
        raise NotImplementedError()
        
    def input_handler(self, choices, prompt, failure_prompt=None, mods = None):
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
                    
    def game_selector(self, folder = SAVE_FOLDER):
        saves = self.list_saves(folder)
        chosen_save = self.input_handler(choices=[[saves,'input']], 
                                     prompt = f"The available games are: {saves}\nPlease input a valid game name: ")
        game = FIAR.from_csv(chosen_save, folder=folder)
        return game
    
    def list_saves(self, folder = SAVE_FOLDER):
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
    
    def player_move(self):
        while True:
            if self.victory:
                self.new_state(Victory)
            else:## Game is not over            
                x = None
                y = None
                ## Ask for inputs
                coords = input(f"Enter 'x,y' coordinates for {game.next_player}'s next move: ")
                #UNDO Special input
                #print("got here 123")
                if coords == 'undo':
                    self.undo()
                ## QUIT special input    
                elif coords.lower() in ['quit','exit','end']:
                    print(f'The game has been ended by the {game.next_player} player')
                    game.to_csv('autosave')
                    exit()
                ## SAVE special input
                elif coords.lower()=='save':
                    self.new_state(SaveGame)
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
    
    
class MainMenu(FIAR_Interface):
    '''
    The first state which greets the user and directs them into the proper place.
    '''
    def run(self):
        try:
        #Welcome players to the game
            
            ##Ask if playing new or saved game
            mode = self.input_handler(choices=[(['new','new game'],'new'),
                                               (['load','save','load save','load game','cont','continue'],'load'),
                                               (['view'],'view')],
                                      prompt="Would you like to play a 'new' game, 'load' a save, or 'view' a save?\n",
                                      mods=[str.lower, str.strip])
            #If new:
            if mode == 'new':
                self.new_state(NewGame)
            #If saved:
            elif mode == 'load':
                #Perform selection of a saved game
                self.new_state(LoadGame)
                # game = self.game_selector()
                # FIAR.run_game(game)
            elif mode == 'view':
                self.new_state(ViewGame)
                # ##Select a folder
                # folder  = FIAR.input_handler(choices =[(['r','records','record','history'],'records'),
                #                                        (['s','saves','save'],'saves')],
                #                              prompt = "Would you like to view a 'save' game or 'record' game?\n",
                #                              mods=[str.lower, str.strip])
                # folder = {'saves':SAVE_FOLDER,
                #           'records':RECORDS_FOLDER}[folder]
                # ## Select a game to view
                # game = FIAR.game_selector(folder=folder)
                # ## Launch viewer with selected game.
                # FIAR.game_viewer(game)                
            print("NotAnError: Out of 'run'way")
        except SystemExit:
            print('System Exit')
            #os._exit(1)


class NewGame(FIAR_Interface):
    '''
    Performs the 
    '''
    def run(self):
        ## Ask whether this will be a PvP or PvAI game
        ai_game = self.input_handler(choices = [(['pvai','comp','computer','1p','ai','one player', 'single player', 'single'],True),
                                                (['pvp','two player','2p', 'two_player','versus','vs','player'],False)], 
                                      prompt="Would you like to play against a friend in 'PvP' mode or against the computer in 'PvAI' mode?",
                                      mods=[str.lower,str.strip])
        ## IF the opponent is an AI
        if ai_game:
            ## Determine player color
            self.player_color = self.input_handler(choices =[(['black','b'],'black'),
                                                            (['red','r'],'red')],
                                                  prompt = "Would you like to play as 'black' or 'red'?")
            self.ai_color = {'red':'black',
                        'black':'red'}[self.player_color]
            ## Determine turn order
            first_player = FIAR.input_handler(choices=[(['p','me','myself','self','human', 'first','1'],'player'),
                                                       (['c','ai','computer','robot','second','2'], 'computer')],
                                              prompt= "Would you like yourself to go first or the computer?\n",
                                              failure_prompt="    {} is not an option.",
                                              mods = [str.lower, str.strip])
            self.next_color = {'computer':self.ai_color,
                           'player':self.player_color}[first_player]
            self.game = FIAR(first_player=self.next_color)
            self.new_state(PvAIGame)
        ## The opponent is another player
        else:   
            self.new_state(PvPGame)


class LoadGame(FIAR_Interface):
    def run(self):
        self.game = self.game_selector()        
        ## Ask whether this will be a PvP or PvAI game
        ai_game = self.input_handler(choices = [(['pvai','comp','computer','1p','ai','one player', 'single player', 'single'],True),
                                                (['pvp','two player','2p', 'two_player','versus','vs','player'],False)], 
                                      prompt="Would you like to play against a friend in 'PvP' mode or against the computer in 'PvAI' mode?",
                                      mods=[str.lower,str.strip])
        ## IF the opponent is an AI
        if ai_game:
            ## State the next move
            ## Determine player color
            self.player_color = self.input_handler(choices =[(['black','b'],'black'),
                                                            (['red','r'],'red')],
                                                  prompt = "Would you like to play as 'black' or 'red'?")
            self.ai_color = {'red':'black',
                        'black':'red'}[self.player_color]
            self.next_color = self.game.next_player
            self.new_state(PvAIGame)
        ## The opponent is another player
        else:   
            self.new_state(PvPGame)
            
        
class PvPGame(FIAR_Interface):
    def undo(self):
        self.game.undo()
    
    def run(self):
        while True:
            self.player_move()
    
class PvAIGame(FIAR_Interface):
    def undo(self):
        self.game.undo()
        self.game.undo()
        
    def run(self):
        while True:
            self.player_move()
            self.ai_move()

class Victory(FIAR_Interface):
    def run(self):
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
    
class ViewGame(FIAR_Interface):
    def run(self):
        pass
    
class SaveGame(FIAR_Interface):
    def run(self):
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