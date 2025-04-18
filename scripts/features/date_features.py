#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 21:57:44 2025
date_features.py 
@author: jasperyu
"""
import pandas as pd 
import datetime as dt

def add_date_features(df):
    
    #identify which day of the week the date falls on (0-6)
    df['day_of_week'] = df['date'].dt.dayofweek
    
    #identify whether it is a weekend (1) or weekday (0)
    df['weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    #identify month of the year (1-12)
    df['month'] = df['date'].dt.month
    
    #identify season (1-4)
    df['season'] = df['month'] % 12 // 3 + 1
    
    return df 
    
