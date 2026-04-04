import os

from src.etl.get_decfec_file import get_filepath
from pymongo import MongoClient
import pandas as pd

def load_decfec():

    FILE_PATH = get_filepath()

    port = os.getenv("MONGO_PORT", "27017")
    user = os.getenv("MONGO_USER")
    password = os.getenv("MONGO_PASSWORD")
    db_name = os.getenv("MONGO_DB_NAME")
    mongo_uri = f"mongodb://{user}:{password}@mongo_db:{port}/{db_name}?authSource=admin"

    df = pd.read_csv(
        FILE_PATH,
        sep=';',
        encoding='latin-1',
    )

    filtro = ['DEC', 'FEC']

    df_filtrado = df[df['SigIndicador'].isin(filtro)]

    df_filtrado = (
        df_filtrado
        .drop_duplicates()
        .dropna(subset=['SigIndicador'])
        .reset_index(drop=True)
    )


    df_filtrado = df_filtrado.rename(columns={
        'SigAgente': 'agent_acronym',
        'NumCNPJ': 'cnpj_number',
        'IdeConjUndConsumidoras': 'consumer_unit_set_id',
        'DscConjUndConsumidoras': 'consumer_unit_set_description',
        'SigIndicador': 'indicator_type_code',
        'AnoIndice': 'year',
        'NumPeriodoIndice': 'period',
        'VlrIndiceEnviado': 'value',
        'DatGeracaoConjuntoDados': 'generation_date',
    })

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db['distribution_indices']

    df_filtrado['generation_date'] = pd.to_datetime(df_filtrado['generation_date'], errors='coerce')
    df_filtrado['year'] = df_filtrado['year'].fillna(0).astype(int)
    df_filtrado['period'] = df_filtrado['period'].fillna(0).astype(int)
    df_filtrado['value'] = pd.to_numeric(df_filtrado['value'], errors='coerce')
    df_filtrado['cnpj_number'] = df_filtrado['cnpj_number'].astype(str)
    df_filtrado['consumer_unit_set_id'] = df_filtrado['consumer_unit_set_id'].astype(str)
    df_filtrado['value'] = pd.to_numeric(df_filtrado['value'], errors='coerce').fillna(0.0)

    df_filtrado = df_filtrado.drop_duplicates().reset_index(drop=True)

    registros = df_filtrado.to_dict(orient='records')

    resultado = collection.insert_many(registros)

    return resultado.inserted_ids
if __name__ == "__main__":
    load_decfec()