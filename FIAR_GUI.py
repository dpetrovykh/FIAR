#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 14:13:57 2021

@author: dpetrovykh
"""



from PyQt5.uic import loadUiType
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QMovie, QPainter, QPixmap

from functools import partial
import copy

import FIAR
from FIAR import OutOfBounds, RepeatMove
from FIAR_Plot import FIAR_Plot
from FIAR_Saves import FIAR_Saves, RECORDS_FOLDER, EmptySaveSlot
from FIAR_Sounds import FIAR_Sounds
import FIAR_Analyzer

IMAGE_FOLDER = 'images/'

## DEBUGGING SETTINGS
PRINT_STATE_TRANS = False

## StackedFrame Constants for switching displayed frame
PLAY = 0
VIEWER = 1
SAVEDGAMES = 2
MAINMENU = 3

Ui_MainWindow, QMainWindow = loadUiType('FIAR_Main_Window.ui')
Ui_NewGame, QNewGame = loadUiType("NewGame.ui")	
Ui_ResumeGame, QResumeGame = loadUiType("ResumeGame.ui")	
Ui_SaveName, QSaveName = loadUiType("SaveName.ui")
Ui_ViewerQuery, QViewerQuery = loadUiType("ViewerQuery.ui")
# COde for compiling GUI resources
# pyrcc5 QtResources.qrc -o QtResources_rc.py

class FIAR_Main_Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(FIAR_Main_Window, self).__init__()
        self.setupUi(self)
        ## Game Properties
        self.game = None
        self.ai_player = None
        self.savename = None
        ## Other classes
        self.saves = FIAR_Saves()
        self.analysis = FIAR_Analyzer.FIAR_Analyzer()
        self.sounds= FIAR_Sounds()
        # GIF SETUP
        self.movie = QMovie(IMAGE_FOLDER+"FIAR-Home-Screen_BG.gif")
        self.movie.frameChanged.connect(self.repaint)
        self.movie.start()
        # self.centralwidget.setStyleSheet('QGraphicsView {background-color: rgb(0,0,0);}')
        #Play intro sound
        self.sounds.start()
        # Setup first window
        self.new_state(MainMenu)
        self.initialization()
    
    # @abstractmethod
    # def initialization(self):
    #     '''Performs the setup neccessary upon entering a new state for the first time.'''
    #     pass
    #     # Forces implementation in child classes
    
    # @abstractmethod
    # def exit_cleanup(self):
    #     '''Performs the teardown necessary prior to exiting the current state'''
    #     pass
    #     # Forces implementation in child classes    
        
    def to_MainMenu(self):
        self.sounds.click()
        self.state_trans(MainMenu)
    
    def to_PvP(self):
        self.sounds.click()
        self.state_trans(PvP)

    def to_PvAI(self):
        self.sounds.click()
        self.state_trans(PvAI)
    
    def to_Saving(self):
        self.sounds.click()
        self.state_trans(Saving)
        
    def to_Loading(self):
        self.sounds.click()
        self.state_trans(Loading)
        
    def to_Viewing(self):
        self.sounds.click()
        self.state_trans(Viewing)   
        
    def new_state(self, newstate):
        '''Changes the state of the Main Window'''
        prev_class = self.__class__
        self.__class__ = newstate
        if PRINT_STATE_TRANS:
            print(f"Changed state from {prev_class} to {self.__class__}")
    
    def set_frame(self,frame):
        '''Sets new frame to be displayed'''
        self.stackedWidget.setCurrentIndex(frame)
    
    def state_trans(self,newstate):
        '''
        Performs a controlled transfer to another state by calling the exit_cleanup() method of the current state and the initialization() of the newstate.

        Parameters
        ----------
        newstate : child class of FIAR_Main_Window
            The new state to which the application should transition.

        Returns
        -------
        None.

        '''
        self.exit_cleanup()
        self.new_state(newstate)
        self.initialization()
        
    def paintEvent(self, event):
        currentFrame = self.movie.currentPixmap()
        frameRect = currentFrame.rect()
        frameRect.moveCenter(self.rect().center())
        # if frameRect.intersects(event.rect()):
        painter = QPainter(self)
        painter.drawPixmap(frameRect.left(), frameRect.top(), currentFrame)    
    
        
class MainMenu(FIAR_Main_Window):
    def initialization(self):
        self.set_frame(MAINMENU)
        print('movie init')
        # self.show()
        
        ## Link Main Menu Buttons
        self.Continue.clicked.connect(self.to_Loading)
        self.NewGame.clicked.connect(self.new_game)
        self.Records.clicked.connect(self.to_Viewing)
    
    def exit_cleanup(self):
        # self.movie.stop()
        try:
            self.Continue.clicked.disconnect()
            self.NewGame.clicked.disconnect()
            self.Records.clicked.disconnect()
            # self.movie.frameChanged.disconnect()
        except TypeError as ex:
            print(ex)
    
    def new_game(self):
        '''
        Responds to press of NewGame button on the Main Menu
        '''
        # print('Clicked main_newgame')
        self.sounds.click()
        newgame_window = NewGame_Dialogue(callback=self.to_Play)
        newgame_window.exec_()
        # If dialogue interaction is successful, then MainMenu.receieve_newgame_inputs() gets called by dialogue.
 
    def to_Play(self,inputs):
        self.sounds.click()
        game = FIAR.FIAR(first_player = inputs['first_player'])
        self.exit_cleanup()
        if inputs['mode'] == 'PvP':
            self.new_state(PvP)
            self.initialization(game)
        elif inputs['mode'] == 'PvAI':
            self.new_state(PvAI)
            self.initialization(game, inputs['ai_player'])
                
    
class Play(FIAR_Main_Window):
    def initialization(self,game):
        self.game = game#Assumes that self.game has already been set.
        self.set_frame(PLAY)
        self.newmpl()
        self.update_np_label()
        self.Play_TopLabel.setText("")
        self.analysis.new_game(self.game) # Feed new game into analyzer
        self.check_victory()
        ## Button Connections
        self.Play_Undo.clicked.connect(self.undo)
        self.Play_Save.clicked.connect(self.save)
        self.Play_Surrender.clicked.connect(self.surrender)
        # self.Play_Move.clicked.connect(self.move)
        self.Play_MainMenu.clicked.connect(self.to_MainMenu)
    
    def exit_cleanup(self):
        self.game=None
        self.analysis.clear()
        self.rmmpl()
        self.savename = None
        try:
            self.Play_Undo.clicked.disconnect()
            self.Play_Save.clicked.disconnect()
            # self.Play_Move.clicked.disconnect()
            self.Play_MainMenu.clicked.disconnect()
        except TypeError:
            pass

    def refresh_mpl(self):
        self.rmmpl()
        self.newmpl()
        
    def update_np_label(self):
        self.NextPlayerLabel.setText(self.game.next_player.capitalize())    
        self.NextPlayerLabel.setStyleSheet(f"color: {self.game.next_player}")
        
    def update_mode_label(self, mode):
        self.ModeLabel.setText(mode + " mode")
        
    def newmpl(self):
        self.plot = FIAR_Plot(self.game, self.click_react)
        self.Play_mpl_layout.addWidget(self.plot.canvas)
        self.plot.canvas.draw()

    def rmmpl(self):
        self.plot.canvas.ax.cla()
        self.Play_mpl_layout.removeWidget(self.plot.canvas)
        # print("Closing Play canvas")
        self.plot.canvas.close()
    
    def click_react(self, from_left, from_top):
        '''Reacts to a click on the game board in order to process the cursor position and make a move'''
        print(f"received normalized position of click, from left: {from_left}, from_top: {from_top}")
        ## Calculate distance from left and top in cells
        cell_width = self.plot.disp_width #width of plot in cells
        cell_height = self.plot.disp_height #height of plot in cells
        c_left = from_left*cell_width #distance in cells from left edge
        c_top = from_top*cell_height #distance in cells from top edge
        print(f"Cell distance from...top: {c_top}, left: {c_left}")
        print(f"left_edge: {self.plot.disp_edges['left']}, top_edge: {self.plot.disp_edges['top']}")
        x = c_left+self.plot.disp_edges['left'] # decimal x distance in cells from x,y origin
        y = self.plot.disp_edges['top']-c_top # decimal y distance in cells from x,y origin
        x_cell = round(x)
        y_cell = round(y)
        print(f"calculated final move of x: {x_cell}, y: {y_cell}")
        ## Make a move with these new_found move coordinates.
        self.auto_move(x_cell,y_cell)
    
    def refresh_all(self):
        self.refresh_mpl()
        self.update_np_label()
        
    def check_victory(self):
        if self.analysis.victory:
            self.game_over()

    def game_over(self, winner = None):
        self.sounds.victory()
        if winner == None:
            winner = self.analysis.victory
        else:
            assert winner.lower() in ['black','red']
        self.Play_TopLabel.setText(f"{winner.capitalize()} is Victorious!")
        # Get name for record and save it.
        savename_window = SaveName_Dialogue(callback= self.record_game,
                                        namevalid= self.saves.valid_save_name)
        savename_window.exec_()
        # Delete current game from autosave
        self.saves.delete_listed_save('auto')
        # Check that the game was saved and that it is listed in the records
        if self.savename:
            # Ask users whether they would like to view the game in the viewer and do it.            
            viewerquery_window = ViewerQuery_Dialogue(callback_yes= self.to_Viewing,
                                                      callback_no = self.to_MainMenu)
            viewerquery_window.exec_()            
   
    def surrender(self):
        print("'Surrender' clicked.")
        winner = self.game.previous_player
        self.game_over(winner=winner)
        
    def save(self):
        self.sounds.click()
        ## Pop up saveName dialogue
        savename_window = SaveName_Dialogue(callback= self.to_Saving,
                                            namevalid= self.saves.valid_save_name)
        savename_window.exec_()
    
    def to_Saving(self,savename):
        game = copy.deepcopy(self.game)
        ## Cleanup
        self.exit_cleanup()
        ## transition to Saving state
        self.new_state(Saving)
        self.initialization(game, savename)
    
    def to_Viewing(self):
        game = copy.deepcopy(self.game)
        savename = self.savename
        ## Cleanup
        self.exit_cleanup()
        ## transition to saving state
        self.new_state(Viewing)
        if savename in self.saves.list_all_records():    
            self.initialization(savename=savename)
        else:
            self.initialization(game=game)
        
    def record_game(self,savename):
        self.saves.save_record(self.game, savename)
        self.savename = savename
        
        
class PvP(Play):        
    def initialization(self, game):
        super(PvP, self).initialization(game)
        self.update_mode_label("PvP")
        ## Reconnect MainMenu button
        # self.Play_MainMenu.clicked.disconnect()
     
    def exit_cleanup(self):
        super(PvP, self).exit_cleanup()  
        
    def undo(self):
        self.sounds.click()
        # Modify game
        try:
            self.game.undo()
        except IndexError as ex:
            print(ex)
        # Update all
        self.refresh_all()

    # def move(self):
    #     self.sounds.move()
    #     try:
    #         # pull data from fields
    #         x = self.Play_X_Val.value()
    #         y = self.Play_Y_Val.value()
    #         # feed data to game
    #         self.game.move(x,y)
    #         self.saves.autosave(self.game)
    #     except OutOfBounds as ex:
    #         pass
    #         print(ex.message)
    #     except RepeatMove as ex:
    #         pass
    #         print(ex.message)
    #     self.refresh_all()
    #     self.analysis.new_game(self.game)
    #     self.check_victory()
        
    def auto_move(self,x,y):
        self.sounds.move()
        try:
            # feed data to game
            self.game.move(x,y)
            self.saves.autosave(self.game)
        except OutOfBounds as ex:
            pass
            print(ex.message)
        except RepeatMove as ex:
            pass
            print(ex.message)
        self.refresh_all()
        self.analysis.new_game(self.game)
        self.check_victory()
        
class PvAI(Play):
    def initialization(self, game, ai_player):
        super(PvAI, self).initialization(game)
        self.ai_player = ai_player
        self.set_frame(PLAY)
        self.update_mode_label("PvAI")
        if self.game.next_player == self.ai_player:
            self.ai_move()
            self.refresh_all()
    # def new_game(self, first_player, ai_color):
    #     print(f"PvAI.new_game received first_player: {first_player}, ai_color: {ai_color}")
    #     self.game = FIAR.FIAR(first_player=first_player)
    
    def exit_cleanup(self):
        super(PvAI, self).exit_cleanup()    
        self.ai_player = None
    
    # def move(self):
    #     self.sounds.move()
    #     # Perform User move first
    #     try:
    #         # pull data from fields
    #         x = self.Play_X_Val.value()
    #         y = self.Play_Y_Val.value()
    #         # feed data to game
    #         self.game.move(x,y)
    #     except OutOfBounds as ex:
    #         pass
    #         print(ex.message)
    #     except RepeatMove as ex:
    #         pass
    #         print(ex.message)
    #     else: #User move went properly
    #         ## AI Makes a move
    #         self.analysis.new_game(self.game)
    #         self.ai_move()
    #         self.saves.autosave(self.game)
    #     finally:
    #         self.refresh_all() 
    #         ## Check for victory
    #         self.analysis.new_game(self.game)
    #         self.check_victory()
    
    def auto_move(self,x,y):
        self.sounds.move()
        # Perform User move first
        try:
            # feed data to game
            self.game.move(x,y)
        except OutOfBounds as ex:
            pass
            print(ex.message)
        except RepeatMove as ex:
            pass
            print(ex.message)
        else: #User move went properly
            ## AI Makes a move
            self.analysis.new_game(self.game)
            self.ai_move()
            self.saves.autosave(self.game)
        finally:
            self.refresh_all() 
            ## Check for victory
            self.analysis.new_game(self.game)
            self.check_victory()
    
    def ai_move(self):
            ai_coords = self.analysis.game_decider(self.game, FIAR_Analyzer.FIAR_Analyzer.evaluate_point_sum)
            self.game.move(*ai_coords)
            
    def undo(self):
        self.sounds.click()
        # Modify game. Undo twice because must revert AI and player turn
        game = copy.deepcopy(self.game)
        try:
            self.game.undo()
            self.game.undo()
        except IndexError as ex:
            self.game = game
            print(ex)
        # Update image
        self.refresh_all()
    
    
class Saves(FIAR_Main_Window):
    def initialization(self):
        # Set new frame to be displayed
        # print("Performing Saves initialization")
        self.set_frame(SAVEDGAMES)
        # Display labels on button appropriate to the corresopnding saves
        for button, listing_id in [(self.Save1,1),
                                   (self.Save2,2),
                                   (self.Save3,3)]:
            self.label_button(button, listing_id)
        self.Saves_MainMenu.clicked.connect(self.to_MainMenu)
            
    def exit_cleanup(self):
        self.game = None
        try:
            self.Autosave.clicked.disconnect()
            self.Save1.clicked.disconnect()
            self.Save2.clicked.disconnect()
            self.Save3.clicked.disconnect()
            self.Saves_MainMenu.clicked.disconnect()
        except TypeError:
            pass


class Saving(Saves):
    def initialization(self, game, savename):
        super(Saving, self).initialization()
        self.game = game
        self.savename = savename
        # print("Performing Saving initialization")
        # Tell the player to choose a slot to save in
        self.Saves_Banner.setText("Please select a save location for your game")
        self.Save1.clicked.connect(partial(self.save_game, listing_id = 1))
        self.Save2.clicked.connect(partial(self.save_game, listing_id = 2))
        self.Save3.clicked.connect(partial(self.save_game, listing_id = 3))
        
    def exit_cleanup(self):
        super(Saving, self).exit_cleanup()
        self.savename = None
        
    def save_game(self, listing_id):
        self.sounds.click()
        # Save the current game
        self.saves.save_game(game=self.game,
                             savename=self.savename,
                             listing_id = listing_id)
        self.state_trans(MainMenu)
        
    def label_button(self, button, listing_id):
        if self.saves.listing[listing_id] != None:
            button.setText("Overwrite - " +self.saves.listing[listing_id])
        else:
            button.setText("Save in Empty Slot")
        
        
class Loading(Saves):
    def initialization(self):
        super(Loading, self).initialization()
        # print("Performing Loading initialization")
        self.set_frame(SAVEDGAMES)
        # Tell the user to choose a slot to load
        self.Saves_Banner.setText("Please select a game to load")
        self.Autosave.clicked.connect(partial(self.load_game, listing_id='auto'))
        self.Save1.clicked.connect(partial(self.load_game, listing_id = 1))
        self.Save2.clicked.connect(partial(self.load_game, listing_id = 2))
        self.Save3.clicked.connect(partial(self.load_game, listing_id = 3))
        
    def load_game(self, listing_id):
        self.sounds.click()
        try:
            self.game = self.saves.load_game(listing_id)
        except EmptySaveSlot as ex:
            print(ex.message)
        else:
            resumegame_window = ResumeGame_Dialogue(callback = self.to_Play)
            resumegame_window.exec_()
        
    def exit_cleanup(self):
        super(Loading, self).exit_cleanup()
        
    def label_button(self, button, listing_id):
        if self.saves.listing[listing_id] != None:
            button.setText("Load - " +self.saves.listing[listing_id])
        else:
            button.setText("No Save Here")
    
    def receive_resumegame_inputs(self,inputs):
        kwargs = {key:val for key,val in inputs.items() if key != "mode"}
        # print(f"newgame kwargs: {kwargs}")
        if inputs['mode'] == 'PvP':
            self.to_PvP()
            
        elif inputs['mode'] == 'PvAI':
            self.ai_player = kwargs['ai_player']
            self.to_PvAI()
     
    def to_Play(self, inputs):
        game = copy.deepcopy(self.game)
        self.exit_cleanup()
        if inputs['mode'] == 'PvP':
            self.new_state(PvP)
            self.initialization(game)
        elif inputs['mode'] == 'PvAI':
            self.new_state(PvAI)
            self.initialization(game,inputs['ai_player'])
            
    
class Viewing(FIAR_Main_Window):
    def initialization(self, game= None, savename = None):
        print("Viewing Initialization")
        assert not(game and savename) #Only one can be provided
        self.set_frame(VIEWER)
        self.view_indices = {}
        self.item=None
        # Dsiplay record games in list
        for record in self.saves.list_all_records():
            self.mplfigs.addItem(record)
            ## Save records view index
            record_game = FIAR.FIAR.from_csv(record, folder = RECORDS_FOLDER)
            self.view_indices[record] = record_game.num_moves
        if savename: # The name of an existing record has been provided
            self.item = self.mplfigs.findItems(savename, Qt.MatchFlag.MatchExactly)[0]    
            self.new_game(self.item)
            self.item.setSelected(True)
            print("item set by savename: {savename}")
        elif game: # A game not saved in the records has been provided
            self.game = game
            print("using provided game")
        else: # The first record in the list is provided
            self.item = self.mplfigs.item(0)
            self.new_game(self.item)
            self.item.setSelected(True)
            print("First item set")
        self.newmpl(self.game)
        self.view_index = self.game.df.shape[0]
        ## Link Buttons
        self.Viewer_MainMenu.clicked.connect(self.to_MainMenu)
        self.BackButton.clicked.connect(self.back)
        self.ForwardButton.clicked.connect(self.forward)
        self.Viewer_Play.clicked.connect(self.resume_game)
        self.mplfigs.itemClicked.connect(self.change_game)
        self.OverlayToggle.stateChanged.connect(self.overlay_toggle)
    
    def exit_cleanup(self):
        self.game = None
        self.view_index = None
        self.analysis.clear()
        self.rmmpl()
        self.item = None
        try:
            self.Viewer_MainMenu.clicked.disconnect()
            self.BackButton.clicked.disconnect()
            self.ForwardButton.clicked.disconnect()
            self.Viewer_Play.clicked.disconnect()
            self.mplfigs.itemClicked.disconnect()
            self.OverlayToggle.stateChanged.disconnect()
        except TypeError:
            pass
        self.mplfigs.clear()
        
    def back(self):
        self.sounds.click()
        ## move backwards in time on the current game if possible
        if self.view_index>1:
            self.view_index-=1
            new_df = self.game.df.iloc[:self.view_index,:]
            viewed_game = FIAR.FIAR(df= new_df)
            self.rmmpl()
            self.newmpl(viewed_game)
            self.view_indices[self.item.text()] = self.view_index
        else:
            print("We cannot go any further back in this game.")
    
    def forward(self):
        self.sounds.click()
        if self.view_index< self.game.df.shape[0]:
                self.view_index +=1
                ## move forward in time on the current game if possible
                new_df = self.game.df.iloc[:self.view_index,:]
                viewed_game = FIAR.FIAR(df= new_df)
                self.rmmpl()
                self.newmpl(viewed_game)
                self.view_indices[self.item.text()] = self.view_index
        else:
            print("This is the latest view of the game.")

    def resume_game(self):
        self.sounds.click()
        current_df = self.game.df.iloc[:self.view_index,:]
        self.game = FIAR.FIAR(df=current_df)
        resumegame_window = ResumeGame_Dialogue(callback = self.to_Play)
        resumegame_window.exec_()
    
    def to_Play(self, inputs):
        game = copy.deepcopy(self.game)
        self.exit_cleanup()
        if inputs['mode'] == 'PvP':
            self.new_state(PvP)
            self.initialization(game)
        elif inputs['mode'] == 'PvAI':
            self.new_state(PvAI)
            self.initialization(game,inputs['ai_player'])
            
    def receive_resumegame_inputs(self,inputs):
        if inputs['mode'] == 'PvP':
            self.to_PvP()
        elif inputs['mode'] == 'PvAI':
            self.ai_player = inputs['ai_player']
            self.to_PvAI()
        
    def new_game(self, item):    
        name = item.text()
        self.game = FIAR.FIAR.from_csv(name, folder = RECORDS_FOLDER)
        
    def change_game(self, item):
        self.item = item
        self.sounds.click()
        self.rmmpl()
        self.new_game(item)
        #self.view_index = self.game.df.shape[0]
        self.view_index = self.view_indices[self.item.text()]
        new_df = self.game.df.iloc[:self.view_index,:]
        viewed_game = FIAR.FIAR(df= new_df)
        self.newmpl(viewed_game)
        
    #TODO def Overlay_Toggle(self):
    def newmpl(self, game):
        self.plot = FIAR_Plot(game)
        if self.OverlayToggle.isChecked():
            analysis = FIAR_Analyzer.FIAR_Analyzer()
            analysis.new_game(game)
            PoTs = analysis.PoTs            
            self.plot.draw_PoTs(PoTs)     
        self.View_mpl_layout.addWidget(self.plot.canvas)
        self.plot.canvas.draw()

    def rmmpl(self):
        self.plot.canvas.ax.cla()
        self.View_mpl_layout.removeWidget(self.plot.canvas)
        # print("Closing Viewer canvas")
        self.plot.canvas.close()    
    
    def overlay_toggle(self):
        self.sounds.click()
        self.change_game(self.item)
        #self.rmmpl()
        # viewed_df = self.game.df.iloc[:self.view_index,:]
        # viewed_game = FIAR.FIAR(df= viewed_df)
        # self.plot = FIAR_Plot(viewed_game)
        # if self.OverlayToggle.isChecked():
        #     analysis = FIAR_Analyzer.FIAR_Analyzer()
        #     analysis.new_game(viewed_game)
        #     PoTs = analysis.PoTs            
        #     self.plot.draw_PoTs(PoTs)            
        # else: #it was unchecked
        #     pass
        # self.View_mpl_layout.addWidget(self.plot.canvas)
        # self.plot.canvas.draw()
    
    def to_PvP(self):
        '''
        State transition to PvP just like standard to_PvP() except without deletion of self.game

        Returns
        -------
        None.

        '''
        #Cleanup
        self.view_index = None
        self.analysis.clear()
        self.rmmpl()
        #state change
        self.new_state(PvP)
        #new state initialization
        self.initialization()
    
    def to_PvAI(self):
        '''
        State transition to PvAI just like standard to_PvAI() except without deletion of self.game

        Returns
        -------
        None.

        '''
        #Cleanup
        self.view_index = None
        self.analysis.clear()
        self.rmmpl()
        #state change
        self.new_state(PvAI)
        #new state initialization
        self.initialization()
#------------------------------------------------------------------------------

class NewGame_Dialogue(QNewGame, Ui_NewGame):
    def __init__(self, callback):
        super(NewGame_Dialogue, self).__init__()
        # print(f"NewGameDialogue type: {self.__class__}")
        self.callback = callback
        self.setupUi(self)
        self.update_state()
        self.NewGame_Play.clicked.connect(self.newgame_play)
        self.sounds = FIAR_Sounds()
    
    def update_state(self):
        mode = self.ModeSelector.currentText()
        self.new_state({'PvP':NewGame_PvP,
                        'PvAI':NewGame_PvAI}[mode])
    
    def new_state(self,newstate):
        self.__class__ = newstate
        if PRINT_STATE_TRANS:    
            print(f"Changed NewGame_Dialogue state to {self.__class__}")
    
    def newgame_play(self):
        '''Responds to the click of the Play button on the New Game Dialogue'''
        self.sounds.click()
        # print("Clicked newgame_play")
        self.update_state()
        self.save_data()
    
class NewGame_PvP(NewGame_Dialogue):
    def save_data(self):
        first_player = self.PvPFirstSelector.currentText().lower()
        output = {'mode':'PvP',
                  'first_player':first_player}
        self.callback(output.copy())
        self.reject()

class NewGame_PvAI(NewGame_Dialogue):
    def save_data(self):
        # Passes all of the settings to MainWindow
        first_player = self.PvAIFirstSelector.currentText().lower()
        ai_player = self.AIColorSelector.currentText().lower()
        output = {'mode':'PvAI',
                  'first_player':first_player,
                  'ai_player':ai_player}
        self.callback(output.copy())
        # closes itself
        self.reject()     
        
        
#------------------------------------------------------------------------------
class ResumeGame_Dialogue(QResumeGame, Ui_ResumeGame):
    def __init__(self, callback):
        super(ResumeGame_Dialogue, self).__init__()
        # print(f"NewGameDialogue type: {self.__class__}")
        self.callback = callback
        self.setupUi(self)
        self.update_state()
        self.ResumeGame_Play.clicked.connect(self.resumegame_play)
        self.sounds = FIAR_Sounds()
    
    def update_state(self):
        mode = self.ModeSelector.currentText()
        self.new_state({'PvP':ResumeGame_PvP,
                        'PvAI':ResumeGame_PvAI}[mode])
    
    def new_state(self,newstate):
        self.__class__ = newstate
        if PRINT_STATE_TRANS:    
            print(f"Changed NewGame_Dialogue state to {self.__class__}")
    
    def resumegame_play(self):
        '''Responds to the click of the Play button on the Resume Game Dialogue'''
        self.sounds.click()
        # print("Clicked resumegame_play")
        self.update_state()
        self.save_data()
    
class ResumeGame_PvP(ResumeGame_Dialogue):
    def save_data(self):
        output = {'mode':'PvP'}
        self.callback(output.copy())
        self.reject()

class ResumeGame_PvAI(ResumeGame_Dialogue):
    def save_data(self):
        # Passes all of the settings to MainWindow
        ai_player = self.AIColorSelector.currentText().lower()
        output = {'mode':'PvAI',
                  'ai_player':ai_player}
        self.callback(output.copy())
        # closes itself
        self.reject()     

#------------------------------------------------------------------------------
class SaveName_Dialogue(QSaveName, Ui_SaveName):
    def __init__(self, callback, namevalid):
        super(SaveName_Dialogue, self).__init__()
        # print(f"NewGameDialogue type: {self.__class__}")
        self.callback = callback
        self.namevalid = namevalid
        self.setupUi(self)
        self.sounds = FIAR_Sounds()
        # self.update_state()
        self.SaveName_Save.clicked.connect(self.save)
        self.SaveName_Name.installEventFilter(self)
        
    
    def save(self):
        '''Responds to the click of the Save button on the SaveName Dialogue'''
        self.sounds.click()
        # print("Clicked SaveName_Save button")
        # print(f"Entered text: {self.SaveName_Name.toPlainText()}")
        if self.namevalid(self.SaveName_Name.toPlainText()):
            # print('savename valid')
            output = self.SaveName_Name.toPlainText()
            # print(f"Passing Outputs to callback: {output}")
            self.callback(output)
            self.reject()
        else:
            print("Save name not valid")

    def eventFilter(self, obj, event):

        if event.type() == QEvent.KeyPress:
            # print(f"Pressed key: {event.key()}")
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                # print("Enter was pressed")
                self.SaveName_Save.click()
                return True
        return super(QSaveName, self).eventFilter(obj, event)

#------------------------------------------------------------------------------
class ViewerQuery_Dialogue(QViewerQuery, Ui_ViewerQuery):
    def __init__(self, callback_yes, callback_no):
        super(ViewerQuery_Dialogue, self).__init__()
        # print(f"NewGameDialogue type: {self.__class__}")
        self.callback_yes = callback_yes
        self.callback_no = callback_no
        self.setupUi(self)
        self.sounds = FIAR_Sounds()
        # self.update_state()
        self.Yes.clicked.connect(self.yes)
        self.No.clicked.connect(self.no)
        
    def yes(self):
        self.sounds.click()
        self.callback_yes()
        self.reject()
        
    def no(self):
        self.sounds.click()
        self.callback_no()
        self.reject()
        
if __name__ == '__main__':
    import sys
    from PyQt5 import QtWidgets

 
    app = QtWidgets.QApplication(sys.argv)
    main = FIAR_Main_Window()
    main.show()
    sys.exit(app.exec_())