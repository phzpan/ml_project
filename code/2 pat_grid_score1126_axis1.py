# -*- coding: utf-8 -*-
"""
2. 

NLP system for NIMH notes

@author: hpan
"""

import re
import os
import csv
import pandas as pd
#%%
# Change to working directory
os.getcwd()
os.chdir('Z:/project')

# Read Grid file
std = pd.read_csv("./KB/371-KIOUS-Patient-Grid-Plain-fill_1116.csv") #, nrows=5
std = std.fillna('nav')

# Read csv to dataframe and change to a dictionary with keywords and their score.
ann_target_score = pd.read_csv("./KB/NIMH_target_score_1116.csv", sep='$')   # to lowercase
score= {str(x[0]).lower(): x[1] for x in ann_target_score.itertuples(index=False)}

#%%
# Sum score for each row and add to the score list
score_list=[]

for index, row in std.iterrows():
    score1=0
    for i in [15,16,17,18,19,10,21,39]:
        try:
            score1 = score1 + score[row[i].lower()]
        except:
            #print("{} not in dict" .format(row[i]))
            print(row[i])
            #pass
    score_list.append(score1)
        #print (i)
        
#%%
# Add score to the Grid dataframe
se = pd.Series(score_list)
std['r_score_axis'] = se.values

#%%
 
std.to_csv('./KB/371-KIOUS-Patient-Grid-Plain-fill_1116_score_axis.csv', index=False)

#%%
# add files size to the dataframe table

std1 = pd.read_csv("./KB/371-KIOUS-Patient-Grid-Plain-fill_1116_score_axis.csv")
patvisit = std1['PAT_VISIT']
path = 'Z:/project/notes'
filesizes = []
for pid in patvisit:
    fname=pid + ".txt"
    try:
        filesize = os.path.getsize(os.path.join(path,fname))
        filesize = filesize//1000
    except:
        filesize = 0
    filesizes.append(filesize)
    
se1 = pd.Series(filesizes)
std1['fsize'] = se1.values

#%%
std1.to_csv('./KB/371-KIOUS-Patient-Grid-Plain-fill_1116_score_size_axis.csv', index=False)
