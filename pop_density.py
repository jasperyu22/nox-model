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

# api = 'https://api.census.gov/data/2022/acs/acs5'
# key = 'f8d4aa69801bc8dfd5784c121ea7f2baf1c749a3'

# #Limiting geographic units to NY counties
# in_clause = 'state:36'

# #select Queens county data
# for_clause = 'county:081'

# #grab total population variable 
# var = 'B01003_001E'

# #query string 
# payload = {'get':var,
#            'for':for_clause, 
#            'in':in_clause, 
#            'key':key}

# #call to build HTTPS query string and collect the response
# response = requests.get(api, payload)
# pop = parse_response(response,label='Population',result_key='Data')

#read in population file, headers start at row 4
pop = pd.read_excel('co-est2024-pop-36.xlsx',header=3)
pop = pop.rename(columns={pop.columns[0]: 'county'})
pop = pop.drop(pop.columns[1],axis=1)

#Clean county name format 
pop['county'] = pop['county'].str.replace(r'^\.\s*', '', regex=True) \
                             .str.replace(', New York', '', regex=False)

#select queens county 
qpop = pop.query('county.str.contains("Queens")')
qpop = qpop.drop(qpop.columns[0],axis=1)

#transpose dataframe
qpop = pd.melt(qpop,var_name='year',value_name='population')

#%% 
#Calculate population density 

#read in zipfile
with zipfile.ZipFile('2023_Gaz_counties_national.zip', "r") as zip_ref:
    zip_ref.extractall("county_sizes")

countysize = pd.read_csv('county_sizes/2023_Gaz_counties_national.txt',sep="\t")

#extract Queens County land area in sq miles
qsize = countysize.loc[countysize['GEOID']==36081,'ALAND_SQMI'].item()

#calculate population density 
qpop['pop_density'] = qpop['population'] / qsize
