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
    
    #adjusts weight of site_nox when traffic data is imputed/less reliable 
    df['sitenox_X_traffimput'] = df['site_nox'] * df['traff_imputed']
    
    #capture humidity effects on plant nox dispersion
    df['plant_nox_X_humid'] = df['plant_nox_weighted'] * df['avg_rel_humid']
    
    df['site7davg_X_wind'] = df['site_nox_7day_avg'] * df['avg_wind_speed']
    
    df['site_lag1_X_wind'] = df['site_nox_lag1'] * df['avg_wind_speed']
    
    #capturing seasonality of temperature
    # df['temp_X_season'] = df['avg_temp'] * df['season']
    
    # df['site7davg_X_humid'] = df['site_nox_7day_avg'] * df['avg_rel_humid']

    # df['plantnox_X_day'] = df['plant_nox_weighted'] * df['day_of_week']
    
    # df['plantnox_X_wind_humid'] = df['plant_nox_weighted'] * df['avg_wind_speed'] * df['avg_rel_humid']
    
    #capturing dispersion effect of nox from plant sites 
    # df['plant_nox_X_wind'] = df['plant_nox_weighted'] * df['avg_wind_speed']
    
    #capture humidity effects on traffic volume 
    # df['traff_X_humid'] = df['traffic_vol'] * df['avg_rel_humid']
    
    # #weighs traffic volume data less when imputed 
    # df['traff_vol_X_imput'] = df['traffic_vol'] * df['traff_imputed']
    
    #captures correlation between traffic volume patterns and warmer weather
    # df['traff_vol_X_temp'] = df['traffic_vol'] * df['avg_temp']
    
    # #captures potential population exposure from plant nox 
    # df['plant_nox_X_pop'] = df['plant_nox_weighted'] * df['pop_density']
    
    # #scales traffic volume by weekend to capture behavior changes 
    # df['traff_X_weekend'] = df['traffic_vol'] * df['weekend']
    
    # #captures interaction of rain and wind effects on possible pollutant clearing or dispersion 
    # df['precip_X_wind'] = df['precipitation'] * df['avg_wind_speed']
    
    return df 