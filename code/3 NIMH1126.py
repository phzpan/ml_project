# -*- coding: utf-8 -*-
"""
3.

NLP system for NIMH notes

@author: hpan
"""
#%%
# Import libs

import re
import os
import csv
import pandas as pd
import codecs
import chardet
#from nltk.tokenize import sent_tokenize #trim sentence problem
from PyRuSH.RuSH import RuSH
#%%
class Annotation(object):
    def __init__(self, start_index=-1, end_index=-1, type='Annotation', spanned_text='', ann_id=0):
        self.ann_id = ann_id
        self.start_index = start_index
        self.end_index = end_index
        self.type = type
        self.spanned_text = spanned_text
        self.linked_document = None
        self.attributes=dict()
    def toString(self, doc_text=''):
        line = str(self.ann_id)
        attrs = ''
        for key in self.attributes.keys():
            att = ''
            if isinstance(self.attributes.get(key), Annotation):
                att = self.attributes.get(key).spanned_text
            else:
                att = str(self.attributes.get(key))
            attrs = attrs + '[' + key + ':' + att +']'
        line = line + ' ' + str(self.type)
        line = line + ' ' + str(self.start_index)
        line = line + ' ' + str(self.end_index)
        if self.spanned_text == '':
            if len(doc_text)>self.end_index:
                self.spanned_text = doc_text[self.start_index: self.end_index]
        line = line + ' ' + self.spanned_text
        line = line + ' ' + attrs
        return line
    
class Document(object):
    def __init__(self, document_id=-1, text=''):
        self.document_id = document_id
        self.text = text
        self.annotations = []
        self.attributes = dict()
    def toString(self):
        line = ''
        delimiter = '\r\n-------\r\n'
        for a in self.annotations:
            line = line + a.toString(self.text)+ '\r\n'
        return str(self.document_id) + delimiter+ self.text + delimiter +line

#%%
os.getcwd()

os.chdir('Z:/project')

class NLPClassificationSystem:
    def __init__(self):
        #initiate necessary components        
        self.target_rules=self.getTargetRegexes()        
        self.negation_rules = self.getNegRegexes()
        self.section_rules = self.getSectionRegexes() # new
        self.target_scores = self.target_score() # new
        self.sentence_rules='KB/rush_rules.tsv'
        self.sentence_segmenter = RuSH(self.sentence_rules)
                
    def process(self, document):
        # document.text = self.filterSection(document.text) # new
        document_id = document.document_id
        ann_index=0
        #---------
        #all_sent = sent_tokenize(document.text)
        sentences=self.sentence_segmenter.segToSentenceSpans(document.text)
        #sent_begin = 0
        for sentence in sentences:   
            sent=document.text[sentence.begin:sentence.end].lower()
        #---------
            for reg in self.target_rules:
                for match in reg.finditer(sent):
                    ann_id = 'NLP_'+ document_id + '_' + str(ann_index)    #str(document_id) if document_id is numeric use this
                    ann_index=ann_index+1
                    new_annotation = Annotation(start_index=int(match.start()+sentence.begin), 
                                        end_index=int(match.end()+sentence.begin), 
                                        type='psy_ann',
                                        ann_id = ann_id
                                        )
                    new_annotation.spanned_text = match.group() 
                    #new_annotation.spanned_text = sent[new_annotation.start_index:new_annotation.end_index]
                    
                    for neg_regex in self.negation_rules:
                        if re.search(neg_regex, sent):
                            new_annotation.attributes["Negation"] ="Negated"
    
                    document.annotations.append(new_annotation)
            #sent_begin = sent_begin + len(sent)
        return document 
    
    def getTargetRegexes(self):
        target_regexes = []
        with open('./KB/NIMH_target_1116.csv', 'r') as f1:      #NIMH_target_1116.csv
            regexes = f1.read().splitlines()
        for reg in regexes:
            if reg.startswith( '#' ): # == '#':
                continue
            reg = reg.replace("\"", "")
            target_regexes.append(re.compile(reg, re.IGNORECASE))
        return target_regexes

    def getNegRegexes(self):
        neg_regexes = []
        with open('./KB/NIMH_negation_1116.csv', 'r') as f1:     
            regexes = f1.read().splitlines()

        for reg in regexes:
            if reg.startswith( '#' ): # == '#':
                continue
            reg = reg.replace("\"", "")
            neg_regexes.append(re.compile(reg, re.IGNORECASE))
        return neg_regexes
    
    def getSectionRegexes(self):  # new
        section_regexes = []
        with open('./KB/section_1116.csv', 'r') as f1:     
            regexes = f1.read().splitlines()

        for reg in regexes:
            if reg.startswith( '#' ): # == '#':
                continue
            reg = reg.replace("\"", "")
            section_regexes.append(re.compile(reg, re.IGNORECASE|re.MULTILINE|re.DOTALL|re.UNICODE))
        return section_regexes
    
    def filterSection(self, txt):  # new
        txt_list = []
        for reg in self.section_rules:
            for match in reg.finditer(txt):
                txt_list.append(match.group())
        txt_str = '...... '.join(txt_list)
        return txt_str
    
    def target_score(self):
        ann_target_score = pd.read_csv("./KB/NIMH_target_score_1116.csv", sep='$') 
        score1 = dict()
        for index, row in ann_target_score.iterrows():
            row0 = str(row[0]).lower()
            score= {row0: row[1]}
            score1.update(score)
        return score1

