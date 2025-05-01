# Daily NOx Concentration Prediction in Queens, NY (2020–2024)

## I. Purpose of the Analysis
The purpose of this analysis was to model and predict daily nitrogen oxide (NOx) concentration at the site-level for Queens County. Using an XGBoost regression model, this project integrates data on power plant emissions, weather, traffic volume, and population density to predict average daily NOx concentration at EPA AQS Site 0125, located at Queens College.

## II. Sourcing Input Data

### • Daily NOx Concentration
- Sourced from the EPA's Air Quality System (AQS) API.

### • Traffic Volume
- Sourced from the NY Department of Transportation Traffic Data Viewer (TDV).
- Data is collected from Site 050062000000 (I-495 from EXIT 23 MAIN ST OVER to EXIT 24 KISSENA BLVD OVER).
- Daily data available at:  
  https://nysdottrafficdata.drakewell.com/calendar_alt.asp?node=NYSDOT_CCS&cosit=050062000000
- Download AADT data month-by-month for 4/2024 to 9/2024.
- Organize into folder: `data/raw/traff_monthly_summaries`
- Download annual AADT for missing dates from annual statistics section 
- Organize into

### • Weather
- Sourced from NOAA NCEI Climate Data Online (CDO).
- Data from LaGuardia Airport site, station ID `GHCND:USW00014732`.  
  https://www.ncdc.noaa.gov/cdo-web/datasets/GHCND/locations/FIPS:36081/detail

### • Power Plant Emissions
- Sourced from the EPA Clean Air Markets (CAM) API.

### • County Population
- Sourced from the US Census Bureau’s County Population Totals (2020–2024).  
  https://www.census.gov/data/datasets/time-series/demo/popest/2020s-counties-total.html  
  Download: `CO-EST2024-POP-36` (New York dataset)

### • Queens County Land Area
- Sourced from the US Census Bureau Gazetteer.  
  https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/  
  Download: `2023_Gaz_counties_national.zip`

---

## III. Scripts

### • Script Execution Order
1. Run `collect_nox.py` first
2. Then run the other collect scripts (`collect_traffic.py`, `collect_weather.py`, `collect_plant_nox.py`, `pop_density.py`) in any order
3. Run `merge_data.py`
4. Finally, run `train_xgb_model.py`
5. Use Features scripts to test additions/removals of features 

---

### • Utils

- `functions.py`: Contains reusable helper functions, including `parse_response` for robust API response parsing.

---

### • Collect

- `collect_nox.py`
  - Downloads daily NOx data from AQS API.
  - Retrieves site coordinates.
  - Output: `data/processed/site_nox_daily.csv`

- `collect_traffic.py`
  - Loads monthly traffic CSVs, imputes missing AADT.
  - Input: `data/raw/traff_monthly_summaries`, `traff_yearly_summary.xlsx`
  - Output: `data/processed/traffic_daily.csv`

- `collect_weather.py`
  - Downloads temperature, wind, humidity, and precipitation data from NOAA API.
  - Output: `data/processed/weather_daily.csv`

- `collect_plant_nox.py`
  - Downloads and weights NOx emissions from power plants within 50km of the site.
  - Output: `data/processed/plant_nox_daily.csv`

- `pop_density.py`
  - Loads population and county area data.
  - Output: `data/processed/queens_population.csv`

---

### • Merge

- `merge_data.py`
  - Merges NOx, weather, traffic, emissions, and population datasets.
  - Output: `data/processed/merged_data.csv`

---

### • Features

- `create_interactions.py`: Generates interaction terms (e.g., emissions × wind speed).
- `date_features.py`: Extracts time-based features and calculates lag/rolling averages.

---

### • Modeling

- `train_xgb_model.py`
  - Trains and evaluates XGBoost regression model.
  - Includes model tuning, feature importance, and performance plots.
  - Input: `data/processed/merged_data.csv`
  - Output:
    - `outputs/feature_importance_score.png`
    - `outputs/performance_lineplot.png`
    - `outputs/performance_scatterplot.png`

---

## IV. Results

The XGBoost model showed strong performance with an R² of **0.66** and RMSE of **8.39**. Top predictors included lagged NOx, wind speed, and plant emissions within 50 km. The model captured both short-term and seasonal trends in NOx, offering useful insights for air quality forecasting.

### Model Limitations:
- Traffic data was imputed from annual averages, omitting daily variability.
- Wind direction data was unavailable, limiting ability to model pollution transport.
- Weighted emissions assume proximity equals impact, which may oversimplify dispersion effects.

### Future Improvements:
- Add airport emissions or flight data as predictors (Queens is near JFK and LGA).
- Incorporate wind direction as a vector feature to better model fate and transport of NOx.
