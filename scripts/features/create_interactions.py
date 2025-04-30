#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 18 10:07:41 2025
create_interactions.py
@author: jasperyu
"""

def create_interaction_terms(df):
    
    #captures dispersion effect of plant nox due to wind speed
    df['plant_nox_X_wind'] = df['plant_nox_weighted'] * df['avg_wind_speed'] 
    
    return df 