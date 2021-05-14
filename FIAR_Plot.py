#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 12:26:54 2021

@author: dpetrovykh
"""

import matplotlib.pyplot as plt
plt.ioff()
## TODO
## Make sure that ion() and ioff() when neccessary.
import numpy as np
import itertools

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas)

from FIAR_Analyzer import SPOT_TEMPLATE, HPOT_TEMPLATE, SOFT_POWER, HARD_POWER, SOFT_THREAT, HARD_THREAT

DRAW_SPOTS = False
DRAW_HPOTS = False
## Constants
G_SCALE = 4 # global scaler 
# Defines gridline display
GRID_DICT = {'color': 'blue',
             'alpha': 0.2,
             'linewidth':0.5}
## Marker which denotes distance on board
GRID_MARKER_SPACING = int(3)
GRID_MARKER = '+'
GRID_MARKER_KWARGS = {'color':'grey',
                      'markersize': 10}
#Size of figure
FIGSIZE = 0.5
#Tile coloring
TILE_DICT = {'alpha':0.2,
             'color':'yellow'}
## Vertical and Horizontal placement compensations for 1 and 2 digit numbers
X1DCOMP = 0 #-0.2
Y1DCOMP = -0.1 #-0.2
X2DCOMP = 0 #-0.35
Y2DCOMP = -0.1 #-0.2
# NUmber of empty tiles to display outside of the outer-most pieces
MIN_EDGE_GAP = 2
## Settings for displaying numbers
# NUM_DICT = {'size':10,
#             'alpha':1,
#             'horizontalalignment':'center',
#             'verticalalignment':'center',
#             'fontstyle':'normal'}
NUM_DICT = {'alpha':1,
            'horizontalalignment':'center',
            'verticalalignment':'center',
            'fontstyle':'normal'}
NUM_BASE_SIZE = 240

PLAYER2MARKER = {'red':'r',
                     'black':'b'}

## PoT Plotting Constants
COLOR_DICT = {'red':'red',
                 'black':'black'}
## Defuser Plotting Constants
D_MARKER = {SOFT_THREAT:'*',
            HARD_THREAT:'*'}
D_MARKERDICT = {
                SOFT_THREAT: {'size':14,
                              'alpha':0.3,
                              'horizontalalignment':'center',
                              'verticalalignment':'center',},
                HARD_THREAT: {'size':20,
                              'alpha':0.6,
                              'horizontalalignment':'center',
                              'verticalalignment':'center',}
                }
## Trigger Plotting Constants
T_MARKER = {SOFT_POWER:'o',
            HARD_POWER:'o'}
T_MARKERDICT = {
                SOFT_POWER: {'size':14,
                             'alpha':0.3,
                             'horizontalalignment':'center',
                             'verticalalignment':'center'},
                HARD_POWER: {'size':20,
                             'alpha':0.6,
                             'horizontalalignment':'center',
                             'verticalalignment':'center'}
                }            
## Through-line Plotting Constants for all powers and threats
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
## Soft Power Potential Plotting Constants
SPOT_MARKER  = {'red':'>',
                'black':'<'}
SPOT_MARKERDICT = {'size': 10,
               'alpha': 1,
               'horizontalalignment':'center',
               'verticalalignment':'center'}
SPT_X_CORR = -0.05
SPT_Y_CORR = -0.05
## Hard Power Potential Plotting Constants

HPOT_MARKER  = {'red':'=',
                'black':'|'}
HPOT_MARKERDICT = {'size': 10,
                   'alpha': 1,
                   'horizontalalignment':'center',
                   'verticalalignment':'center'}


class MplCanvas(FigureCanvas):
    
    def __init__(self, click_callback=None, parent = None, width=10, height=10, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
        self.ax = fig.add_subplot(111)
        self.click_callback = click_callback
        super(MplCanvas, self).__init__(fig)

    def mousePressEvent(self, event):
        #print("mouse pressed in figure")
        #print(f"Position: {(event.x(),event.y())}")
        # Calculate normalized position of click in frame and pass to callback function for move processing.
        from_left = event.x()/self.frameSize().width()
        from_top = event.y()/self.frameSize().height()
        self.click_callback(from_left,from_top)

class FIAR_Plot():
    '''
    TIC-TAC-TOE Five In A Row game. Contains all functionality for manually playing a game with the right commands.
    '''
    def __init__(self, game, click_callback=None):
        '''
        
        '''
        self.game = game
        disp_bounds = self.display_bounds() 
        self.disp_edges = self.square_display_bounds(disp_bounds)
        self.canvas = MplCanvas(click_callback, self, width=self.disp_width*FIGSIZE, height=self.disp_height*FIGSIZE, dpi=100)
        self.update_canvas()
        
    @property
    def disp_height(self):
        return int(self.disp_edges['top']-self.disp_edges['bottom'])
    
    @property
    def disp_width(self):
        return int(self.disp_edges['right'] - self.disp_edges['left'])
    
    def update_canvas(self):
        '''
        Helper method which draws the board and markers

        Returns
        -------
        None.

        '''
        # global overlay
        # Linux
        # if sys.platform.startswith('linux'):
        #     os.system('clear')
        # # Windows
        # elif sys.platform.startswith('win32'):
        #     os.system('cls')
        # if self.fig:
        #     plt.close(self.fig)
        self.draw_board()
        self.draw_markers()
        # if overlay:
        #     # print("display_all sees overlay== True")
        #     self.draw_PoTs()
        # else:
        #     pass
        #     # print(f"display_all sees overlay== {overlay}")
        # self.render()
        
    def draw_board(self):
        '''
        Creates a new figure and axes and draws the board on them.
        figure and axes saved in self.fig and self.canvas.ax

        Returns
        -------
        None.

        '''
        # plt.rcParams['figure.figsize'] = (self.disp_width*FIGSIZE, self.disp_height*FIGSIZE)
        # print(f"disp_width: {self.disp_width}")
        # print(f"disp_height: {self.disp_height}")
        lEdge = self.disp_edges['left']
        rEdge = self.disp_edges['right']
        tEdge = self.disp_edges['top']
        bEdge = self.disp_edges['bottom']
        #Draws the Board
        # self.fig, self.canvas.ax = plt.subplots()
        # Control size of figure
        self.canvas.ax.set_xlim(lEdge, rEdge)
        self.canvas.ax.set_ylim(bEdge, tEdge)
        # print(f"xlims: ({lEdge},{rEdge})")
        # print(f"ylims: ({bEdge},{tEdge})")
        
        ## Hide original Axes and labels
        for side in['top','right','left','bottom']:
            self.canvas.ax.spines[side].set_visible(False)
        self.canvas.ax.tick_params(axis='both',
                       which='both',
                       bottom=False,
                       top=False,
                       labelbottom=False,
                       labelleft=False,
                       left=False,
                       right=False)
        ## Drawing the grid lines
        for x in np.arange(lEdge, rEdge+1):
            # self.canvas.ax.axvline(x, color = GRIDCOLOR, linewidth = 1, alpha = 0.5)
            # print(f"drawing vline @ x={x}")
            self.canvas.ax.axvline(x, **GRID_DICT)
        for y in np.arange(bEdge,tEdge+1):
            # print(f"drawing hline @ y={y}")
            self.canvas.ax.axhline(y, **GRID_DICT)
        
        ## Drawing the grid squares
        for x in np.arange(lEdge, rEdge):
            for y in np.arange(bEdge, tEdge):
                if (np.abs(x+0.5)+np.abs(y+0.5))%2==1:
                    rect = plt.Rectangle((x,y),1,1, **TILE_DICT)
                    self.canvas.ax.add_artist(rect)
                    
    ## Draw the grid markers denoting distance
        # neg_x_dir = int(abs(self.disp_edges['left'])//GRID_MARKER_SPACING)
        # pos_x_dir = int(abs(self.disp_edges['right'])//GRID_MARKER_SPACING)
        # pos_y_dir = int(abs(self.disp_edges['top'])//GRID_MARKER_SPACING)
        # neg_y_dir = int(abs(self.disp_edges['bottom'])//GRID_MARKER_SPACING)
        # # print(f"neg_x_dir: {neg_x_dir}")
        # # print(f"pos_x_dir: {pos_x_dir}")
        # xs = list(range(neg_x_dir,pos_x_dir+GRID_MARKER_SPACING,GRID_MARKER_SPACING))
        # ys = list(range(neg_y_dir,pos_y_dir+GRID_MARKER_SPACING, GRID_MARKER_SPACING))
        # for x in xs:
        #     for y in ys:
        #         self.canvas.ax.plot([x-0.05],[y],GRID_MARKER,**GRID_MARKER_KWARGS)
                
        # draw it
    def draw_markers(self):
        '''
        Draws all of the markers present in this game's dataframe onto self.fig.

        Returns
        -------
        None.

        '''
        for rowi in range(self.game.num_moves):
            row = self.game.df.iloc[rowi,:] 
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
            self.canvas.ax.text(x+X1DCOMP,
                         y+Y1DCOMP,
                         str(int(num)),
                         color=color,
                         size = NUM_BASE_SIZE/self.disp_width,
                         fontdict=NUM_DICT)
        elif len(str(int(num)))==2:
            self.canvas.ax.text(x+X2DCOMP,
                         y+Y2DCOMP,
                         str(int(num)),
                         color=color,
                         size = NUM_BASE_SIZE/self.disp_width,
                         fontdict=NUM_DICT)
        else:
            raise Exception("There's been a terrible error")
        # plt.close(self.fig)

    def draw_PoTs(self, PoTs):
        #For each PoT
        for PoT in PoTs:
            #print(f"PoTtype: {PoTtype}")
            PoTtype = type(PoT)
            #print(f"PoT: {PoT}")
            color = COLOR_DICT[PoT.player]
            #if PoT is a power:
            if PoTtype in [SOFT_POWER,HARD_POWER]:
                #draw appropriate marker for SP or HP
                for x,y in PoT.trigger_locs:
                    if self.on_figure((x,y)):
                        self.canvas.ax.text(x+X1DCOMP,y+Y1DCOMP,T_MARKER[PoTtype], color=color, fontdict = T_MARKERDICT[PoTtype])
                #Calculate line end points
                all_points = list(PoT.trigger_locs)
                all_points.extend(PoT.marker_locs)
                p1,p2 = FIAR_Plot.extreme_points(all_points)
                #draw appropriate line for SP or HP
                x1,y1 = p1
                x2,y2 = p2
                self.canvas.ax.plot((x1,x2),(y1,y2),color=color, **LINEKWARGS[PoTtype])
            #if PoT is a ST or HT
            elif PoTtype in [SOFT_THREAT, HARD_THREAT]:              
                ## Get all points connecting marker locations
                p1,p2 = FIAR_Plot.extreme_points(PoT.marker_locs)
                x1,y1 = p1
                x2,y2 = p2
                #Draw thick lines representing threats
                self.canvas.ax.plot((x1,x2),(y1,y2),color=color, **LINEKWARGS[PoTtype])
                ## Draw defuser Locations
                for x,y in PoT.defuser_locs:
                    if self.on_figure((x,y)):
                        self.canvas.ax.text(x+X1DCOMP,y+Y1DCOMP,D_MARKER[PoTtype], color=color, fontdict = D_MARKERDICT[PoTtype])
            elif PoTtype == SPOT_TEMPLATE:
                if DRAW_SPOTS:
                    # print("draw_PoTs detected a spot")
                    # print(f"Spot: {PoT}")
                    ## Draw trigger locations for SPots
                    # print(f"PoT.trigger_locs: {PoT.trigger_locs}")
                    # print(f"list(zip(*PoT.trigger_locs)): {list(zip(*PoT.trigger_locs))}")
                    for x, y in PoT.trigger_locs:
                        if self.on_figure((x,y)):
                            self.canvas.ax.text(x+SPT_X_CORR,y+SPT_Y_CORR,SPOT_MARKER[color], color = color, fontdict = SPOT_MARKERDICT)
            elif PoTtype == HPOT_TEMPLATE:
                if DRAW_HPOTS:
                    for x,y in PoT.booster_locs:
                        if self.on_figure((x,y)):
                            self.canvas.ax.text(x+SPT_X_CORR,y+SPT_Y_CORR,HPOT_MARKER[color], color = color, fontdict = HPOT_MARKERDICT)
                
                
    

    
    # def render(self):
    #     '''
    #     Refreshes the game. Display method depends on 'display' setting.
    #     '''
    #     print(f"render. self.display = {self.display}")
    #     if self.display == 'regular':
    #         self.show()
    #     elif self.display == 'Jupyter':
    #         self.JNshow()
    #     else:
    #         raise Exception("display value invalid")
    
    # def show(self):
    #     '''
    #     Regular method for drawing the figure
    #     '''
    #     print("attempting fig.show()")
    #     self.fig.show()
        
    # def JNshow(self):
    #     '''
    #     Jupyter-Notebook-specific display method
    #     '''
    #     print("Attempting to display(self.fig)")
    #     display(self.fig)
    
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
        marker_bounds = self.game.marker_bounds()
        right = marker_bounds['right'] + padding+0.5
        top = marker_bounds['top'] + padding+0.5
        left = marker_bounds['left'] - padding-0.5
        bottom = marker_bounds['bottom'] - padding -0.5
        return {'right':right,
                'top':top,
                'left':left,
                'bottom':bottom}
    
    def square_display_bounds(self, disp_bounds):
        new_bounds = disp_bounds.copy()
        disp_height = int(disp_bounds['top'] - disp_bounds['bottom'])
        disp_width = int(disp_bounds['right'] - disp_bounds['left'])
        if disp_height != disp_width:
            # right = disp_bounds['right']
            # left = disp_bounds['left']
            # top = disp_bounds['top']
            # bottom = disp_bounds['bottom']
            diff = abs(int(disp_height-disp_width))
            cyc = None #"allocate memory"
            if disp_height>disp_width:
                cyc = itertools.cycle([('left',-1),
                                       ('right',1)])
            else:
                cyc = itertools.cycle([('bottom',-1),
                                       ('top', 1)])
            for _ in range(diff):
                side, delta = next(cyc)
                new_bounds[side] += delta
        return new_bounds
                
     
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
        p1,p2 = np.array(FIAR_Plot.extreme_points(points))
        x1,y1 = p1
        x2,y2 = p2
        ## Calculate the directional vector from one extreme point to another
        vector = p2-p1
        dir_vect = vector/abs(vector)
        dir_vect = dir_vect.astype(int)
        ## Generate all the points from one extreme point to another stepping along the unit vector
        n_points = max(abs(y2-y1),abs(x2-x1))+1
        return tuple([tuple(p1+dir_vect*n) for n in range(n_points)])