def file_size(path,fname):
    #import os
    try:
        statinfo = os.stat(os.path.join(path,fname))
        return statinfo.st_size	
    except:
        try:
            return os.path.getsize(os.path.join(path,fname))
        except:
            return 0
		
	
def str(sth):
    return sth.__str__()

#%%
nlp_classification_system = NLPClassificationSystem()

#%%

#%%
# Instead using csv file, using txt files
path = "./notes" #"./select"   # "./notes"                    
files = os.listdir(path)
len(files)

note_txt = []
output = []
counter = 0
note_count =  0
for fname in files[:]:
    
    if ".txt" not in fname:
        continue    
    if "_.txt" in fname:
        continue
    #print(os.stat(os.path.join(path,fname)).st_size)
    #print(os.path.getsize(os.path.join(path,fname)))
    if file_size(path,fname) < 10000 or file_size(path,fname) > 400000: 
	     continue
    if ".txt" in fname:
        note_count = note_count + 1  #
#        if note_count > 30:          # count the number of text notes want to process ***
#            break                    

        with open(os.path.join(path,fname)) as f:
            doc_text = f.read()

    index=0
    row_TEXT = nlp_classification_system.filterSection(doc_text) # new section filter, next line row.TEXT to row_TEXT
    doc = Document(document_id=fname, text=row_TEXT + " Rush rule.")   # str(row.PAT_ID) to PAT_VISIT if non-numeric
    nlp_classification_system.process(doc)
    if(len(doc.annotations) > 0):        
        
        i = 1
        for a in doc.annotations:
            if( a.type == 'psy_ann'):
                neg_flag = 0
                # Switch the flag to 1 when the mention is negated
                # if('Negated' in a.attributes): # definite_negated_existence Negated
                if a.attributes == {'Negation': 'Negated'}:
                    neg_flag=1
                ### Each row in the dictionary
                record_id  = str(note_count)+'_'+str(i)
                index=index+1
                subject_id =  fname.split('.')[0] # row.PAT_VISIT             # row.PAT_ID to PAT_VISIT
                note_id = str(subject_id) + '_' + str(index)
                annotation_type = a.type
                snippet = row_TEXT[int(a.start_index): int(a.end_index)]
                out_list = [record_id, subject_id, note_id, annotation_type, \
                            a.start_index, a.end_index, \
                            snippet, neg_flag]
                output.append(out_list)
                i=i+1
                counter=counter+1
                # Print . after 10 identified records
                if counter%100 == 0:
                    print('.', end='')
    else:
        i = 1
        neg_flag=0
        ### Each row in the dictionary
        record_id  = str(note_count)+'_'+str(i)
        index=index+1
        subject_id =  fname.split('.')[0] # row.PAT_VISIT             # row.PAT_ID to PAT_VISIT
        note_id = str(subject_id) + '_' + str(index)
        annotation_type = 'psy_ann'
        snippet = 'n'
        out_list = [record_id, subject_id, note_id, annotation_type, \
                    a.start_index, a.end_index, \
                    snippet, neg_flag]
        output.append(out_list)
        
    note_txt.append(row_TEXT)
    
    if note_count%100 == 0:
        print(note_count, end='')                    
