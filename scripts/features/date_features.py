#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 21:57:44 2025
date_features.py 
@author: jasperyu
"""

def add_date_features(df):
    
    #add 1 day lagged site_nox levels
    df['site_nox_lag1'] = df['site_nox'].shift(1)

    #add rolling 3 day average site_nox levels excluding current day 
    df['site_nox_3day_avg'] = df['site_nox'].shift(1).rolling(window=3).mean()

    #add rolling 7 day average 
    df['site_nox_7day_avg'] = df['site_nox'].shift(1).rolling(window=7).mean()
    
    return df 
    
