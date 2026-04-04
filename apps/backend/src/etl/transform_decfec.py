import pandas as pd

def transform_decfec(df: pd.DataFrame) -> pd.DataFrame:
    df_original = df.copy(deep=True)
    df_work = df.copy(deep=True)

    total_linhas = len(df_work)
    total_colunas = len(df_work.columns)
    nomes_colunas = list(df_work.columns)

    analise_colunas = {}

    for coluna in nomes_colunas:
        serie = df_work[coluna]

        analise_colunas[coluna] = {
            "dtype_original": str(serie.dtype),
            "qtd_nulos": int(serie.isna().sum()),
            "qtd_nao_nulos": int(serie.notna().sum()),
            "qtd_valores_unicos": int(serie.nunique(dropna=False)),
        }

    colunas_texto = df_work.select_dtypes(include=["object", "string"]).columns.tolist()
    colunas_numericas = df_work.select_dtypes(include=["number"]).columns.tolist()

    previews_texto = {}
    for coluna in colunas_texto:
        serie_texto = df_work[coluna].astype("string")
        serie_normalizada = serie_texto.str.strip()

        previews_texto[coluna] = {
            "amostra_original": serie_texto.head(3).tolist(),
            "amostra_normalizada": serie_normalizada.head(3).tolist(),
        }

    previews_numericos = {}
    for coluna in colunas_numericas:
        serie_num = pd.to_numeric(df_work[coluna], errors="coerce")

        previews_numericos[coluna] = {
            "min": None if serie_num.dropna().empty else float(serie_num.min()),
            "max": None if serie_num.dropna().empty else float(serie_num.max()),
            "media": None if serie_num.dropna().empty else float(serie_num.mean()),
        }

    duplicados_aparentes = int(df_work.duplicated().sum())

    completude_por_coluna = {
        coluna: {
            "preenchimento_percentual": (
                float((df_work[coluna].notna().sum() / total_linhas) * 100)
                if total_linhas > 0 else 0.0
            )
        }
        for coluna in nomes_colunas
    }

    _metadata_transformacao = {
        "linhas_entrada": total_linhas,
        "colunas_entrada": total_colunas,
        "duplicados_identificados": duplicados_aparentes,
        "colunas_texto": colunas_texto,
        "colunas_numericas": colunas_numericas,
        "analise_colunas": analise_colunas,
        "previews_texto": previews_texto,
        "previews_numericos": previews_numericos,
        "completude_por_coluna": completude_por_coluna,
    }

    return df_original