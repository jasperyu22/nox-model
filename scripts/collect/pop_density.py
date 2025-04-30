#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 12:48:52 2025
pop_density.py
@author: jasperyu
"""

import pandas as pd 
import zipfile

#read in population file, headers start at row 4
pop = pd.read_excel('data/raw/co-est2024-pop-36.xlsx',header=3)
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
with zipfile.ZipFile('data/raw/2023_Gaz_counties_national.zip', "r") as zip_ref:
    zip_ref.extractall("county_sizes")

countysize = pd.read_csv('county_sizes/2023_Gaz_counties_national.txt',sep="\t")

#extract Queens County land area in sq miles
qsize = countysize.loc[countysize['GEOID']==36081,'ALAND_SQMI'].item()

#convert sq miles to sq km 
qsize = qsize * 2.58999

#calculate population density in square kilometers
qpop['pop_density'] = qpop['population'] / qsize

qpop = qpop.drop(columns='population')

#convert year-level data to daily for later merge 
daily_rows = []

for _, row in qpop.iterrows():
    year = int(row['year'])
    value = row['pop_density']
    dates = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31', freq='D')
    daily_rows.extend({'date': d, 'pop_density': value} for d in dates)

qpop_daily = pd.DataFrame(daily_rows)

#save to csv
qpop_daily.to_csv('data/processed/queens_population.csv', index=False)



