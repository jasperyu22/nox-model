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

#%%
#Identify NOx measuring monitors in NY to determine county sites 
#=====================================================================

#personal API key
email_value = 'jyu115@syr.edu'
key_value = 'tauperam51'

#read in api 
api = 'https://aqs.epa.gov/data/api/monitors/byState'

#limit geographic units to NY counties
state = '36'

#select NOx parameters
param = ['42603','42602','42601']

    #NOx = 42603
    #NO = 42601
    #NO2 = 42602

#set begin and end dates (YYYYMMDD)
bdate = '20000101'
edate = '20241231'

#query string for required parameters
payload = {'email':email_value,
            'key':key_value,
            'param':param,
            'bdate':bdate,
            'edate':edate,
            'state':state
            }
            
#call to build HTTPS query string and collect the response
response = requests.get(api, params= payload)

#Check response success and read data into DF
monitors = parse_response(response,'Monitors','Data')

#filter to only active monitors 
monitors = monitors.query('close_date.isna()')

#filter to only NOx monitors in Queens 
monitors_queens = monitors[monitors['county_code']=='081']

#%%
#Collect Daily Data from monitors 
#=====================================================================

#read in api 
api = 'https://aqs.epa.gov/data/api/dailyData/byCounty'

#refine parameters to just select NOx data
param = '42603'

#variable to limit to queens county 
county = '081'

#empty container for all NOx data through years of interest
nox_data_total = []

#loop over each year from 2020 to 2024
for year in range(2020, 2025):
    bdate = f"{year}0101"
    edate = f"{year}1231"
    print(f"\nFetching NOx data for {year}...")

    payload = {
        'email': email_value,
        'key': key_value,
        'param': param,  
        'bdate': bdate,
        'edate': edate,
        'state': state,
        'county': county
    }

    response = requests.get(api, params=payload)

    noxdata_seg = parse_response(response, label=f"NOx {year}", result_key='Data')

    if noxdata_seg is not None:
        nox_data_total.append(noxdata_seg)
        time.sleep(1)  
    else:
        print(f"No data found for {year}.")

#combine all years into one DF
noxlvldaily = pd.concat(nox_data_total, ignore_index=True)

noxlvldaily = noxlvldaily.sort_values(by='date_local',ascending = True)

#filter to essential columns
trim = noxlvldaily[['date_local','site_number','observation_count',
                     'arithmetic_mean','first_max_value','first_max_hour',
                     'local_site_name']]

trim = trim.sort_values(by='date_local',ascending = True)

trim_wide = trim.pivot(index='date_local', columns='site_number', values='arithmetic_mean')

#ADD: construct NOx column that is average of two sites and if one is missing then take the other 

# trim_wide = trim_wide.rename(columns={
#     '0124': 'Away from Highway',
#     '0125': 'Near Highway'
# })

#%%
#visualize varying NOx levels across two sites 
#=====================================================================

# #plot time-series comparison
# trim_wide.plot(figsize=(12, 6))
# plt.title('Daily NOx Levels at Two Nearby Sites')
# plt.xlabel('Date')
# plt.ylabel('NOx concentration')
# plt.legend(title="Monitoring Sites")
# plt.show()

# #correlation analysis
# corr = trim_wide.corr().iloc[0,1]
# print(f"Correlation between sites: {corr:.2f}")





