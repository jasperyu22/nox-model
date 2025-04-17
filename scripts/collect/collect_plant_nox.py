#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  5 21:58:15 2025
collect_powerplant.py
@author: jasperyu
"""

import pandas as pd 
import requests 
from functions import parse_response
from haversine import haversine
import time 

#%%
#=====================================================================
#collect list of facilities within 50 km radius 
#=====================================================================

#set parameters
api = "https://api.epa.gov/easey/facilities-mgmt/facilities/attributes"
key_value = 'a1HpwUeV6Wpw2B8cTq7GFJBBIYHTufLT9aTF6EJY'

years = "2020|2021|2022|2023|2024"

programcodes = 'SIPNOX|CSNOX'

headers = {'x-api-key': key_value}

facil_params = {'year':years,
          'programCodeinfo':programcodes,
          'stateCode':'NY|NJ',
          'page':1,
          'perPage':500}


all_facilities = []
session = requests.Session()

#Loop through pages 

while True:
    print(f"Fetching page {facil_params['page']}")
    response = session.get(api, headers= headers, params= facil_params)
    facil_seg = parse_response(response,label=f'Facilities Page {facil_params['page']}')
    response.close()
    if facil_seg is None or facil_seg.empty:
        print('All Facilities pages fetched')
        break 
    
    all_facilities.append(facil_seg)
    facil_params['page'] += 1
    time.sleep(1)

session.close()

if all_facilities:
    facilities = pd.concat(all_facilities, ignore_index=True)
    print(f"Final Facilities Shape: {facilities.shape}")
else:
    facilities_df = pd.DataFrame()
    print("No data returned.")
    

keep_cols = ['facilityName','facilityId','unitId','year',
             'latitude','longitude','primaryFuelInfo','secondaryFuelInfo',
             'operatingStatus','programCodeInfo'
             ]

facilities = facilities[keep_cols].copy()

facilities = facilities.drop_duplicates(subset='facilityName')

#fetch lat and lon of site 0125 
from collect_nox import site_0125_coordinates
if site_0125_coordinates is None:
    raise ValueError("site_0125_coordinates was not set. Please check collect_nox.py.")

#calculate distances from each facility to site 0125
facilities['distance_km'] = facilities[['latitude', 'longitude']].apply(lambda row: 
                         haversine(site_0125_coordinates, (row['latitude'], row['longitude'])), axis=1)

#Identify facilities within 50 km of site 0125
within_50 = facilities[facilities['distance_km'] <= 50]


#%%
#=====================================================================
#Collect daily emissions from plants 
#=====================================================================

api = "https://api.epa.gov/easey/emissions-mgmt/emissions/apportioned/daily/by-facility"

#Convert facility IDs to readable form for request 
facility_ids = within_50['facilityId'].astype(str).tolist()
facility_ids = "|".join(facility_ids)


#set initial values for loop
page = 1
per_page = 500

plant_nox_total = []

session = requests.Session()

#Loop through each year
for year in range(2020, 2025):  
    page = 1

    while True: 
        print(f"\nFetching {year}, page {page}")
    
        emissions_params = {'facilityId': facility_ids,
                  'programCodeInfo':programcodes,
                  'beginDate':f'{year}-01-01',
                  'endDate':f'{year}-12-31',
                  'page':page,
                  'perPage':per_page
                  }
        
        #Make API request and read segment of data into segment DF 
        response = session.get(api, headers= headers, params= emissions_params)
        plant_nox_seg = parse_response(response,label=f'Plant Daily NOx ({year},Page {page})')
        response.close()
        
        #append to total list 
        if plant_nox_seg is not None and not plant_nox_seg.empty:
            plant_nox_total.append(plant_nox_seg)
            page += 1
            time.sleep(1)  
        else:
            print(f"All pages fetched for {year}")
            break

session.close()
#%%
#=====================================================================
#Weigh NOx emissions by distance to site 0125 and export
#=====================================================================

#concatenate all plant_nox segments into one df
plant_noxlvldaily = pd.concat(plant_nox_total, ignore_index=True)

#merge distances to site 0125 to main df 
merged = plant_noxlvldaily.merge(within_50[['facilityId','distance_km']],
                                            on='facilityId',how='left',validate='m:1',
                                            indicator=False)

#weigh nox levels by distance to site 0125 
merged['plant_nox_weighted']= merged['noxMass'] / merged['distance_km']

#sum weighted nox daily 
merged_weighted_daily = merged.groupby("date", as_index=False)["plant_nox_weighted"].sum()

#save to csv
merged_weighted_daily.to_csv('plant_nox_daily.csv', index=False)













