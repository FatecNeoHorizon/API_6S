# LOAD_AND_PREPARE_THE_DATA
Link to access: https://colab.research.google.com/drive/1TP3jefy6YgZDYVNqrn9JKudEAwSoCXFc?usp=sharing

## 1. Overview

This document describes the end-to-end process for loading, cleaning, transforming, and consolidating multiple CSV datasets related to continuity indicators (e.g., DEC and FEC) from ANEEL.

The pipeline is designed to:

- Standardize heterogeneous datasets
- Ensure data consistency and quality
- Merge historical and recent data
- Prepare a unified dataset for analysis and modeling

## 2. Data Sources

The pipeline consumes four main CSV files:

- indicadores-continuidade-coletivos-2010-2019.csv | Historical indicators (2010–2019)
- indicadores-continuidade-coletivos-2020-2029.csv | Recent indicators (2020–2029)
- indicadores-continuidade-coletivos-atributos.csv | Additional attributes and complementary indicator data
- indicadores-continuidade-coletivos-limite.csv	| Regulatory limits for indicators

All files are stored in Google Drive and accessed via Google Colab.

## 3. Environment Setup

The pipeline starts by mounting Google Drive:

```
from google.colab import drive
drive.mount('/content/drive')
```

## 4. Data Loading

A reusable function is implemented to load CSV files:

```
def load_csv(path):
    try:
        return pd.read_csv(path, encoding='latin1', sep=';', low_memory=False)
    except Exception as e:
        print(f'Error loading {path}: {e}')
        return pd.DataFrame()
```

Key considerations:
- Encoding: latin1 is used due to special characters
- Delimiter: ; (semicolon)
- Error handling: Prevents pipeline failure by returning empty DataFrames

## 5. Data Cleaning and Standardization

A generalized cleaning function is applied to all datasets:

```
def clean_df(df, val_col, date_col='DatGeracaoConjuntoDados'):
```

### 5.1 Date Parsing
- Converts date columns to datetime
- Invalid values are coerced to NaT

### 5.2 Numeric Standardization
- Replaces comma decimal separators ("," → ".")
- Converts values to numeric (float)
- Handles invalid values using NaN

### 5.3 Column Type Normalization

The following columns are coerced to numeric:

- NumCNPJ
- IdeConjUndConsumidoras
- AnoIndice
- NumPeriodoIndice
- AnoLimiteQualidade
### 5.4 Text Standardization
- SigAgente is normalized to:
  - Uppercase
  - Trimmed (no leading/trailing spaces)

## 6. Data Consolidation
### 6.1 Merging Historical and Recent Data

```
df_10_29 = pd.concat([df_10_19, df_20_29], ignore_index=True)
```

### 6.2 Filtering by Minimum Year
A cutoff year is defined:

```
ANO_MINIMO = 2015
```

All datasets are filtered to include only recent data:

- Indicators (AnoIndice >= 2015)
- Attributes (AnoIndice >= 2015)
- Limits (AnoLimiteQualidade >= 2015)

## 7. Processing Regulatory Limits

The limits dataset is handled separately:

### 7.1 Column Alignment

```
df_limit_processed = df_limit_processed.rename(
    columns={
        'AnoLimiteQualidade': 'AnoIndice',
        'VlrLimite': 'VlrIndiceEnviado'
    }
)
```
This ensures compatibility with indicator datasets.

### 7.2 Indicator Expansion

The limits dataset is duplicated to represent both indicators:

- DEC
- FEC

```
df_limit_dec['SigIndicador'] = 'DEC'
df_limit_fec['SigIndicador'] = 'FEC'
```

Then merged:

```
df_limit = pd.concat([df_limit_dec, df_limit_fec], ignore_index=True)
```

### 7.3 Record Classification

A new column is introduced:

```
df_limit_processed['TipoRegistro'] = 'Limite'
```

## 8. Processing Measured Indicators
Indicator data (historical + attributes) is combined:

```
df_apurados = pd.concat([df_10_29, df_atrib], ignore_index=True)
df_apurados['TipoRegistro'] = 'Apurado'
```

## 9. Final Dataset Construction
### 9.1 Column Standardization

A common schema is defined:

```
common_cols = [
    'IdeConjUndConsumidoras',
    'SigIndicador',
    'AnoIndice',
    'NumPeriodoIndice',
    'VlrIndiceEnviado',
    'TipoRegistro'
]
```

### 9.2 Final Merge

```
df_indicadores = pd.concat([
    df_apurados[common_cols],
    df_limit[common_cols]
], ignore_index=True)
```

This produces a unified dataset containing:

- Measured values (Apurado)
- Regulatory limits (Limite)

## 10. Final Adjustments
### 10.1 Type Enforcement

```
df_indicadores['IdeConjUndConsumidoras'] = df_indicadores['IdeConjUndConsumidoras'].astype(int)
df_indicadores['AnoIndice'] = df_indicadores['AnoIndice'].astype(int)
```

### 10.2 Time Index Preparation
```
df_indicadores['NumPeriodoIndice_key'] = pd.to_numeric(
    df_indicadores['NumPeriodoIndice'], errors='coerce'
).fillna(0).astype(int)
```

This creates a clean numeric time index for:

- Sorting
- Time series modeling