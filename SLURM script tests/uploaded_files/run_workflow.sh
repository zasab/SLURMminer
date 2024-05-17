#!/bin/bash

# Change mode of all files in the current directory to executable
chmod +x *

# Remove some files and directories
rm -rf *.log
rm -rf *.txt
rm -rf times

# Convert line endings from DOS to UNIX format for all files
dos2unix *

# Execute sbatch_file.sh
sbatch 2856_srun_file1.sh
