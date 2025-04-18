#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 18 10:07:41 2025
create_interactions.py
@author: jasperyu
"""

#should be applied after date features are implemented 

def create_interaction_terms(df):
    #in order of importance to model (pre-testing)
    
    #capturing dispersion effect of nox from plant sites 
    df['plant_nox_X_wind'] = df['plant_nox_weighted'] * df['avg_wind_speed']
    
    #captures potential population exposure from plant nox 
    df['plant_nox_X_pop'] = df['plant_nox_weighted'] * df['pop_density']
    
    #capturing seasonality of temperature
    df['temp_X_season'] = df['avg_temp'] * df['season']
    
    #scales traffic volume by weekend to capture behavior changes 
    df['traff_X_weekend'] = df['traff_vol'] * df['weekend']
    
    #captures interaction of rain and wind effects on possible pollutant clearing or dispersion 
    df['precip_X_wind'] = df['precipitation'] * df['avg_wind_speed']
    
    #adjusts weight of site_nox when traffic data is imputed/less reliable 
    df['sitenox_X_traffimput'] = df['site_nox'] * df['traff_imputed']
    
    # #weighs traffic volume data less when imputed 
    # df['traff_vol_X_imputed'] = df['traff_vol'] * df['traff_imputed']
    
    #captures correlation between traffic volume patterns and warmer weather
    #df['traff_vol_X_temp'] = df['traff_vol'] * df['avg_temp']
    
    return df 