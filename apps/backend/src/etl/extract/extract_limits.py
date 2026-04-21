import pandas as pd
import os
from pathlib import Path

#The list returned can be retrieved with commands such as "data_dict[1]" or data_dict[1]['UF']
#Only the 'DatGeracaoConjuntoDados' column won't be used

def extract_limits():
    path_value = os.getenv("LIMITS_FILE_PATH")
    
    if not path_value:
        raise ValueError("LIMITS_FILE_PATH environment variable is not set.")

    path = Path(path_value)

    df : pd.DataFrame = pd.read_csv(path, sep=";", encoding="latin-1")
    df = df.drop(columns=['DatGeracaoConjuntoDados'])
    data_dict = df.to_dict(orient='records')

    #For demonstration purposes, only the first 50 items are returned to be showed on the test endpoint
    return data_dict[0:50]