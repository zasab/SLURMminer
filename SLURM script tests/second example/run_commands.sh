#!/bin/bash

# Change mode of all files in the current directory to executable
chmod +x *

# Remove all files with the .log extension
rm -rf *.log
rm -rf *.txt

# Convert line endings from DOS to UNIX format for all files
dos2unix *

# Execute sbatch_file.sh
./sbatch_file.sh
