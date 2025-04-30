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
import statsmodels.api as sm

#%% 
#=====================================================================
#Load in data and add features 
#=====================================================================

df = pd.read_csv('data/processed/merged_data.csv')

#convert date to datetime for date features 
df['date'] = pd.to_datetime(df['date'], errors='coerce')

#add date-basd features
df = add_date_features(df)

#add basic interaction terms
df = create_interaction_terms(df)

#filter out empty site nox values for training set 
train_df = df.dropna(subset=['site_nox','site_nox_lag1',
                             'site_nox_3day_avg','site_nox_7day_avg'])

print(train_df.columns)

#export to files for documentation 
train_df.to_csv('data/processed/training_data.csv',index=False)

#define outcome variable 
y = train_df['site_nox']

#filter out date, site_nox, and population density from predictor variables
x = train_df.drop(columns=['date','site_nox', 'pop_density'])


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
                         max_depth = 8, #set max depth of each tree at 8 for controling complexity 
                         random_state = 42
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
plt.title('Feature Importance [Final]')
plt.savefig('outputs/feature importance tracking/feature_importance.png', dpi=300, bbox_inches='tight')
plt.show()

#%%
#=====================================================================
#Fine tune parameters using GridSearchCV
#=====================================================================
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import make_scorer, root_mean_squared_error


#define model
xgb_model = xgb.XGBRegressor(
    objective='reg:squarederror',
    random_state=42,
)

#define parameter grid
param_grid = {
    'n_estimators': [200,250,300],
    'max_depth': [4, 6, 8, 10],
    'learning_rate': [0.05, 0.08, 0.1],
    'subsample': [0.7,0.8],
    'colsample_bytree': [0.8, 1.0]
}

#custom scoring function using RMSE
rmse_scorer = make_scorer(root_mean_squared_error, greater_is_better=False)

#use time-aware cross-validation (if data is time-ordered)
tscv = TimeSeriesSplit(n_splits=5)

#set up GridSearchCV
grid_search = GridSearchCV(
    estimator=xgb_model,
    param_grid=param_grid,
    scoring=rmse_scorer,
    cv=tscv,  
    verbose=1,
    n_jobs=-1
)

#fit the model
grid_search.fit(X_train, y_train)

#view best parameters and RMSE
print("Best Parameters:", grid_search.best_params_)
print("Best RMSE:", -grid_search.best_score_)

#%%
#=====================================================================
#Visualize Performance
#=====================================================================

#scatter plot
plt.figure(figsize=(8,6))
plt.scatter(y_test, y_pred, alpha=0.6)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel("Actual NOx Levels")
plt.ylabel("Predicted NOx Levels")
plt.title("Predicted vs Actual NOx Levels")
plt.grid(True)
plt.tight_layout()
plt.savefig('outputs/performance graphics/performance_scatterplot.png', dpi=300, bbox_inches='tight')
plt.show()


#time series plot
plot_df = X_test.copy()
plot_df['date'] = df.loc[X_test.index, 'date']
plot_df['Actual'] = y_test
plot_df['Predicted'] = y_pred

plot_df = plot_df.sort_values('date')

plt.figure(figsize=(12,6))
plt.plot(plot_df['date'], plot_df['Actual'], label='Actual', linewidth=2)
plt.plot(plot_df['date'], plot_df['Predicted'], label='Predicted', linewidth=2)
plt.xlabel('Date')
plt.ylabel('NOx Level')
plt.title('NOx Levels: Actual vs Predicted Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('outputs/performance graphics/performance_lineplot.png', dpi=300, bbox_inches='tight')
plt.show()


#%%
#=====================================================================
#Test against OLS Regression 
#=====================================================================

from sklearn.model_selection import train_test_split

#add constant to predictors
X = sm.add_constant(train_df.drop(columns=['date', 'site_nox']))
y = train_df['site_nox']

#combine into one DataFrame for safe dropping
df_clean = pd.concat([X, y], axis=1)

df_clean = df_clean.replace([np.inf, -np.inf], np.nan).dropna()

#re-separate X and y
X = df_clean.drop(columns='site_nox')
y = df_clean['site_nox']

#split into train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

ols_model = sm.OLS(y_train, X_train).fit()

y_pred = ols_model.predict(X_test)

print(ols_model.summary())

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("OLS Regression Test Results:")
print(f"RMSE: {rmse:.2f}")
print(f"MAE: {mae:.2f}")
print(f"R² Score: {r2:.2f}")





