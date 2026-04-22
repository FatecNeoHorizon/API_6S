import os
import pandas as pd
from pathlib import Path

#The list returned can be retrieved with commands such as "data_dict[1]" or data_dict[1]['UF']
#All columns of the excel file will be used
def extract_losses():

    # path_value = os.getenv("LOSSES_FILE_PATH")
    file_name = os.getenv("LOSSES_FILE_PATH")
    search_folder = os.getenv("TMP_UPLOAD_PATH")

    path_value = _find_file(file_name, search_folder)
    
    if not path_value:
        raise ValueError("LOSSES_FILE_PATH environment variable is not set.")

    path = Path(path_value)

    df = pd.read_excel(path)
    data_dict = df.to_dict(orient='records')

    return data_dict

def _find_file(file_name, search_folder):
    for root, dirs, files in os.walk(search_folder):
        if file_name in files:
            return os.path.join(root, file_name)
    return None