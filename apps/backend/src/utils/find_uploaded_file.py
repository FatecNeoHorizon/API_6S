import os

def find_file_full_path(file_name, search_folder):
    for root, dirs, files in os.walk(search_folder):
        if file_name in files:
            return os.path.join(root, file_name)
    return None