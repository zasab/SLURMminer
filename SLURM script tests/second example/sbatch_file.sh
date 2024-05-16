#!/usr/local_rwth/bin/zsh

JOB_ID_1=$(sbatch --parsable srun_file1.sh)
JOB_ID_2=$(sbatch --parsable --dependency=afterok:$JOB_ID_1 srun_file2.sh)
JOB_ID_3=$(sbatch --parsable --dependency=afterok:$JOB_ID_2 srun_file3.sh)
JOB_ID_4=$(sbatch --parsable --dependency=afterok:$JOB_ID_2 srun_file4.sh)
JOB_ID_5=$(sbatch --parsable --dependency=afterok:$JOB_ID_3,$JOB_ID_4 srun_file5.sh)
JOB_ID_6=$(sbatch --parsable --dependency=afterok:$JOB_ID_5 srun_file6.sh)
JOB_ID_7=$(sbatch --parsable --dependency=afterok:$JOB_ID_6 srun_file7.sh)
JOB_ID_8=$(sbatch --parsable --dependency=afterok:$JOB_ID_5 srun_file8.sh)
JOB_ID_9=$(sbatch --parsable --dependency=afterok:$JOB_ID_8 srun_file9.sh)
JOB_ID_17=$(sbatch --parsable --dependency=afterok:$JOB_ID_5 srun_file17.sh)
JOB_ID_10=$(sbatch --parsable --dependency=afterany:$JOB_ID_9:$JOB_ID_7,$JOB_ID_17 srun_file10.sh)

