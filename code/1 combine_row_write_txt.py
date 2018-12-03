# -*- coding: utf-8 -*-
"""
1.

NLP system for NIMH notes

@author: hpan
"""

import os
import csv
import pandas as pd
os.chdir('Z:/project')

#%%

notes = pd.read_csv("./notes/309NOTES_simp2.csv", keep_default_na=False)

pat_id_list = [notes['PAT_VISIT'][0]]    # PAT_ID to PAT_VISIT
text_list = [notes['TEXT'][0]]

for pat_id, text in zip(notes['PAT_VISIT'][1:], notes['TEXT'][1:]):
    if pat_id == pat_id_list[-1]:        # If pad_id matches the last value in pat_id_list,
        text_list[-1] += ". \n\n\n section:  section. " \
        "\n----------------------------------------------------------------------------------------------------" \
        "\n####################################################################################################" \
        "\n____________________________________________________________________________________________________" \
        "\n----------------------------------------------------------------------------------------------------" \
        "\n section:  section. \n\n\n" + str(text) # add text to the last value in text_list
    else:  # Otherwise add a new row with the values
        pat_id_list.append(pat_id)
        text_list.append(text)

## Create a new dataframe using these result lists
notes2 = pd.DataFrame({'PAT_VISIT': pat_id_list, 'TEXT': text_list})
notes2.to_csv("./notes/309NOTES_join3.csv", sep='|', index=False)






#%%
## Write csv file dataframe to seperate text file with PAT_VISIT as the file name.
docs_text = pd.read_csv("./notes/309NOTES_join3.csv", sep='|', lineterminator='\n')
#print(docs_text.head())
#docs_text = pd.read_csv("./309NOTES_join1.csv", sep='|', keep_default_na=False)  #, nrows=10
path = "./notes"
for index, row in docs_text.iterrows():
    new_file_path_txt = path+"/"+str(row[0]) + ".txt"     
    f=open(new_file_path_txt, "w")
    f.write(row[1])
    f.close()
