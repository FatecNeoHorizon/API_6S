# Time Series Forecasting for DEC and FEC Indicators
Link to access: https://colab.research.google.com/drive/1TP3jefy6YgZDYVNqrn9JKudEAwSoCXFc#scrollTo=UZa9bXbbvFd2

## 1. Objective

This process aims to train and evaluate time series forecasting models for DEC (Duration Equivalent of Interruption per Consumer Unit) and FEC (Frequency Equivalent of Interruption per Consumer Unit) using historical data from ANEEL.

The baseline model used is Random Forest, with the goal of later comparing its performance against boosting models (XGBoost and LightGBM), which are expected to better capture peaks due to iterative residual correction.

## 2. Data Preparation
### 2.1 Filtering and Cleaning

For both DEC and FEC:

- Filter dataset by indicator (SigIndicador == 'DEC' or 'FEC')
- Remove rows with missing time period (NumPeriodoIndice)
- Create a proper datetime column (data) combining:
  - AnoIndice (year)
  - NumPeriodoIndice_key (month)

```
df_dec = df_indicadores[df_indicadores['SigIndicador'] == 'DEC'].copy()
df_dec = df_dec.dropna(subset=['NumPeriodoIndice'])
```

### 2.2 Time Series Structuring
- Data is sorted by:
    - Consumer unit (IdeConjUndConsumidoras)
    - Date (data)

This ensures chronological consistency for each unit.

## 3. Feature Engineering (Lag Creation)

To transform the time series into a supervised learning problem:

- Create 12 lag features (lag_1 to lag_12)
- Each lag represents the value from previous months

```
for i in range(1, 13):
    dec_por_agente[f'lag_{i}'] = ...
```

These features allow the model to learn temporal dependencies.

## 4. Model Training per Consumer Unit
### 4.1 Processing Function

A function processar_unidade is defined to handle each unit independently:

Steps:
1. Drop missing lag values
2. Minimum data validation
    - Skip units with less than 20 observations
3. Split dataset
    - 80% training
    - 20% testing
4. Train model

```
model = RandomForestRegressor(
    n_estimators=100,
    n_jobs=-1,
    random_state=42
)
```
5. Evaluate performance
    - Metric used: MAE (Mean Absolute Error)
## 5. Recursive Forecasting (12 Months Ahead)

The model predicts future values iteratively:

- Use last 12 observed values as input
- Predict next value
- Append prediction to history
- Repeat for 12 steps

```
lags = historico[-12:][::-1]
pred = model.predict(...)
```

This is a recursive multi-step forecasting strategy.

## 6. Model Persistence

Each trained model is saved individually using joblib:

```
joblib.dump(model, '/modelos/modelo_dec_{cod}.pkl')
```

This allows reuse without retraining.

## 7. Batch Processing for All Units
- Iterate over all unique consumer units
- Apply the processing function
- Handle:
    - Successful runs
    - Insufficient data
    - Exceptions

```
for cod in todas_unidades:
    ...
```

Memory is managed using:

```
gc.collect()
```

## 8. Results Storage
### 8.1 Metrics

- MAE per unit is stored in:
```
metricas_dec_todas_unidades_br.csv
metricas_fec_todas_unidades_br.csv
```

### 8.2 Forecasts
- Future predictions (12 months) are stored in:

```
previsoes_dec_todas_unidades_br.csv
previsoes_fec_todas_unidades_br.csv
```

## 9. Replication for FEC

The exact same pipeline is applied to FEC, ensuring:

- Consistency in preprocessing
- Comparable results between DEC and FEC