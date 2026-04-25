import pandas as pd
import os
from pathlib import Path
from src.utils.find_uploaded_file import find_file_full_path

#The list returned can be retrieved with commands such as "data_dict[1]" or data_dict[1]['UF']
#Only the 'DatGeracaoConjuntoDados' column won't be used
def extract_limits():

    file_name = os.getenv("LIMITS_FILE_NAME")
    search_folder = os.getenv("TMP_UPLOAD_PATH")

    path_value = find_file_full_path(file_name, search_folder)
    
    if not path_value:
        raise ValueError("LIMITS_FILE_NAME environment variable is not set.")

    path = Path(path_value)

    df : pd.DataFrame = pd.read_csv(path, sep=";", encoding="latin-1")
    df = df.drop(columns=['DatGeracaoConjuntoDados'])
    data_dict = df.to_dict(orient='records')

    #For demonstration purposes, only the first 50 items are returned to be showed on the test endpoint
    return data_dict[0:50]