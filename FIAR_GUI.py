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
from datetime import datetime

import FIAR
from FIAR import OutOfBounds, RepeatMove
from FIAR_Plot import FIAR_Plot
from FIAR_Saves import FIAR_Saves, RECORDS_FOLDER, EmptySaveSlot, METADATA_TEMPLATE
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
        metadata = copy.deepcopy(METADATA_TEMPLATE)
        newgame_window = NewGame_Dialogue(callback=self.to_Play,
                                          namevalid= self.saves.valid_text,
                                          metadata=metadata)
        newgame_window.exec_()
        # If dialogue interaction is successful, then MainMenu.receieve_newgame_inputs() gets called by dialogue.
 
    def to_Play(self, metadata, other_data):
        self.sounds.click()
        game = FIAR.FIAR(first_player = other_data['first_player'])
        self.exit_cleanup()
        if metadata['mode'] == 'PvP':
            self.new_state(PvP)
            self.initialization(game, metadata)
        elif metadata['mode'] == 'PvAI':
            self.new_state(PvAI)
            self.initialization(game, metadata, other_data['ai_player'])
        else:
            raise ValueError("odd mode")
                
    
class Play(FIAR_Main_Window):
    def initialization(self,game, metadata):
        self.game = game
        self.metadata = metadata
        print(f"Metadata for new game: {metadata}")
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
        self.metadata = None
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
        next_player_name = self.metadata[self.game.next_player+'_player']
        self.NextPlayerLabel.setText(next_player_name)    
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
        #print(f"received normalized position of click, from left: {from_left}, from_top: {from_top}")
        ## Calculate distance from left and top in cells
        cell_width = self.plot.disp_width #width of plot in cells
        cell_height = self.plot.disp_height #height of plot in cells
        c_left = from_left*cell_width #distance in cells from left edge
        c_top = from_top*cell_height #distance in cells from top edge
        #print(f"Cell distance from...top: {c_top}, left: {c_left}")
        #print(f"left_edge: {self.plot.disp_edges['left']}, top_edge: {self.plot.disp_edges['top']}")
        x = c_left+self.plot.disp_edges['left'] # decimal x distance in cells from x,y origin
        y = self.plot.disp_edges['top']-c_top # decimal y distance in cells from x,y origin
        x_cell = round(x)
        y_cell = round(y)
        #print(f"calculated final move of x: {x_cell}, y: {y_cell}")
        ## Make a move with these new_found move coordinates.
        self.auto_move(x_cell,y_cell)
        print(f"metadata: {self.metadata}")
    
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
                                        namevalid= self.saves.valid_save_name,
                                        metadata=self.metadata)
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
        ## function which is called upon pressing the "Save" button while playing in either PvP or PvAI mode
        # make click sound
        self.sounds.click()
        ## collect part of metadata that will be neccessary to create a proper save later
        ## Pop up saveName dialogue
        savename_window = SaveName_Dialogue(callback= self.to_Saving,
                                            namevalid= self.saves.valid_save_name, 
                                            metadata= self.metadata)
        savename_window.exec_()
    
    def gen_metadata(self):
        metadata = copy.deepcopy(METADATA_TEMPLATE)
        metadata['mode'] = self.get_mode()
        metadata['datetime'] = datetime.now()
        metadata['num_moves'] = self.game.num_moves
        return metadata
    
    def to_Saving(self,metadata):
        game = copy.deepcopy(self.game)
        print(f"game: {game}")
        ## Cleanup
        self.exit_cleanup()
        print(f"game: {game}")
        ## transition to Saving state
        self.new_state(Saving)
        self.initialization(game, metadata)
    
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
        
    def get_mode(self):
        print(f"type(self): {type(self)}")
        return {PvP:'PvP', PvAI:'PvAI'}[type(self)]
        
        
class PvP(Play):        
    def initialization(self, game, metadata):
        super(PvP, self).initialization(game, metadata)
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
            self.metadata['datetime'] = datetime.now()
            self.metadata['num_moves'] = self.game.num_moves
            metadata = copy.deepcopy(self.metadata)
            metadata['name'] = 'autosave'
            self.saves.autosave(self.game, metadata)
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
    def initialization(self, game, metadata, ai_player):
        super(PvAI, self).initialization(game, metadata)
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
            self.metadata['datetime'] = datetime.now()
            self.metadata['num_moves'] = self.game.num_moves
            metadata = copy.deepcopy(self.metadata)
            metadata['name'] = 'autosave'
            self.saves.autosave(self.game, metadata)
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
        Save1_button_suite = {'player1':self.Save1_Player1,
                              'player2':self.Save1_Player2,
                              'move':self.Save1_Move,
                              'date':self.Save1_Date}
        self.label_button_suite(1,Save1_button_suite)
    
    def label_button_suite(self, listing_id, button_suite):
        metadata = self.saves.get_metadata(listing_id)
        button_suite['player1'].setText(f"{metadata['red_player']}")
        button_suite['player1'].setStyleSheet("color: red")
        button_suite['player2'].setText(f"{metadata['black_player']}")
        button_suite['player2'].setStyleSheet("color: black")
        button_suite['move'].setText(f"Moves: {metadata['num_moves']}")
        button_suite['date'].setText(f"{metadata['datetime'].strftime('%-I:%-M %p %b %-d,%Y')}")
        
            
    def exit_cleanup(self):
        self.game = None
        for button, desc in [(self.Autosave, 'autosave'),
                             (self.Save1, "Save 1"), 
                             (self.Save2, "Save 2"), 
                             (self.Save3, "Save 3"), 
                             (self.Saves_MainMenu, "Main_Menu")]:
            try:
                button.clicked.disconnect()
            except TypeError:
                print(f"Failed to disconnect button {desc}")


