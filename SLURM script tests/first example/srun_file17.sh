#!/usr/local_rwth/bin/zsh

job_name=$(basename "$0" .sh)
#SBATCH --job-name="$job_name"
#SBATCH --output=output_%j.log
#SBATCH --partition=your_partition  # Specify the partition you want to use
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=4G
#SBATCH --time=1:00:00

# Load any necessary modules or set up the environment
# module load your_module

# Run the shell script with srun
srun ./app17.sh