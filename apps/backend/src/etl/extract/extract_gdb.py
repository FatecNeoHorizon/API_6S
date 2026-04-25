import geopandas as gpd
import os
from pathlib import Path
from src.utils.find_uploaded_file import find_file_full_path

def extract_gdb():

    file_name = os.getenv("GDB_FILE_PATH")
    search_folder = os.getenv("TMP_UPLOAD_PATH")

    path_value = find_file_full_path(file_name, search_folder)
    
    if not path_value:
        raise ValueError("GDB_FILE_PATH environment variable is not set.")

    path = Path(path_value)

    layers = gpd.list_layers(path)

    df = gpd.read_file(path)
    tables = layers["name"].tolist()

    tables_dict = dict(enumerate(tables))

    return tables_dict