class Saving(Saves):
    def initialization(self, game, metadata):
        super(Saving, self).initialization()
        print("Entered Saving State")
        self.game = game
        print(f"Saving received game: {game}")
        self.metadata = metadata
        # print("Performing Saving initialization")
        # Tell the player to choose a slot to save in
        self.Saves_Banner.setText("Please select a save location for your game")
        self.Autosave.clicked.connect(self.sounds.click)
        self.Save1.clicked.connect(partial(self.save_game, listing_id = 1))
        self.Save2.clicked.connect(partial(self.save_game, listing_id = 2))
        self.Save3.clicked.connect(partial(self.save_game, listing_id = 3))
        
    def exit_cleanup(self):
        super(Saving, self).exit_cleanup()
        self.metadata = None
        
    def save_game(self, listing_id):
        print("calling Saving.save_game()")
        self.sounds.click()
        # Save the current game
        self.saves.save_game(game=self.game,
                             metadata=self.metadata,
                             listing_id = listing_id)
        self.state_trans(MainMenu)
        
    def label_button(self, button, listing_id):
        if self.saves.get_name(listing_id) != None:
            button.setText("Overwrite - " +self.saves.get_name(listing_id))
        else:
            button.setText("Save in Empty Slot")
        
        
class Loading(Saves):
    def initialization(self):
        super(Loading, self).initialization()
        print("Entered Loading State")
        # print("Performing Loading initialization")
        self.set_frame(SAVEDGAMES)
        # Tell the user to choose a slot to load
        self.Saves_Banner.setText("Please select a game to load")
        self.Autosave.clicked.connect(partial(self.load_game, listing_id='auto'))
        self.Save1.clicked.connect(partial(self.load_game, listing_id = 1))
        self.Save2.clicked.connect(partial(self.load_game, listing_id = 2))
        self.Save3.clicked.connect(partial(self.load_game, listing_id = 3))
        
    def load_game(self, listing_id):
        print("calling Loading.load_game()")
        self.sounds.click()
        try:
            self.game = self.saves.load_game(listing_id)
        except EmptySaveSlot as ex:
            print(ex.message)
        else:
            metadata = self.saves.get_metadata(listing_id)
            resumegame_window = ResumeGame_Dialogue(callback = self.to_Play,
                                                    validname = self.saves.valid_save_name,
                                                    metadata = metadata)
            resumegame_window.exec_()
        
    def exit_cleanup(self):
        super(Loading, self).exit_cleanup()
        
    def label_button(self, button, listing_id):
        if self.saves.get_name(listing_id) != None:
            button.setText("Load - " +self.saves.get_name(listing_id))
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
     
    def to_Play(self, metadata, other_data):
        game = copy.deepcopy(self.game)
        self.exit_cleanup()
        if other_data['mode'] == 'PvP':
            self.new_state(PvP)
            self.initialization(game, metadata)
        elif other_data['mode'] == 'PvAI':
            self.new_state(PvAI)
            self.initialization(game, metadata, other_data['ai_player'])
            
    
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
    ''' Dialogue window which saves chosen settings for a new game.
    metadata is a dictionary with game properties.
    callback gets passed the updated metadata upon passing through this dialogue.
    '''
    def __init__(self, callback, namevalid, metadata):
        super(NewGame_Dialogue, self).__init__()
        # print(f"NewGameDialogue type: {self.__class__}")
        self.callback = callback
        self.namevalid = namevalid
        self.metadata = copy.deepcopy(metadata)
        self.metadata['name'] = 'autosave'
        self.metadata['datetime'] = datetime.now()
        self.metadata['num_moves'] = 0
        self.setupUi(self)
        self.update_state()
        self.NewGame_Play.clicked.connect(self.newgame_play)
        self.sounds = FIAR_Sounds()
    
    def update_state(self):
        ## read the selected text from a combobox and apply the relevant state to the dialogue box
        mode = self.ModeSelector.currentText()
        self.new_state({'PvP':NewGame_PvP,
                        'PvAI':NewGame_PvAI}[mode])
    
    def new_state(self,newstate):
        ## Modifies the state of the dialogue
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
        ## Saves the selections made in the dialogue and sends them to the callback
        first_player = self.PvPFirstSelector.currentText().lower()
        red_player = self.PvP_RedPlayer.toPlainText()
        black_player = self.PvP_BlackPlayer.toPlainText()
        if self.namevalid(red_player) and self.namevalid(black_player):
            self.metadata['mode'] = 'PvP'
            self.metadata['red_player'] = red_player
            self.metadata['black_player'] = black_player
            other_data = {'first_player': first_player}
            self.callback(self.metadata, other_data)
            self.reject()

