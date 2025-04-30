#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 30 20:04:08 2025
collect_weather.py
@author: jasperyu
"""
import pandas as pd 
import requests 
from scripts.utils.functions import parse_response
import time 
import json 

#%%
#=====================================================================
#Identify station of observation 
#=====================================================================

#load API keys from JSON 
with open('keys.json') as fh:
    keys = json.load(fh)

email_value = keys['email']
token = keys['noaa_key']

#read in api 
api = 'https://www.ncei.noaa.gov/cdo-web/api/v2/stations'

#limit geographic units to Queens County
location = 'FIPS:36081'

#query string for required parameters
payload = {'locationid':location,
           'limit':100,
           'offset':1
            }

headers = {'token':token}
            
#call to build HTTPS query string and collect the response
response = requests.get(api, params= payload, headers= headers)

#Check response success 
sites = parse_response(response,'Sites','results')

#limit sites to those that still provide data as of 2025 
sites = sites.query('maxdate >= "2025-03-01"')
sites = sites[['id','name','mindate','maxdate','datacoverage']]
lgasite = sites[(sites['name'] == "LAGUARDIA AIRPORT, NY US") & 
                (sites['id'].str.startswith("GHCND"))]['id'].values[0]

#%%
#=====================================================================
#Read in daily weather data from Queens County LGA Site
#=====================================================================

api = 'https://www.ncei.noaa.gov/cdo-web/api/v2/data'
headers = {'token':token}

#limit to most important weather elements
welements = ['PRCP', #Precipitation (tenths of mm)
            'TAVG', #Average daily temperature (tenths of degrees C), corresponds to an average of hourly readings
            'AWDR', #Average daily wind direction (degrees)
            'AWND', #Average daily wind speed (tenths of meters per second)
            'RHAV' #Average relative humidity for the day (percent)
            ]

#years of Interest (2019–2024)
years = range(2020, 2025)
weather_data_total = []

session = requests.Session()

#API limits requests to 1000, so loop through each year of interest, fetching daily weather data 
for year in years:
    bdate = f"{year}-01-01"
    edate = f"{year}-12-31"
    print(f"\nFetching weather data for {year}...")
    
    offset = 1
    limit = 1000
    finished = False
    
    while not finished:
        payload = {
            'datasetid': 'GHCND',
            'datatypeid': welements,
            'stationid': lgasite,
            'startdate': bdate,
            'enddate': edate,
            'limit': limit,
            'offset': offset
        }
        
        try: 
            response = session.get(api, params=payload, headers=headers)
            wdata_seg = parse_response(response, label=f"{year} Offset: {offset}",result_key='results')
        finally: 
            response.close()
        
        if wdata_seg is not None and not wdata_seg.empty:
            weather_data_total.append(wdata_seg)
            offset += limit
            
            #add delays between each request to avoid request errors
            time.sleep(3)
        else:
            finished = True

session.close()

#%%
#=====================================================================
#Convert values and set up data file
#=====================================================================
weather_all = pd.concat(weather_data_total, ignore_index=True)
weatherdaily = weather_all.pivot(index='date', columns='datatype', values='value').reset_index()

#Convert temperature to proper units
weatherdaily['TAVG'] = (weatherdaily['TAVG'] / 10) 

#Convert precipitation to proper units
weatherdaily['PRCP'] = (weatherdaily['PRCP'] / 10) 

#Convert wind speed to proper units
weatherdaily['AWND'] = (weatherdaily['AWND'] / 10) 

#Convert Relative Humidity to decimal percentage 
weatherdaily['RHAV'] = weatherdaily['RHAV'] / 100 


#rename columns 
n_names = {'TAVG': 'avg_temp',
           'AWND':'avg_wind_speed',
           'PRCP': 'precipitation',
           'RHAV': 'avg_rel_humid'
           }

weatherdaily = weatherdaily.rename(columns= n_names)
weatherdaily = weatherdaily.sort_values(by='date',ascending=True)

#save to csv
weatherdaily.to_csv('data/processed/weather_daily.csv', index=False)



