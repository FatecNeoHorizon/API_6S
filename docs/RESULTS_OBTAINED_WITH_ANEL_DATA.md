# Time Series Forecasting for ANEEL Indicators (DEC & FEC)
Linkl to access: https://colab.research.google.com/drive/1TP3jefy6YgZDYVNqrn9JKudEAwSoCXFc?usp=sharing
## 1. Overview

This project implements a time series forecasting pipeline using ANEEL data, focusing on two key continuity indicators:

- DEC (Duration Equivalent of Interruption per Consumer Unit)
- FEC (Frequency Equivalent of Interruption per Consumer Unit)

The objective is to:

- Process and consolidate historical data
- Train machine learning models per consumer unit
- Generate forecasts for future periods
- Evaluate model performance using error metrics

## 2. Data Processing
### Data Sources

The following datasets were used:

- indicadores-continuidade-coletivos-2010-2019.csv
- indicadores-continuidade-coletivos-2020-2029.csv

After loading:

- The datasets were merged into a unified structure
- Invalid and missing values were removed
- Date fields were standardized

### Key Transformations
- Creation of a datetime column (data) using:
    - AnoIndice (year)
    - NumPeriodoIndice (month)
- Filtering by indicator:
    - DEC dataset
    - FEC dataset
- Sorting data by:
    - Consumer unit (IdeConjUndConsumidoras)
    - Time (data)
## 3. Feature Engineering

To enable time series learning, lag features were created:

- lag_1 to lag_12

These represent the values from the previous 12 months, allowing the model to capture:

- Temporal dependencies
- Seasonal patterns
## 4. Model Training
### Algorithm Used
- Random Forest Regressor (scikit-learn)
### Training Strategy
- A separate model was trained for each consumer unit
- For each unit:
    - Rows with missing lag values were removed
    - Data was split into training and validation
    - Model was trained using lag features
### Evaluation Metric
- MAE (Mean Absolute Error)

Example results:

```
✓ Unit 964  | MAE: 0.2278 (DEC) | 0.2364 (FEC)
✓ Unit 2142 | MAE: 0.1289 (DEC) | 0.1450 (FEC)
✓ Unit 2922 | MAE: 0.1153 (DEC) | 0.1178 (FEC)
✓ Unit 4536 | MAE: 0.4997 (DEC) | 0.3695 (FEC)
```

Interpretation:

- Most units achieved low MAE (< 0.3) → good predictive performance
- Some units showed higher errors → likely due to:
    - High volatility
    - Sparse or irregular data
## 5. Generated Files
### Metrics Files
- metricas_dec_todas_unidades_br.csv
- metricas_fec_todas_unidades_br.csv

### Content:

- cod_unidade
- mae

### These files allow:

- Performance comparison across units
- Identification of poorly predicted series
### Forecast Files
- previsoes_dec_todas_unidades.csv
- previsoes_fec_todas_unidades.csv

### Content:

- cod_unidade
- data
- previsao

### Example:

```
cod_unidade | data       | previsao
964         | 2026-03-01 | 0.7920
964         | 2026-04-01 | 0.4160
964         | 2026-05-01 | 0.4089
```

### These files provide:

- Future monthly predictions per unit
- Input for visualization and decision-making

### MongoDB persistence format

When the forecasts are saved to the `predictions` collection, the persistence layer stores the target month and year separately instead of a full datetime.

Stored fields:

- consumer_unit_set_id
- indicator
- forecast_year
- forecast_period
- forecast_value
- model

This makes the saved records easier to query by reporting period and aligns the database schema with the monthly nature of the forecasts.

At runtime, the backend also reapplies the `predictions` collection validator on startup so existing environments are migrated to the same year/month schema instead of keeping the legacy `forecast_date` document shape.
## 6. Insights from the Results
### Model Performance
- The Random Forest model performed well for most units
- Low MAE values indicate:
    - Strong ability to capture temporal patterns
    - Effective use of lag features
### Temporal Behavior
- The use of 12 lags suggests:
    - Presence of annual seasonality
    - Recurring patterns in DEC and FEC indicators
### Variability Across Units
- Some units have significantly higher errors
- Possible causes:
    - Irregular interruption patterns
    - External factors not captured by the model
    - Data quality issues
### Predictive Patterns
- Forecasts show:
    - Smooth transitions between months
    - No extreme spikes (typical of Random Forest smoothing)

### This indicates:

- The model prioritizes stability over abrupt changes
- It may underperform in sudden anomaly scenarios
## 7. Conclusion

### This pipeline demonstrates that:

- Machine learning models (Random Forest) can effectively forecast electrical continuity indicators
- Lag-based features are sufficient to capture temporal dependencies
- Training models per unit improves prediction accuracy

### However:

- The model does not explicitly model seasonality (like SARIMA or Prophet would)
- Performance varies depending on data quality and variability