#        else:
#            continue
#        break
#%%
# Output to CSV file
columns=['record_id','subject_id', 'note_id', 'annotation_type', 'span_start', 'span_end', 'PSY_snippet', 'neg_flag']
result_data_frame = (pd.DataFrame(output, columns=columns))

result_data_frame.describe()

#%%

result_data_frame.to_csv('./results/ann_table_1116.csv', index=False)
print('Done')

#%%
# Sum annotations
#ann_table = pd.read_csv("./results/ann_table_1113.csv")
#ann_table.head()

ann_table = result_data_frame
#%%
# Read csv to dataframe and change to a dictionary with keywords and their score.
ann_target_score = pd.read_csv("./KB/NIMH_target_score_1116.csv", sep='$') #, index_col=0)   # to lowercase
#ann_target_score.head()
#ann_target_score1=ann_target_score.apply(lambda x: x.astype(str).str.lower())
#df = df.applymap(lambda s:s.lower() if type(s) == str else s)
#ann_target_score1 = ann_target_score.apply(lambda x: x.lower() if type(x) == str else x)
#ann_target_score1
score1 = dict()
for index, row in ann_target_score.iterrows():
    row0 = str(row[0]).lower()
    score= {row0: row[1]}
    score1.update(score)
#score= {x[0]: x[1] for x in ann_target_score.itertuples(index=False)}
score = score1

#%%
pat_id_list = [ann_table['subject_id'][0]]  
ann_list = [ann_table['PSY_snippet'][0]]
flag0 = ann_table['neg_flag'][0]
ann_list_all = []
#sum_list=[score[ann_table['PSY_snippet'][0]]]
#sum_list_all = []

for pat_id, ann, flag in zip(ann_table['subject_id'][1:], ann_table['PSY_snippet'][1:], ann_table['neg_flag'][1:]):
    
        
    if pat_id == pat_id_list[-1]:        # If pad_id matches the last value in pat_id_list,    
        if flag ==0:
            ann_list.append(str(ann).lower()) # add text to the last value in text_list
        else:
            ann_list.append("n")   # in target score, set n$0
        #sum_list.append(score[ann.lower()])
    else:  # Otherwise add a new row with the values
        pat_id_list.append(pat_id)
        ann_list_all.append(set(ann_list))
        ann_list=[]
        ann_list.append(str(ann).lower())
        
ann_list_all.append(set(ann_list))

#============================================    
# try here
sum_list = []


for alist in ann_list_all:
    
    score_list = []
    for ann in alist:
        try:
            score_list.append(score[ann.lower()])
        except:
            print("{} not in dict" .format(ann))
    sum_list.append(sum(score_list))

if flag0 == 1:
    sum_list[0] = sum_list[0]-score[ann_table['PSY_snippet'][0].lower()]

    
#============================================

# Create a new dataframe using these result lists

ann2 = pd.DataFrame({'pat_visit': pat_id_list, 'sum1':sum_list, 'ann': ann_list_all, 'note_txt': note_txt}) #
ann2.to_csv("./results/ann_table_sum_1116.csv")   
ann2.to_csv("./results/ann_table_sum_sep_1116.csv", sep='|', index=False)
# import csv to PostgreSQL
# COPY table_name FROM '/path_to_csv_file.csv' DELIMITERS ',' CSV;
#%%
ann3 = pd.DataFrame({'pat_visit': pat_id_list, 'sum1':sum_list, 'ann': ann_list_all}) #
ann3.to_csv("./results/ann_table_sum_n_1116.csv")

#%%
# Test
table1 = pd.read_csv("./results/ann_table_sum_1116.csv")
table2 = pd.read_csv("./results/ann_table_sum_sep_1116.csv", sep='|')
#%%
# Rule-based NLP system done


