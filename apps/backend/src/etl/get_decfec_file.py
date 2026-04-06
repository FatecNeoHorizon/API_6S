import os 

def get_filepath() -> str:
    path = os.getenv("CSV_FILE_PATH")
    if not path:
        raise ValueError("CSV_FILE_PATH environment variable is not set.")
    return path