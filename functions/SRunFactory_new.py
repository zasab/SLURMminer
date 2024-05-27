from functions import BpmnUtils
import config


def srun_file_content(srun_file, srun_file_name, command):
    text1 = """#!/bin/bash

#SBATCH --mem-per-cpu=6G
#SBATCH --cpus-per-task=16
#SBATCH --nodes=2
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --output={0}_res_%j.txt

# Load Python module (adjust this according to your cluster environment)
module load Python/3.9.6

# Execute the Python script using srun
srun python3 {1}
""".format(srun_file_name[:-3], command)
    
    text2 = """
if [ $? -eq 0 ]; then
    echo "0" >> "exit_code1_${SLURM_JOB_ID}.txt"
    exit 0
else
    echo "1" >> "exit_code2_${SLURM_JOB_ID}.txt"
    exit 1
fi
"""

    srun_file.write(text1 + text2)

def create(srun_file_name, command, should_be_uploaded_list):
    srun_file_path = "{}/{}".format(config.bpmn.uploaded_files_directory, srun_file_name)
    should_be_uploaded_list.add(srun_file_path)
    srun_file = open(srun_file_path, 'w')
    srun_file_content(srun_file, srun_file_name, command)