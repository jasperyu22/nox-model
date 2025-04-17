#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 30 21:01:32 2025
functions.py
@author: jasperyu
"""

import pandas as pd

#function to parse API responses and generate DF of response results
# def parse_response(response, label="data",result_key='results'):
#     if response.status_code != 200: 
#         print(f"[{label}] HTTP Error {response.status_code}")
#         print(response.text)
#         response.raise_for_status()
    
#     try:
#         json_data = response.json()
        
#         #Response is a list 
#         if isinstance(json_data, list):
#             if len(json_data) > 0 and isinstance(json_data[0], dict):
#                 return pd.DataFrame(json_data)
#             else:
#                 print(f"[{label}] Response is an empty list or not list of dicts.")
#                 return None
        
#         #Response is a dictionary with a key like 'results' or 'data'
#         elif isinstance(json_data, dict) and result_key in json_data:
#             if len(json_data[result_key]) > 0:
#                 return pd.DataFrame(json_data[result_key])
#             else:
#                 print(f"[{label}] No data in '{result_key}' key.")
#                 return None
#         else:
#             print(f"[{label}] Unexpected JSON structure.")
#             return None
        
#     except Exception as e:
#         print(f"Error parsing response: {e}")
#         raise


def parse_response(response, label="data", result_key='data'):
    if response.status_code != 200: 
        print(f"[{label}] HTTP Error {response.status_code}")
        print(response.text)
        response.raise_for_status()

    try:
        data = response.json()

        #Case 1: Top-level list
        if isinstance(data, list) and data:
            return pd.DataFrame(data)

        #Case 2: Dictionary with nested list under a key
        elif isinstance(data, dict) and result_key in data and isinstance(data[result_key], list) and data[result_key]:
            return pd.DataFrame(data[result_key])

        else:
            if label: 
                print(f"[{label}] No data at found at key '{result_key} or empty response'")
            return None

    except Exception as e:
        print(f"[{label}] Exception while parsing: {e}")
        raise
