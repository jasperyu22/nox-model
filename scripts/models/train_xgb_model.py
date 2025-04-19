#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 18 11:47:27 2025
train_model.py
@author: jasperyu
"""
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np 
from scripts.features.date_features import add_date_features
from scripts.features.create_interactions import create_interaction_terms
import xgboost as xgb 
from sklearn.metrics import root_mean_squared_error, r2_score
from itertools import combinations 

#%% 
#=====================================================================
#Load in data and add features 
#=====================================================================

df = pd.read_csv('/Users/jasperyu/Documents/GitHub/nox-model/data/processed/merged_data.csv')

#convert date to datetime for date features 
df['date'] = pd.to_datetime(df['date'], errors='coerce')

#add 1 day lagged site_nox levels
df['site_nox_lag1'] = df['site_nox'].shift(1)

#add rolling 3 day average site_nox levels excluding current day 
df['site_nox_3day_avg'] = df['site_nox'].shift(1).rolling(window=3).mean()

#add rolling 7 day average 
df['site_nox_7day_avg'] = df['site_nox'].shift(1).rolling(window=7).mean()

#add date features
df = add_date_features(df)

#create interaction terms 
df = create_interaction_terms(df)

#filter out empty site nox values for training set 
train_df = df.dropna(subset=['site_nox','site_nox_lag1',
                             'site_nox_3day_avg','site_nox_7day_avg'])

print(train_df.columns)

#define outcome variable 
y = train_df['site_nox']

#filter out date and site_nox from predictor variables
x = train_df.drop(columns=['date','site_nox','pop_density','season','day_of_week','month'])

#%%
#=====================================================================
#Split data into training and testing using time-based split 
#=====================================================================

#use 80% of data for training 
train_size = int(len(train_df) * 0.8)
X_train = x.iloc[:train_size]
X_test = x.iloc[train_size:]
y_train = y.iloc[:train_size]
y_test = y.iloc[train_size:]

#%% 
#=====================================================================
#Train XGBoost Regressor 
#=====================================================================

#initialize model
model = xgb.XGBRegressor(
                         objective='reg:squarederror', #use squared error as loss function 
                         n_estimators=200, #set at 200 trees
                         learning_rate = 0.1, #set lower for slower cautious learning 
                         max_depth = 8, #set max depth of each tree at 6 for controling complexity 
                         random_state = 42,
                         )

#fit model 
model.fit(X_train,y_train)

y_pred = model.predict(X_test)
			
#evaluate
mse = root_mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"\nModel Results: \nMean Squared Error: {mse:.2f} \nR2: {r2:.2f}")

#Record least important features 
feature_names = X_train.columns
importances = model.feature_importances_
least10 = np.argsort(importances)[:10]

#create dictionary of bottom 10 features 
least_important_features = {feature_names[i]: importances[i] for i in least10}

#Visualize feature importance 
xgb.plot_importance(model)
plt.title('Feature Importance [9th Iter.]')
# plt.savefig('/Users/jasperyu/Documents/GitHub/nox-model/outputs/feature importance tracking/feature_importance9.png', dpi=300, bbox_inches='tight')
plt.show()


#%%
#=====================================================================
#Test removing least important features 
#=====================================================================
low_features = list(least_important_features.keys())

results = []

#test removing 1-2 features at a time 
for r in [1, 2]:
    for remove_features in combinations(low_features, r):
        print(f"Testing removal of: {remove_features}")
        
        #drop selected features
        X_train_mod = X_train.drop(columns=list(remove_features))
        X_test_mod = X_test.drop(columns=list(remove_features))

        #train model
        model = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=150,
            learning_rate=0.1,
            max_depth=9,
            subsample=0.8,
            random_state=42,
        )
        model.fit(X_train_mod, y_train)

        #predict and evaluate
        preds = model.predict(X_test_mod)
        rmse = root_mean_squared_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        #store results
        results.append({
            'removed': remove_features,
            'rmse': round(rmse, 3),
            'r2': round(r2, 3)
        })

results_df = pd.DataFrame(results).sort_values(by='rmse')
print(results_df)



