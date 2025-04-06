#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  3 17:40:17 2025
collect_traffic.py
@author: jasperyu
"""
import pandas as pd 
import numpy as np 
import glob 
import os 


#%%
#Select data from All Directions table (5) from each html file 
folder = 'traffic_volume'

xls_files = glob.glob(os.path.join(folder,'*.xls'))

traffic_data_total = []

#extract data from the traffic_volume folder
for f in xls_files:
    try:
        tables = pd.read_html(f)
        traff_seg = tables[5]
        trim = traff_seg.iloc[0:24].copy()
        traffic_data_total.append(trim)
    except Exception as e:
        print(f"Failed to extract {f}: {e}")

#Combine files and reset index 
tdaily = pd.concat(traffic_data_total,ignore_index=True)

#%%
#clean and aggregate the data 

#Rename first column to 'hour' and flatten multi-index col to the dates
df_multiheader = tdaily
df_multiheader = df_multiheader.rename(columns={df_multiheader.columns[0]: "hour"})
df_multiheader.columns = ["hour"] + [col[2] for col in df_multiheader.columns[1:]]

#Reshape from wide to long format
tlong = df_multiheader.melt(id_vars="hour",
                                   var_name="date",
                                   value_name="volume"
                                   )

#Clean and sort traffic DF
tlong["date"] = pd.to_datetime(tlong["date"], errors="coerce")
tlong['volume'] = pd.to_numeric(tlong['volume'],errors='coerce')
tlong = tlong.sort_values(["date", "hour"]).reset_index(drop=True)

#Calculate daily total count of the hourly volume as total volume for a given day 
t_april_dec_24 = tlong.groupby("date", as_index=False)["volume"].sum()

#%% 
#Fill values for 2020-2023 where individual daily values are missing

#read in annual summary table from NYCDOT
yrsummary = pd.read_excel('traff_yearly_summary.xlsx')

#clean yrsummary 
yrsummary.columns = yrsummary.iloc[0]
yrsummary = yrsummary.drop(index=0)
yrsummary = yrsummary.rename(columns={yrsummary.columns[0]: 'year'})

#slice yrsummary to just year and AADT for years of interest
yrsummary = yrsummary[['year','AADT']]
yrsummary = yrsummary.query('year in ["2020","2021","2022","2023"]')

#convert values to numercic 
yrsummary['AADT'] = pd.to_numeric(yrsummary['AADT'])
yrsummary['year'] = yrsummary['year'].astype(int)

#create days missing from trafficdaily
missing_dates = pd.date_range(start='2020-01-01',
                             end='2024-04-14',
                             freq='D')
t_2020_2023 = pd.DataFrame({'date':missing_dates})
t_2020_2023['year'] = t_2020_2023['date'].dt.year

#merge AADT values into missing dates 
t_2020_2023 = t_2020_2023.merge(yrsummary,on='year',how='left',validate='m:1')
t_2020_2023 = t_2020_2023.rename(columns={'AADT':'volume'})
t_2020_2023 = t_2020_2023.drop(columns='year')

#mark imputed values 
t_april_dec_24['traff_imputed'] = 0 
t_2020_2023['traff_imputed'] = 1

#Add missing dates into main trafficdaily 
trafficdaily = pd.concat([t_april_dec_24,t_2020_2023],ignore_index=True)
trafficdaily = trafficdaily.sort_values(by='date',ascending=True).reset_index(drop=True)

#ensure missing volume values from april24 to dec24 stay NaN for model to split tree accordingly
trafficdaily['volume'] = trafficdaily['volume'].replace(0, np.nan)
trafficdaily['traff_imputed'] = trafficdaily['traff_imputed'] | trafficdaily['volume'].isna().astype(int)

#Use 2023 as a proxy for missing data from Jan 1, 2024 to April 14, 2024







