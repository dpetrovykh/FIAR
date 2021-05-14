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
from collections import namedtuple
import math
import random


## DEBUGGING CONSTANTS
PRINT_CELL_CHOICE = False
SHOW_QUEUES = False
SHOW_PoTs = False
SHOW_SPots = False
SHOW_HPots =False
SHOW_Evals = False


MAX_MOVE_REACH = 5
EMPTY_CHAR = '+'
PLAYER2MARKER = {'red':'r',
                     'black':'b'}
BLACK_VICTORY = ['b']*5
RED_VICTORY = ['r']*5

PoT_HISTORY_TEMP = pd.DataFrame({'marker':[],
                                 'SPoTs':[],
                                 'HPoTs':[],
                                 'softPower':[],
                                 'hardPower':[],
                                 'softThreat':[],
                                 'hardThreat':[],
                                 'player':[]})

## Power and Threat Patterns which have not been processed.

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


class FIAR_Analyzer():
    '''
    Performs analysis of a FIAR game. Useful for visualizing patterns and for allowing an AI to make moves.
    '''
    def __init__(self, game=None):
        '''
        Test documentation for FIAR __init__()
        '''
        if game:
            self.new_game(game)
        else:
            self.clear()
        # print("Powers Or Threats:")
        # for PoT in self.PoTs:
        #     print(PoT)
    
    def new_game(self, game):
        self.game = game
        ## Placeholders for analysis results
        self.victory = None #black, red, or False once game is processed.
        self.matrix = None
        self.PoTs = None
        self.PoTs_dict = None
        self.PoTs_count = None
        self.PoT_history = None
        ## Update all results
        self.update_matrix()
        self.update_PoTs()
        self.update_PoTs_dict()
        self.update_PoTs_count()
        # self.update_PoT_History()
    
    def clear(self):
        self.game = None
        self.victory = None #black, red, or False once game is processed.
        self.matrix = None
        self.PoTs = None
        self.PoTs_dict = None
        self.PoTs_count= None
        self.PoT_history = None
    
    def update_matrix(self):
        '''
        Runs through the game's df and generates a matrix of string characters that represent the markers on each tile.

        Returns
        -------
        None.

        '''
        matrix = np.ones((self.game.height,self.game.width), dtype=str)
        #print(f"width: {self.width}, height: {self.height}")
        matrix[:,:] = EMPTY_CHAR
        for rowi in range(self.game.df.shape[0]):
            x,y,player = self.game.df[['x','y','player']].iloc[rowi,:]
            i,j = self.xy_to_ij((x,y))
            #print(f" x,y: {x,y} to ij: {i,j}")
            matrix[i,j]= PLAYER2MARKER[player]
        self.matrix = matrix
        
    def update_PoTs(self):
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
                        self.victory = 'red'
                    elif queue5 == BLACK_VICTORY:
                        self.victory = 'black'
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
        ## Debugging displays of various things found.
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
    
    def update_PoTs_count(self):
        PoTs_count = {
                'red':{SPOT_TEMPLATE:0,
                       HPOT_TEMPLATE:0,
                    SOFT_POWER:0,
                    HARD_POWER:0,
                    SOFT_THREAT:0,
                    HARD_THREAT:0},
                'black':{SPOT_TEMPLATE:0,
                         HPOT_TEMPLATE:0,
                     SOFT_POWER:0,
                     HARD_POWER:0,
                     SOFT_THREAT:0,
                     HARD_THREAT:0}}
        for PoT in self.PoTs:
            PoTs_count[PoT.player][type(PoT)] +=1
        self.PoTs_count= PoTs_count
    
    def update_PoT_History(self):
        '''
        Updates the PoT count for the entire game history

        Returns
        -------
        None.

        '''
        df = PoT_HISTORY_TEMP.copy(deep=True)
        for game_state in self.game:
            analysis = FIAR_Analyzer(game_state)
            new_rows = FIAR_Analyzer.PoT_count_to_df(game_state, analysis.PoTs_count)
            df = pd.concat([df, new_rows], ignore_index=True)
        self.PoT_History = df
        
    @staticmethod
    def PoT_count_to_df(game, PoT_count):
        df_return = PoT_HISTORY_TEMP.copy(deep=True)
        for player in ['red','black']:
            df = PoT_HISTORY_TEMP.copy(deep=True)
            df.marker = [game.num_moves]
            df.SPoTs = [PoT_count[player][SPOT_TEMPLATE]]
            df.HPoTs = [PoT_count[player][HPOT_TEMPLATE]]
            df.softPower = [PoT_count[player][SOFT_POWER]]
            df.hardPower = [PoT_count[player][HARD_POWER]]
            df.softThreat = [PoT_count[player][SOFT_THREAT]]
            df.hardThreat = [PoT_count[player][HARD_THREAT]]
            df.player = [player]
            df_return = pd.concat([df_return, df], ignore_index=True)
        return df_return
            
    
    
    # {'SPoTs':[],
    #                              'HPoTs':[],
    #                              'softPower':[],
    #                              'hardPower':[],
    #                              'softThreat':[],
    #                              'hardThreat':[],
    #                              'player':[]})
    
    def point_evaluater(self, evaluator):
        '''
        A closure which returns a function for the querying of any location's move rating.'

        Parameters
        ----------
        evaluator : TYPE
            DESCRIPTION.

        Returns
        -------
        evaluate_point : function
            Given a board location, prints the rating of potentially moving there.

        '''
        cell_dict = self.cell_dict_gen()
        def evaluate_point(x,y): 
            cell = cell_dict[(x,y)]
            cell.rating = evaluator(cell)
            print(cell)
        return evaluate_point        
    
    def game_decider(self, game, evaluator):
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
        cell_dict = self.cell_dict_gen()
        # print(f"cell_dict_keys: {cell_dict.keys()}")
        #print(f"original cell_dict: {cell_dict}")
        ## Limit entries in cell dict
            #limited_cell_dict = {key:val for key, val in cell_dict.items() if key in game.playable_points()}
        ## Apply evaluator to cell_dict
        cell_dict = FIAR_Analyzer.evaluate_cell_dict(cell_dict, evaluator)
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
        NOT CURRENTLY USED. INTENDED FOR FUTURE VERSION WHERE SPECIAL CASES ARE CONSIDERED, like Ficks.
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
        '''
        Applies a weighted sum to the features stored in an individual cell.

        Parameters
        ----------
        cell : TYPE
            DESCRIPTION.

        Returns
        -------
        float
            Weighted sum.

        '''
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
        for max_dim, axis, loc, u_vec in zip((self.game.height, self.game.width),
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
        vert_list = list(range(0,self.game.height))
        horz_list = list(range(0,self.game.width))
        if side=='left':
            i = list(vert_list)
            j = [0]*self.game.height
        elif side=='right':
            i = list(vert_list)
            j = [self.game.width-1]*self.game.height
        elif side == 'top':
            i = [0]*self.game.width
            j = list(horz_list)
        elif side == 'bottom':
            i = [self.game.height-1]*self.game.width
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
        friend = self.game.next_player
        enemy = self.game.previous_player
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

    def playable_locs(self, scan_reach = int(4)):
        '''
        returns a list of empty points within scan_reach of previously-played points

        Returns
        -------
        points: list of (x,y) int tuples.
            Empty points within scan_reach of previous points

        '''
        points = []
        for x in range(self.game.game_edges['left']-scan_reach, self.game.game_edges['right']+scan_reach+1):
            for y in range(self.game.game_edges['bottom']-scan_reach,self.game.game_edges['top']+scan_reach+1):
                points.append((int(x),int(y)))
        return points
    
    def xy_to_ij(self, xy):
        '''
        Transforms a coordinate pair from the game coordinate system to the matrix coordinate system
        '''
        x,y = xy
        return int(self.game.game_edges['top']-y), int(x-self.game.game_edges['left'])
    
    def ij_to_xy(self, ij):
        '''
        Transforms a coordinate pair from the matrix coordinate system to the game coordinate system.
        '''
        i,j = ij
        return j+self.game.game_edges['left'], self.game.game_edges['top']-i

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