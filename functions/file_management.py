import os
import shutil

def save_value(value, file_name):
    with open(file_name, 'w') as file:
        file.write(value)

def get_value(file_name):
    with open(file_name, 'r') as file:
        return file.read()

def remove_files_and_folders_from_list(folderdir, txt_file_path):
    try:
        with open(txt_file_path, 'r') as file:
            paths_list = file.readlines()
        
        for path in paths_list:
            # Remove leading/trailing whitespaces and newlines
            path = path.strip()
            full_path = os.path.join(folderdir, path)
            if os.path.exists(full_path):
                if os.path.isfile(full_path):
                    os.remove(full_path)
                elif os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    print(f"Unable to remove: {full_path} (not a file or directory)")
    
    except Exception as e:
        print(f"An error occurred: {e}")