import os
import pandas as pd
from pathlib import Path
from src.utils.find_uploaded_file import find_file_full_path

#The list returned can be retrieved with commands such as "data_dict[1]" or data_dict[1]['UF']
#All columns of the excel file will be used
def extract_losses():

    file_name = os.getenv("LOSSES_FILE_NAME")
    search_folder = os.getenv("TMP_UPLOAD_PATH")

    path_value = find_file_full_path(file_name, search_folder)
    
    if not path_value:
        raise ValueError("LOSSES_FILE_NAME environment variable is not set.")

    path = Path(path_value)

    df = pd.read_excel(path)
    data_dict = df.to_dict(orient='records')

    return data_dict
