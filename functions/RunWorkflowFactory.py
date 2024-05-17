def run_workflow_content(run_workflow_file, sbatch_file_name):
    text1 = """#!/bin/bash

# Change mode of all files in the current directory to executable
chmod +x *

# Remove some files and directories
rm -rf *.log
rm -rf *.txt
rm -rf times

# Convert line endings from DOS to UNIX format for all files
dos2unix *

# Execute sbatch_file.sh
sbatch {0}
""".format(sbatch_file_name)

    run_workflow_file.write(text1)

def create(run_workflow_file_path, sbatch_file_name):
    run_workflow_file = open(run_workflow_file_path, 'w')
    run_workflow_content(run_workflow_file, sbatch_file_name)