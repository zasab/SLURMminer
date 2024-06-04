import config

def commands_content(run_command_file, sbatch_file_name, zipped_script_folder_fullname, zipped_script_folder_name):
    text1 = """#!/bin/bash

# Change mode of all files in the current directory to executable
chmod +x *

# Remove all files with the .log extension
rm -rf *.log
rm -rf *.txt

# Unzip the folder named script (assuming it's a zip archive)
unzip -q {1}

# Move all contents of the script folder outside of its directory
mv {2}/* .

# Remove the empty script directory
rm -rf {2}

# Load Python module
module load Python/3.9.6

# Uninstall cvxopt
pip3 uninstall cvxopt -y

# Change mode of all files in the current directory to executable
chmod +x *

# Convert line endings from DOS to UNIX format for all files
dos2unix *

nohup ./squeue_logger.sh &

# Execute {0}
./{0}
""".format(sbatch_file_name, zipped_script_folder_fullname, zipped_script_folder_name)

    run_command_file.write(text1)

def create(run_command_filename, sbatch_file_name, zipped_script_folder_fullname, should_be_uploaded_list):
    run_command_file_path = "{}/{}".format(config.bpmn.uploaded_files_directory, run_command_filename)
    should_be_uploaded_list.add(run_command_file_path)
    run_command_file = open(run_command_file_path, 'w')
    zipped_script_folder_name = zipped_script_folder_fullname.split('.')
    commands_content(run_command_file, sbatch_file_name, zipped_script_folder_fullname, zipped_script_folder_name[0])
        