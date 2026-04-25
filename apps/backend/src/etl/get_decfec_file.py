import os
from pathlib import Path


PREFERRED_FILENAME = "indicadores-continuidade-coletivos-2020-2029.csv"


def get_filepath() -> str:
    path_value = os.getenv("CSV_FILE_NAME")
    if not path_value:
        raise ValueError("CSV_FILE_NAME environment variable is not set.")

    path = Path(path_value)

    if path.is_file():
        return str(path)

    if path.is_dir():
        preferred_file = path / PREFERRED_FILENAME
        if preferred_file.is_file():
            return str(preferred_file)

        csv_files = sorted(path.glob("*.csv"))
        if len(csv_files) == 1:
            return str(csv_files[0])

        if len(csv_files) > 1:
            raise ValueError(
                "CSV_FILE_NAME points to a directory with multiple CSV files. "
                "Set CSV_FILE_NAME to a single file path."
            )

        raise ValueError(
            "CSV_FILE_NAME points to a directory, but no CSV files were found."
        )

    raise ValueError(
        f"CSV_FILE_NAME does not exist: {path_value}"
    )