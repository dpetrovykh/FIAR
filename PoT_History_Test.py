#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 07:30:43 2021

@author: dpetrovykh
"""

from FIAR import FIAR
from FIAR_Saves import RECORDS_FOLDER
from FIAR_Analyzer import FIAR_Analyzer
import pandas as pd

# master_game = FIAR()
# ## Make some moves
# master_game.move(0,0)
# master_game.move(1,1)
# master_game.move(-1,1)
# master_game.move(1,0)
# master_game.move(1,-1)
# master_game.move(-2,2)
# master_game.move(0,2)

## Import a game to analyze
game = FIAR.from_csv('Assy_Lassie',RECORDS_FOLDER)
## Analysis
analysis = FIAR_Analyzer(game)
analysis.update_PoT_History()
df = analysis.PoT_History
## Look
print(df)

import seaborn as sns
# sns.lineplot(data = df, x='marker',hue='player')
df_black = df[df.player == 'black']
# sns.lineplot(data=df_black)


df_sum = pd.DataFrame()
df_sum['marker'] = df['marker']
df_sum['powers'] = df['softPower'] + df['hardPower']
df_sum['threats'] = df['softThreat'] + df['hardThreat']
df_sum['player'] = df['player']
df_sum.set_index('marker')

df_sum_melt = pd.melt(df_sum, 
        id_vars = ['marker','player'],
        value_vars = ['powers','threats'],
        value_name = 'count')

sns.lineplot(data=df_sum_melt, x = 'marker', y='count', hue='player', style='variable')

