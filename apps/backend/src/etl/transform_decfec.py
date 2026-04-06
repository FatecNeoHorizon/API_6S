import pandas as pd


def transform_decfec(df: pd.DataFrame) -> pd.DataFrame:
    df_work = df.copy(deep=True)

    # --- Texto: strip ---
    colunas_texto = df_work.select_dtypes(include=["object", "string"]).columns.tolist()
    for coluna in colunas_texto:
        df_work[coluna] = df_work[coluna].astype("string").str.strip()

    # --- VlrIndiceEnviado: vírgula → ponto, converte para float ---
    if "VlrIndiceEnviado" in df_work.columns:
        df_work["VlrIndiceEnviado"] = (
            df_work["VlrIndiceEnviado"]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .pipe(pd.to_numeric, errors="coerce")
        )

    # --- Tipos garantidos para o validator do Mongo ---
    if "AnoIndice" in df_work.columns:
        df_work["AnoIndice"] = (
            pd.to_numeric(df_work["AnoIndice"], errors="coerce").fillna(0).astype(int)
        )

    if "NumPeriodoIndice" in df_work.columns:
        df_work["NumPeriodoIndice"] = (
            pd.to_numeric(df_work["NumPeriodoIndice"], errors="coerce").fillna(0).astype(int)
        )

    return df_work