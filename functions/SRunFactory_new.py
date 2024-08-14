from functions.graphObject import JOB
import config
from pm4py.objects.bpmn.obj import BPMN


def srun_file_content(srun_file, srun_file_name, command):
    text1 = """#!/bin/bash

# Assuming the first argument is FILES_DIR
FILES_DIR=$1$2
mkdir $FILES_DIR

#SBATCH --mem-per-cpu=6G
#SBATCH --cpus-per-task=16
#SBATCH --nodes=2
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --output={0}_res_%j.txt

# Execute the Python script using srun
srun python3 {1}
""".format(srun_file_name[:-3], command)
    
    text2 = """
if [ $? -eq 0 ]; then
    echo "0" >> "exit_code0_${SLURM_JOB_ID}.txt"
    exit 0
else
    echo "1" >> "exit_code1_${SLURM_JOB_ID}.txt"
    exit 1
fi
"""

    srun_file.write(text1 + text2)

def create(should_be_uploaded_list):
    for job in JOB.get_all_jobs():
        # if job.get_choice_flag():
        # print()
        # job_task = job.get_task()
        # print("task: ", job_task)
        # print("job id: ", job.get_job_id())
        # print("choice_flag: ", job.get_choice_flag())
        # print("application: ", job.get_application())
        # print("srun_file_name: ", job.get_srun_file_name())
        # print("input_files: ", job.get_input_files())
        # print("output_file: ", job.get_output_file())
        # print("dependency_script: ", job.get_dependency_script())
        # print()
        # new_command = f"{job.get_application()}{' ' +' '.join(job.get_input_files()) if job.get_input_files() else ''} {len(job.get_input_files())}{' ' +job.get_output_file()[0] if job.get_output_file() else ''} {len(job.get_output_file())}"
        new_command = f"{job.get_application()}{' $FILES_DIR'}{' ' +' '.join(['$FILES_DIR/'+file for file in job.get_input_files()]) if job.get_input_files() else ''} {len(job.get_input_files())}{' ' +' '.join(['$FILES_DIR/'+file for file in job.get_output_file()]) if job.get_output_file() else ''} {len(job.get_output_file())}"
        srun_file_name = job.get_srun_file_name()
        srun_file_path = "{}/{}".format(config.bpmn.uploaded_files_directory, srun_file_name)
        should_be_uploaded_list.add(srun_file_path)
        srun_file = open(srun_file_path, 'w')
        srun_file_content(srun_file, srun_file_name, new_command)
