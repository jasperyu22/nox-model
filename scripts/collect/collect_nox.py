#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 23 09:29:00 2025
collect_nox.py
@author: jasperyu
"""

import pandas as pd 
import requests 
import matplotlib.pyplot as plt
import time
from functions import parse_response

# Personal API key
email_value = 'jyu115@syr.edu'
key_value = 'tauperam51'
state = '36'

#%%
#=====================================================================
#Identify NOx measuring monitors in NY to determine county sites 
#=====================================================================

#define site coordinatres variable for global use 
site_0125_coordinates = None
monitors_queens = None 

#create accessible function for site coordinates
def fetch_monitor_coordinates():
    global site_0125_coordinates, monitors_queens
    
    #select NOx parameters
    # param = ['42603','42602','42601']
    param = ['42603','42602','42601']
    bdate = '20000101'
    edate = '20241231'
    api = 'https://aqs.epa.gov/data/api/monitors/byState'

    payload = {
        'email': email_value,
        'key': key_value,
        'param': param,
        'bdate': bdate,
        'edate': edate,
        'state': state
    }

    session = requests.Session()
    response = None 
    
    try: 
        response = session.get(api, params=payload)
        monitors = parse_response(response, 'Monitors', 'Data')
    finally: 
        response.close()
        session.close()

    monitors = monitors.query('close_date.isna()')
    monitors_queens = monitors[monitors['county_code'] == '081'].copy()

    lat = monitors_queens.loc[monitors_queens['site_number'] == '0125', 'latitude'].item()
    lon = monitors_queens.loc[monitors_queens['site_number'] == '0125', 'longitude'].item()
    site_0125_coordinates = (lat, lon)

# Fetch on import
fetch_monitor_coordinates()

#%%
#=====================================================================
#Collect Daily Data from monitors 
#=====================================================================

if __name__ == "__main__":
    #read in api 
    api = 'https://aqs.epa.gov/data/api/dailyData/byCounty'
    
    #refine parameters to just select NOx data
    param = '42603'
    
    #variable to limit to queens county 
    county = '081'
    
    #empty container for all NOx data through years of interest
    nox_data_total = []
    session = requests.Session()
    
    #loop over each year from 2020 to 2024
    for year in range(2020, 2025):
        bdate = f"{year}0101"
        edate = f"{year}1231"
        print(f"\nFetching NOx data for {year}...")
    
        nox_payload = {
            'email': email_value,
            'key': key_value,
            'param': param,  
            'bdate': bdate,
            'edate': edate,
            'state': state,
            'county': county
        }
        
        try: 
            response = session.get(api, params= nox_payload)
            noxdata_seg = parse_response(response, label=f"NOx {year}", result_key='Data')
        finally: 
            response.close()
        
        if noxdata_seg is not None:
            nox_data_total.append(noxdata_seg)
            time.sleep(1)  
        else:
            print(f"No data found for {year}.")
    session.close()
    
    #combine all years into one DF
    noxlvldaily = pd.concat(nox_data_total, ignore_index=True)
    
    noxlvldaily = noxlvldaily.sort_values(by='date_local',ascending = True)
    
    #filter to essential columns
    trim = noxlvldaily[['date_local','site_number','observation_count',
                         'arithmetic_mean','first_max_value','first_max_hour',
                         'local_site_name']]
    
    trim = trim.sort_values(by='date_local',ascending = True)
    
    trim_wide = trim.pivot(index='date_local', columns='site_number', values='arithmetic_mean')
    

    noxlvldaily = trim_wide[['0125']].copy()
    noxlvldaily = noxlvldaily.rename(columns={'0125':'site_nox'})
    noxlvldaily.to_csv('site_nox_daily.csv')
    
    
  





