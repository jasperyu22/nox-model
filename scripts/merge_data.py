#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 18:36:51 2025
merge_data.py 
@author: jasperyu
"""
import pandas as pd 
import glob 
import os
from functools import reduce 

#%% Merge datasets into one working file 
proc_data_path = '/Users/jasperyu/Documents/GitHub/nox-model/data/processed'
csv_files = glob.glob(os.path.join(proc_data_path,'*.csv'))

dfs = {}

#read CSV files into individual dataframes
for f in csv_files :
    file_key = os.path.splitext(os.path.basename(f))[0]
    df = pd.read_csv(f)
    
    #reset index only if 'date' is in the index
    if 'date' not in df.columns and df.index.name == 'date':
        df = df.reset_index()
   
   #ensure 'date' is a string or datetime
    if 'date' in df.columns:
       df['date'] = pd.to_datetime(df['date'], errors='coerce')
       
   #drop CSV-exported index column if present
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns='Unnamed: 0')
        
    dfs[file_key] = df

#convert dictionary of dataframes into a list 
dfs_list = list(dfs.values())

#merge all data together on date
merged_df = reduce(lambda left, right: pd.merge(left, right, on='date', how='outer'), dfs_list)
 
#export to csv 
merged_df.to_csv('/Users/jasperyu/Documents/GitHub/nox-model/data/processed/merged_data.csv',index=False)

