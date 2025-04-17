#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 12:48:52 2025
pop_density.py
@author: jasperyu
"""

import pandas as pd 
import requests 
from functions import parse_response
import zipfile

#read in population file, headers start at row 4
pop = pd.read_excel('co-est2024-pop-36.xlsx',header=3)
pop = pop.rename(columns={pop.columns[0]: 'county'})
pop = pop.drop(pop.columns[1],axis=1)

#clean county name format 
pop['county'] = pop['county'].str.replace(r'^\.\s*', '', regex=True) \
                             .str.replace(', New York', '', regex=False)

#select queens county 
qpop = pop.query('county.str.contains("Queens")')
qpop = qpop.drop(qpop.columns[0],axis=1)

#transpose dataframe
qpop = pd.melt(qpop,var_name='year',value_name='population')

#%% 
#calculate population density 

#read in zipfile
with zipfile.ZipFile('2023_Gaz_counties_national.zip', "r") as zip_ref:
    zip_ref.extractall("county_sizes")
    
#maybe add line to delete zip file? 

countysize = pd.read_csv('county_sizes/2023_Gaz_counties_national.txt',sep="\t")

#extract Queens County land area in sq miles
qsize = countysize.loc[countysize['GEOID']==36081,'ALAND_SQMI'].item()

#calculate population density in sq miles 
qpop['pop_density'] = qpop['population'] / qsize

qpop = qpop.rename(columns={'population':'pop'})

#save to csv
qpop.to_csv('queens_population.csv',index=False)
