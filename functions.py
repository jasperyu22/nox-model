#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 30 21:01:32 2025
functions.py
@author: jasperyu
"""

import pandas as pd

#function to parse API responses and generate DF of response results
def parse_response(response, label="data",result_key='results'):
    if response.status_code != 200: 
        print(f"[{label}] HTTP Error {response.status_code}")
        print(response.text)
        response.raise_for_status()
    
    try:
        row_list = response.json()
        if result_key in row_list and len(row_list[result_key]) > 0:
            colnames = list(row_list[result_key][0].keys())
            datarows = row_list[result_key]
            return pd.DataFrame(datarows, columns=colnames)
        else:
            print(f"{label} No data available for the provided parameters.")
            return None
        
    except Exception as e:
        print(f"Error parsing response: {e}")
        raise


