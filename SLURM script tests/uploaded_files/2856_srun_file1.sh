#!/usr/local_rwth/bin/zsh

# Runtime and memory
#SBATCH --mem-per-cpu=6G

# For parallel jobs
#SBATCH --cpus-per-task=16
#SBATCH --nodes=2
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --output=2856_srun_file1_res_%j.txt

#### Your shell commands below this line ####

# Set a reasonable RLIMIT_NPROC
ulimit -u 10000

CURRENT_DIR=$(pwd)
PYTHON_PATH=$(which python3)

export LD_LIBRARY_PATH="/usr/local_rwth/sw/python/3.8.7/x86_64/lib/:${LD_LIBRARY_PATH}"
srun ${CURRENT_DIR}/wrap_time.sh ${PYTHON_PATH} srun_file1.py

if [ $? -eq 0 ]; then
    echo "0" >> "file1_${SLURM_JOB_ID}.txt"
    exit 0
else
    echo "1" >> "file2_${SLURM_JOB_ID}.txt"
    exit 1
fi
