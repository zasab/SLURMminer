#!/bin/bash

#SBATCH --mem-per-cpu=6G
#SBATCH --cpus-per-task=16
#SBATCH --nodes=2
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --output=discovery_res_%j.txt

# Load Python module (adjust this according to your cluster environment)
module load Python/3.9.6

# Execute the Python script using srun
srun python3 discovery.py running-example.xes

if [ $? -eq 0 ]; then
    echo "0" >> "exit_code1_${SLURM_JOB_ID}.txt"
    exit 0
else
    echo "1" >> "exit_code2_${SLURM_JOB_ID}.txt"
    exit 1
fi