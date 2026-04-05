from src.etl.get_decfec_file import get_filepath
from src.etl.transform_decfec import transform_decfec
from src.config.parameters import get_mongo_settings, get_mongo_uri
from pymongo import MongoClient
import pandas as pd

def load_decfec():
    FILE_PATH = get_filepath()

    _, _, _, _, db_name = get_mongo_settings()
    mongo_uri = get_mongo_uri()

    df = pd.read_csv(
        FILE_PATH,
        sep=';',
        encoding='latin-1',
    )

    df = transform_decfec(df)
    
    filtro = [
        'DEC', 
        'DEC1i', 
        'DEC1x', 
        'DECINC', 
        'DECIND', 
        'DECINE', 
        'DECINO', 
        'DECIP', 
        'DECIPC', 
        'DECXN', 
        'DECXNC', 
        'DECXP', 
        'DECXPC', 
        'DECi', 
        'DECx', 
        'Dec1', 
        'Dec1r', 
        'Decr', 
        'FEC', 
        'FEC1i', 
        'FEC1x', 
        'FECINC', 
        'FECIND', 
        'FECINE', 
        'FECINO', 
        'FECIP', 
        'FECIPC', 
        'FECXN', 
        'FECXNC', 
        'FECXP', 
        'FECXPC', 
        'FECi', 
        'FECx', 
        'Fec1', 
        'Fec1r', 
        'Fecr'
    ]

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

    df_filtrado['generation_date'] = df_filtrado['generation_date'].fillna('').astype(str)
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