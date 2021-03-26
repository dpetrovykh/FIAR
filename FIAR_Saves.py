#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 10:37:03 2021

@author: dpetrovykh
"""

import pickle
import os

import FIAR


SAVE_FOLDER = 'saves'
RECORDS_FOLDER = 'records'
LISTING_NAME = "save_listing.p"

LISTING_TEMP = {'auto':None,
                1:None,
                2:None,
                3:None}

class EmptySaveSlot(Exception):
    def __init__(self, message=None):
        super(EmptySaveSlot, self).__init__()
        self.message = message

class FIAR_Saves():
    def __init__(self):
        pass
        # try to open up pickle file listing
        try:
            self.listing = self.depickle_listing()
            if not self.listing_valid(self.listing):
                raise Exception('Listing not valid')
        except:
            print("Old listing invalid or non-existent. New listing being created.")
            self.listing = self.new_listing()
            self.pickle_listing(self.listing)
        # If there is no pickle file listing:
            # Create new pickle listing
            
        
    def pickle_listing(self, listing, folder= SAVE_FOLDER):
        pickle.dump( listing, open( folder+'/'+LISTING_NAME, "wb" ) )

    def depickle_listing(self, folder=SAVE_FOLDER):
        return pickle.load( open( folder+'/'+LISTING_NAME, "rb" ) )
    
    def listing_valid(self,listing):
        ## Checks to see if all of the save names are valid
        all_saves = self.list_all_saves()
        for key,val in listing.items():
            if val != None:
                if val not in all_saves:
                    return False
        return True
    
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
        listing = LISTING_TEMP.copy()
        if 'autosave' in all_saves:
            listing['auto'] = 'autosave'
            all_saves.remove('autosave')
        # for each empty spot in listing, place a game there
        for key in listing.keys():
            if key != 'auto':
                try:
                    listing[key] = all_saves.pop(0)
                except IndexError: #popping from empty list
                    break

        if delete_extras:
            self.delete_save_files(all_saves)
        return listing
                
    def delete_save_files(self, saves, folder=SAVE_FOLDER):
        for save in saves:
            try:
                os.remove(folder+'/'+save+'.csv')
            except:
                print(f"Failed to delete {folder}/{save}.csv")
    
    def delete_listed_save(self, listing_id):
        # Delete file
        old_save = self.listing[listing_id]
        if old_save != None:
            self.delete_save_files([old_save])
        # Remove save from listing
        self.listing[listing_id] = None        
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
        return list(self.listing.values())
    
    def load_game(self, listing_id, folder=SAVE_FOLDER):
        save_name = self.listing[listing_id]
        if save_name == None:
            raise EmptySaveSlot("This save slot is empty")
        else:
            return FIAR.FIAR.from_csv(save_name, folder=folder)

    def save_game(self, game, savename, listing_id, folder=SAVE_FOLDER):
        # Delete old file
        old_save = self.listing[listing_id]
        if old_save != None:
            self.delete_save_files([old_save])
        # Save new file
        game.to_csv(savename, folder=folder)
        #Update listing
        self.listing[listing_id] = savename
        # save listing
        self.pickle_listing(self.listing)
        
    def save_record(self, game, savename, folder=RECORDS_FOLDER):
        game.to_csv(savename, folder=folder)
    
    def autosave(self,game):
        self.save_game(game, 'autosave','auto')
        
    def load_autosave(self):
        return self.load_game('auto')
    
    def valid_save_name(self,name):
        try:
            assert len(name)>0
            # print(f"len({name}) = {len(name)}")
            assert name not in self.list_saves()
            filename = 'name'+'.qwbd'
            open(filename,'w+')
            os.remove(filename)
            return True
        except:
            return False

    @staticmethod
    def del_pickles(filename = LISTING_NAME, folder=SAVE_FOLDER):
        os.remove(folder+'/'+filename)
        