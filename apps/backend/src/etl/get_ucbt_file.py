import os


def get_ucbt_filepath():
    return os.getenv("UCBT_CSV_FILE_PATH") or os.getenv("CSV_FILE_PATH")