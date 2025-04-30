#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 30 21:01:32 2025
functions.py
@author: jasperyu
"""

import pandas as pd


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
