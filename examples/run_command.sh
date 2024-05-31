#!/bin/bash

# Check if the script file is provided as an argument
if [ $# -ne 1 ]; then
    echo "Usage: $0 <sbatch_script>"
    exit 1
fi

# Assign the argument to the script variable
sbatch_script="$1"

# Change mode of all files in the current directory to executable
chmod +x *

# Remove all files with the .log extension
rm -rf *.log
rm -rf *.txt

# Convert line endings from DOS to UNIX format for all files
dos2unix *

# Execute provided sbatch script
./"$sbatch_script"
