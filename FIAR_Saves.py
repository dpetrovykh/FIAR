#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 10:37:03 2021

@author: dpetrovykh
"""

import pickle
import os
from copy import deepcopy
from datetime import datetime

import FIAR


SAVE_FOLDER = 'saves'
RECORDS_FOLDER = 'records'
LISTING_NAME = "save_listing.p"


METADATA_TEMPLATE = {'name': None,
                  'mode': None,
                  'datetime': None,
                  'num_moves':None,
                  'red_player': None,
                  'black_player': None}
LISTING_TEMP = {key:deepcopy(METADATA_TEMPLATE) for key in ['auto',1,2,3]} #template from which to create a save listing if none exists or if it is corrupt

class EmptySaveSlot(Exception):
    def __init__(self, message=None):
        super(EmptySaveSlot, self).__init__()
        self.message = message
        

class FIAR_Saves():
    '''
    FIAR_Saves manages FIAR's save slots. It allows for both saving and loading of games. Metadata associated with games, such as their names or who was playing them, is saved by using the pickle module.
    '''
    def __init__(self):
        # # try to open up existing pickled file listing
        # try:
        #     self.listing = self.depickle_listing()
        #     if not self.listing_valid(self.listing):
        #         raise Exception('Listing not valid')
        # except:
        #     # old pickled listing must be invalid or nonexistent. A new one is created.
        #     print("Old listing invalid or non-existent. New listing being created.")
        #     self.listing = self.new_listing()
        #     # Save the listing to a file
        #     self.pickle_listing(self.listing)         
            
        ## Try to open a listing file.
        try:
            self.listing = self.depickle_listing()
        # If we are unable to read a listing file:
        except: #failed to open listing
            # Create a completely new listing
            print("Failed to depickle listing.")
            print("Creating and pickling new listing...")
            self.listing = self.new_listing()
            self.pickle_listing(self.listing)
            print("...new listing created and pickled.")
        # else #we are able to read the listing file
        else:
            print("Listing successfully depickled.")
            #for each metadata
            for listing_id, metadata in self.listing.items():
                # if the metadata is not empty
                if not self.metadata_empty(metadata):
                    # if a corresponding game does not exist
                    if not (metadata['name'] in self.list_all_saves()):
                        # Delete the metadata
                        print(f"No save file found for listing_id: {listing_id}, name: {metadata['name']}...")
                        print("...deleting metadata")
                        self.wipe_metadata(listing_id)
                    # elif the metadata is invalid:
                    elif not self.valid_metadata(metadata):
                        print(f"Invalid metadata for listing_id: {listing_id}, name: {metadata['name']}")
                        # delete the save file with metadata
                        print("...deleting save and metadata.")
                        self.delete_listed_save(listing_id)
                    # else # the save file and metadata are fine
                    else: #save file and metadata are good
                        # all good
                        pass
                else: #metadata is empty
                    pass
            self.pickle_listing(self.listing)
                    
        
    def pickle_listing(self, listing, folder= SAVE_FOLDER):
        ## saves the provided listing to a pickle file
        pickle.dump( listing, open( folder+'/'+LISTING_NAME, "wb" ) )

    def depickle_listing(self, folder=SAVE_FOLDER):
        ## loads a listing from a specified pickle file
        return pickle.load( open( folder+'/'+LISTING_NAME, "rb" ) )
    
    def listing_valid(self,listing):
        ## Checks to see if all of the save names in the provided listing are valid
        #List all csv files that represent saved games. The listed saves may be a subset of all saves.
        all_saves = self.list_all_saves()
        # For each listing in the provided listing
        for listing_id in listing.keys():
            # if the save slot is occupied
            if not self.slot_empty(listing_id):
                # if this listed save is not within all_saves
                if self.get_name(listing_id) not in all_saves:
                    # at least one listed save is not valid, so the listing is invalid
                    return False
        # all of the listed save slots had corresponding save files, so the listing is valid.
        return True
    
    def slot_empty(self, listing_id):
        ## Returns True if the save slot corresponding to the provided listing_id is empty
        # The 'name' field should always be filled out for an occupied slot.
        return self.get_name(listing_id) == None
    
    def new_listing(self, delete_extras = False):
        '''
        Generates a new listing from existing games and deletes any extras

        Side-Effects
        ------------
        Deletes any saves for which there is not room in the finite save listing.
        
        Returns
        -------
        A listing object

        '''
        # Obtain list of saves
        all_saves = self.list_all_saves()
        # Create empty save_listing
        listing = deepcopy(LISTING_TEMP)
        print(f"listing: {listing}")
        if 'autosave' in all_saves:
            #update autosave listing
            self.set_name('auto', 'autosave', listing)
            # remove 'autosave' listing from list of saves
            all_saves.remove('autosave')
        ## for each empty spot in listing, place a game there
        # for each slot
        for listing_id in listing.keys():
            # if the slot is not the 'autosave' slot
            if listing_id != 'auto':
                try:
                    # try to take a savename and apply it to the currently-considered slot
                    self.set_name(listing_id, all_saves.pop(0), listing)
                except IndexError: #popping from empty list. i.e. There are no more save files.
                    # exit the for loop
                    break
        # If the option to delete save files not fitting into the 4 slots is selected
        if delete_extras:
            # delete all save files left in the all_saves list
            self.delete_save_files(all_saves)
        # return the completed new listing
        return listing
                
    def delete_save_files(self, saves, folder=SAVE_FOLDER):
        for save in saves:
            try:
                os.remove(folder+'/'+save+'.csv')
            except:
                print(f"Failed to delete {folder}/{save}.csv")
    
    def delete_listed_save(self, listing_id):
        print(f"Deleteing save with id: {listing_id}")
        old_save = self.get_name(listing_id)
        # if previous metadata has a name (i.e. exists)
        if old_save != None:
            # delete the associated csv
            self.delete_save_files([old_save])
        # Remove save from listing and replace it with empty metadata template
        self.listing[listing_id] = deepcopy(METADATA_TEMPLATE)        
        # Save listing
        self.pickle_listing(self.listing)
    
    def list_all_saves(self, folder = SAVE_FOLDER):
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
    
    def list_all_records(self):
        return self.list_all_saves(folder = RECORDS_FOLDER)
    
    def list_saves(self):
        #return list(self.listing.values())
        return [metadata['name'] for metadata in self.listing.values()]
    
    def get_name(self, listing_id):
        assert listing_id in LISTING_TEMP.keys()
        return self.listing[listing_id]['name']
    
    def get_metadata(self, listing_id):
        assert listing_id in LISTING_TEMP.keys()
        return deepcopy(self.listing[listing_id])
    
    def set_name(self, listing_id, savename, listing = None):
        if listing == None:
            self.listing[listing_id]['name'] = savename
        else:
            listing[listing_id]['name'] = savename
    
    def load_game(self, listing_id, folder=SAVE_FOLDER):
        save_name = self.get_name(listing_id)
        if save_name == None:
            raise EmptySaveSlot("This save slot is empty")
        else:
            return FIAR.FIAR.from_csv(save_name, folder=folder)

    def save_game(self, game, metadata, listing_id, folder=SAVE_FOLDER):
        # Delete old file
        old_savename = self.get_name(listing_id)
        if old_savename != None:
            self.delete_save_files([old_savename])
        # Save new file
        savename = metadata['name']
        game.to_csv(savename, folder=folder)
        #print(f"metadata: {metadata}")
        ## Update listing properties
        for name, prop in metadata.items():
            # if the property is defined in the provided metadata
            if prop != None:
                # overwrite the property in the current listing.
                self.listing[listing_id][name] = prop
        # save listing
        self.pickle_listing(self.listing)
        
    def save_record(self, game, savename, folder=RECORDS_FOLDER):
        game.to_csv(savename, folder=folder)
    
    def autosave(self, game, metadata):
        self.save_game(game, metadata,'auto')
        
    def load_autosave(self):
        return self.load_game('auto')
    
    def wipe_metadata(self, listing_id):
        ## Replaces metadata in self.listing at listing_id key with default metadata
        self.listing[listing_id] = deepcopy(METADATA_TEMPLATE)
    
    def valid_metadata(self, metadata):
        try:
            assert self.valid_text(metadata['name'])
            assert metadata['mode'] in ['PvP','PvAI']
            assert type(metadata['datetime']) == datetime
            assert type(metadata['num_moves']) == int and metadata['num_moves']>=0
            assert self.valid_text(metadata['red_player'])
            assert self.valid_text(metadata['black_player'])
            return True
        except:
            return False
        
    def metadata_empty(self, metadata):
        try:
            for value in metadata.values():
                if value != None:
                    raise ValueError
            return True
        except ValueError:
            return False
    
    def valid_save_name(self,name):
        try:
            assert self.valid_text(name)
            assert name not in self.list_saves()
            return True
        except:
            return False

    def valid_text(self, text):
        unwanted_chars = ['.', ',', '/', '~','!','@','#','$','%','^','&','*','(',')','-','+','=','`',"\\",'[',']','{','}',';',':','"',"'",'?','<','>']
        try:
            assert len(text)>0
            assert len(text)<20
            assert len(text.split())<2
            # print(f"len({name}) = {len(name)}")
            for char in unwanted_chars:
                assert char not in text
            return True
        except:
            return False        

    @staticmethod
    def del_pickles(filename = LISTING_NAME, folder=SAVE_FOLDER):
        os.remove(folder+'/'+filename)