class NewGame_PvAI(NewGame_Dialogue):
    def save_data(self):
        ## Saves the selections made in the dialogue and sends them to the callback
        first_player = self.PvAIFirstSelector.currentText().lower()
        ai_player = self.AIColorSelector.currentText().lower()
        player_name = self.PvAI_PlayerName.toPlainText()
        if self.namevalid(player_name):
            self.metadata['mode'] = 'PvAI'
            if ai_player == 'red':
                self.metadata['red_player'] = 'AI'
                self.metadata['black_player'] = player_name
            elif ai_player == 'black':
                self.metadata['red_player'] = player_name
                self.metadata['black_player'] = 'AI'
            other_data = {'ai_player': ai_player,
                          'first_player': first_player}
            self.callback(self.metadata, other_data)
            # closes itself
            self.reject()     
        
        
#------------------------------------------------------------------------------
class ResumeGame_Dialogue(QResumeGame, Ui_ResumeGame):
    def __init__(self, callback, validname, metadata):
        super(ResumeGame_Dialogue, self).__init__()
        # print(f"NewGameDialogue type: {self.__class__}")
        self.callback = callback
        self.validname = validname
        self.metadata = copy.deepcopy(metadata)
        self.setupUi(self)
        # Set combobox state to mode in metadata
        if metadata['mode']:
            mode_index = {'PvP':0,'PvAI':1}[metadata['mode']]
            print(f"mode_index: {mode_index}")
            self.ModeSelector.setCurrentIndex(mode_index)
            self.stackedWidget.setCurrentIndex(mode_index)
        self.update_state()
        self.display_metadata(self.metadata)
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
    def display_metadata(self, metadata):
        # Set redname to previous value
        if metadata['red_player']:
            self.PvP_RedPlayer.setPlainText(metadata['red_player'])
        # Set black name to previous value
        if metadata['black_player']:
            self.PvP_BlackPlayer.setPlainText(metadata['black_player'])
    
    def save_data(self):
        other_data = {'mode':'PvP'}
        self.metadata['red_player'] = self.PvP_RedPlayer.toPlainText()
        self.metadata['black_player'] = self.PvP_BlackPlayer.toPlainText()
        self.metadata['mode'] = 'PvP'
        self.callback(copy.deepcopy(self.metadata), other_data.copy())
        self.reject()

class ResumeGame_PvAI(ResumeGame_Dialogue):
    def display_metadata(self, metadata):
        if metadata['red_player'] !=None:
        ## Set combobox value for AI color
            ai_color = None
            player_name = None
            if metadata['red_player'] == "AI":
                ai_color = "red"
                player_name = metadata['black_player']
            elif metadata['black_player'] == "AI":
                ai_color = "black"
                player_name = metadata['red_player']
            else:
                raise Exception
            ai_color_index = {'red':0,'black':1}[ai_color]
            self.AIColorSelector.setCurrentIndex(ai_color_index)
            self.PvAI_PlayerName.setPlainText(player_name)
    
    def save_data(self):
        ai_player = self.AIColorSelector.currentText().lower()
        other_data = {'mode':'PvAI',
                  'ai_player':ai_player}
        ai_color_label = {'red':'red_player',
                          'black':'black_player'}[ai_player]
        player_color_label = {'red_player':'black_player',
                              'black_player':'red_player'}[ai_color_label]
        self.metadata[ai_color_label] = "AI"
        self.metadata[player_color_label] = self.PvAI_PlayerName.toPlainText()
        self.metadata['mode'] = 'PvAI'
        self.callback(copy.deepcopy(self.metadata), other_data.copy())
        # closes itself
        self.reject()     

#------------------------------------------------------------------------------
class SaveName_Dialogue(QSaveName, Ui_SaveName):
    def __init__(self, callback, namevalid, metadata):
        super(SaveName_Dialogue, self).__init__()
        # print(f"NewGameDialogue type: {self.__class__}")
        self.callback = callback
        self.namevalid = namevalid
        self.metadata = copy.deepcopy(metadata)
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
            self.metadata['name'] = self.SaveName_Name.toPlainText()
            # print(f"Passing Outputs to callback: {output}")
            self.callback(self.metadata)
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