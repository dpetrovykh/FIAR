#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 09:36:41 2021

@author: dpetrovykh
"""

from pydub import AudioSegment
from pydub.playback import play

AUDIO_FOLDER = 'audio/'

Sound_Settings = {'background':{'file':'sound_1.wav',
                                'slice':slice(None)},
                  'start':{'file':'sound_1.wav',
                           'slice':slice(100,500)},
                  'click':{'file':'sound_1.wav',
                           'slice':slice(100,150)},
                  'victory':{'file':'sound_1.wav',
                             'slice':slice(None)},
                  'move':{'file':'sound_1.wav',
                          'slice':slice(0,100)},
                  'end':{'file':'sound_1.wav',
                         'slice':slice(1000,1200)},
                  'defeat':{'file':'sound_1.wav',
                            'slice':slice(1500,1800)}
                  }

class FIAR_Sounds():
    def __init__(self, SndSets = Sound_Settings):
        self.click_sound = self._setup_sound('click',SndSets)
        self.start_sound = self._setup_sound('start',SndSets)
        self.victory_sound = self._setup_sound('victory',SndSets)
        self.move_sound = self._setup_sound('move',SndSets)
        self.end_sound = self._setup_sound('end',SndSets)
        self.defeat = self._setup_sound('defeat',SndSets)

    def click(self):
        play(self.click_sound)
        
    def move(self):
        play(self.move_sound)
        
    def victory(self):
        play(self.victory_sound)
        
    def start(self):
        play(self.start_sound)
        
    def end(self):
        play(self.end_sound)
        
    def defeat(self):
        play(self.defeat_sound)
        
    def _setup_sound(self, name, SndSets):
        return self._load_wav(SndSets[name]['file'])[SndSets[name]['slice']]

    def _load_wav(self,file,folder=AUDIO_FOLDER):
        return AudioSegment.from_wav(folder+file)

if __name__=='__main__':
    sounds = FIAR_Sounds()
    sounds.victory()